import asyncio
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import exceptions
from time import sleep
from selenium.webdriver.common.keys import Keys

options = Options()
options.add_argument("start-maximized")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-notifications")
options.add_argument("--disable-features=PopupBlocking")
s = Service('./chromedriver')
driver = webdriver.Chrome(service=s, options=options)
driver.implicitly_wait(15)
driver.get('https://online.metro-cc.ru/category/sladosti-chipsy-sneki/shokolad-batonchiki?in_stock=1')

actions = ActionChains(driver)

actions.move_by_offset(0, 0).click().perform()

close = driver.find_element(By.XPATH, "//button[@class='simple-button reset-button catalog--online offline-prices-sorting--best-level shop-select-dialog__close only-desktop']")
close.click()

wait = WebDriverWait(driver, 15)

city_set = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='header-address__receive-button address-placeholder delivery']")))
city_set.click()
city_obtainment = driver.find_element(By.XPATH, "//span[@class='obtainments-list__content']")
city_obtainment.click()
city_name = driver.find_element(By.XPATH, "//input[@class='multiselect__input']")
driver.find_element(By.XPATH, "//span[@class='multiselect__single']").click()
# city = input("Введите название города: ")
city_name.send_keys("Санкт-Петербург")
city_name.send_keys(Keys.ENTER)
btn = driver.find_element(By.XPATH, "//button[@class='rectangle-button reset--button-styles blue lg normal wide']")
btn.click()

count = driver.find_element(By.XPATH, "//span[@class='heading-products-count subcategory-or-type__heading-count']").text
count = count.split()
count = int(count[0])

while True:
    wait = WebDriverWait(driver, 15)
    try:
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='rectangle-button reset--button-styles subcategory-or-type__load-more best-blue-outlined medium normal']")))
        button.click()
        sleep(1)
    except exceptions.TimeoutException:
        break

products = driver.find_elements(By.XPATH, "//a[@data-qa='product-card-photo-link']")
product_links = [products[i].get_attribute('href') for i in range(count)] ## ПОменять на count  при запуске

"""Функция обработки ссылки, получение данных о продукте и сохранение в JSON-файл"""
async def process_product(link):
    try:
        driver.get(link)
        sleep(1)
        product_id = driver.find_element(By.XPATH, "//p[@itemprop='productID']").text
        product_id = int(product_id.split()[1])
        brand = driver.find_element(By.XPATH, "//a[@class='product-attributes__list-item-link reset-link active-blue-text']").text
        url = link
        name = driver.find_element(By.XPATH, "//meta[@itemprop='name']").get_attribute('content')
        price = driver.find_elements(By.XPATH, "//div[@class='product-prices-block product-page-content__prices-main style--product-page-top catalog--online offline-prices-sorting--best-level']//span[@class='product-price__sum-rubles']")
        try:
            if len(price[0].text) > 2:
                price, sale_price = int(price[0].text.replace(' ', '')), int(price[1].text.replace(' ', ''))
            else:
                price, sale_price = int(price[0].text), int(price[1].text)
        except Exception:
            if len(price[0].text) > 2:
                price = int(price[0].text.replace(' ', ''))
            else:
                price = int(price[0].text)
            sale_price = None
        item = {
            "id": product_id,
            "brand": brand,
            "url": url,
            "name": name,
            "price": price,
            "sale_price": sale_price
        }

        with open('processed_items.json', 'a') as f:
            json.dump(item, f, indent=4)
            f.write('\n')
    except Exception as err:
        print(err)



"""Функция для обработки всех ссылок продуктов"""
async def process_all_products():
    tasks = []
    for link in product_links:
        task = asyncio.create_task(process_product(link))
        tasks.append(task)
    await asyncio.gather(*tasks)

# Запуск обработки ссылок на продукты
asyncio.run(process_all_products())

# Закрытие браузера
driver.quit()




