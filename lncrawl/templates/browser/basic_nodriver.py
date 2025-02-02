import logging
from abc import abstractmethod

import nodriver

from typing import Optional, List, Generator

from PIL import Image

from lncrawl.core.asyncrunner import run_coroutine_sync
from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import ScraperErrorGroup, FallbackToBrowser
from lncrawl.models import Chapter, SearchResult

logger = logging.getLogger(__name__)


def search_novel_in_browser(
    query: str
) -> Generator[SearchResult, None, None]:
    """Search for novels with `self.browser`"""
    return []


class BasicNoDriverCrawler(Crawler):

    def __init__(
        self,
        headless: bool = False,
        timeout: Optional[int] = 120,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
    ) -> None:
        self._browser = None
        self.timeout = timeout
        self.headless = headless
        super().__init__(
            workers=workers,
            parser=parser,
        )

    @property
    def using_browser(self) -> bool:
        return hasattr(self, "_browser") and self._browser.active

    def __del__(self) -> None:
        self.close_browser()
        super().__del__()

    @property
    def browser(self) -> "Browser":
        """
        A webdriver based browser.
        Requires Google Chrome to be installed.
        """
        self.init_browser()
        return self._browser

    def init_browser(self):
        if self.using_browser:
            return
        self.init_executor(1)
        self._browser = run_coroutine_sync(nodriver.start(headless=True,
                                                          sandbox=False,
                                                          browser_args=["--kiosk", "--start-maximized",
                                                                        "--window-size=1920,1080"]))

    def close_browser(self):
        if not self.using_browser:
            return
        run_coroutine_sync(self._browser.close())

    def search_novel(self, query: str) -> List[SearchResult]:
        try:
            return list(self.search_novel_in_scraper(query))
        except ScraperErrorGroup as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed search novel: %s", e)
            self.init_browser()
            return list(search_novel_in_browser(query))
        finally:
            self.close_browser()

    def read_novel_info(self) -> None:
        try:
            self.read_novel_info_in_scraper()
        except ScraperErrorGroup as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed in read novel info: %s", e)
            self.init_browser()
            self.volumes.clear()
            self.chapters.clear()
            self.read_novel_info_in_browser()
        finally:
            self.close_browser()

    def download_chapters(
            self,
            chapters: List[Chapter],
            fail_fast=False,
    ) -> Generator[int, None, None]:
        self.init_browser()

        if not self.browser:
            return

        for chapter in self.progress_bar(chapters, desc="Chapters", unit="item"):
            if not isinstance(chapter, Chapter) or chapter.success:
                yield 1
                continue
            try:
                chapter.body = self.download_chapter_body_in_browser(chapter)
                self.extract_chapter_images(chapter)
                chapter.success = True
            except Exception as e:
                logger.error("Failed to get chapter: %s", e)
                chapter.body = ""
                chapter.success = False
                if isinstance(e, KeyboardInterrupt):
                    break
            finally:
                yield 1

        self.close_browser()

    def download_image(self, url: str, headers={}, **kwargs) -> Image:
        self.init_browser()

        self._browser.get(url)


        # try:
        #     return super().download_image(url, headers, **kwargs)
        # except ScraperErrorGroup as e:
        #     if logger.isEnabledFor(logging.DEBUG):
        #         logger.exception("Failed in download image: %s", e)
        #     self.init_browser()
            # self._browser.visit(url)
            # self.browser.wait("img", By.TAG_NAME)
            # png = self.browser.find("img", By.TAG_NAME).screenshot_as_png
            # return Image.open(BytesIO(png))


    def search_novel_in_scraper(
        self, query: str
    ) -> Generator[SearchResult, None, None]:
        """Search for novels with `self.scraper` requests"""
        raise FallbackToBrowser()

    def read_novel_info_in_scraper(self) -> None:
        """Read novel info with `self.scraper` requests"""
        raise FallbackToBrowser()

    @abstractmethod
    def read_novel_info_in_browser(self) -> None:
        """Read novel info with `self.browser`"""
        raise NotImplementedError()

    def download_chapter_body(self, chapter: Chapter) -> str:
        return self.download_chapter_body_in_scraper(chapter)

    def download_chapter_body_in_scraper(self, chapter: Chapter) -> str:
        """Download the chapter contents using the `self.scraper` requests"""
        raise FallbackToBrowser()

    @abstractmethod
    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        """Download the chapter contents using the `self.browser`"""
        raise NotImplementedError()
