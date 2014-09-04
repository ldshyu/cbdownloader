#!/bin/python
# vim: set fileencoding=utf-8
"""
    This script is for fetching comic from dm.idler-et.com.
    Just change book_url and that's it.
"""
from urllib import urlopen
import re
from comic_base_oo import comic_base, chapter_base

class comic_books(comic_base):
	def get_chlist(self):
		super(comic_books, self).get_chlist()
		website_base = 'http://dm.idler-et.com'
		href_symbol = "href='"
		title_symbol = "'>"
		url = urlopen(self.book_url)
		source = url.read()
		parse = re.split('</a>', source) #split lines
		for content in parse:
			if 'comiclist' in content:
				href_start = content.find(href_symbol)
				content = content[href_start:]
				href_start = 0
				title_start = content.find(title_symbol)
				if href_start != -1 and title_start != -1:
					href = content[href_start + len(href_symbol):title_start]
					title = content[title_start + len(title_symbol):].strip('\n').decode('gb2312')
					#title = str_parsing(title.encode('utf-8'))
					href = website_base + href
					self.chapter_list.append(chapters(href[:-5], title.encode('utf-8'))) # drop 1.htm

class chapters(chapter_base):
	def get_imagelist(self):
		page = 1
		while True:
			ch_url = '%s%d.htm' % (self.ch_url, page)
			url = urlopen(ch_url)
			source = url.read()
			parse = re.split('>', source)
			link_symbol = "src='"
			for line in parse:
				if 'img' in line and 'DisComic' in line:
					link_start = line.find(link_symbol)
					link_end = link_start + len(link_symbol)
					while line[link_end] != "'":
						link_end += 1
					img_link = line[link_start + len(link_symbol):link_end].translate(None, '\n')
					self.jpg_list.append(img_link)
					break
			else:
				break
			page += 1
	def download_img(self, referer):
		return super(chapters, self).download_img('--referer="dm.idler-et.com"')
	
if __name__ == '__main__':
# for full download
#	book_url = 'http://dm.idler-et.com/comiclist/633/'
#	book_name = '結界師'
#	cb = comic_books(book_url, book_name)
#	cb.download_chapters(all=True)
#	cb.endbook()
#for multiple episode download
	book_url = 'http://dm.idler-et.com/comiclist/628/'
	book_name = '妖精的尾巴'
	cb = comic_books(book_url, book_name)
	cb.download_chapters(304, 304)
	cb.endbook()

