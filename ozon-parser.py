from selenium import webdriver
import time
from bs4 import BeautifulSoup


def strToInt(str) -> int:
    result = ''
    for s in str:
        if s.isdigit():
            result += s
    return int(result)


class Selenium:
    def _init_driver(self):
        """ Сборка браузера """
        options = webdriver.ChromeOptions()
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/115.0.0.0 Safari/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def _delete_driver(self):
        """ Завершение браузера """
        self.driver.close()
        self.driver.quit()

    def _parse_page(self, url: str) -> BeautifulSoup:
        """ Парсинг страницы """
        try:
            self._init_driver()
            self.driver.get(url)
            time.sleep(3)
            self.driver.execute_script('window.scrollTo(5, 4000);')
            time.sleep(5)
            return BeautifulSoup(self.driver.page_source, features='html.parser')
        except Exception as ex:
            print(ex)
            self._delete_driver()
        finally:
            self._delete_driver()

    def _parse_product(self, url) -> (str, int, dict):
        """ Сбор данных о продукте """
        if type(url) == str:
            page = self._parse_page(url)
        else:
            page = url
        name = page.find(attrs={'data-widget': 'webProductHeading'}).find('h1').text
        span_list = page.find_all('span')
        prices_list = []
        for item in span_list:
            if '₽' in item.text:
                prices_list.append(item.text)
        price = strToInt(prices_list[2])
        div_characteristics = page.find('div', attrs={'data-widget': 'webCharacteristics'})
        characteristics_name = div_characteristics.findAll('dt')
        characteristics_value = div_characteristics.findAll('dd')
        characteristics = {key.text: value.text for key, value in zip(characteristics_name, characteristics_value)}
        return name, price, characteristics

    def parse(self, url: str):
        """ Парсинг страницы. """
        page = self._parse_page(url)
        if page.find('div', attrs={'data-widget': 'webCharacteristics'}):  # Дана страница товара
            name, price, characteristics = self._parse_product(page)
            print(f'Название: {name}\nЦена:{price}\nХарактериски:{characteristics}\n')
        elif page.find(attrs={'data-widget': 'searchResultsSort'}):  # Дан результат фильтра
            href_list = page.find(attrs={'data-widget': 'searchResultsV2'}).find_all('a')
            product_list = []
            for item in href_list:
                link = f'https://www.ozon.ru{item.attrs["href"]}'
                if link not in product_list:
                    product_list.append(link)
            """ Вывод в консоль """
            for i, item in enumerate(product_list):
                name, price, characteristics = self._parse_product(item)
                print(f'{i}) Название: {name}\nЦена:{price}\nХарактериски:{characteristics}\n')


