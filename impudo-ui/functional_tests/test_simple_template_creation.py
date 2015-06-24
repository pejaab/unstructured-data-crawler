from functional_tests.base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time

class UserTest(FunctionalTest):

    def test_can_start_new_template_and_retrieve_it_later(self):
        # Mike checks out the crawler. He checks out its homepage
        self.browser.get(self.server_url)

        # He notices the page title and header mention crawler
        self.assertIn('Impudo Crawler', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Create crawling template', header_text)

        # He is invited to enter a url to be scraped
        inputbox = self.get_url_input_box()
        self.assertEqual(
                inputbox.get_attribute('placeholder'), 'Enter a url, e.g. http://www.etoz.ch/model-21245/'
                )
        
        # He types "www.etoz.ch/model-21245/" into a text box
        inputbox.send_keys('http://www.etoz.ch/model-21245/')
        
        # He is also invited to enter the text that he wants to be scraped
        inputbox = self.get_desc_text_area()
        self.assertEqual(
                inputbox.get_attribute('placeholder'), 'Enter text to scrape'
                )

        # He types into the text box
        # "ALVAR AALTO
        # MODEL 2145, 1942/ 1950S
        # EMBRU, SWITZERLAND
        # 75 CM X 200 CM X 90 CM
        # TUBULAR STEEL, ORIGINAL CUSHION WITH WOOLEN UPHOLSTERY, BAKELITE ARMRESTS
        # FOLDING SYSTEM HAS BEEN RENEWED.
        # C.F. BLASER: ALVAR AALTO ALS DESIGNER, PG. 109
        # PRICE ON REQUEST"
        inputbox.send_keys('ALVAR AALTO\nMODEL 2145, 1942/ 1950S\nEMBRU, SWITZERLAND\n75 CM X 200 CM X 90 CM' +
                'TUBULAR STEEL, ORIGINAL CUSHION WITH WOOLEN UPHOLSTERY, BAKELITE ARMRESTS\n' +
                'FOLDING SYSTEM HAS BEEN RENEWED.\nC.F. BLASER: ALVAR AALTO ALS DESIGNER, PG. 109\n\n' +
                'PRICE ON REQUEST')
        time.sleep(1)

        # When he hits enter, the page updates, and now another page shows
        # the scraped data from the particular website
        button = self.browser.find_element_by_id('id_submit')
        self.assertEqual(
                button.get_attribute('value'), 'Generate crawler template'
                )
        button.send_keys(Keys.ENTER)
        mike_template_url = self.browser.current_url
        self.assertRegex(mike_template_url, '/templates/.+')

        self.assertIn('http://www.etoz.ch/model-21245/', self.browser.page_source)

