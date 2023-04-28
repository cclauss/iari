import logging
import re
from io import BytesIO
from typing import Dict, List

import requests
from pydantic import BaseModel
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.models.api.job.check_url_job import UrlJob
from src.models.exceptions import MissingInformationError

logger = logging.getLogger(__name__)


class PypdfHandler(BaseModel):
    job: UrlJob
    content: bytes = b""
    links: Dict[int, List[str]] = {}
    error: bool = False
    pages: Dict[int, str] = {}
    error_details: str = ""

    @property
    def total_number_of_links(self):
        return len(self.__all_links__)

    @property
    def __all_links__(self) -> List[str]:
        links = []
        for page in self.links:
            links.extend(self.links[page])
        return links

    def __download_pdf__(self):
        """Download PDF file from URL"""
        if not self.content:
            response = requests.get(self.job.url, timeout=self.job.timeout)
            if response.content:
                self.content = response.content
            else:
                self.error = True
                self.error_details = (f"Got no content from URL using "
                                      f"requests and timeout {self.job.timeout}")
                logger.warning(self.error_details)

    def __extract_links__(self) -> None:
        """Extract all links from the text extract per page"""
        links = {}
        for index, page in enumerate(self.pages):
            # provided by chatgpt
            regex = r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?"
            urls = re.findall(regex, self.pages[page])
            cleaned_urls = self.__clean_urls__(urls=urls)
            valid_urls = self.__discard_invalid_urls__(urls=cleaned_urls)
            links[index] = valid_urls
        self.links = links

    def __extract_pages__(self) -> None:
        """Extract all text from all pages"""
        if not self.content:
            raise MissingInformationError()
        with BytesIO(self.content) as pdf_file:
            try:
                pdf_reader = PdfReader(pdf_file)
                for index, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    self.pages[index] = text
            except PdfReadError:
                self.error = True
                self.error_details = "Not a valid PDF according to pypdf"
                logger.error(self.error_details)

    def download_and_extract(self):
        self.__download_pdf__()
        if not self.error:
            self.__extract_pages__()
        if not self.error:
            self.__extract_links__()

    def get_dict(self):
        """Return data to the patron"""
        return dict(
            links=self.links, pages=self.pages, links_total=self.total_number_of_links
        )

    @staticmethod
    def __clean_urls__(urls: List[str]) -> List[str]:
        """Some links have spaces in them when returned from pypdf2 so we fix that"""
        cleaned_links = []
        for link in urls:
            # this was generated by chatgpt
            clean_link = (
                link.replace("\u0020", "")
                .replace("\u0009", "")
                .replace("\u000A", "")
                .replace("\u000B", "")
                .replace("\u000C", "")
                .replace("\u000D", "")
                .replace("\u0085", "")
                .replace("\u1680", "")
                .replace("\u180E", "")
                .replace("\u2000", "")
                .replace("\u2001", "")
                .replace("\u2002", "")
                .replace("\u2003", "")
                .replace("\u2004", "")
                .replace("\u2005", "")
                .replace("\u2006", "")
                .replace("\u2007", "")
                .replace("\u2008", "")
                .replace("\u2009", "")
                .replace("\u200A", "")
                .replace("\u2028", "")
                .replace("\u2029", "")
                .replace("\u202F", "")
                .replace("\u205F", "")
                .replace("\u3000", "")
            )
            # logger.debug(f"output: {clean_link}")
            cleaned_links.append(clean_link)
        return cleaned_links

    @staticmethod
    def __discard_invalid_urls__(urls: List[str]) -> List[str]:
        """This should discard any url with "www" and without 2 dots and a tld
        e.g. https://www.science"""
        valid_links = []
        # generated by chatgpt and edited by hand by Dennis
        regex = r".*\.[^\.]+\.[a-zA-Z]{2,}.*"
        for link in urls:
            if "www" in link and not re.search(regex, link):
                # had www but not 2 dots and a tld
                logger.info(f"discarded url: {link}")
            else:
                valid_links.append(link)
        return valid_links
