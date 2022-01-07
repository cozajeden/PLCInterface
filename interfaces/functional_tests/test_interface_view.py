from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import threading
import dummyPLC


class IndexViewTest(ChannelsLiveServerTestCase):
    """
    Test for index view
    """
    fixtures = ['db.json']
    migrate_from = ('interfaces', '0001_initial')
    migrate_to = ('interfaces', '0008_alter_order_completed_amount')

    def setUp(self):
        """
        Method for setting up test
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.interface_url = f'{self.live_server_url}/interfaces/interface1/'

        self.wait = WebDriverWait(self.browser, 10)

        self.dummmy_plc_stop_event = threading.Event()
        dummy_plc_started = threading.Event()
        self.server_thread = threading.Thread(
            target=dummyPLC.test_server,
            args=(True, self.dummmy_plc_stop_event, dummy_plc_started),
            daemon=True
        ).start()
        dummy_plc_started.wait()

    def tearDown(self):
        """
        Method for tearing down test
        """
        self.browser.quit()
        self.dummmy_plc_stop_event.set()
        time.sleep(2)

    def test_view_status_code_is_ok(self):
        """
        Test for checking status code of view
        """
        response = self.client.get(self.interface_url)
        self.assertEquals(response.status_code, 200)

    def test_view_has_start_button(self):
        """
        Test for checking if view has start button
        """
        self.browser.get(self.interface_url)
        button = self.browser.find_element_by_id('button_start')
        self.assertIsNotNone(button)

    def test_view_has_stop_button(self):
        """
        Test for checking if view has stop button
        """
        self.browser.get(self.interface_url)
        button = self.browser.find_element_by_id('button_stop')
        self.assertIsNotNone(button)

    def test_has_frame_table(self):
        """
        Test for checking if view has frame table
        """
        self.browser.get(self.interface_url)
        frame = self.browser.find_element_by_id('table')
        self.assertIsNotNone(frame)

    def test_show_status(self):
        """
        Test for checking if view shows status
        """
        self.browser.get(self.interface_url)
        status = self.browser.find_element_by_id('status')
        self.assertIsNotNone(status)

    def test_show_order(self):
        """
        Test for checking if view shows order
        """
        self.browser.get(self.interface_url)
        order = self.browser.find_element_by_id('order')
        self.assertIsNotNone(order)

    def test_show_amount(self):
        """
        Test for checking if view shows amount
        """
        self.browser.get(self.interface_url)
        amount = self.browser.find_element_by_id('amount')
        self.assertIsNotNone(amount)

    def test_status_is_connected(self):
        """
        Test for checking if view shows connected status
        """
        self.browser.get(self.interface_url)
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.ID, 'status'), 'Połączono'))
        except TimeoutException:
            self.fail('Connection did not work')

    def test_status_after_first_update_is_stopped(self):
        """
        Test for checking if view shows stopped status after first update
        """
        self.browser.get(self.interface_url)
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.ID, 'status'), 'Stop'))
        except TimeoutException:
            self.fail('First update did not work')

    def test_can_start_PLC(self):
        """
        Test for checking if PLC can be started
        """
        self.browser.get(self.interface_url)
        self.browser.find_element_by_id('id_number').send_keys('1')
        self.browser.find_element_by_id('id_requested_amount').send_keys('666')
        self.browser.find_element_by_id('button_start').click()
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.ID, 'status'), 'Start'))
        except TimeoutException:
            self.fail('Start button did not work')
        remqining_amount = self.browser.find_element_by_id('amount').text
        order = self.browser.find_element_by_id('order').text
        self.assertEqual(remqining_amount, '666')
        self.assertEqual(order, '1')
        
    def test_can_stop_PLC(self):
        """
        Test for checking if PLC can be stopped
        """
        self.browser.get(self.interface_url)
        self.browser.find_element_by_id('id_number').send_keys('1')
        self.browser.find_element_by_id('id_requested_amount').send_keys('666')
        self.browser.find_element_by_id('button_start').click()
        self.wait.until(EC.text_to_be_present_in_element((By.ID, 'status'), 'Start'))
        self.browser.find_element_by_id('button_stop').click()
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.ID, 'status'), 'Stop'))
        except TimeoutException:
            self.fail('Stop button did not work')

    def test_show_no_connection_status_when_PLC_is_not_connected(self):
        """
        Test for checking if view shows no connection status when PLC is not connected
        """
        self.browser.get(self.interface_url)
        self.dummmy_plc_stop_event.set()
        self.browser.find_element_by_id('button_stop').click()
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.ID, 'status'), 'Brak połączenia z PLC'))
        except TimeoutException:
            self.fail('Does not show no connection status when PLC is not connected')

    def test_reamining_amount_is_updating_during_production(self):
        """
        Test for checking if view shows remaining amount during production
        """
        self.browser.get(self.interface_url)
        self.browser.find_element_by_id('id_number').send_keys('1')
        self.browser.find_element_by_id('id_requested_amount').send_keys('200')
        self.browser.find_element_by_id('button_start').click()
        self.wait.until(EC.text_to_be_present_in_element((By.ID, 'status'), 'Start'))
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.ID, 'amount'), '198'))
        except TimeoutException:
            self.fail('Does not show remaining amount during production')

    def test_table_is_showing_frames(self):
        """
        Test for checking if view shows frames in table
        """
        self.browser.get(self.interface_url)
        self.browser.find_element_by_id('id_number').send_keys('1')
        self.browser.find_element_by_id('id_requested_amount').send_keys('200')
        self.browser.find_element_by_id('button_start').click()
        self.wait.until(EC.text_to_be_present_in_element((By.ID, 'status'), 'Start'))
        table = self.browser.find_element_by_id('table')
        cells = [cell.text for cell in table.find_elements_by_tag_name('th')]
        self.assertIn('sent', cells)
        self.assertIn('received', cells)