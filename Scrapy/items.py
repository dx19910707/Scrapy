# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item,Field


class TestItem(Item):
    title = Field()
    link = Field()

class MeiNvItem(Item):
    title = Field()
    link = Field()

class TiebaItem(Item):
    name = Field()
    title = Field()
    author = Field()
    reply = Field()

class WeiboInfoItem(Item):
    Uid = Field()  # 用户ID
    NickName = Field()  # 昵称
    Fans = Field()  # 粉丝数
    Follows = Field()  # 关注数
    Profiles = Field()  # 微博数
    Gender = Field()  # 性别
    Province = Field()  # 所在省
    City = Field()  # 所在城市
    BriefIntroduction = Field()  # 简介
    Birthday = Field()  # 生日
    SexualOrientation = Field()  # 性取向
    Sentiment = Field()  # 感情状况
    VIPlevel = Field()  # 会员等级
    Authentication = Field()  # 认证
    School = Field()  # 毕业学校
    Tag = Field()  # 标签
