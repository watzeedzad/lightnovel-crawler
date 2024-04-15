import logging
import random
import time
from io import BytesIO

from PIL import Image

from lncrawl.models import Chapter
from lncrawl.templates.browser.basic import BasicBrowserTemplate
from seleniumbase import SB

logger = logging.getLogger(__name__)
search_url = "https://www.foxaholic.com/?s=%s&post_type=wp-manga"


def open_turnstile_page(base, url):
    # open web page using uc
    base.driver.uc_open_with_reconnect(url, reconnect_time=3)


def click_turnstile(base):
    # do turnstile challenge
    base.driver.switch_to_frame("iframe")
    base.driver.uc_click("span.mark")


class FoxaholicCrawler(BasicBrowserTemplate):
    base_url = [
        "https://foxaholic.com/",
        "https://www.foxaholic.com/",
        "https://18.foxaholic.com/",
        "https://global.foxaholic.com/",
    ]

    def initialize(self) -> None:
        self.init_executor(1)

    def read_novel_info_in_browser(self) -> None:
        with SB(uc=True, test=True, headless=self.headless, headless2=self.headless) as sb:
            open_turnstile_page(sb, self.novel_url)
            click_turnstile(sb)

            # verify that page is loaded
            sb.assert_element('.wp-manga-chapter.free-chap a', timeout=60)
            # get bs4 from web page
            soup = sb.get_beautiful_soup()

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
        with SB(uc=True, test=True, headless=self.headless, headless2=self.headless) as sb:
            open_turnstile_page(sb, chapter['url'])
            click_turnstile(sb)

            # verify that page is loaded
            sb.assert_element('.entry-content_wrap', timeout=60)
            # get bs4 from web page
            soup = sb.get_beautiful_soup()

            contents = soup.select_one('.entry-content_wrap')
            return self.cleaner.extract_contents(contents)

    def download_image(self, url, **kwargs):
        with SB(uc=True, test=True, headless=self.headless, headless2=self.headless) as sb:
            open_turnstile_page(sb, url)
            click_turnstile(sb)

            # verify that page is loaded
            sb.assert_element('img', timeout=60)

            img = sb.find_element('img').screenshot_as_png
            return Image.open(BytesIO(img))
