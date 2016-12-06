# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import json
import os
import time
import socket
import sys
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as Queue
else:
    import queue as Queue
from threading import Thread,Lock
from bs4 import BeautifulSoup
from p2t import p2t
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

lock = Lock()

class infoCrawl(Thread):
    post_url=""
    header ={}
    stockInfo=[]
    stockFolder=""
    fileList={}
    
    
    def __init__(self,tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.post_url = 'http://www.cninfo.com.cn/information/companyinfo_n.html?fulltext?szmb'
        self.header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
             'Origin':'http://www.cninfo.com.cn'}
        stockFolder = os.getcwd()
        self.p2tMac = p2t()
        info = file('stock.txt','r')
        self.stockInfo = dict()
        for line in info:
            line = line.strip().split(':')
            self.stockInfo[line[0]] = line[1]
        info.close()

        self.start()


    def downloadFile(self,stockId,announcementId,date):
        part_url = '%s?announceTime=%s' % (announcementId,date)
        file_name = self.stockInfo[stockId].decode('gbk')+'_'+stockId+'_'+ date + ".pdf"
        self.fileList[stockId] = file_name
        download_url =  download_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/sse/download/'+part_url
        try:
            datas=urllib2.urlopen(download_url,timeout = 50)
            f = open(file_name,'wb')
            block_sz = 8192
            while True:
                buffer = datas.read(block_sz)
                if not buffer:
                    break;
                f.write(buffer)
            f.close()
        except Exception as e:
            print e

    def getPages(self,infile):
        outfile = infile.replace('pdf','txt')
        print outfile
        removeNoneLine = re.compile(r'\n[\s|]*\n')
        debug = 0
        pagenos = set()
        password = ''
        maxpages = 0
        rotation = 0
        codec = 'utf-8'   #输出编码
        caching = True
        imagewriter = None
        laparams = LAParams()
        #
        PDFResourceManager.debug = debug
        PDFPageInterpreter.debug = debug

        rsrcmgr = PDFResourceManager(caching=caching)
        outfp = file(outfile,'w')#pdf转换
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                imagewriter=imagewriter)
        
        fp = file(infile,'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)#处理文档对象中每一页的内容
        for page in PDFPage.get_pages(fp, pagenos,
                     maxpages=maxpages, password=password,
                     caching=caching, check_extractable=True) :
            #page.rotate = (page.rotate+rotation) % 360
            interpreter.process_page(page)
        fp.close()
        device.close()
        outfp.close()
        return

    def transfer(self):
        key = self.fileList.keys()
        key.sort()
        for index in key:
           self.getPages(self.fileList[index])
            
            
    def run(self):
        try:
            stockId = self.tasks.get()
            dest_url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
            post_data={
                'stock':stockId,
                'category':'category_ndbg_szsh',
                'pageNum':'1',
                'pageSize':'15',
                'column':'sse',
                'tabName':'fulltext'
                }
            post_data_url = urllib.urlencode(post_data)
            request = urllib2.Request(dest_url,headers=self.header,data=post_data_url)
            response = urllib2.urlopen(request,timeout=30)
            pageCode = response.read().decode('utf-8')
        except Exception as e:
            print e
            return 

        data = json.loads(pageCode)
        for item in data['announcements']:
            if item[u'announcementTitle'].find(u'摘要') == -1 and item[u'announcementTitle'].find(u'已取消') == -1 and item[u'announcementTitle'].find(u'英文') == -1 and item[u'adjunctUrl'].find('2016') >0:
                #print os.getcwd()
               # os.mkdir(self.stockFolder+"\\stockPdf"+"\\60001")
                self.downloadFile(stockId,item[u'announcementId'],item['adjunctUrl'].split('/')[1])

        self.transfer()
                


class ThreadPool:
    def __init__(self,num_threads):
        self.tasks = Queue.Queue()
        for _ in range(num_threads):
            infoCrawl(self.tasks)

    def add_task(self):
        #self.tasks.put('600111')
        #self.tasks.put('000001')
        #self.tasks.put('000002')
        self.tasks.put('000004')

    def wait_completion(self):
        self.tasks.join()

    

if __name__ == '__main__':
    pool = ThreadPool(4)
    pool.add_task()
    pool.wait_completion()
    

    

        

    

