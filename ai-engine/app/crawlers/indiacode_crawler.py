import logging
import re

from bs4 import BeautifulSoup

from app.crawlers.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

# Key central acts to crawl from India Code
ACTS_TO_CRAWL = [
    {"title": "Indian Penal Code, 1860", "id": 37, "year": 1860},
    {"title": "Code of Criminal Procedure, 1973", "id": 12, "year": 1973},
    {"title": "Code of Civil Procedure, 1908", "id": 11, "year": 1908},
    {"title": "Indian Contract Act, 1872", "id": 27, "year": 1872},
    {"title": "Indian Evidence Act, 1872", "id": 28, "year": 1872},
    {"title": "Transfer of Property Act, 1882", "id": 58, "year": 1882},
    {"title": "Hindu Marriage Act, 1955", "id": 24, "year": 1955},
    {"title": "Consumer Protection Act, 2019", "id": 200, "year": 2019},
    {"title": "Motor Vehicles Act, 1988", "id": 35, "year": 1988},
    {"title": "Negotiable Instruments Act, 1881", "id": 36, "year": 1881},
    {"title": "Information Technology Act, 2000", "id": 30, "year": 2000},
    {"title": "Specific Relief Act, 1963", "id": 55, "year": 1963},
    {"title": "Limitation Act, 1963", "id": 34, "year": 1963},
    {"title": "Arbitration and Conciliation Act, 1996", "id": 5, "year": 1996},
    {"title": "Protection of Women from Domestic Violence Act, 2005", "id": 170, "year": 2005},
    {"title": "Right to Information Act, 2005", "id": 171, "year": 2005},
    {"title": "Bharatiya Nyaya Sanhita, 2023", "id": 250, "year": 2023},
    {"title": "Bharatiya Nagarik Suraksha Sanhita, 2023", "id": 251, "year": 2023},
    {"title": "Bharatiya Sakshya Adhiniyam, 2023", "id": 252, "year": 2023},
    {"title": "Companies Act, 2013", "id": 165, "year": 2013},
]

BASE_URL = "https://www.indiacode.nic.in"


class IndiaCodeCrawler(BaseCrawler):

    @property
    def source_site(self) -> str:
        return "indiacode"

    async def crawl(self) -> list[dict]:
        """Crawl sections from India Code acts."""
        documents = []

        for act_info in ACTS_TO_CRAWL:
            try:
                act_docs = await self._crawl_act(act_info)
                documents.extend(act_docs)
                logger.info(
                    "Crawled %d sections from %s",
                    len(act_docs), act_info["title"],
                )
            except Exception as e:
                logger.error("Error crawling %s: %s", act_info["title"], e)

        await self.close()
        return documents

    async def _crawl_act(self, act_info: dict) -> list[dict]:
        """Crawl all sections of a single act."""
        act_id = act_info["id"]
        toc_url = f"{BASE_URL}/show-data?actid=AC_CEN_{act_info['year']}_{act_id}"

        html = await self.fetch(toc_url)
        if not html:
            # Fallback URL pattern
            toc_url = f"{BASE_URL}/handle/{act_id}"
            html = await self.fetch(toc_url)
            if not html:
                return []

        section_links = self._extract_section_links(html)
        if not section_links:
            # Try alternate parsing - extract text directly from TOC page
            return self._extract_sections_from_page(html, act_info)

        docs = []
        for sec in section_links:
            sec_html = await self.fetch(sec["url"])
            if not sec_html:
                continue

            text = self._extract_section_text(sec_html)
            if text and len(text) > 50:
                docs.append({
                    "title": f"{act_info['title']} — Section {sec['number']}",
                    "text": text,
                    "source_url": sec["url"],
                    "source_type": "statute",
                    "metadata": {
                        "act_name": act_info["title"],
                        "section_number": sec["number"],
                        "year": act_info["year"],
                    },
                })
        return docs

    def _extract_section_links(self, html: str) -> list[dict]:
        """Parse TOC page to find section links."""
        soup = BeautifulSoup(html, "lxml")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            sec_match = re.search(r"[Ss]ection\s+(\d+[A-Za-z]*)", text)
            if sec_match and ("section" in href.lower() or "show-data" in href):
                url = href if href.startswith("http") else f"{BASE_URL}{href}"
                links.append({"url": url, "number": sec_match.group(1)})

        return links

    def _extract_section_text(self, html: str) -> str:
        """Extract section body text from a section page."""
        soup = BeautifulSoup(html, "lxml")

        # Remove scripts, styles, nav
        for tag in soup.find_all(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        # Try common content containers
        content = (
            soup.find("div", class_=re.compile(r"section-content|act-content|main-content"))
            or soup.find("div", id=re.compile(r"content|main"))
            or soup.find("article")
            or soup.find("main")
        )

        if content:
            return content.get_text(separator="\n", strip=True)
        return soup.get_text(separator="\n", strip=True)

    def _extract_sections_from_page(self, html: str, act_info: dict) -> list[dict]:
        """Fallback: extract sections directly from the full act page."""
        soup = BeautifulSoup(html, "lxml")
        for tag in soup.find_all(["script", "style", "nav"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        if not text or len(text) < 100:
            return []

        # Split by section markers
        parts = re.split(r"(?=\b[Ss]ection\s+\d+[A-Za-z]*[\.\:\-])", text)
        docs = []
        for part in parts:
            part = part.strip()
            if len(part) < 50:
                continue
            sec_match = re.match(r"[Ss]ection\s+(\d+[A-Za-z]*)", part)
            sec_num = sec_match.group(1) if sec_match else str(len(docs))
            docs.append({
                "title": f"{act_info['title']} — Section {sec_num}",
                "text": part,
                "source_url": BASE_URL,
                "source_type": "statute",
                "metadata": {
                    "act_name": act_info["title"],
                    "section_number": sec_num,
                    "year": act_info["year"],
                },
            })

        return docs
