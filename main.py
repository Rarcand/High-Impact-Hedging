import os
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from data.scraper import EventSpider
from data.volatility import print_volatility
from model.model import main as run_model

def get_user_dates():
    """Prompt the user for start and end dates and validate them."""
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    # Convert to datetime objects
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    if end_dt < start_dt:
        print("Error: End date cannot be before start date.")
        exit()

    return start_date, end_date

def run_spider(start_date, end_date):
    """Run Scrapy spider with the provided date range."""
    process = CrawlerProcess(get_project_settings())
    process.crawl(EventSpider, start_date=start_date, end_date=end_date)
    process.start()

if __name__ == "__main__":
    start_date, end_date = get_user_dates()  # Get user-defined date range
    run_spider(start_date, end_date)  # Run Scrapy with the given dates
    print_volatility()  # Print volatility after the spider finishes
    run_model()  # Run model to filter high-impact events
