import time,json,re
from scrapy import Request
from scrapy import Spider
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox
from ..config import pwd
from ..items import WeiboInfoItem
from scrapy.selector import Selector
import datetime
from lxml import etree
import requests

class WeiboSpider(Spider):
    name = "weibo"
    host = "https://weibo.cn/"
    account = 'dx19910707@qq.com'
    password = pwd

    start_uids = ['3222383844']

    custom_settings = {
        'ROBOTSTXT_OBEY':False,
        'ITEM_PIPELINES':{'Scrapy.pipelines.MysqlPipeline': 1,}
    }

    def start_requests(self):
        for uid in self.start_uids:
            url = self.host + uid
            cookies = self.get_cookie(self.account,self.password)
            return [Request(url,cookies=eval(cookies), callback=self.post_login)]

    def post_login(self,response):
        uid = re.findall('https://weibo.cn/(\d+)', response.url)
        if uid:
            uid = uid[0]
        else:
            uid = response.xpath('//body//div[@class="ut"]/a').xpath('@href').extract()
            uid = re.findall('/(\d+)/info',str(uid))[0]
        texts = response.xpath('//body//div[@class="tip2"]/*/text()')
        texts = str(texts.extract())
        num_profiles = re.findall('微博\[(\d+)\]', texts)
        num_follows = re.findall('关注\[(\d+)\]', texts)
        num_fans = re.findall('粉丝\[(\d+)\]', texts)
        info_item = WeiboInfoItem()
        info_item['Uid'] = uid
        info_item['Profiles'] = num_profiles[0]
        info_item['Follows'] = num_follows[0]
        info_item['Fans'] = num_fans[0]
        info = {}
        info['info'] = info_item
        yield Request(url="https://weibo.cn/%s/info" % uid, callback=self.parse_information,dont_filter=True,meta={'info':info_item})
        # yield Request(url="https://weibo.cn/%s/profile?page=1" % uid, callback=self.parse_profiles, dont_filter=True)
        # yield Request(url="https://weibo.cn/%s/follow" % uid, callback=self.parse_relationship, dont_filter=True)
        # yield Request(url="https://weibo.cn/%s/fans" % uid, callback=self.parse_relationship, dont_filter=True)

    def parse_information(self, response):
        """ 抓取个人信息 """
        info = self.get_info(response)
        yield info
        # yield Request(url="https://weibo.cn/%s/profile?filter=1&page=1" % ID, callback=self.parse_tweets, dont_filter=True)
        # yield Request(url="https://weibo.cn/%s/profile?page=1" % ID, callback=self.parse_tweets, dont_filter=True)
        # yield Request(url="https://weibo.cn/%s/follow" % ID, callback=self.parse_relationship, dont_filter=True)
        # yield Request(url="https://weibo.cn/%s/fans" % ID, callback=self.parse_relationship, dont_filter=True)

    def parse_profiles(self, response):
        """ 抓取微博数据 """
        ID = re.findall('(\d+)/profile', response.url)[0]
        divs = response.xpath('body/div[@class="c" and @id]')
        for div in divs:
            time.sleep(2)
            profiles = self.get_profiles(ID,div)
            yield profiles
        url_next = response.xpath('body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], callback=self.parse_profiles, dont_filter=True)

    def parse_relationship(self, response):
        """ 打开url爬取里面的个人ID """
        if "/follow" in response.url:
            ID = re.findall('(\d+)/follow', response.url)[0]
            flag = True
        else:
            ID = re.findall('(\d+)/fans', response.url)[0]
            flag = False
        urls = response.xpath('//a[text()="关注他" or text()="关注她"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        for uid in uids:
            relationshipsItem = {}
            relationshipsItem["Host1"] = ID if flag else uid
            relationshipsItem["Host2"] = uid if flag else ID
            yield relationshipsItem
            yield Request(url="https://weibo.cn/%s/info" % uid, callback=self.parse_information)

        next_url = response.xpath('//a[text()="下页"]/@href').extract()
        if next_url:
            yield Request(url=self.host + next_url[0], callback=self.parse_relationship, dont_filter=True)

    def get_cookie(self,account, password):
        """ 获取一个账号的Cookie """
        try:
            options = Options()
            options.add_argument('-headless')  # 无头参数
            browser = Firefox(firefox_options=options)  # 配了环境变量第一个参数就可以省了，不然传绝对路径
            browser.get("https://weibo.cn/login/")
            time.sleep(1)

            failure = 0
            while "微博" in browser.title and failure < 5:
                failure += 1
                username = browser.find_element_by_id("loginName")
                username.clear()
                username.send_keys(account)

                pwd = browser.find_element_by_xpath('//input[@type="password"]')
                pwd.clear()
                pwd.send_keys(password)

                commit = browser.find_element_by_id("loginAction")
                commit.click()
                time.sleep(3)
                browser.save_screenshot("aa.png")
                if "我的首页" not in browser.title:
                    time.sleep(4)
                if '未激活微博' in browser.page_source:
                    print('账号未开通微博')
                    return {}

            cookie = {}
            if "我的首页" in browser.title:
                for elem in browser.get_cookies():
                    cookie[elem["name"]] = elem["value"]
            return json.dumps(cookie)
        except Exception as e:
            return ""
        finally:
            try:
                browser.quit()
            except Exception as e:
                pass

    def get_info(self, response):
        info = response.meta['info']
        text1 = ";".join(response.xpath('body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
        nickname = re.findall('昵称;:?(.*?);', text1) or re.findall('昵称:(.*?);', text1)
        gender = re.findall('性别;:?(.*?);', text1) or re.findall('性别:?(.*?);', text1)
        place = re.findall('地区;:?(.*?);', text1) or re.findall('地区:(.*?);', text1)
        briefIntroduction = re.findall('简介;:?(.*?);', text1) or re.findall('简介:(.*?);', text1)
        birthday = re.findall('生日;:?(.*?);', text1) or re.findall('生日:(.*?);', text1)
        sexOrientation = re.findall('性取向;:?(.*?);', text1) or re.findall('性取向:(.*?);', text1)
        sentiment = re.findall('感情状况;:?(.*?);', text1) or re.findall('感情状况:(.*?);', text1)
        vipLevel = re.findall('会员等级;:?(.*?);', text1) or re.findall('会员等级：(.*?);', text1)
        authentication = re.findall('认证;:?(.*?);', text1) or re.findall('认证:(.*?);', text1)
        school = re.findall('·;(.*?);', text1) or re.findall('·(.*?);', text1)
        tag = re.findall('标签:;(.*?)更多',text1)

        info['School'] = school[0].replace('\xa0','') if school else ''
        info["NickName"] = nickname[0] if nickname else ''
        info["Gender"] = gender[0] if gender else ''
        if place:
            place = place[0].split(" ")
        info["Province"] = place[0] if place else ''
        info["City"] = place[1] if len(place) > 1 else ''
        info["BriefIntroduction"] = briefIntroduction[0] if briefIntroduction and briefIntroduction[0] else ''
        birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d") if birthday else ''
        info["Birthday"] = birthday
        info["Sentiment"] = sentiment[0] if sentiment else ''
        info["VIPlevel"] = vipLevel[0].replace('\xa0','') if vipLevel else 0
        info["Authentication"] = authentication[0] if authentication else ''
        info["Tag"] = tag[0].replace(';\xa0','') if tag else ''
        if sexOrientation and sexOrientation[0]:
            if sexOrientation[0] == gender[0]:
                info["SexualOrientation"] = "同性恋"
            else:
                info["SexualOrientation"] = "异性恋"
        else:
            info["SexualOrientation"] = ''
        return info

    def get_profiles(self,ID,div):
        tweetsItems = {}
        id = div.xpath('@id').extract_first()  # 微博ID
        content = div.xpath('div/span[@class="ctt"]//text()').extract()  # 微博内容
        cooridinates = div.xpath('div/a/@href').extract()  # 定位坐标
        like = re.findall('赞\[(\d+)\]', div.extract())  # 点赞数
        transfer = re.findall('转发\[(\d+)\]', div.extract())  # 转载数
        comment = re.findall('评论\[(\d+)\]', div.extract())  # 评论数
        others = div.xpath('div/span[@class="ct"]/text()').extract()  # 求时间和使用工具（手机或平台）

        tweetsItems["_id"] = ID + "-" + id
        tweetsItems["ID"] = ID
        if content:
            tweetsItems["Content"] = " ".join(content).strip('[位置]')  # 去掉最后的"[位置]"
        if cooridinates:
            cooridinates = re.findall('center=([\d.,]+)', cooridinates[0])
            if cooridinates:
                tweetsItems["Co_oridinates"] = cooridinates[0]
        if like:
            tweetsItems["Like"] = int(like[0])
        if transfer:
            tweetsItems["Transfer"] = int(transfer[0])
        if comment:
            tweetsItems["Comment"] = int(comment[0])
        if others:
            others = others[0].split('来自')
            tweetsItems["PubTime"] = others[0]
            if len(others) == 2:
                tweetsItems["Tools"] = others[1]
        return tweetsItems