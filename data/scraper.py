import scrapy
import os
import pandas as pd
from pytz import timezone
from datetime import datetime, timedelta
from scrapy_playwright.page import PageMethod

class EventSpider(scrapy.Spider):
    name = "events"

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "COOKIES_ENABLED": True,
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    }

    def __init__(self, start_date=None, end_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

        # Convert date strings to datetime objects
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Generate the date range for the URLs
        self.start_urls = [
            f"https://www.forexfactory.com/calendar?day={(self.start_date + timedelta(days=i)).strftime('%b%d.%Y').lower()}"
            for i in range((self.end_date - self.start_date).days + 1)
        ]

    def format_date(self, date_str):
        dt = datetime.strptime(date_str, "%b%d.%Y")
        day_suffix = self.get_day_suffix(dt.day)
        return dt.strftime(f"%B {dt.day}{day_suffix}, %Y")

    @staticmethod
    def get_day_suffix(day):
        if 11 <= day <= 13:
            return "th"
        return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    def start_requests(self):
        for url in self.start_urls:
            date_str = url.split("day=")[-1]  # Extract the date from the URL
            formatted_date = self.format_date(date_str)
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "tr[data-event-id]"),
                    ],
                    "date": formatted_date  # Pass the formatted date
                },
            )

    async def parse(self, response):
        if response.status == 403:
            self.logger.error("Access Denied (403 Forbidden). Try changing the User-Agent or using proxies.")
            return

        page_date = response.meta.get("date")  # Get formatted date from URL
        rows = response.css("tr[data-event-id]")
        
        for row in rows:
            time = row.css("td.calendar__cell.calendar__time span::text").get()
            impact = row.css("td.calendar__cell.calendar__impact span::attr(title)").get()
            event_name = row.css("span.calendar__event-title::text").get()

            item = {
                "date": page_date,  # Include formatted date in output
                "time": time,
                "impact": impact,
                "event_name": event_name,
            }
            self.items.append(item)
            yield item

    def closed(self, reason):
        df = pd.DataFrame(self.items)

        # Forward-fill missing times
        df["time"] = df["time"].ffill()

        # Convert times from CT to ET
        ct = timezone('US/Central')
        et = timezone('US/Eastern')

        def convert_time(ct_time):
            if ct_time == 'All Day':
                return 'All Day'
            try:
                dt = pd.to_datetime(f'2025-03-31 {ct_time}', format='%Y-%m-%d %I:%M%p')
                dt_ct = ct.localize(dt)
                dt_et = dt_ct.astimezone(et)
                return dt_et.strftime('%-I:%M%p').lower()
            except:
                return None

        df["time"] = df["time"].apply(convert_time)

        # Save to CSV
        file_path = os.path.join(os.path.dirname(__file__), 'news.csv')
        df.to_csv(file_path, index=False)
        print(df)
