from functional_tests.base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from unittest import skip
import time

class ItemValidationTest(FunctionalTest):
 
    def test_cannot_add_empty_template(self):
        # Mike goes to the home page and accidentally tries to submit
        # an empty template. He hits Enter on the empty input box
        self.browser.get(self.server_url)
        self.browser.find_element_by_id('id_submit').send_keys(Keys.ENTER)
        
        # The home page refreshes, and there is an error message saying
        # that templates cannot be blank
        error = self.browser.find_element_by_css_selector('.has-error')
        self.assertEqual(error.text, 'You cannot have an empty URL\nYou cannot have an empty description')
        
        # He tries again with some input for the template, which now works
        self.get_url_input_box().send_keys('http://www.etoz.ch/model')
        self.get_desc_text_area().send_keys('Bitumen ashtray')
        self.browser.find_element_by_id('id_submit').send_keys(Keys.ENTER) 
        
        # He decides to submit blank input again
        inputbox = self.get_url_input_box()
        inputbox.clear()
        textarea = self.get_desc_text_area()
        textarea.clear()
        self.browser.find_element_by_id('id_submit').send_keys(Keys.ENTER)
        
        # He receives a similar warning on the template page
        error = self.browser.find_element_by_css_selector('.has-error')
        self.assertEqual(error.text, 'You cannot have an empty URL\nYou cannot have an empty description')
        
        # And he can correct it by filling some text in
        self.get_url_input_box().send_keys('http://www.etoz.ch/model/')
        self.get_desc_text_area().send_keys('Bitumen ashtray')
        self.browser.find_element_by_id('id_submit').send_keys(Keys.ENTER)
