from flask import Flask,render_template,request,url_for,send_from_directory,redirect,send_file
from multiprocessing import Process,Manager
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from wellfoundscrape.spiders.jobscrape import JobscrapeSpider
import pandas as pd
import os
from datetime import datetime
import json

keyword_list = []
generated_files = []

app = Flask(__name__,template_folder="templates")

@app.route('/')

def scraper_html():
    return render_template("Wellfound_scraper.html")

@app.route('/search',methods=['GET','POST'])
def submit():
    if request.method == 'POST':
        keyword = request.form['job_role']
        global k
        k = keyword
        manager = Manager()
        generated_files = manager.list()
        keyword_list = keyword.split(',')

        for i in keyword_list:
            p = Process(target=run_spider , args= (i,generated_files))
            p.start()
            p.join()
    return render_template('page.html', keyword = keyword,fl_name=list(generated_files))

def run_spider(keyword, generated_files):

    keyword_list = keyword
    # to get the current date and time to add to filename
    cdt = (datetime.now().strftime("%Y_%B_%d_%H_%M_%S")).replace(":",'')
    # we are setting the settings to settings.py
    settings = get_project_settings()
    settings.set("FEED_FORMAT", "json")
    settings.set("FEED_URI", f"{keyword}_{cdt}.json")
    #Run scrapy spider with latest input
    process = CrawlerProcess(settings)
    process.crawl(JobscrapeSpider, keyword_list = keyword_list)
    process.start()
    process.join()

    file_name = f"{keyword}_{cdt}.json"
    file_path = os.path.join(os.getcwd(),file_name)

    if os.path.exists(file_path):
        data_df = pd.read_json(file_path)

        #From data_df we are fetching relevant data and saving to two dataframes
        Jobs_df = data_df.iloc[:,:19].dropna(subset=['Job title'])
        Company_df = data_df.iloc[:,18:].dropna(subset=['Company Name'])
        Merged_df = pd.merge(Jobs_df, Company_df, on='Company Page Link')

        #Save dataframes to csv with required text, current date and time
        current_datetime = datetime.now().strftime("%Y%b%d_%H:%M:%S")
        ct = current_datetime.replace(":",'')

        #creating respective csv files with the names fetched from above
        jobs_csv_name = f"Jobs_{keyword}_{ct}.csv"
        company_csv_name =f"Company_{keyword}_{ct}.csv"
        merged_csv_name = f"Merged_{keyword}_{ct}.csv"

        Jobs_df.to_csv(jobs_csv_name, index=False)
        Company_df.to_csv(company_csv_name, index=False)
        Merged_df.to_csv(merged_csv_name, index=False)

        generated_files.extend([jobs_csv_name, company_csv_name, merged_csv_name])
        os.remove(file_name)

    else:
        print(f"File '{file_name}' not found")

@app.route('/files/<filename>')
def download_file(filename):
    return send_from_directory(os.getcwd(), filename)


if __name__ == '__main__':
    app.run(debug=True)





