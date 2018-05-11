# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
import re,pymysql


class MeinvPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['link']:
            if re.match(r'^http://.*$',url):
                yield Request(url,meta={'item':item})

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        if not isinstance(request,Request):
            url = request
        else:
            url = request.url
        image_name = url.split('/')[-1][:-4]
        image_path = item['title'][0] + '\\' + image_name
        return '%s.jpg' % image_path


from .items import WeiboInfoItem
class MysqlPipeline(object):
    def __init__(self):
        self.count = 1
        self.conn = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='sina',
            use_unicode = True,
            charset = 'utf8',
        )
        self.cr = self.conn.cursor()

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, WeiboInfoItem):
            try:
                print("***********at beginning of saving**********")
                key = []
                value = []
                for k, v in item._values.items():
                    if v:
                        key.append(k)
                        value.append(v)
                key = str(key).replace('[', '(').replace(']', ')').replace('\'', '`')
                value = str(value).replace('[', '(').replace(']', ')').replace('\\\\','\\')
                query = 'INSERT INTO info ' + key + ' VALUES ' + value
                self.cr.execute(query)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                if e.args[0] != 1062:
                    try:
                        query = 'INSERT INTO error_info(UID,Nickname,error_info) VALUES ' + str((item._values['Uid'],item._values['NickName'],(e.args[1]).replace('\"','').replace('\'','').replace('\\\\','\\')))
                        self.cr.execute(query)
                        self.conn.commit()
                    except Exception as e:
                        print(e,item._values['Uid'],item._values['NickName'])
        return item
