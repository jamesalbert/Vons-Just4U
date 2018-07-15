from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import threading
import random
import re
import sys
import time

try:
    sys.argv.pop(0)
    username, password = sys.argv
except:
    exit('you must give a username and password')


storedId = 2229
loginUrl = "https://www.safeway.com/ShopStores/OSSO-Login.page?goto=http%3A%2F%2Fwww.safeway.com%2FIFL%2FGrocery%2FHome"
url = 'http://www.safeway.com/ShopStores/Justforu-Coupons.page#/category/all'
threadLock = threading.Lock()

class CouponThread(threading.Thread):

    def __init__(self, offer):
        threading.Thread.__init__(self)
        self.offer = offer


    def run(self):
        threadLock.acquire()
        self.offer.click()
        time.sleep(1)
        threadLock.release()


class VonsHelper(object):

    def __init__(self, driver):
        self.driver = driver
        self.savings = 0.00
        self.threads = []


    def handle_popups(self):
        '''close change my store popup'''
        # try:
        self.random_user_interaction()
        store = WebDriverWait(self.driver, 10000).until(
            EC.element_to_be_clickable((By.ID, 'ssAdvancedDialogLeftButton'))
        )
        if store:
            store.click()
            time.sleep(10)
        # except:
            # '''no popup opened'''
            # pass


    def random_user_interaction(self):
        for i in range(20):
            y = random.choice(["document.body.scrollHeight"] * 10 + ["0"])
            print(f"scrolling to {y}")
            self.driver.execute_script(f'window.scrollTo(0, {y});')


    def add_deals(self):
        '''click all displayed (unadded) deals, go through 20 pages'''
        added = list()
        unadded = list()
        while len(unadded + added) < 400:
            print(f'added: {len(added)}; unadded: {len(unadded)}')
            try:
                unadded = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_all_elements_located((By.LINK_TEXT, 'Add')))
                added = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[text()='Added']")))
            except:
                pass
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
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
    # driver.get(loginUrl)

    '''login'''
    driver.get(url)
    uid = driver.find_element_by_name('input-email')
    uid.send_keys(username)
    psw = driver.find_element_by_name('password-password')
    psw.send_keys(password + Keys.ENTER)

    '''add deals'''
    helper.handle_popups()
    helper.add_deals()

    '''close browser'''
    driver.quit()
