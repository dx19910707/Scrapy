import scrapy
from ..items import MeiNvItem

class MeiNv(scrapy.Spider):
    name = 'meinv'
    hearder = {
        'User-Agent': 'User-Agent:Mozilla/5.0(X11; Linux x86_64)'
                        'AppleWebKit/537.36(KHTML, like Gecko)'
                        'Chrome/63.0.3239.84 Safari/537.36',
        'Host': 'www.win4000.com',
        'Referer': 'http://www.win4000.com/meitu.html'
    }
    custom_settings = {
        'ITEM_PIPELINES': {'Scrapy.pipelines.MeinvPipeline': 1,},
        'IMAGES_STORE':'E:/spider_download/images2',
    }

    def start_requests(self):
        urls = [
            'http://www.win4000.com/meitu.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url,headers=self.hearder,callback=self.parse_homepage)

    def parse_homepage(self, response):
        d = {}
        a_space = response.xpath('//div[@class="tab_box"]/*/ul[@class="clearfix"]/li/a')
        for a in a_space:
            d[a.xpath('p/text()').extract()[0]] = a.xpath('@href').extract()[0]
        for v in d.values():
            yield scrapy.Request(url=v,callback=self.parse_details)

    def parse_details(self, response):
        origin_url = response.url
        r = ''
        if '_' not in response.url:
            r = origin_url[:-5]
        else:
            r = origin_url.split('_')[0]
        title = response.xpath('//div[@class="ptitle"]/h1/text()').extract()[0]
        img_link = response.xpath('//div[@class="pic-meinv"]/a/img/@data-original').extract()[0]
        next_link = response.xpath('//div[@class="pic-meinv"]/a/@href').extract()[0]
        if r in next_link:
            yield scrapy.Request(url=next_link,callback=self.parse_details)
        item = MeiNvItem()
        item['title'] = [title]
        item['link'] = [img_link]
        yield item
