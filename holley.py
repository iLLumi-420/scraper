import asyncio
import re
from urllib.parse import urljoin, urlparse
import json
from curl_cffi import AsyncSession
from base_scraper import BaseScraper
from bs4 import BeautifulSoup
import requests
import urllib
import urllib.parse


class HolleyScraper(BaseScraper):

    def get_id_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        clean = parsed.netloc + parsed.path
        clean = re.sub(r"[^\w\-\.]", "_", clean)
        return clean.strip("_")
    
    async def directory(self, tag: str, parent_data: dict, data: dict | None = None) -> dict:
        if tag == "categories":
            return await self.get_categories(url=parent_data["url"])
        elif tag == "sub-categories":
            return await self.get_products_filtered(url=parent_data["url"])
        
            
    async def get_products_filtered(self, url: str):    
        session = await self.create_session()

        await session.request("GET", url=url)

        api_url = "https://www.holley.com/assets/php/widget_helpers.php"

        payload = {
            "action": "filter_grid_search",
            "guid": "CC559896-3E4E-4936-8A6C-22B44F6BB58E",
            "pageType": "category",
            "filters": {
                "availability": {"instock": False, "build_to_order": False},
                "attributes": {},
                "platform_attributes": {},
                "categories": {},
                "ymm": {},
                "shopByEngine": {}
            },
            "facets": ["availability", "brand"],
            "page": 1,
            "isDesktop": True,
            "sort": "default"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://www.holley.com",
            "Referer": "https://www.holley.com/products/marine_and_powersports/small_engine/",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-GPC": "1",
        }




        kwargs = {
            "json": payload,
            "headers": headers
        }

        response = await self.request(session, "post", api_url, kwargs)

        print("Response headers:", response.headers)
        print("response text:", response.text)  

        response.raise_for_status()

        data = response.text 
        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Optional: parse products
        products = soup.select(".product-info") 
        return products

        


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


    # await scraper.scrape_directory(tag="categories")


    await scraper.scrape_directory(tag="sub-categories", parent_tag="categories")


if __name__ == "__main__":
    asyncio.run(main())