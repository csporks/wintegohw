import asyncio
from user_scraper import scraper


if __name__ == '__main__':
    task = scraper.get_user_data("35.188.78.78:8912", "user1", "pass1")
    asyncio.get_event_loop().run_until_complete(task)
    