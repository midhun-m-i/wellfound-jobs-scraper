import scrapy
from datetime import datetime
from scrapy.selector import Selector



class JobscrapeSpider(scrapy.Spider):
    name = "jobscrape"

    def __init__(self, keyword_list, location='united-states', *args, **kwargs):
        print("Keyword list", keyword_list)
        super(JobscrapeSpider, self).__init__(*args, **kwargs)
        #Formatting the search text
        k1=[]
        k1.append(keyword_list.strip())
        self.keyword_list = k1
        self.location = location
        self.start_urls = [self.construct_url()]

    def construct_url(self):
        for k in self.keyword_list:
            base_url = "https://wellfound.com/role/l"
            return f"{base_url}/{k.replace(' ', '-').lower()}/{self.location}"

    def parse(self, response):
        jobs = response.css('div[class="styles_jobListingList__32RYX"] a::attr(href)').getall()
        #Iterating through each jobs in a page
        for job in jobs:
            job_url = 'https://wellfound.com' + job
            yield response.follow(job_url, callback=self.parse_job_page)

        #Looping through each page(commend this looping for crawling the first page only (for faster output/testing))
        next_page = response.css('li[class=styles_next__Dugw4] a::attr(href)').get()

        if next_page is not None:
            next_page_url = 'https://wellfound.com' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_job_page(self,response):
        #Extracting the salary and formatting it.
        sal=response.css('div[class="w-full sm:w-2/3"]').css('div[class="mt-2 text-lg font-medium text-gray-800"]::text').get()
        if sal is not None:
            sal = sal.split('•')[0]
            l = sal.split('–')
            min_sal = l[0]
            max_sal = l[-1]
        else:
            min_sal = None
            max_sal = None

        #Getting current date
        today = datetime.now().strftime('%d-%m-%Y')
        #Extracting the job posted date and formatting it.
        posted_date = response.css('div[class="w-full sm:w-2/3"]').css('div[class="mb-4 mt-1 text-sm font-medium text-gray-800"]::text').getall()
        if len(posted_date)>1:
            posted_date ="".join(posted_date[len(posted_date)-1])
        elif len(posted_date)==0:
            posted_date = None
        else:
            posted_date ="".join(posted_date)

        #Getting the job id from the page url
        page_link=response.url
        parts = page_link.split('/')
        if len(parts) > 2 and not any(ext in parts[-1] for ext in ['.html', '.pdf', '.com']):
            job_id = parts[-1]
            job_id = job_id[0:7]
            if '-' in job_id:
                job_id = job_id[0:6]

        #Extracting the location date and formatting it.
        location = response.css('div[class="flex flex-wrap"] a::text').getall()
        if location is not None:
            location = ",".join(location)
        else:
            location = None

        # Extracting the skills date and formatting it.
        skills = response.css('div[class="mr-2 mt-2 rounded-3xl bg-gray-200 px-2 py-1 text-sm font-normal text-black"]::text').getall()
        if skills is not None:
            skills = ",".join(skills)
            if skills == "":
                skills = None
        else:
            skills = None

        job_description = response.css('div.styles_description__o_yxO#job-description').getall()
        # Combine and clean the extracted text
        description_text = ''.join(job_description)
        sel = Selector(text=description_text)

        # Remove HTML tags
        cleaned_text = sel.xpath('//text()').getall()
        # Join the text lines and strip whitespace
        cleaned_text = ' '.join(cleaned_text).strip()
        cleaned_text = cleaned_text.replace('\n', '')

        # Extracting the company type and formatting it.
        company_type = response.css('div[class="flex items-start gap-2"] div[class="rounded-3xl bg-gray-200 px-2 py-1 text-sm font-normal text-black"]::text').getall()
        if company_type is not None:
            company_type = ','.join(company_type)
            if company_type == "":
                company_type = None
        else:
            company_type = None

        # Extract the src attribute
        logo_url = response.css(
            'div.relative.inline-flex.h-14.w-14.flex-row.items-center.rounded-md img::attr(src)').get()

        # Extract the part starting from "https://"
        clean_url = ''
        if logo_url:
            start_index = logo_url.find('https://')
            if start_index != -1:
                clean_url = logo_url[start_index:]
        next_url = response.css('div.content-center a::attr(href)').get()
        company_url = "https://wellfound.com"+ next_url



        yield {
            'Job title': response.css('div[class="w-full sm:w-2/3"] h1::text').get(),
            'Company_name': response.css('div[class="w-full sm:w-2/3"]').css('div[class="content-center"] span::text').get(),
            #'Salary': sal,
            'Minimum salary': min_sal,
            'Maximun salary':max_sal,
            'Posted date': posted_date,
            'Location': location,
            'Job type': response.css('div:nth-child(2) p::text').get(),
            'Visa sponsorship': response.css('div:nth-child(3) p span::text').get(),
            'Jobcard page link': response.url,
            'Jobcard ID': job_id,
            'Scrapping date': today,
            'Search phrase' : self.keyword_list,
            'Skills' : skills,
            'Preferred timezones': response.xpath('//div[@class="grid grid-cols-1 gap-6 p-4 py-6 md:grid-cols-2"] //div[@class="flex flex-wrap"]/text()').get(),
            'Job description': cleaned_text,
            'Role': response.css('div[class="w-full sm:w-2/3"] h1::text').get(),
            'Company type': company_type,
            'Company logo': clean_url,
            'Company Page Link': company_url


        }
        yield response.follow(company_url, callback=self.parse_company_page)

    def parse_company_page(self, response):
        # Getting current date
        today = datetime.now().strftime('%d-%m-%Y')
        # Formatting company locations and providing null value if not present.
        company_locations = response.xpath('//div[@class="styles_component__eH77m"] //a[@class="styles_component__UCLp3 styles_defaultLink__eZMqw !text-dark-aaa underline"]/text()').getall()
        if company_locations is not None:
            company_locations = ",".join(company_locations)
        else:
            company_locations = None

        # Formatting company markets and providing null value if not present.
        markets = response.xpath('//dt[@class="styles_tags__y_J8v"]//span[@class="underline styles-module_component__2E93_ inline-flex flex-row items-center mr-2 last:mr-0 rounded-full align-middle bg-gray-200 text-gray-700 gap-2 text-xs px-3 py-1"]/text()').getall()
        if markets is not None:
            markets = ",".join(markets)
        else:
            markets = None

        cpl = response.url

        company_data = {
                'Company Name': response.css('div[class="styles_name__qn8jG"] a::text').get(),
                'Company title': response.css('div[class="styles_name__qn8jG"] h2::text').get(),
                'Company description': ''.join(response.css('div[class="styles_description__YMjmO"] div::text').getall()),
                'Company Website': response.xpath('//div[@class="styles_component__g_WAp styles_links__VvYv7"] //button[@class="styles_websiteLink___Rnfc"]/text()').get(),
                'Company locations': company_locations,
                'Company size': response.xpath('//div[@class="styles_component__eH77m"]//dd[text()="Company size"]//following-sibling::dt/text()').get(),
                'Markets': markets,
                'Scrapping_date':today,
                'Company Page Link': cpl,

            }

        #Creating company_tabs for looping through each tab and extracting details from it.
        company_tabs = ['people', 'culture_and_benefits', 'jobs', 'funding']
        for tab in company_tabs:
            tab_url = f"{response.url}/{tab}"
            yield response.follow(tab_url, callback=self.parse_company_tab,meta={'company_data': company_data, 'tab': tab})

    def parse_company_tab(self,response):
        company_data = response.meta['company_data']
        tab = response.meta['tab']

        if tab == 'people':
            # Formatting company founders.
            founders = response.xpath(
                '//div[@class="styles_component__ivX7J styles_twoColumn__XlBrn"]//h4/text() | //div[@class="styles_component__ivX7J styles_twoColumn__XlBrn"]//h4//a/text()').getall()
            if founders is not None:
                founders = ",".join(founders)

            #Formatting team.
            team = response.xpath(
                '//div[@class="styles_component__ivX7J styles_threeColumn__Txyiv"]//h4/text()').getall()
            if team is not None:
                team = ",".join(team)

            company_data['Founders'] = founders if founders else None
            company_data['Team'] = team if team else None

        if tab == 'culture_and_benefits':
            culture_overview = response.xpath(
                '//div[@class="flex flex-col gap-8"]//div[@class="styles_statement__o2uzj styles_component__481pO"]//text()').getall()
            # Combine and clean the extracted text
            culture_overview = ''.join(culture_overview)
            sel = Selector(text=culture_overview)

            # Remove HTML tags
            cleaned_overview = sel.xpath('//text()').getall()
            # Join the text lines and strip whitespace
            cleaned_overview = ' '.join(cleaned_overview).strip()

            #Formatting perks and benefits
            perks_and_benefits = response.xpath(
                '//div[@class="styles_component__ivX7J mb-8 lg:mb-12 styles_twoColumn__XlBrn"]//h4/text()').getall()
            if perks_and_benefits is not None:
                perks_and_benefits = ",".join(perks_and_benefits)

            company_data['Culture Overview'] = cleaned_overview if cleaned_overview else None
            company_data['Perks and benefits'] = perks_and_benefits if perks_and_benefits else None

        if tab == 'jobs':
            posted_jobs = response.xpath('//a[@class="styles_component__UCLp3 styles_defaultLink__eZMqw styles_anchor__aTiEC styles_body__KvYlr"]//h4/text()').getall()
            posted_date = response.xpath('//div[@class="styles_headerRight__iwb9v"]//span[@class="styles_desktop__m9OkS"]/text()').getall()
            #Formatting available jobs and its posted date into a single column
            i = 0
            l = []
            while (i < len(posted_date)):
                for job in posted_jobs:
                    available_jobs = job + "    (" + posted_date[i] + " " + posted_date[i + 1] + ")"
                    i += 2
                    l.append(available_jobs)

            company_data['Available jobs'] = ",".join(l) if l else None

        if tab == 'funding':
            #Formatting the investors
            investors = response.xpath('//div[@class="styles_component__ivX7J styles_threeColumn__Txyiv"]//div[@class="styles_left__aDiT6"]//h4/text() | //div[@class="styles_component__ivX7J styles_threeColumn__Txyiv"]//div[@class="styles_left__aDiT6"]//h4//a/text()').getall()
            if investors is not None:
                investors = ",".join(investors)
            amount = response.xpath('//div[@class="styles_statement__thwrP"]//span[@class="styles_value__SHCrT"]/text()').get()
            rounds = response.xpath('//div[@class="styles_statement__thwrP"]//span[@class="styles_desktop__xTjjQ"]/text()').get()

            company_data['Total Funding(amount in $)'] = amount if amount else None
            company_data['Rounds'] = rounds if rounds else None
            company_data['Investors'] = investors if investors else None

        #Checking the company page tabs for yielding the company page data
        tabs_to_check = ['Company Name', 'Company title', 'Company description', 'Company Website', 'Company locations', 'Company size', 'Markets',
                         'Company Page Link', 'Founders', 'Team', 'Culture Overview', 'Perks and benefits', 'Available jobs', 'Total Funding(amount in $)', 'Rounds', 'Investors']
        if all(key in company_data for key in tabs_to_check):
            yield company_data


