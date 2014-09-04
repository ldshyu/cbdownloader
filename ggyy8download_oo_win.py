#!/usr/bin/env python3
# vim: set fileencoding=utf-8
"""
    This script is for fetching comic from www.ggyy8.cc.
    Just change book_url and that's it.
"""
from urllib.request import urlopen
import urllib.request as u
import re
from comic_base_oo_win import comic_base, chapter_base
class comic_books(comic_base):
    def get_chlist(self):
        website_base = 'http://www.ggyy8.cc'
        url = urlopen(self.book_url)
        source = url.read().decode('utf-8')
        comic_start = source.find('章节列表开始')
        comic_end = source.find('章节列表结束')
        parse = re.split('<li>', source[comic_start:comic_end]) #split lines and throw away html codes that are not needed
        for content in parse:
            href = content.find('href')
            title = content.find('title')
            if href != -1 and title != -1:
                exec('self.' + content[href:title]) #href=""
                rbracket = content.find('>')
                title = content[title:rbracket]
                title = title[:6] + "'" + title[7:-1] + "'" 
                exec('self.' + title) #title=""
                href = website_base + self.href
                self.chapter_list.append(chapters(href, self.title))
        super(comic_books, self).get_chlist()

class chapters(chapter_base):
    def get_imagelist(self):
        server = 'http://img.ggyy8.cc'
        url = urlopen(self.ch_url)
        source = url.read().decode('utf-8')
        parse = re.split('<', source)
        get_links = [href for href in parse if 'var __arr' in href ]
        start = get_links[0].find('__arr')
        end = get_links[0].find(']')
        #The '+2' below is due to that we cannot use __arr in side class, otherwise it will prepend class name to _chapters__arr because of attribute hiding
        exec('self.' + get_links[0][start+2:end + 1]) 
        img_list = self.arr 
        start2 = get_links[0].find('__p')
        url_base = get_links[0][start2:]
        end = url_base.find(';')
        exec('self.' + url_base[2:end]) #__p=[]
        url_base = self.p
        for img in img_list:
            if 'http://' in img:
                self.jpg_list.append(img)
            else:
                url = u.quote(url_base + img, encoding='utf-8')
                img_path = server + url
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

if __name__ == '__main__':
    book_url = 'http://www.ggyy8.cc/html/info84727.html'
    book_name = '魔王的父親'
    cb = comic_books(book_url, book_name)
    cb.download_chapters(176,176)
    cb.endbook()

