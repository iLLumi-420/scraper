import asyncio
import re
from urllib.parse import urlparse
from base_scraper import BaseScraper
from bs4 import BeautifulSoup

class HolleyScraper(BaseScraper):

    def get_id_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        clean = parsed.netloc + parsed.path
        clean = re.sub(r"[^\w\-\.]", "_", clean)
        return clean.strip("_")
    
    async def directory(self, tag: str, parent_data: dict, data: dict | None = None) -> dict:
        print(parent_data)
        if tag == "categories":
            return await self.get_categories(url=parent_data["url"])
        if tag == "sub-categories":
            return await self.get_sub_categories(url=parent_data["url"])
        
    async def get_sub_categories(self, url:str ) -> dict:
        return 'test123'

        

    async def get_categories(self, url):
        session = await self.create_session()
        response = await self.request(session=session, method="get", url=url)
        soup = BeautifulSoup(response.text, "html.parser")

        ul = soup.find("ul", class_="subnav")

        seen_urls = set()
        rows = []


        for a_tag in ul.find_all("a"):
            href = a_tag["href"]
            text = a_tag.get_text(strip=True)
            full_url = f"https://www.holley.com{href}"
            product_id = self.get_dir_name_for_url(href)

            if full_url not in seen_urls:
                seen_urls.add(full_url)

                rows.append({
                    "id": product_id,
                    "url": full_url,
                    "text": text
                })

        return {"rows": rows}

    
    async def detail(self, tag: str, parent_data: dict) -> dict:
        print('test')
        return parent_data
    



async def main():
    url = "https://www.holley.com/"
    scraper = HolleyScraper(url)


    await scraper.scrape_directory(tag="categories")


    await scraper.scrape_directory(tag="sub-categories", parent_tag="categories")


if __name__ == "__main__":
    asyncio.run(main())