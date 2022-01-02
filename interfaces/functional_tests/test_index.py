from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from interfaces.models import Interface


class IndexViewTest(ChannelsLiveServerTestCase):
    """
    Test for index view
    """
    fixtures = ['db.json']
    migrate_from = ('interfaces', '0001_initial')
    migrate_to = ('interfaces', '0008_alter_order_completed_amount')

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    def tearDown(self):
        self.browser.quit()

    def test_index_view_status_code_is_ok(self):
        """
        Test for checking status code of index view
        """
        response = self.client.get(self.live_server_url)
        self.assertEquals(response.status_code, 200)

    def test_index_view_contains_correct_html(self):
        """
        Test for checking if index view contains correct html
        """
        response = self.client.get(self.live_server_url)
        self.assertContains(response, '<h1>Lista paneli operatorskich</h1>')

    def test_index_view_contains_correct_html(self):
        """
        Test for checking if index view contains correct html
        """
        response = self.client.get(self.live_server_url)
        self.assertTemplateUsed(response, 'interfaces/index.html')

    def test_index_view_contains_defaul_interface_link(self):
        """
        Test for checking if index view contains default interface link
        """
        self.browser.get(self.live_server_url)
        link = self.browser.find_element_by_partial_link_text('interface1')
        self.assertEqual(
            link.get_attribute('href'),
            f'{self.live_server_url}/interfaces/interface1/'
        )

    def test_link_to_new_interface_appears_on_index_page(self):
        """
        Test for checking if link to new interface appears on index page
        """
        interface = Interface.objects.create(
            name='Test', plc_address='localhost', plc_port=12345
        )
        self.browser.get(self.live_server_url)
        link = self.browser.find_element_by_partial_link_text(interface.name)
        self.assertEqual(
            link.get_attribute('href'),
            f'{self.live_server_url}/interfaces/{interface.name}/'
        )

    def test_link_to_new_interface_work(self):
        """
        Test for checking if link to new interface work
        """
        interface = Interface.objects.create(
            name='Test', plc_address='localhost', plc_port=12345
        )
        self.browser.get(self.live_server_url)
        link = self.browser.find_element_by_partial_link_text(interface.name)
        link.click()
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/interfaces/{interface.name}/'
        )