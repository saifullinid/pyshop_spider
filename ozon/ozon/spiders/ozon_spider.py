# coding: cp1251
import random
import time

import scrapy


class OzonSpider(scrapy.Spider):
    name = 'ozon'
    phones_links = []
    base_url = 'https://www.ozon.ru'

    def add_links_to_phones_links(self, phones_links):
        for link in phones_links:
            self.phones_links.append(f'{self.base_url}{link}')

    def start_requests(self):
        url = 'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating&type=49659'
        yield scrapy.Request(url, callback=self.get_phones_links_from_first_page)

    def get_phones_links_from_first_page(self, response, **kwargs):
        next_page_url = response.selector.xpath("//a[./div/div[contains(text(), 'Дальше')]]/@href").get()
        start_url = next_page_url[:next_page_url.find('page=')]
        end_url = next_page_url[next_page_url.find('&', next_page_url.find('page=')):]

        links_to_phone_pages = response.selector.xpath('//a[@class="tile-hover-target k8n"]/@href').getall()
        self.add_links_to_phones_links(links_to_phone_pages)

        current_page = 1
        while len(self.phones_links) < 100:
            current_page += 1
            next_page_url = f'{self.base_url}{start_url}page={current_page}{end_url}'
            time.sleep(random.randint(2, 4))

            yield scrapy.Request(next_page_url, callback=self.get_phones_links_from_next_pages)

        with open('ozon/spiders/file.txt', 'w'):
            pass

        for url in self.phones_links[:100]:
            time.sleep(random.randint(1, 8))
            yield scrapy.Request(url, callback=self.parse_data)

    def get_phones_links_from_next_pages(self, response, **kwargs):
        time.sleep(random.randint(2, 4))
        links_to_phone_pages = response.selector.xpath('//a[@class="tile-hover-target k8n"]/@href').getall()

        self.add_links_to_phones_links(links_to_phone_pages)

    def parse_data(self, response, **kwargs):
        time.sleep(random.randint(3, 7))

        data = response.selector.xpath("//dl[.//span[contains(text(),'Версия ')]]/dd/text()").get()
        if not data:
            data = response.selector.xpath("//dl[.//span[contains(text(),'Версия ')]]/dd/a/text()").get()

        # у некоторых телефонов не указана версия ОС
        if not data:
            data = 'Not found OS'

        with open('ozon/spiders/file.txt', 'a') as file:
            file.write(data + '\n')
