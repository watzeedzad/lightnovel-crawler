import logging

from bs4 import BeautifulSoup, Tag

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class HelScans(MangaStreamTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://helscans.com/"]

    def initialize(self) -> None:
        self.init_executor(1)
        self.cleaner.bad_tags.update(["h3"])

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("#readerarea")
