from base_scraper import BaseScraper
from bs4 import BeautifulSoup
import asyncio

class HolleyScraper(BaseScraper):
    async def directory(self, tag: str, parent_data: dict, data: dict | None = None) -> dict:
        url = parent_data['url']
        session = await self.create_session()
        response = await self.request(session=session, method="get", url=url)
        soup = BeautifulSoup(response.text, "html.parser")

        print(soup)

        rows = []

        for card in soup.select("div.card-background"):
            a_tag = card.find("a", href=True)
            if not a_tag:
                continue

            href = a_tag["href"]
            full_url = f"https://www.holley.com{href}"
            title = a_tag.find("h4", class_="card_title")
            img = a_tag.find("img", class_="card_image")
            desc = a_tag.find("div", class_="card-short_description")
            price = a_tag.find("div", class_="card-price")
            part_number = a_tag.find("div", class_="card-partnumber")

            product_id = part_number.text.strip() if part_number else href.strip("/").split("/")[-1]

            rows.append({
                "id": product_id,
                "url": full_url,
                "title": title.text.strip() if title else None,
                "image": f"https:{img['src']}" if img and img.get("src") else None,
                "description": desc.text.strip() if desc else None,
                "price": price.text.strip() if price else None,
            })

        return {"rows": rows}
    
    async def detail(self, tag: str, parent_data: dict) -> dict:
        print('test')
        return parent_data
    

async def main():
    url = "https://www.holley.com/showcase/new_products/"
    scraper = HolleyScraper(url)

    print("Scraping new products...")
    await scraper.scrape_directory(tag="new_products")


if __name__ == "__main__":
    asyncio.run(main())