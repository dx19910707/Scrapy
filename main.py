from scrapy import cmdline

# cmdline.execute("scrapy crawl meinv".split())  # 爬取美女图片
# cmdline.execute("scrapy crawl tieba -o tieba.json".split())  # 爬取百度贴吧
cmdline.execute("scrapy crawl weibo".split())