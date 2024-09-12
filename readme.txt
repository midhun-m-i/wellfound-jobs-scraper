-------------Wellfound US Job scraper----------------

This is used for scraping job details and company details from wellfoundjobs.com.
Steps for running the project:

First create a virtual environment in the project folder
Install the requirements.txt (pip install -r requirements.txt)
Create a scrapeops account for proxy aggregator(refer : https://scrapeops.io/docs/web-scraping-proxy-api-aggregator/integration-examples/python-scrapy-example/)
Give API key in settings.py, set 'SCRAPEOPS_PROXY_ENABLED' to True and give some 'DOWNLOAD_DELAY'.
Then python main.py to run the flask application.