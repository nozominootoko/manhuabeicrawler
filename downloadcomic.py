# -*- coding: utf-8 -*-
import requests as rq
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# 引入模块
import os
import threadpool as tp
import threading as td
import time


class DownComic:
    driver = None
    website = 'https://www.manhuabei.com/'
    sleeptime = 0.1
    timeout = 6
    comicroot = ''
    logfile = None
    alreadydw = []
    pool = None
    pool_size = 2
    lck = td.Lock()
    drivers = []
    driver_pool = None
    huapool = None
    isMultiDownHua = False

    def getdriver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        self.drivers.append(driver)
        return driver

    def gettemdriver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        self.drivers.append(driver)
        return driver

    def init(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.pool = tp.ThreadPool(self.pool_size)
        self.drivers.append(self.driver)
        self.huapool = tp.ThreadPool(self.pool_size)
        print("Start Downloading")

    def end(self):
        try:
            for drv in dc.drivers:
                drv.close()
                drv.quit()
        except Exception as e:
            print(e)
        print("下载结束")

    def down_comics_pool(self, comicurl, position=""):
        html = rq.get(comicurl).text
        parser = etree.HTMLParser()
        tree = etree.fromstring(html, parser)
        tree_elements = tree.xpath('/html/body/div[3]/div[1]//*[@class="zj_list_con autoHeight"]')
        for i in tree_elements:
            tree_element = i.xpath('.//a')
            parent_element = i.xpath('./..//em')
            parent_name = parent_element[0].text + 'ttyy/'
            comicname = i.xpath('/html/body/div[3]/div[1]/div[1]/div[2]/h1')[0].text
            self.comicroot = position + comicname + '/'
            self.mkdir(self.comicroot)
            self.logfile = open(self.comicroot + '/log', 'a+')
            self.logfile.seek(0, 0)
            items = self.logfile.readlines()
            ldict = {}
            is_can = os.path.exists(self.comicroot + '/log') and os.path.getsize(self.comicroot + '/log') > 0
            if len(items) > 0:
                for item in items:
                    itemsl = item.split(" ")
                    palready_page = int(itemsl[1].split("/")[0])
                    if int(ldict[itemsl[0]].split("/")[0]) < palready_page:
                        ldict[itemsl[0]] = itemsl[1]
            if len(tree_elements) == 1:
                parent_name = ''
            for j in tree_element:
                huaurl = self.website + j.get('href')
                name = j.get('title')
                director = self.comicroot + parent_name + name
                already_download_page = 1
                try:
                    if is_can:
                        already_page = int(ldict[director].split("/")[0])
                        max_download_page = int(ldict[director].split("/")[1])
                        if director in ldict.keys() and (already_page == max_download_page):
                            print('存在下载' + director)
                            continue
                        if director in ldict.keys() and (already_page < max_download_page):
                            already_download_page = already_page + 1
                except Exception as e:
                    print(e)
                argument = [huaurl, director, already_download_page]
                if not self.isMultiDownHua:
                    requests = tp.makeRequests(self.downhua_pool, [(argument, None)])
                else:
                    requests = tp.makeRequests(self.downhua_pool, [(argument.append(False), None)])
                [self.pool.putRequest(req) for req in requests]
                # self.downhua(huaurl, director, already_download_page)
        self.pool.wait()
        self.logfile.close()

    def down_comics(self, comicurl, position=""):
        html = rq.get(comicurl).text
        parser = etree.HTMLParser()
        tree = etree.fromstring(html, parser)
        tree_elements = tree.xpath('/html/body/div[3]/div[1]//*[@class="zj_list_con autoHeight"]')

        for i in tree_elements:
            tree_element = i.xpath('.//a')
            parent_element = i.xpath('./..//em')
            parent_name = parent_element[0].text + 'ttyy/'
            comicname = i.xpath('/html/body/div[3]/div[1]/div[1]/div[2]/h1')[0].text
            self.comicroot = position + comicname + '/'
            self.mkdir(self.comicroot)
            self.logfile = open(self.comicroot + '/log', 'a+')
            self.logfile.seek(0, 0)
            items = self.logfile.readlines()
            ldict = {}
            is_can = os.path.exists(self.comicroot + '/log') and os.path.getsize(self.comicroot + '/log') > 0
            if len(items) > 0:
                for item in items:
                    itemsl = item.split(" ")
                    new_page = int(itemsl[1].split("/")[0])
                    if len(ldict) == 0 or itemsl[0] not in ldict:
                        ldict[itemsl[0]] = itemsl[1]
                    else:
                        if int(ldict[itemsl[0]].split("/")[0]) < new_page:
                            ldict[itemsl[0]] = itemsl[1]
            if len(tree_elements) == 1:
                parent_name = ''
            for j in tree_element:
                huaurl = self.website + j.get('href')
                name = j.get('title')
                director = self.comicroot + parent_name + name
                already_download_page = 1
                try:
                    if is_can:
                        already_page = int(ldict[director].split("/")[0])
                        max_download_page = int(ldict[director].split("/")[1])
                        if director in ldict.keys() and (already_page == max_download_page):
                            print('存在下载' + director)
                            continue
                        if director in ldict.keys() and (already_page < max_download_page):
                            already_download_page = already_page + 1
                except Exception as e:
                    print(e)
                if not self.isMultiDownHua:
                    self.downhua(huaurl, director, already_download_page)
                else:
                    self.muitidown_hua(huaurl, director, already_download_page)
        self.logfile.close()

    def downhua_pool(self, huaurl, position, lastpage=1, usesingletidown=True):
        try:
            driver = self.gettemdriver()
            driver.get(huaurl)
            # 本话的页数
            counte = driver.find_element_by_xpath('/html/body/div[2]/div[4]/div/p').text
            nmb = self.getallpage(counte)
            if nmb == lastpage:
                return
            for i in range(lastpage, nmb + 1):
                picpage = huaurl + '?p=' + str(i)
                # ------------------------------------------多线程下载漫画
                if usesingletidown:
                    picurl = self.findpicurl_pool(picpage)
                    self.downonepage(picurl, i, position, nmb)
                else:
                    argument = [picpage, i, position, nmb]
                    requests = tp.makeRequests(self.findpicurl_and_ownonepage, [(argument, None)])
                    [self.huapool.putRequest(req) for req in requests]
                # time.sleep(self.sleeptime)
            self.huapool.wait()
            driver.close()
            driver.quit()
            print('完成下载：' + position)
        except Exception as e:
            print(e)

    def muitidown_hua(self, huaurl, position, lastpage=1):
        suffix = '?p='
        driver = self.gettemdriver()
        driver.get(huaurl)
        # 本话的页数
        counte = driver.find_element_by_xpath('/html/body/div[2]/div[4]/div/p').text
        nmb = self.getallpage(counte)
        if nmb == lastpage:
            return
        for i in range(lastpage, nmb + 1):
            try:
                picpage = huaurl + '?p=' + str(i)
                # ------------------------------------------多线程下载漫画
                argument = [picpage, i, position, nmb]
                requests = tp.makeRequests(self.findpicurl_and_ownonepage, [(argument, None)])
                [self.huapool.putRequest(req) for req in requests]
                # time.sleep(self.sleeptime)
            except Exception as e:
                pass
        driver.close()
        driver.quit()
        self.huapool.wait()
        print('完成下载：' + position)

    def findpicurl_and_ownonepage(self, picpage, i, position, nmb):
        driver = self.gettemdriver()
        driver.get(picpage)
        element = driver.find_element_by_xpath('//*[@id="images"]/img')
        picurl = element.get_property('src')
        self.downonepage(picurl, i, position, nmb)
        driver.close()
        driver.quit()

    def downhua(self, huaurl, position, lastpage=1):
        suffix = '?p='
        self.driver.get(huaurl)
        # 本话的页数
        counte = self.driver.find_element_by_xpath('/html/body/div[2]/div[4]/div/p').text
        nmb = self.getallpage(counte)
        if nmb == lastpage:
            return
        self.mkdir(position)
        for i in range(lastpage, nmb + 1):
            try:
                picpage = huaurl + '?p=' + str(i)
                picurl = self.findpicurl(picpage)
                # 下载漫画
                self.downonepage(picurl, i, position, nmb)
                # time.sleep(self.sleeptime)
            except Exception as e:
                print(e)
        print('完成下载：' + position)

    def downonepage(self, picurl, number=1, director='', maxium=0):
        try:
            self.mkdir(director)
            filename = director + '/' + "0" + str(number) + '.jpg'
            if os.path.exists(filename):
                print('存在文件' + filename)
                return
            request = rq.get(picurl, timeout=self.timeout)
            with open(filename, 'wb+') as pf:
                pf.write(request.content)
            self.lck.acquire(True)
            self.logfile.write(director + ' ' + str(number) + '/' + str(maxium) + '\n')
            self.logfile.flush()
            self.lck.release()
            print('完成下载：' + filename)
        except rq.exceptions.RequestException as e:
            with open(director + 'error.txt', 'a+') as pf:
                pf.write(filename + '  ')
                pf.write(picurl)

    def findpicurl(self, weburl):
        picurl = 'default'
        self.driver.get(weburl)
        element = self.driver.find_element_by_xpath('//*[@id="images"]/img')
        picurl = element.get_property('src')
        return picurl

    def findpicurl_pool(self, weburl):
        picurl = 'default'
        driver = self.gettemdriver()
        driver.get(weburl)
        element = driver.find_element_by_xpath('//*[@id="images"]/img')
        picurl = element.get_property('src')
        driver.quit()
        return picurl

    def getallpage(self, lstr):
        strs = lstr.split("/")
        nmb = int(strs[1].strip(')'))
        return nmb

    def mkdir(self, path):
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
    dc = DownComic()
    try:

        dc.init()
        aweburl = 'https://www.manhuabei.com/manhua/huiyedaxiaojiexiangrangwogaobai/'
        dc.isMultiDownHua = True
        dc.down_comics(aweburl)

    except Exception as e:
        print(e)
    finally:
        dc.end()
