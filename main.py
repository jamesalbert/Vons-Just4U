from selenium import webdriver
import threading
import sys

loginUrl = "https://www.vons.com/ShopStores/OSSO-Login.page?goto=http%3A%2F%2Fwww.vons.com%2FIFL%2FGrocery%2FHome"
urls = ['http://www.vons.com/ShopStores/Justforu-PersonalizedDeals.page',
        'http://www.vons.com/ShopStores/Justforu-CouponCenter.page']

open('./output.log', 'w+').close()

try:
    sys.argv.pop(0)
    username, password = sys.argv
except:
    exit('you must give a username and password')


def click_all(buttons):
    for b in buttons:
        try:
            if 'Added' not in b.text:
                b.click()
                print 'added'
        except Exception:
            pass
    return

def addDeals():
    '''
    go through personalized and Just4U deals and add them
    '''
    driver = webdriver.Chrome()
    driver.get(loginUrl)

    '''login'''
    uid = driver.find_element_by_name('userId')
    uid.send_keys(username)
    psw = driver.find_element_by_class_name('fakeiInputAlteredTextBox')
    psw.send_keys(password)
    driver.find_element_by_id('SignInBtn').click()

    for url in urls:
        driver.get(url)

        '''close any popups'''
        try:
            driver.implicitly_wait(5)
            driver.find_element_by_class_name('bt-close-button').click()
        except:
            '''no popup opened'''
            pass

        '''click all displayed (unadded) deals, go through 20 pages'''
        for i in range(20):
            deals = driver.find_elements_by_class_name('lt-place-add-button')
            p = threading.Thread(target=click_all, args=(deals,))
            p.start()
            p.join()
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight / 2);')
            driver.implicitly_wait(5)

    '''close browser'''
    driver.close()
    out.write('deals added...\n')
    out.close()

if __name__ == '__main__':
    out = open('output.log', 'a')
    addDeals()
    out.close()