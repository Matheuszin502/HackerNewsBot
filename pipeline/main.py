from webscraper import HackerNewsScraper
from load import transform_and_load

scraper = HackerNewsScraper()
scraped_data = scraper.scrape_categories()
scraper.display_results(scraped_data)
transform_and_load(scraped_data)