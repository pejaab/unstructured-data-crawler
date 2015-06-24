from functional_tests.base import FunctionalTest
from selenium.webdriver.common.keys import Keys

class LayoutAndStylingTest(FunctionalTest):
    
    def test_layout_and_styling(self):
        # Mike goes to the home page
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 768)

        # He notices the input is nicely centered
        inputbox = self.get_url_input_box()
        inputarea = self.get_desc_text_area()
        self.assertAlmostEqual(
                inputbox.location['x'] + inputbox.size['width'] / 2, 512, delta=5
                )
        self.assertAlmostEqual(
                inputarea.location['x'] + inputarea.size['width'] / 2, 512, delta=5
                )
        
        '''
        # He creates a new template and sees the input is nicely
        # centered there too
        inputbox.send_keys('http://www.test.de/')
        inputarea.send_keys('Test Test')
        button = self.browser.find_element_by_id('id_submit')
        button.send_keys('Keys.ENTER')

        self.assertAlmostEqual()
        '''
