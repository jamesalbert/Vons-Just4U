from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import re
import sys

try:
    sys.argv.pop(0)
    username, password = sys.argv
except:
    exit('you must give a username and password')


loginUrl = "https://www.vons.com/ShopStores/OSSO-Login.page?goto=http%3A%2F%2Fwww.vons.com%2FIFL%2FGrocery%2FHome"
url = 'http://www.vons.com/ShopStores/Justforu-Coupons.page#/category/all'
threadLock = threading.Lock()

class CouponThread(threading.Thread):
    def __init__(self, offer):
        threading.Thread.__init__(self)
        self.offer = offer
    def run(self):
        threadLock.acquire()
        self.offer.click()
        threadLock.release()

class VonsHelper(object):
    def __init__(self, driver):
        self.driver = driver
        self.savings = 0.00
        self.threads = []

    def handle_popups(self):
        '''close change my store popup'''
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'ssAdvancedDialogLeftButton'))
            ).click()
        except:
            '''no popup opened'''
            pass

    def add_deals(self):
        '''click all displayed (unadded) deals, go through 20 pages'''
        for i in range(10):
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            WebDriverWait(self.driver, 3)
        deals = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.LINK_TEXT, 'Add')))
        for deal in deals:
            t = CouponThread(deal)
            self.threads.append(t)
            self.threads[-1].start()
        for thread in self.threads:
            thread.join()
        print("you saved around ${:.2f}".format(self.savings))

if __name__ == '__main__':
    '''initialize browser'''
    driver = webdriver.Chrome()
    helper = VonsHelper(driver)
    driver.get(loginUrl)

    '''login'''
    uid = driver.find_element_by_name('userId')
    uid.send_keys(username)
    psw = driver.find_element_by_class_name('fakeiInputAlteredTextBox')
    psw.send_keys(password)
    driver.find_element_by_id('SignInBtn').click()

    '''add deals'''
    driver.get(url)
    helper.handle_popups()
    helper.add_deals()

    '''close browser'''
    driver.quit()
