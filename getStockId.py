import urllib
import urllib2
import re
import csv

post_url = 'http://www.txsec.com/inc1/gpdm.asp'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
             'Origin':'http://www.cninfo.com.cn'}
try:
    request = urllib2.Request(post_url,headers=header)
    response = urllib2.urlopen(request)
    pageCode = response.read().decode('gbk')
except Exception as e:
    print e

pattern = re.compile('<tr .*?>.*?<td .*?>(.*?)</td>.*?<td .*?>(.*?)</td>.*?'+
                     '<td .*?>(.*?)</td>.*?<td .*?>(.*?)</td>.*?</tr>.*?'+'<tr>.*?<td .*?>(.*?)</td>.*?<td .*?>(.*?)</td>.*?'+
                     '<td .*?>(.*?)</td>.*?<td .*?>(.*?)</td>.*?</tr>',re.S)
#removeNoneLine = re.compile(r'\n[\s|]*\n')
items = re.findall(pattern,pageCode)
#stockFile = file('stock.csv','w')
#write = csv.writer(stockFile)
stockFile = file('stock.txt','w')
stockDict = {}
for item in items:
    #content = [
       # (item[0]+':',item[1].encode('gbk')),
       # (item[2]+':',item[3].encode('gbk'))
      #  ]
    #content = re.sub(removeNoneLine,"\n",content)
    #write.writerows(content)
    stockDict[item[0].strip()]=item[1].strip()
    stockDict[item[2].strip()]=item[3].strip()
    stockDict[item[4].strip()]=item[5].strip()
    stockDict[item[6].strip()]=item[7].strip()

keys=stockDict.keys()
keys.sort()
for item in keys:
    content = item+':'+stockDict[item]+'\n'
    stockFile.write(content.encode('gbk'))
stockFile.close()
        
    
    
    
