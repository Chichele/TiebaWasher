#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tigerstudent'

import requests
import re
import time
import random
import urllib
import sys
from bs4 import BeautifulSoup
from settings import *


def login_check(content):
    """
    通过查找页面中是否包含本帐号的百度ID来验证是否登录成功
    :param content: 页面HTML内容
    :return:
    """
    if content.find(baiduID.encode("utf8")) >= 0:
        return True
    return False


def print_delimiter():
    print '-' * 80


def login():
    """
    登录
    """
    global session
    try:
        session = requests.session()
        session.get(baiduUrl)       #打开一次百度首页，获取相关cookies
        page = session.post(loginUrl, data=loginData, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'})
    except:
        print "Login Error"
        return False

    if not login_check(page.content):
        print 'Login failed'
        return False
    else:
        print 'login successful!'
        return True


def build_data(content):
    """
    构造回复帖子时用到的postData
    :param content: 主题贴的HTML内容
    :return: 返回postData
    """
    soup = BeautifulSoup(content)
    data = {'sub1': u'回帖', 'co': replyWords}
    #找出div标签，class为d h的部分，这些都是回帖表单需要的元素
    subjects = soup.find_all(name="div", attrs={"class": "d h"})
    hidden_elems = subjects[0].find_all(name="input", attrs={"type": "hidden"})
    for elem in hidden_elems:
        data[elem['name']] = elem['value']
    return data


def open_subject(subject_url):
    sub_page = session.get(subject_url)
    data = build_data(sub_page.content)
    reply_request = session.post(tiebaUrl+"/submit", data=data)
    #print reply_request.content
    if reply_request.status_code == 200:
        print "[%s]reply successful!: %s" % (time.asctime(), subject_url)
    else:
        print "[%s]reply failed!: %s" % (time.asctime(), subject_url)


def washer():
    """
    打开指定贴吧页面，遍历找出回复数为0的主题贴，打开它并回复该主题贴。
    :return:
    """
    tieba_page = session.get(tiebaUrl+("/m?kw=%s&lp=1030" % urllib.quote(tiebaName.encode("utf8"))))
    soup = BeautifulSoup(tieba_page.content)

    #找出div标签，class为i的部分，即为主题贴的信息
    subjects = soup.find_all(name="div", attrs={"class": "i"})
    if not len(subjects):
        print "[%s]There is nothing to do." % time.asctime()
        return

    for sub in subjects:
        if sub.p.find(text=re.compile(u"回0")):      #如果找到回复为0的
            print "[%s]open subject:%s" % (time.asctime(), tiebaUrl+"/"+sub.a['href'])
            open_subject(tiebaUrl+"/"+sub.a['href'])     #打开该主题，参数为主题贴链接


def sign_in_all():
    """
    获取我关注的贴吧列表，遍历获取链接，进行签到。
    :return:
    """
    favorite = session.get(tiebaUrl+"/m?tn=bdFBW&tab=favorite")
    soup = BeautifulSoup(favorite.content)
    tieba_list = soup.find_all(name="tr")
    for tieba in tieba_list:
        sign_in(tiebaUrl+"/"+tieba.td.a["href"])
    print u"签到完成！"


def sign_in(url):
    page = session.get(url)
    soup = BeautifulSoup(page.content)
    sign_in_div = soup.find(name="td", attrs={"style": "text-align:right;"})
    if sign_in_div.a and sign_in_div.a.get("href"):
        sign_in_url = sign_in_div.a["href"]
        session.get("http://tieba.baidu.com"+sign_in_url)
        print "[ok]:%s" % "http://tieba.baidu.com"+sign_in_url


if __name__ == '__main__':
    if login():
        #登录成功
        if sys.argv[1] == '-s':     #当运行参数sys.argv[1]为"-s"时，进行签到
            sign_in_all()
        print_delimiter()
        while True:
            try:
                washer()
            except Exception as e:
                print "[%s]wash Error!" % time.asctime()
                print str(e)
            print_delimiter()
            time.sleep(random.randint(timeInterval, timeInterval+10))
