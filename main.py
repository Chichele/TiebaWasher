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
import simsimi
import threading


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
        session.get(baiduUrl)       # 打开一次百度首页，获取相关cookies
        page = session.post(loginUrl, data=loginData, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'})
    except:
        print "Login Error"
        return False

    if not login_check(page.content):
        print 'Login failed'
        return False
    else:
        print 'Login successful!'
        return True


def talk(content, callback):
    global sim
    while 1:
        if sim.ready:
            sim.talk(content, callback)
            break
        else:
            time.sleep(1)


def get_simsimi_response(response):
    """
    构造回复帖子时用到的postData
    :param response: 机器人返回的回答内容
    :return:
    """
    global sim
    sim.http.stop()
    response += u"""
                                                          大声告诉我！这是不是二楼！
    """
    global subject_soup
    data = {'sub1': u'回帖', 'co': response}
    #找出div标签，class为d h的部分，这些都是回帖表单需要的元素
    subjects = subject_soup.find_all(name="div", attrs={"class": "d h"})
    hidden_elems = subjects[0].find_all(name="input", attrs={"type": "hidden"})
    for elem in hidden_elems:
        data[elem['name']] = elem['value']
    reply_request = session.post(tiebaUrl+"/submit", data=data)
    #print reply_request.content
    subject_main_content = subject_soup.find(name="div", attrs={"class": "bc p"}).strong.text
    if reply_request.status_code == 200:
        print "[%s]Reply successful!: name：%s" % (time.asctime(), subject_main_content.encode("utf8"))
    else:
        print "[%s]Reply failed!: name：%s" % (time.asctime(), subject_main_content.encode("utf8"))
                    

def open_subject(subject_url):
    sub_page = session.get(subject_url)    
    global subject_soup
    subject_soup = BeautifulSoup(sub_page.content)
    subject_main_content = subject_soup.find(name="div", attrs={"class": "bc p"}).strong.text
    subject_main_content += subject_soup.find(name="div", attrs={"class": "i"}).text
    talk(subject_main_content, get_simsimi_response)


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
        if sub.p.find(text=re.compile(u"回0")):      # 如果找到回复数为0的帖子
            print "[%s]open subject:%s" % (time.asctime(), tiebaUrl+"/"+sub.a['href'])
            _link = tiebaUrl+"/"+sub.a['href']
            global sim
            sim = simsimi.SimSimiTalk()
            t = threading.Thread(target=open_subject, args=(_link,))
            t.setDaemon(True)
            t.start()
            sim.http.start()


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
    if sign_in_div and sign_in_div.a and sign_in_div.a.get("href"):
        sign_in_url = sign_in_div.a["href"]
        session.get("http://tieba.baidu.com"+sign_in_url)
        print "[ok]:%s" % "http://tieba.baidu.com"+sign_in_url


if __name__ == '__main__':
    if login():
        #登录成功
        if len(sys.argv) >=2 and sys.argv[1] == '-s':     #当运行参数sys.argv[1]为"-s"时，进行签到
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

