# -*- coding: utf-8 -*-
import re
import scrapy
from meitulu.items import MeituluItem


class MtlSpider(scrapy.Spider):
    name = 'mtl'
    allowed_domains = ['www.meitulu.com']
    start_urls = ['https://www.meitulu.com/t/xinggan/2.html']

    def parse(self, response):
        next_pages = response.xpath('//a[@class="a1"]/@href').extract()[1]
        current_page = int(response.xpath('//div[@id="pages"]/span/text()').extract_first())
        next_page = int(re.findall(r'\d+', next_pages)[0])
        if next_page > current_page:
            yield scrapy.Request(next_pages, callback=self.parse)

        links = response.xpath('//li/a[@target="_blank"]/@href').extract()
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_img)

    def parse_img(self, response):
        next_pages = response.xpath('//div[@id="pages"]/a[last()]/@href').extract_first()
        current_page = int(response.xpath('//div[@id="pages"]/span/text()').extract_first())
        next_page = int(re.findall(r'\d+_(\d+)', next_pages)[0])
        if next_page > current_page:
            next_pages = 'https://www.meitulu.com' + next_pages
            yield scrapy.Request(next_pages, callback=self.parse_img)

        item = MeituluItem()
        title = response.xpath('//h1/text()').extract_first()
        item['title'] = re.sub(r' \d+/\d+', '', title)
        item['urls'] = response.xpath('//div[@class="content"]/center/img/@src').extract()

        yield item