from selenium import webdriver
from selenium.webdriver.common.by import By


def site_parser(url):
    # Инициализация chrome webdriver
    driver = webdriver.Chrome()

    # Загрузка страницы
    driver.get(url)

    # Ждём, пока загрузится заголовок при динамическом исполнении JS
    driver.implicitly_wait(10)

    # Selenium может извлечь динамически загруженные элементы
    print(driver.title)

    print(driver.find_element(
        By.XPATH, '//*[@id="notion-app"]/div/div[1]/div/div[1]/main/div/div/div[3]/div').text)

    # Уничтожаем браузер после завершения
    driver.quit()


print(site_parser(
    'https://important-single-18b.notion.site/154a0fae390f4813958094aa948a97fd')
)
