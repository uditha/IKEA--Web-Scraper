#import libs
import pathlib
import re
import time
import json


import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=2560,1440")
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

def hasClass(el, cls):
    return  cls in el.get_attribute('class').split()

def setUpDriver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def getUrlWithTranslator(original_url):
    shorten_url = original_url.replace('https://www.ikea.com', '')
    return f'https://www-ikea-com.translate.goog{shorten_url}?_x_tr_sl=auto&_x_tr_tl=uk&_x_tr_hl=en&_x_tr_pto=wapp'


def acceptCookies(driver):
    try:
        cookieBtn = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
        if cookieBtn:
            cookieBtn.click()
    except:
        pass


def getFullName(driver):
    title = driver.find_element(By.CLASS_NAME, "pip-header-section__title--big").text
    sub_name_el = driver.find_element(By.CLASS_NAME,'pip-header-section__description-text')
    sub_name = WebDriverWait(sub_name_el, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "font"))).text
    return  'IKEA ' + title + ' ' + sub_name


def getProductDescription(driver):
    general_text = driver.find_element(By.CLASS_NAME, 'pip-product-summary__description').text
    general_text = "<p>" + general_text + "</p>"
    #open Model
    fist_btn = driver.find_element(By.CLASS_NAME,'pip-chunky-header__details')
    driver.execute_script("arguments[0].click();", fist_btn)
    
    modalHeader = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='range-modal-mount-node']//*[@class='pip-product-details__title']/font/font"))).text
    modalText = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='range-modal-mount-node']//*[@class='pip-product-details__container']"))).text
    metBtn = driver.find_element(By.XPATH, '//*[@id="product-details-material-and-care"]/div[1]/button').click()
    
    time.sleep(2)
    
    metText = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='SEC_product-details-material-and-care']/div"))).text
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    
    measbtn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pip-product-information-section"]/div[2]/button'))).click()
    measTitle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="range-modal-mount-node"]/div/div[3]/div/div[2]/div/div/div/h2/font/font'))).text
    measText = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="range-modal-mount-node"]/div/div[3]/div/div[2]/div/div/div/div[1]'))).text
    
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    
    return (general_text + "<br> <strong> " + modalHeader + "</strong><br ><br>" + modalText + '<br><br>' + metText + '<br><br><strong>' + measTitle + '</strong><br><br>' + measText).replace('\n', '<br >').replace('Дизайнер', '<br><strong> Дизайнер</strong>').replace('Матеріали', '<strong>Матеріали</strong>')


def getProductSKU(driver):
    return WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pip-product-identifier__value'))).text

def getPrice(driver):
    patternInt = '.*?(?P<Integer>[0-9]+)'
    try:
        intText =  WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pip-temp-price__integer'))).text 
        result = re.compile(patternInt).search(intText)
        pInt = result.group('Integer')
    except:
         pInt = 0
         
    try:
        intText =  driver.find_element(By.CLASS_NAME,'pip-temp-price__decimal').text 
        result = re.compile(patternInt).search(intText)
        pDes = result.group('Integer')
    except:
         pDes = 0
         
    try:
        priceSubscript =  driver.find_element(By.CLASS_NAME,'pip-temp-price__sr-text').text.split('/')[1]
    except:
         priceSubscript = ''
         
    price = float(pInt) + float(int(pDes)/100)
    
    newPrice = price * 1.3 * 7.5
    
    return newPrice
    
    
    
def getImageURL(driver):
    try:
        imageHolder = driver.find_elements(By.CLASS_NAME, 'pip-media-grid__media-image')[0]
        imageURL = imageHolder.find_element(By.TAG_NAME, 'img').get_attribute('src')
    except:
        imageURL = ''
    return imageURL
    
    
def getAvailability(driver):
    try:
        availableBtn = driver.find_element(By.CLASS_NAME, 'pip-availability-modal-open-button')
        action = ActionChains(driver)
        action.move_to_element(availableBtn).click().perform()
    except:
        availableBtn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="pip-stockcheck__text-container"]/span/button')))
        action = ActionChains(driver)
        action.move_to_element(availableBtn).click().perform()
     
    searchInput = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="change-store-input"]'))).send_keys("Katowice")
    getStoreList = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="range-modal-mount-node"]/div/div[3]/div/div[2]/div/div/div/div[3]'))).find_element(By.CLASS_NAME,'pip-status--leading')
    return  hasClass(getStoreList, 'pip-status--green')
  

def getNumPages(driver):
    pagText = driver.find_element(By.CLASS_NAME, 'catalog-product-list__total-count').text 
    numList = (re.findall(r'\d+', pagText))
    pageNumber = (int(numList[1])//int(numList[0])) + 1
    return pageNumber

def scrollToBottom(driver):
    SCROLL_PAUSE_TIME = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
        
def createLinksFile(driver):
    with open('urls.txt') as file:
        lines = file.read().splitlines()
        
    linksToScrape = []
        
    for line in lines[0:1]:
        driver.get(line)
        acceptCookies(driver)
        numPages = getNumPages(driver)
        newURL = line+ f'?page={numPages}'
        time.sleep(3)
        driver.get(newURL)
        acceptCookies(driver)
        scrollToBottom(driver)
        
        productHolder = driver.find_element(By.CLASS_NAME, 'plp-product-list__products')
        cards = productHolder.find_elements(By.CLASS_NAME, 'plp-fragment-wrapper')
        
        for card in cards[0:10]:
            item = {}
            try:
                product = card.find_element(By.CLASS_NAME, 'pip-product-compact')
                
                item["ProductID"] = product.get_attribute('data-product-number')
                item["link"] = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
                item["originalPrice"] = product.get_attribute('data-price')
                
                linksToScrape.append(item)
            except Exception as e:
                print(e)
        
        time.sleep(5)
    
    linksDB = pd.DataFrame(linksToScrape)
    linksDB.to_csv('links.csv', index=False)
    print('[INFO] LINKS File is created.')
    
    
def saveData(path, item):
    if path.is_file():
        df1 = pd.read_csv(path) 
        df2 = pd.DataFrame([item]) 
        frames = [df1,df2]
        df = pd.concat(frames)
    else:
        data = [item]
        df = pd.DataFrame(data)
        
    #df.Description = df.Description.apply(lambda x : x.replace('\n', '\\n'))
    df.to_csv('items.csv', index=False)     
        
def getItem(driver, row):
    url = getUrlWithTranslator(row['link'])
    driver.get(url)
    acceptCookies(driver)
    item = {}
    item['ProductID'] = row['ProductID']
    item['productURL'] = row['link']
    item['Name'] = getFullName(driver)
    item['Description'] = getProductDescription(driver)
    item['ProductSKU'] = getProductSKU(driver)
    item['Price PL'] = float(row['originalPrice'])
    item['Margin'] = 1.3
    item['Convert'] = 7.5
    item['Price UA'] = 0
    item['Price'] = getPrice(driver)
    item['ImageURL'] = getImageURL(driver)
    item['InStock'] = getAvailability(driver)
    print(f"[INFO] ITEM { item['ProductID'] } is added.")
    
    return item
        


def main():
    print('[INFO] Scraping Started.')
      
    driver = setUpDriver()
    
    createLinksFile(driver)
    df = pd.read_csv('links.csv')
    
    pathToFile = "items.csv"
    path = pathlib.Path(pathToFile)
    
    item_in_file = []
    
    if path.is_file():
        item_df = pd.read_csv(path)
        item_in_file = item_df['ProductID'].to_list()
    
    
    for index, row in df.iterrows():
        if row['ProductID'] not in item_in_file:
            item = getItem(driver, row)
            saveData(path, item)
        
    print('[INFO] Scraping FINISED.')
    

if __name__ == '__main__':
    main()