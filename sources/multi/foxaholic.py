import logging
from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup
from seleniumbase import Driver

from lncrawl.models import Chapter
from lncrawl.templates.browser.basic import BasicBrowserTemplate

logger = logging.getLogger(__name__)


def open_turnstile_page(base, url):
    base.reconnect(timeout=3)
    # open web page using uc
    base.uc_open_with_reconnect(url, reconnect_time=3)


def click_turnstile(base):
    base.reconnect(timeout=3)
    # do turnstile challenge
    if base.is_element_visible('.captcha-prompt iframe'):
        base.switch_to_frame('.captcha-prompt iframe')
        base.uc_click('span.mark', reconnect_time=3)


class FoxaholicCrawler(BasicBrowserTemplate):
    driver = None
    base_url = [
        "https://foxaholic.com/",
        "https://www.foxaholic.com/",
        "https://18.foxaholic.com/",
        "https://global.foxaholic.com/",
    ]

    def initialize(self) -> None:
        self.driver = Driver(uc=True, headless=self.headless, headless2=self.headless, chromium_arg='--start-maximized')
        self.init_executor(1)

    def read_novel_info_in_browser(self) -> None:
        open_turnstile_page(self.driver, self.novel_url)
        click_turnstile(self.driver)

        # verify that page is loaded
        self.driver.assert_element('.wp-manga-chapter.free-chap a', timeout=60)
        # get bs4 from web page
        soup = BeautifulSoup(self.driver.get_page_source(), 'html.parser')

        self.novel_title = soup.select_one('.post-title h1').text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(soup.select_one('.summary_image a img')['src'])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href]')
            ]
        )
        logger.info("%s", self.novel_author)

        for a in reversed(soup.select('.wp-manga-chapter.free-chap a')):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a['href']),
                }
            )

    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        open_turnstile_page(self.driver, chapter['url'])
        click_turnstile(self.driver)

        # verify that page is loaded
        self.driver.assert_element('.entry-content_wrap', timeout=60)
        # get bs4 from web page
        soup = BeautifulSoup(self.driver.get_page_source(), 'html.parser')

        contents = soup.select_one('.entry-content_wrap')
        return self.cleaner.extract_contents(contents)

    def download_image(self, url, **kwargs) -> Image:
        open_turnstile_page(self.driver, url)
        click_turnstile(self.driver)

        # verify that page is loaded
        self.driver.assert_element('img', timeout=60)

        img = self.driver.find_element('img').screenshot_as_png
        return Image.open(BytesIO(img))
