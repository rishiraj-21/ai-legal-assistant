import logging
import re

from bs4 import BeautifulSoup

from app.crawlers.base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

BASE_URL = "https://indiankanoon.org"

# Curated search queries covering major legal topics
SEARCH_QUERIES = [
    "Section 302 IPC murder conviction",
    "Section 498A IPC dowry cruelty",
    "Section 138 Negotiable Instruments dishonour cheque",
    "Section 420 IPC cheating",
    "Section 376 IPC rape",
    "Section 304B IPC dowry death",
    "bail anticipatory Section 438 CrPC",
    "quashing Section 482 CrPC",
    "maintenance Section 125 CrPC",
    "divorce mutual consent Section 13B Hindu Marriage Act",
    "specific performance contract",
    "injunction Order 39 CPC",
    "consumer complaint deficiency service",
    "motor accident compensation",
    "landlord tenant eviction rent",
    "partition property coparcener",
    "arbitration award challenge Section 34",
    "writ habeas corpus Article 226",
    "fundamental rights Article 21",
    "right to information RTI appeal",
    "RERA real estate complaint",
    "domestic violence protection order",
    "Section 34 IPC common intention",
    "cybercrime Section 66 IT Act",
    "cheating criminal breach trust",
    "defamation Section 499 IPC",
    "land acquisition compensation",
    "labour dispute industrial tribunal",
    "Section 13 Hindu Marriage cruelty desertion",
    "evidence electronic Section 65B",
]

MAX_RESULTS_PER_QUERY = 5


class IndianKanoonCrawler(BaseCrawler):

    @property
    def source_site(self) -> str:
        return "indiankanoon"

    async def crawl(self) -> list[dict]:
        """Search Indian Kanoon and fetch judgments."""
        documents = []
        seen_urls: set[str] = set()

        for query in SEARCH_QUERIES:
            try:
                results = await self._search(query)
                for result in results:
                    if result["url"] in seen_urls:
                        continue
                    seen_urls.add(result["url"])

                    doc = await self._fetch_judgment(result)
                    if doc:
                        documents.append(doc)
            except Exception as e:
                logger.error("Error processing query '%s': %s", query, e)

        await self.close()
        logger.info("Crawled %d judgments from Indian Kanoon", len(documents))
        return documents

    async def _search(self, query: str) -> list[dict]:
        """Search Indian Kanoon and extract result links."""
        search_url = f"{BASE_URL}/search/?formInput={query.replace(' ', '+')}"
        html = await self.fetch(search_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        results = []

        for div in soup.find_all("div", class_="result"):
            a_tag = div.find("a", href=True)
            if not a_tag:
                continue

            href = a_tag["href"]
            if not href.startswith("/doc/"):
                continue

            url = f"{BASE_URL}{href}"
            title = a_tag.get_text(strip=True)
            results.append({"url": url, "title": title})

            if len(results) >= MAX_RESULTS_PER_QUERY:
                break

        return results

    async def _fetch_judgment(self, result: dict) -> dict | None:
        """Fetch and parse a judgment page."""
        html = await self.fetch(result["url"])
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        # Remove ads, scripts, etc.
        for tag in soup.find_all(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        for div in soup.find_all("div", class_=re.compile(r"ad|sidebar|footer|menu")):
            div.decompose()

        # Extract judgment text
        judgment_div = soup.find("div", class_="judgments") or soup.find("div", id="jd")
        if not judgment_div:
            judgment_div = soup.find("div", class_="doc_bench") or soup.find("pre")

        if not judgment_div:
            return None

        text = judgment_div.get_text(separator="\n", strip=True)
        if len(text) < 200:
            return None

        # Extract metadata
        metadata = self._extract_metadata(soup, text)

        return {
            "title": result["title"],
            "text": text,
            "source_url": result["url"],
            "source_type": "case_law",
            "metadata": metadata,
        }

    def _extract_metadata(self, soup: BeautifulSoup, text: str) -> dict:
        """Extract case metadata from the page."""
        metadata = {
            "case_name": None,
            "court": None,
            "year": None,
            "citations": [],
            "acts_referred": [],
        }

        # Court from doc_bench or title
        bench = soup.find("div", class_="doc_bench")
        if bench:
            bench_text = bench.get_text(strip=True)
            if "Supreme Court" in bench_text:
                metadata["court"] = "Supreme Court of India"
            else:
                hc_match = re.search(r"High Court of (\w[\w\s]+)", bench_text)
                if hc_match:
                    metadata["court"] = f"High Court of {hc_match.group(1).strip()}"

        # Case name from doc_title
        title_div = soup.find("div", class_="doc_title") or soup.find("h2", class_="doc_title")
        if title_div:
            case_text = title_div.get_text(strip=True)
            vs_match = re.search(r"(.+?)\s+(?:vs?\.?|versus)\s+(.+?)(?:\s+on\s+|\Z)", case_text, re.I)
            if vs_match:
                metadata["case_name"] = f"{vs_match.group(1).strip()} v. {vs_match.group(2).strip()}"

        # Year
        date_div = soup.find("div", class_="doc_author")
        if date_div:
            year_match = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", date_div.get_text())
            if year_match:
                metadata["year"] = int(year_match.group(1))

        if not metadata["year"]:
            year_match = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", text[:500])
            if year_match:
                metadata["year"] = int(year_match.group(1))

        # Citations
        citation_patterns = [
            r"\(\d{4}\)\s+\d+\s+SCC\s+\d+",
            r"AIR\s+\d{4}\s+\w+\s+\d+",
        ]
        for pat in citation_patterns:
            metadata["citations"].extend(re.findall(pat, text[:3000]))

        # Acts referred
        act_patterns = [
            r"(?:Indian Penal Code|IPC)",
            r"(?:Code of Criminal Procedure|Cr\.?P\.?C)",
            r"(?:Code of Civil Procedure|CPC)",
            r"(?:Indian Evidence Act)",
            r"(?:Hindu Marriage Act)",
            r"(?:Consumer Protection Act)",
            r"(?:Motor Vehicles Act)",
            r"(?:Negotiable Instruments Act)",
            r"(?:Transfer of Property Act)",
            r"(?:Specific Relief Act)",
        ]
        for pat in act_patterns:
            if re.search(pat, text[:5000], re.I):
                match = re.search(pat, text[:5000], re.I)
                metadata["acts_referred"].append(match.group(0))

        metadata["acts_referred"] = list(set(metadata["acts_referred"]))
        return metadata
