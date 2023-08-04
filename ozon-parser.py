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

    def _parse_seller(self, url: str) -> str:
        """ Парсинг страницы продавца. """
        try:
            self._init_driver()
            self.driver.get(url)
            time.sleep(3)
            self.driver.execute_script('window.scrollTo(5, 4000);')
            time.sleep(5)
            return self.driver.page_source
        except Exception as ex:
            print(ex)
            self._delete_driver()
        finally:
            self._delete_driver()

    def _parse_product(self, url: str) -> (str, int, dict):
        """ Сбор данных о продукте """
        try:
            self._init_driver()
            self.driver.get(url)
        except Exception as ex:
            print(ex)
            self._delete_driver()
        else:
            time.sleep(4)
            self.driver.execute_script('window.scrollTo(5, 4000);')
            time.sleep(3)
            page = BeautifulSoup(self.driver.page_source, features='html.parser')
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
        finally:
            self._delete_driver()

    def parse(self, url: str, count: int):
        """ Главная функция парсинга """
        seller_page = self._parse_seller(url)
        seller_page = BeautifulSoup(seller_page, features='html.parser')
        href_list = seller_page.find(attrs={'data-widget': 'searchResultsV2'}).find_all('a')
        product_list = []
        for item in href_list:
            link = f'https://www.ozon.ru{item.attrs["href"]}'
            if link not in product_list:
                product_list.append(link)
        seller_name = seller_page.find('h1', class_='tsHeadline600Medium').string
        seller = Seller.objects.create(name=seller_name, url=url)
        for i in range(count):
            name, price, characteristics = self._parse_product(product_list[i])
            Product.objects.create(name=name, url=product_list[i], price=price, seller=seller,
                                   characteristics=characteristics)
