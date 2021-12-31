from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from interfaces.models import Interface

class InterfacesListTest(LiveServerTestCase):
    """
    Test for interfaces list
    """
    def setUp(self) -> None:
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(options=options)

    def tearDown(self):
        self.browser.quit()

    def test_can_show_links_to_interfaces(self):
        """
        Test for showing list of interfaces
        """
        self.browser.get(self.live_server_url + '/interfaces')
        interfaces = Interface.objects.all()
        for interface in interfaces:
            self.browser.find_element_by_partial_link_text(interface.name)   


class InterfaceDetailTest(LiveServerTestCase):
    """
    Test for interface detail
    """
    def setUp(self) -> None:
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(options=options)
        self.interface = Interface.objects.create(name='test_interface',
                                             plc_address='127.0.1.101',
                                             plc_port=1024,)

    def tearDown(self):
        self.browser.quit()

    def test_can_show_form(self):
        """
        Test for showing interface detail
        """
        self.browser.get(self.live_server_url + '/interfaces/' + self.interface.name)
        self.browser.find_element_by_id('form')

    def test_can_show_start_button(self):
        """
        Test for showing start button
        """
        self.browser.get(self.live_server_url + '/interfaces/' + self.interface.name)
        buttons = self.browser.find_elements_by_name('button')
        values = [button.get_attribute('value') for button in buttons]
        self.assertTrue('Start' in values)

    def test_can_show_stop_button(self):
        """
        Test for showing stop button
        """
        self.browser.get(self.live_server_url + '/interfaces/' + self.interface.name)
        buttons = self.browser.find_elements_by_name('button')
        values = [button.get_attribute('value') for button in buttons]
        self.assertTrue('Stop' in values)

    def test_table_contains_proper_columns(self):
        """
        Test for showing table with proper columns
        """
        columns = [
            'Type', 'Transaction id', 'Protocol id',
            'Length', 'Unit id', 'Function', 'Data',
        ]
        self.browser.get(self.live_server_url + '/interfaces/' + self.interface.name)
        table = self.browser.find_element_by_class_name('table')
        rows = table.find_elements_by_tag_name('th')
        for column in columns:
            self.assertIn(column, [row.text for row in rows])
        