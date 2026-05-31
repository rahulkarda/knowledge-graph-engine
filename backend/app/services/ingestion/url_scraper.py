from typing import Tuple
import httpx
from bs4 import BeautifulSoup


class UrlScraper:
    async def scrape(self, url: str) -> Tuple[str, str]:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "KnowledgeGraphEngine/1.0"})
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "lxml")

        for tag in soup(["script", "style", "nav", "footer", "aside", "header", "form"]):
            tag.decompose()

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url

        # Try article > main > body fallback
        main = soup.find("article") or soup.find("main") or soup.find("body")
        if main:
            text = main.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)

        return title[:200], text
