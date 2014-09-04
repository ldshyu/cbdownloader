#!/usr/bin/env python
# vim: set fileencoding=utf-8
"""
    This script is for fetching comic from www.ggyy8.cc.
    Just change book_url and that's it.
"""
from urllib import urlopen, quote
import re
import os
import sys
from comic_base_oo import comic_base, chapter_base
class comic_books(comic_base):
    def get_chlist(self):
        super(comic_books, self).get_chlist()
        website_base = 'http://www.ggyy8.cc'
        url = urlopen(self.book_url)
        if sys.platform == 'win32':
            source = url.read().decode('utf-8')
        else:
            source = url.read()
        if sys.platform == 'win32':
            start_tag = '章节列表开始'.decode('utf-8')
            end_tag = '章节列表结束'.decode('utf-8')
        else:
            start_tag = '章节列表开始'
            end_tag = '章节列表结束'
        comic_start = source.find(start_tag)
        comic_end = source.find(end_tag)
        parse = re.split('<li>', source[comic_start:comic_end]) #split lines and throw away html codes that are not needed
        for content in parse:
            href = content.find('href')
            title = content.find('title')
            if href != -1 and title != -1:
                if sys.platform == 'win32':
                    exec('self.' + content[href:title]) #href=""
                else:
                    exec(content[href:title]) #href=""
                rbracket = content.find('>')
                title = content[title:rbracket]
                title = title[:6] + "'" + title[7:-1] + "'" 
                if sys.platform == 'win32':
                    exec('self.' + title) #title=""
                else:
                    exec(title) #title=""
                if sys.platform == 'win32':
                    href = website_base + self.href
                    self.chapter_list.append(chapters(href, self.title))
                else:
                    href = website_base + href
                    self.chapter_list.append(chapters(href, title))

class chapters(chapter_base):
    def get_imagelist(self):
        super(chapters, self).get_imagelist()
        server = 'http://img.ggyy8.cc'
        url = urlopen(self.ch_url)
        if sys.platform == 'win32':
            source = url.read().decode('utf-8')
        else:
            source = url.read()
        parse = re.split('<', source)
        get_links = [href for href in parse if 'var __arr' in href ]
        if get_links == []:
            return
        start = get_links[0].find('__arr')
        end = get_links[0].find(']')
        #The '+2' below is due to that we cannot use __arr inside class, otherwise it will prepend class name to _chapters__arr because of attribute hiding
        if sys.platform == 'win32':
            exec('self.' + get_links[0][start+2:end + 1]) 
            img_list = self.arr 
        else:
            exec(get_links[0][start+2:end + 1]) 
            img_list = arr 
        start2 = get_links[0].find('__p')
        url_base = get_links[0][start2:]
        end = url_base.find(';')
        if sys.platform == 'win32':
            exec('self.' + url_base[2:end]) #__p=[]
            url_base = self.p
        else:
            exec(url_base[2:end]) #__p=[]
            url_base = p
        for img in img_list:
            if 'http://' in img:
                self.jpg_list.append(img)
            else:
                if sys.platform == 'win32':
                    url = quote(url_base + img)#, encoding='utf-8')
                    img_path = server + url
                else:
                    img_path = server + url_base + img
                self.jpg_list.append(img_path)
        if self.name == None:
            ident = 'read_title_top';
            for line in parse:
                id_start = line.find(ident)
                if id_start != -1:
                    id_start = id_start + len(ident) + 2
                    self.name = line[id_start:]
    def download_img(self, referer):
        return super(chapters, self).download_img('--referer="www.ggyy8.cc"')
    def create_zip(self):
        self.file_rename()
        return super(chapters, self).create_zip()
    def file_rename(self):
        ls = os.listdir('./')
        for files in ls:
            a=files.find('_')
            b=files.find('.')
            if a != -1 and b != -1:
                os.rename(files, files[:a]+files[b:])

if __name__ == '__main__':
    book_url = 'http://www.ggyy8.cc/html/info84856.html'
    book_name = '四葉妹妹'
    cb = comic_books(book_url, book_name)
    cb.download_chapters(all=True)
    cb.endbook()
