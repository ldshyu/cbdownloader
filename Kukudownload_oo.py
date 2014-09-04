#!/usr/bin/env python
# vim: set fileencoding=utf-8
"""
   This script is for fetching comic from comic.kukudm.com.
     Change url and that's all you need to do.
"""
from urllib import urlopen
import re
from subprocess import call
from comic_base_oo import comic_base, chapter_base

class comic_books(comic_base):
    def get_chlist(self):
        super(comic_books, self).get_chlist()
        base_url = 'http://comic.kukudm.com'
        url = urlopen(self.book_url)
        index_file = url.read()
        parse = re.split('</[A,a]>', index_file)
        get_links = [href for href in parse if 'href=\'/comiclist/' in href ]
        parsing_target = "href='"
        for K in get_links:
            top = K.find('\xb5\xda') #第
            bottom = K.find('\xbb\xb0') #話
            book_num = K.lower().find('vol_')
            ch = None
            #Does not have 第
            if top == -1 and bottom != -1:
                top = bottom - 1
                while True:
                    top -= 1
                    if not K[top:bottom].isdigit():
                        top += 1
                        break
                ch = 'ch%d' % int(K[top:bottom])
            # have both 第 and 話
        elif top != -1 and bottom != -1:
            top += 2
                ch = 'ch%d' % int(K[top:bottom])
            # have Vol_
        elif book_num != -1:
            book_num += 4
                ch = 'bk%d' % int(K[book_num:])
            addr_top = K.lower().find(parsing_target)
            addr_bottom = K.lower().find('1.htm')
            addr = K[addr_top + len(parsing_target):addr_bottom]
            if ch:
                addr = base_url + addr
                self.chapter_list.append(chapters(addr, ch))

class chapters(chapter_base):
    def get_imagelist(self):
        server = 'http://cc.kukudm.com/'
    #TODO: Assuming jpg/JPG only
        file_format = '.jpg'
        page = 1
        while True:
            in_book_addr = '%s%d.htm' % (self.ch_url, page)
            url2 = urlopen(in_book_addr)
            index_file2 = url2.read()
            parse2 = index_file2.split('>')
            for img in parse2:
                if 'kuku' in img and 'comic' in img:
                    img_path = img
                    break
            else:
                img_path = None
                print('cannot find img path\n')
            if img_path:
                # The image may store in arbitrary server
                server_re = re.compile('kuku[0-9]*comic[0-9]*')
                server_name = re.search(server_re, img_path).group(0)
                top = img_path.lower().find(server_name)
                bottom = img_path.lower().find(file_format)
                img = img_path[top:bottom + len(file_format)]
                img = server + img
                self.jpg_list.append(img)
                page += 1
            else:
                break
    def download_img(self, referer):
        total = len(self.jpg_list)
        got = 0
        for page in range(self.jpg_list):
            if not call(('wget', self.jpg_list[page], '-O', '%03d.jpg' % page, '--referer=comic.kukudm.com', '-a', 'wget.log')):
                got += 1
            time.sleep(1) #防盜鍵
        return True if float(got)/float(total) > 0.8 else False

if __name__ == '__main__':
    book_url = 'http://comic.kukudm.com/comiclist/1301/index.htm'
    book_name = 'JudgementOverman'
    cb = comic_books(book_url, book_name)
    cb.download_chapters(all=True)
    cb.endbook()

