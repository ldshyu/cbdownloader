#!/usr/bin/python
# vim: set fileencoding=utf-8
from os import mkdir, chdir
import os
import errno
from subprocess import call
import time
import zipfile
import sys
import shutil

num = {u'零': 0, u'一': 1, u'二': 2, u'三':3, u'四': 4, u'五':5, u'六':6, u'七':7, u'八':8, u'九': 9, u'十':10, u'百':100, u'千':1000, u'萬':10000, u'點': 0.1}

translation = {u'话':u'話',  u'点':u'點'}

output_quiet = False
use_internal_zip = False
use_internal_download = False

def PRINT(args): 
    if not output_quiet: 
        print args

def zip_folder(foldername, filename):
    PRINT('zipping files...')
    z = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    for root,dirs,files in os.walk(foldername):
        #files of cur file
        for filename in files:
            z.write(os.path.join(root,filename), filename)
        # empty dir 
        if not len(files):
            zif=zipfile.ZipInfo((root+'/'))
            z.writestr(zif,"")
    z.close()

def num_produce(b):
    base = b
    def num_gen(value):
        return value * base
    return num_gen

def process_sub(s, base, fn):
    if not s and base != 1:
        number = fn(1) # hidden "一"
    else:
        # Recursive
        number = fn(chinese2arabic(s))
    return number

def chinese2arabic(s):
    u = s
    len_u = len(u)
    if len_u == 0: #base case: empty string
        return 0
    elif len_u == 1: #base case: length of 1
        return num[s]
    number = 0
    base = 1
    previous_base_fn = num_produce(base)
    substr_start = len_u
    dot = len_u 
    # find decimal position
    for i in range(len_u):
        j = u[i]
        if num[j] == 0.1:
            dot = i

    substr_end = dot
    # transform Chinese decimal to Arabic decimal number
    for i in range(dot + 1, len_u):
        j = u[i]
        k = (i - dot)
        if num[j] >= 10:
            raise ValueError
        elif num[j] > 0:
            number += num[j] * 0.1 ** k
    # Going from lower position to higher position
    for i in range(dot - 1, -1, -1):
        j = u[i]
        # A new base found.  
        if num[j] >= 10 and num[j] > base:
            substr = u[substr_start:substr_end]
            # Recursively parsing substrings
            number += process_sub(substr, base, previous_base_fn)
            base = num[j]
            previous_base_fn = num_produce(base)
            substr_end = i
        elif num[j] > 0:
            substr_start = i
    # Pick up left over 
    substr = u[substr_start:substr_end]
    number += process_sub(substr, base, previous_base_fn)
    return number

def str_parsing(s):
    u = s
    while True:
        for i in range(len(u)):
            # find consecutive Chinese numbers
            if u[i] in num.keys():
                j = i + 1
                while j < len(u) and u[j] in num.keys():
                    j += 1
                u_number = u[i:j]
                number = '%s' % chinese2arabic(u_number)
                u = u.replace(u_number, number)
                break
        else:
            # no more Chinese numbers
            return u

def chr_conversion(func):
    def conversion(*args):
        name = args[-1]
        # Do simplified to traditional characters conversion
        name = name.decode('utf-8')
        for c in translation:
            name = name.replace(c, translation[c])
        converted_name = str_parsing(name) 
        newargs = args[:-1]
        newargs += (converted_name, )
        return func(*newargs)
    return conversion

class comic_base(object):
    def __init__(self, book_url, name = 'book', quiet = False):
        global output_quiet
        global use_internal_zip 
        global use_internal_download
        self.book_url = book_url
        if sys.platform == 'win32':
            self.name = name.decode('utf-8')
        else:
            self.name = name
        self.chapter_list = []
        self.zip_list = []
        output_quiet = quiet
        try:
            os.system('zip --version 1>>/dev/null')
        except OSError:
            use_internal_zip = True
        try:
            os.system('wget --version 1>>/dev/null')
        except OSError:
            use_internal_download = True
        try:
            mkdir(self.name)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise
        chdir(self.name)
        self.get_chlist()
        self.get_already_exist()
    def get_chlist(self):
        PRINT('get chapter lists...')
    def get_already_exist(self):
        PRINT('read files downloaded...')
        ls = os.listdir('./')
        self.zip_list = [filename for filename, ext in map(os.path.splitext, ls) if '.zip' in ext]
    def download_chapters(self, start = -1, end = -1, all = False):
        singlech = False
        if all:
            ch_download = self.chapter_list
        else:
            if start == -1:
                PRINT('errorneous starting chapter')
            if end == -1:
                singlech = True
            #ch_download = [ch for name in ch_range for ch in self.chapter_list if name in ch.name]
            #ch_found = (name for name in ch_range for ch in self.chapter_list if name in ch.name)
            ch_download = []
            ch_found = set([]) 
            if singlech:
                name = str(start)
                not_exist = name
                for ch in self.chapter_list:
                    if name in ch.name:
                        ch_download.append(ch)
                        ch_found.add(name)
                        break
                else:
                    PRINT('chapter %s not exist' % not_exist)
            else:
                ch_range = set(('%s' % ch for ch in range(start, end + 1)))
                for name in ch_range:
                    for ch in self.chapter_list:
                        if name in ch.name:
                            ch_download.append(ch)
                            ch_found.add(name)
                #ch_range_set = set(ch_range)
                not_exist = set.difference(ch_range, ch_found)
                for chap in not_exist:
                    PRINT('chapter %s not exist' % chap)
        for ch in ch_download:
            if sys.platform == 'win32':
                name = ch.name
            else:
                name = ch.name.encode('utf-8')
            if name in self.zip_list:
                PRINT('%s skipped...' % name)
            else:
                ch.get_imagelist()
                ch.download()
    def endbook(self):
        chdir('..')

class chapter_base(object):
    @chr_conversion
    def __init__(self, ch_url, name):
        self.ch_url = ch_url
        self.name = name
        self.jpg_list = []
    def get_imagelist(self):
        PRINT('get image lists...')
    def download_img(self, referer):
        total = len(self.jpg_list)
        if total == 0:
            return False
        got = 0
        for img in self.jpg_list:
            if sys.platform == 'win32' and use_internal_download:
                p = img.split('/')
                try:
                    PRINT('retrieving ' + img)
                    path, res = u.urlretrieve(img, filename=p[-1])
                    got += 1
                except u.URLError:
                    pass
            else:
                if output_quiet:
                    ret = call(('wget', '-c', img, referer, '-a', 'wget-log'))
                else:
                    ret = call(('wget', '-c', img, referer))
            if not ret:
                got += 1
            time.sleep(1) #防盜鍵
        return True if float(got)/float(total) > 0.8 else False
    def download(self):
        try:
            mkdir(self.name)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise
        chdir(self.name)
        complete = self.download_img(None)
        if complete:
            self.create_zip()
        else:
            PRINT('fail to download %s' % self.name)
            chdir('..')
            shutil.rmtree(self.name, ignore_errors=True)

    def create_zip(self):
        compress_err = 0
        chdir('..')
        if sys.platform == 'win32' and use_internal_zip:
            zip_folder(self.name, '%s.zip' % self.name)
        else:
            if sys.platform == 'win32':
                self.name = self.name.encode('cp950') #Warning: using cp950 for big5 encoding
            if output_quiet:
                compress_err = call(['zip', '-q', '-r', '%s.zip' % self.name, self.name])
            else:
                compress_err = call(['zip', '-r', '%s.zip' % self.name, self.name])
        if not compress_err:
            for root,dirs,files in os.walk(self.name):
                for filename in files:
                    os.remove(os.path.join(root,filename))
            os.rmdir(self.name)

if __name__ == '__main__':
    pass
