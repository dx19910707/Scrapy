import scrapy
from ..items import TestItem

class TestSpider(scrapy.Spider):
    name = 'test_spider'
    hearder = {
        'User-Agent': 'User-Agent:Mozilla/5.0(X11; Linux x86_64)'
                        'AppleWebKit/537.36(KHTML, like Gecko)'
                        'Chrome/63.0.3239.84 Safari/537.36',
        'Host': 'www.win4000.com',
        'Referer': 'http://www.win4000.com/meitu.html'
    }

    def start_requests(self):
        urls = [
            'http://www.win4000.com/meitu.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url,headers=self.hearder,callback=self.parse)

    def parse(self, response):
        item = TestItem()
        a_space = response.xpath('//div[@class="tab_box"]/*/ul[@class="clearfix"]/li/a')
        for a in a_space:
            item['title'] = a.xpath('p/text()').extract()
            item['link'] = a.xpath('img/@data-original').extract()
            yield item