# -*- coding: utf-8 -*-
import requests as rq
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# 引入模块
import os
import time
driver =None
website = 'https://www.manhuabei.com/'
sleeptime = 1
timeout = 6

def init():
    global driver
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    print("Start Downloading")


def end():
    global driver
    try:
        driver.quit()
    except Exception as e :
        print(e)
    print("下载结束")


def down_comics(comicurl,position=""):
    html = rq.get(comicurl).text
    parser = etree.HTMLParser()
    tree = etree.fromstring(html, parser)
    tree_elements = tree.xpath('/html/body/div[3]/div[1]//*[@class="zj_list_con autoHeight"]')
    for i in tree_elements:
        tree_element = i.xpath('.//a')
        parent_element = i.xpath('./..//em')
        parent_name = parent_element[0].text + '/'
        comicname=i.xpath('/html/body/div[3]/div[1]/div[1]/div[2]/h1')[0].text
        if (len(tree_elements) == 1):
            parent_name = ''
        for j in tree_element:
            huaurl = website + j.get('href')
            #漫画名字
            name = j.get('title')
            with open('log','a+') as lg:
                lg.write
            downhua(huaurl, position+comicname+'/'+parent_name + name)
            print('已下载：' + parent_name + name)

def downhua(huaurl,position):
    suffix = '?p='
    driver.get(huaurl)
    # 本话的页数
    counte = driver.find_element_by_xpath('/html/body/div[2]/div[4]/div/p').text
    nmb = getallpage(counte)
    for i in range(1, nmb + 1):
        try:
            picpage = huaurl + '?p=' + str(i)
            picurl = findpicurl(picpage)
            # 下载漫画
            downonepage(picurl,i, position)
            print('正在下载第 ', i, ' 页')
            # 等待数秒
            time.sleep(sleeptime)
        except Exception:
            pass


def downonepage(picurl, number=1, director=''):
    try:
        mkdir(director)
        filename = director + '/' + "0" + str(number) + '.jpg'
        if os.path.exists(filename):
            print('存在文件'+filename)
            return
        request = rq.get(picurl, timeout=timeout)
        print('已下载：'+filename)
        with open(filename, 'wb+') as pf:
            pf.write(request.content)
    except rq.exceptions.RequestException as e:
        with open(director + 'error.txt', 'a+') as pf:
            pf.write(filename + '  ')
            pf.write(picurl)

def findpicurl(weburl):
    picurl = 'default'
    driver.get(weburl)
    element = driver.find_element_by_xpath('//*[@id="images"]/img')
    picurl = element.get_property('src')
    return picurl


def getallpage(lstr):
    strs = lstr.split("/")
    nmb = int(strs[1].strip(')'))
    return nmb


def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 判断路径是否存在
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False



if __name__ == '__main__':
    try:
        init()
        aweburl = 'https://www.manhuabei.com/manhua/huiyedaxiaojiexiangrangwogaobai/'
        down_comics(aweburl)
    except Exception as e:
        print(e)
        end()