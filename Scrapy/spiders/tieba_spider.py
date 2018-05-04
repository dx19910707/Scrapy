from scrapy import Spider,Request
from ..items import TiebaItem

class TiebaSpider(Spider):
    _description = "爬取百度贴吧第一页帖子的帖子名称，发帖人，回复数量"

    name = 'tieba'
    # Tname = input('请输入需要查询的贴吧名称:')
    Tname = '福州'
    start_urls = ['https://tieba.baidu.com/f?ie=utf-8&kw={}&fr=search'.format(Tname)]

    def parse(self, response):

        item = TiebaItem()
        name = response.xpath('//a[@class=" card_title_fname"]/text()').extract()
        tops = response.xpath('//li[@class=" j_thread_list thread_top j_thread_list clearfix"]')
        bodies = response.xpath('//li[@class=" j_thread_list clearfix"]')

        if not name:
            Tname = input('贴吧%s不存在！请重新输入:'%(self.Tname if self.Tname else name))
            self.Tname = ''
            url = 'https://tieba.baidu.com/f?ie=utf-8&kw={}&fr=search'.format(Tname)
            yield Request(url=url, callback=self.parse)

        def update_item(item,data):
            # 不知道什么BUG会导致取到某一条数据时把后面的数据都取完了，只取第一条就好
            item['title'] = data.xpath('.//a[@class="j_th_tit "]/text()').extract()[:1]
            try:
                item['author'] = data.xpath('.//span[@class="tb_icon_author "]/@title').extract()[0].split('主题作者: ')[1:]
            except:
                item['author'] = data.xpath('.//span[@class="frs-author-name-wrap"]/a/text()').extract()
            item['reply'] = data.xpath('.//span[@class="threadlist_rep_num center_text"]/text()').extract()[:1]
            return item

        item['name'] = name[0].split()
        for top in tops:
            item = update_item(item, top)
            yield item

        for body in bodies:
            item = update_item(item, body)
            yield item

