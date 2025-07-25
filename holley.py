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
        
            
    async def get_products_filtered(self, url):
        visit_url = "https://www.holley.com/products/exhaust/"
        api_url = "https://www.holley.com/assets/php/widget_helpers.php"

        async with AsyncSession(impersonate="chrome136") as session:

            visit_response = await session.get(visit_url)
            print("Visit status:", visit_response.status_code)


            payload = {
                "action": "filter_grid_search",
                "guid": "E3F52F68-D3D2-44C9-8A7F-76D605923CDA",
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
                "Referer": visit_url,
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Sec-GPC": "1"
            }


            encoded_payload = {"json": json.dumps(payload)}
            response = await session.post(api_url, data=encoded_payload, headers=headers)

            print("POST status:", response.status_code)
            print("POST headers:", response.headers)
            print("First 1000 characters of response:\n", response.text[:1000])

            try:
                data = response.json()
                print("Parsed JSON keys:", list(data.keys()))
            except Exception as e:
                print("JSON parse error:", e)
        


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