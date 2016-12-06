import sys
import os
import re
from binascii import b2a_hex
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines



class p2t():

    def __init__(self):
        return
    
    def with_pdf(self,pdf_doc, fn, pdf_pwd, *args):
        result = ""
        try:
            fp = open(pdf_doc,'rb')
            parser = PDFParser(fp)
            doc = PDFDocument(parser,pdf_pwd)
            parser.set_document(doc)
            if doc.is_extractable:
                result = fn(doc,*args)

            fp.close()
        except:
            pass
        return result

    def _parse_toc(self,doc):
        toc=[]
        try:
            outlines = doc.get_outlines()
            for (level,title,dest,a,se) in outlines:
                toc.append((level,title))
        except:
            pass
        return toc

    def get_toc(self,pdf_doc,pdf_pwd=''):
        return self.with_pdf(pdf_doc,self._parse_toc,pdf_pwd)


    def write_file(self,folder,filename,filedata,flags='w'):
        result =false;
        if os.path.isdir(folder):
            try:
                file_obj = open(os.path.join(folder,filename),flags)
                file_obj.write(filedata)
                file_obj.close()
                result = True
            except IOErro:
                pass
        return result

    def determine_image_type(self,stream_first_4_bytes):
        file_type = None
        bytes_as_hex = b2a_hex(stream_first_4_bytes)
        if bytes_as_hex.startswith('ffd8'):
            file_type = '.jpeg'
        elif bytes_as_hex == '89504e47':
            file_type = ',png'
        elif bytes_as_hex == '47494638':
            file_type = '.gif'
        elif bytes_as_hex.startswith('424d'):
            file_type = '.bmp'
        return file_type

    def save_image(self,it_image,page_number,images_folder):
        result = None
        if it_image.stream:
            file_stream = it_image.stream.get_rawdata()
            if file_stream:
                 file_ext = self.determine_image_type(file_stream[0:4])
                 print file_ext
                 if file_ext:
                     file_name = ''.join([str(page_number),'_',it_image.name,file_ext])
                     if self.write_file(images_folder,file_name,file_stream,flags='wb'):
                         result = file_name
        return result

    def to_bytestring(self,s,enc='utf-8'):
        if s:
            if isinstance(s,str):
                 return s
            else:
                 return s.encode(enc)

    def update_page_text_hash(self,h,lt_obj,pct=0.1):
        x0 = lt_obj.bbox[0]
        x1 = lt_obj.bbox[2]
        key_found = False
        for k,v in h.items():
            hash_x0 = k[0]
            if x0 >= (hash_x0*(1.0-pct)) and (hash_x0 * (1+pct)) >= x0:
                hash_x1 = k[1]
                if x1 >= (hash_x1*(1-pct)) and (hash_x1*(1+pct)) >= x1:
                    key_found = True
                    v.append(self.to_bytestring(lt_obj.get_text()))
                    h[k] = v
        if not key_found:
            h[(x0,x1)] = [self.to_bytestring(lt_obj.get_text())]
        return h

    def parse_lt_objs(self,lt_objs,page_number,images_folder,text=[]):
        text_content = []
        page_text = {}
        result = ""
        for lt_obj in lt_objs:
            if isinstance(lt_obj,LTTextBox) or isinstance(lt_obj,LTTextLine):
                page_text = self.update_page_text_hash(page_text,lt_obj)              
           # elif isinstance(lt_obj,LTImage):
             #   saved_file = self.save_image(lt_obj,page_number,images_folder)
             #   if saved_file:
             #       text_content.append('<img src="' + os.path.join(images_folder,saved_file)+'"/>')
             #   else:
             #       print >> sys.stderr,"error saving image on page", page_number,lt_obj.__repr__     
            elif isinstance(lt_obj,LTFigure):
                text_content.append(self.parse_lt_objs(lt_obj,page_number,images_folder,
                                                  text_content))

           
        for k,v in sorted([(key,value) for (key,value) in page_text.items()]):
            text_content.append(''.join(v))
        return result.join(text_content)

    def _parse_pages(self,doc,images_folder):
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr,laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr,device)
       
        text_content = []
        for i,page in enumerate(PDFPage.create_pages(doc)):
            interpreter.process_page(page)
            layout = device.get_result()
            text_content.append(self.parse_lt_objs(layout,(i+1),images_folder))
        return text_content

    def get_pages(self,pdf_doc,pdf_pwd='',images_folder='/tmp'):
        return self.with_pdf(pdf_doc,self._parse_pages,pdf_pwd,*tuple([images_folder]))

tmp = p2t()
#os.chdir('C:\Users\liwei\Desktop\python\scrapy\programs\自动下载数据')
a = open('result.txt','a')
removeNoneLine = re.compile(r'\n[\s|]*\n')
for i in tmp.get_pages('000004_2016-04-30.pdf'):
    i= re.sub(removeNoneLine,"\n",i)
    a.write(i)
a.close()

        
