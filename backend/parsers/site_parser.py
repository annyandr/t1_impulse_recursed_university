from selenium import webdriver
from selenium.webdriver.common.by import By


def site_parser(url, out_file='output.txt'):
    # Инициализация chrome webdriver
    driver = webdriver.Chrome()

    # Загрузка страницы
    driver.get(url)

    # Ждём, пока загрузится заголовок при динамическом исполнении JS
    driver.implicitly_wait(10)

    text = str(driver.find_element(
        By.XPATH, '//*[@id="notion-app"]/div/div[1]/div/div[1]/main').text)

    # Уничтожаем браузер после завершения
    driver.quit()

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(text)

    return text


if __name__ == '__main__':
    print(site_parser(
        'https://www.notion.so/154a0fae390f4813958094aa948a97fd'))
