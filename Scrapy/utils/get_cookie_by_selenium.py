from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox
from selenium.webdriver.common.proxy import *
try:
    from . import my_proxy
except ImportError:
    import my_proxy
import time,json,random

""" 获取一个账号的Cookie """
def get_cookie(account, password):
    """ 随机从代理池中取一个"""
    count = 0
    while count < 5:
        myProxy = random.sample(my_proxy.MY_PROXY_LIST, 1)
        try:
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': myProxy,
                'ftpProxy': myProxy,
                'sslProxy': myProxy,
                'noProxy': ''  # set this value as desired
            })
            options = Options()
            options.add_argument('-headless')  # 无头参数
            browser = Firefox(firefox_options=options, proxy=proxy)
            browser.get("https://weibo.cn/login/")
            time.sleep(1)

            if "微博" in browser.title:
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

                cookie = {}
                if "我的首页" in browser.title:
                    for elem in browser.get_cookies():
                        cookie[elem["name"]] = elem["value"]
                    return json.dumps(cookie)
                if '未激活微博' in browser.page_source:
                    print('账号未开通微博')
                    return {}
        except Exception as e:
            print(e)
            count += 1
        finally:
            try:
                browser.quit()
            except Exception as e:
                pass