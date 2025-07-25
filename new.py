import asyncio
import re
from base_scraper import BaseScraper
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class NewScraper(BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None

    async def get_soup(self, url: str) -> Optional[object]:
        if not self.session:
            self.session = await self.create_session()
        response = await self.request(session=self.session, method="get", url=url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    
    def get_id_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        clean = parsed.netloc + parsed.path
        clean = re.sub(r"[^\w\-\.]", "_", clean)
        return clean.strip("_")


    async def directory(self, tag: str, parent_data: dict, data: dict | None = None) -> dict:
        if tag == "collections":
            return {
                "rows": await self.extract_links(url=parent_data["url"], tag=tag)
            }
        
        elif tag == "products":
            return await self.extract_products(url=parent_data["url"], data=data)
    
    async def extract_links(self, url: str, tag: str) -> list:
        soup = await self.get_soup(url)
        ul = soup.find("ul", class_="header-navigation-list header-navigation-list--primary")

        seen_urls = set()
        rows = []

        if not ul:
            print('NO ul')
            return
        a_tags = ul.find_all("a", class_="category-section-list-item")
        if not a_tags:
            print("No a_tags found inside UL.")
            return rows

        for a_tag in a_tags:
            data_url = a_tag.get("href")
            text = a_tag.get_text(strip=True)
            a_id = a_tag.get("data-clicktrigger-cat-id").lower()

            if not data_url:
                print('No URL for', a_tag)
                continue

            full_url = urljoin(url, data_url)

            if full_url not in seen_urls:
                seen_urls.add(full_url)
                rows.append({
                    "text": text,
                    "url": full_url,
                    "id": a_id
                })
                print(f"{text} → {full_url}")

        return rows

    async def extract_products(self, url: str, data: Optional[dict] = None) -> dict:

        soup = await self.get_soup(url)
        seen_products = set()
        products = []

        product_grid = soup.find("div", class_="productgrid")
 
        if not product_grid:
            print("No productgrid found.")
            return
        
        for a_tag in product_grid.find_all("a", class_="producttile-gallery-inner"):
            product_url = a_tag.get("href")
            if not product_url:
                continue

            product_id = product_url.rstrip("/").split("/")[-1].replace(".html", "")

            parent = a_tag.find_parent("div", class_="producttile")
            text = a_tag.get_text(strip=True)

            products.append({
                "id": product_id,
                "text": text,
                "url": product_url
            })
        print(url, products)
        return products





    async def detail(self, tag: str, parent_data: dict) -> dict:
        print('detail')
        return
    
async def main():
    scraper = NewScraper(url="https://www.etro.com/")
    await scraper.scrape_directory(tag="collections")

    await scraper.scrape_directory(tag="products", parent_tag="collections")



if __name__ == "__main__":
    asyncio.run(main())