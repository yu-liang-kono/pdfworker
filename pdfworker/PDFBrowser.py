#!/usr/bin/env python

# standard library imports
import logging as logger
import os.path

# third party related imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

# local library imports
from PDFDocument import PDFDocument
from PDFPage import PDFPage


class PDFBrowserError(Exception): pass


class PDFBrowser(object):
    """Load pdf in browser

    PDFBrowser loads the specified pdf in browser and extract some
    information.

    Attributes:
        browser: An instance of selenium Firefox.
        num_page_viewed: An integer to indicating how many pages have
            been viewed. Due to the memory issue, we have to refresh
            browser after viewing a number of pages.
        abs_filename: A string inidcating the absolute path of the
            specified pdf file.

    """

    # The pdf viewer html page
    HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '..', 'pdfjs', 'web', 'viewer.html')
    # If loading pdf takes more time than it, raise exception
    GLOBAL_TIMEOUT = 15
    # Available scales
    AVAILABLE_SCALES = ('0.5', '0.75', '1', '1.25', '1.5', '2')
    # Due to some memory issue, we have to refresh browser after viewing
    # such number of pages.
    MAX_PAGE_VIEWED = 20

    OUTER_CONTAINER_ID = 'outerContainer'
    # The <input type="file"> to load pdf
    FILE_INPUT_ID = 'fileInput'
    # The <input type="number"> to browse pdf
    PAGE_INPUT_ID = 'pageNumber'
    # The <select> to adjust pdf scale
    SCALE_INPUT_ID = 'scaleSelect'
    # The main div contains all pdf page
    VIEWER_ID = 'viewer'

    def __init__(self, filename):

        self.browser = None
        self.num_page_viewed = 0
        self.abs_filename = os.path.abspath(filename)

        # ensure file exist
        if not os.path.exists(self.abs_filename):
            raise PDFBrowserError('%s does not exist' % self.abs_filename)

    def __del__(self):

        if self.browser is not None:
            try:
                self.browser.quit()
            except Exception:
                pass

    def _init_browser(self, scale=1):
        """Initialize a new browser."""

        if self.browser is not None:
            try:
                self.browser.quit()
            except Exception, e:
                pass

        self.browser = webdriver.Firefox()
        self.num_page_viewed = 0
        self._open_pdf()
        self._set_scale(scale)

    def _refresh_browser(self, scale=1):
        """Refresh the current browser."""

        self._init_browser(scale)

    def get_page(self, page_ix, scale=1):
        """Get text information in the specified page.

        Args:
            filename:

        """

        if self.browser is None:
            self._init_browser()

        page_num = page_ix + 1

        try:
            self._go_to_page(page_num, scale)
        except TimeoutException:
            logger.error('Render page %s timeout', page_num)

        elem = self.browser.find_element_by_id('pageContainer%s' % page_num)
        text_elem = elem.find_element_by_class_name('textLayer')
        text_dom = self.browser.execute_script('return arguments[0].innerHTML',
                                               text_elem)
        canvas_elem = elem.find_element_by_tag_name('canvas')
        width = int(canvas_elem.get_attribute('width'))
        height = int(canvas_elem.get_attribute('height'))

        page = PDFPage.create_by_pdfjs(page_num, width, height, text_dom)

        self.num_page_viewed += 1
        if self.num_page_viewed >= self.MAX_PAGE_VIEWED:
            self._refresh_browser(scale)

        return page

    def run(self, pages=None, scale=1, page_rendered_cb=None):
        """The entry to start parse pdf.

        Args:
            filename: A string, PDF filename.
            pages: A list containing what pages we want to parse.
            page_rendered_cb: A callable which will be called after
                a page is rendered.

        Returns:
            An instance of PDFDocument.

        """

        ret = PDFDocument(self.abs_filename)

        self._init_browser(scale)

        page_cb = lambda x: x
        if callable(page_rendered_cb):
            page_cb = page_rendered_cb

        if pages is None:
            pages = xrange(ret.num_pages)

        for page_ix in pages:
            page = self.get_page(page_ix, scale)
            ret.add_page(page_ix, page)
            page_cb(page)

        self.browser.quit()

        return ret

    def _open_pdf(self):
        """Open the specified pdf."""

        # Load page
        self.browser.get('file://%s' % self.HTML_PATH)

        # Load pdf file
        file_input = self.browser.find_element_by_id(self.FILE_INPUT_ID)
        file_input.send_keys(self.abs_filename)

        def _is_in_progress(browser):

            elem = browser.find_element_by_id(self.OUTER_CONTAINER_ID)
            return elem.get_attribute('class') == ''

        wait = WebDriverWait(self.browser, self.GLOBAL_TIMEOUT, 0.1)
        wait.until(_is_in_progress)

    def _get_num_pages(self):
        """Get the total number of page."""

        def _isready(browser):

            elem = browser.find_element_by_id(self.PAGE_INPUT_ID)
            return elem.get_attribute('max')

        # wait until pdf is loaded
        wait = WebDriverWait(self.browser, self.GLOBAL_TIMEOUT, 0.1)
        wait.until(lambda browser: (_isready(browser) or '').isdigit())

        return int(_isready(self.browser))

    def _go_to_page(self, page_num, scale=1):
        """Go to the specified page number."""

        elem = self.browser.find_element_by_id(self.PAGE_INPUT_ID)
        self._fill(elem, str(page_num), pass_newline=True)

        # wait until pdf page is loaded
        message = 'Rendering page %s takes more than %s seconds' % \
                  (page_num, self.GLOBAL_TIMEOUT)
        wait = WebDriverWait(self.browser, self.GLOBAL_TIMEOUT, 0.1)
        wait.until(lambda browser: self._is_page_loaded(browser, page_num))

    def _set_scale(self, scale):
        """Set the pdf viewer scale option."""

        if str(scale) not in self.AVAILABLE_SCALES:
            raise PDFBrowserError('scale: %s is not supported' % scale)

        elem = self.browser.find_element_by_id(self.SCALE_INPUT_ID)
        if not self._select(elem, str(scale)):
            raise PDFBrowserError("can't select option %s" % scale)

        # wait until pdf is rendered
        wait = WebDriverWait(self.browser, self.GLOBAL_TIMEOUT, 0.1)
        wait.until(self._is_page_loaded)

    def _is_page_loaded(self, browser, page_num=1):
        """Test whether a given page is loaded."""

        elem = browser.find_element_by_id('pageContainer%s' % page_num)

        try:
            elem.find_element_by_class_name('loadingIcon')
            return False
        except NoSuchElementException:
            return True

    def _select(self, select_element, option_value=None, option_text=None):
        """Select an option by value or text."""

        if option_value is not None:
            for option in self.browser.find_elements_by_tag_name('option'):
                if option.get_attribute('value') == option_value:
                    option.click()
                    return True

        elif option_text is not None:
            for option in self.browser.find_elements_by_tag_name('option'):
                if option.text == option_text:
                    option.click()
                    return True

        return False

    def _fill(self, text_element, value, pass_newline=False):
        """Fill a text input by the specified value."""

        text_element.click()
        text_element.send_keys(Keys.BACK_SPACE)
        text_element.clear()
        text_element.send_keys(value)

        if pass_newline:
            text_element.send_keys(Keys.ENTER)

