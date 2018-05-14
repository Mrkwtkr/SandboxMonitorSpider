import requests
import re
import time
from bs4 import BeautifulSoup
from lxml import etree
from urllib import parse

# 尝试从网页获取内容
def get_html(url):
	try:
		r = requests.get(url, timeout=30)
		r.raise_for_status()
		r.encoding = 'utf-8'
		return r.text
	except:
		print("获取网页内容时发生错误！状态码:", r.status_code)

# 传入HTML内容和XPath表达式，筛选内容
def xpath_filter(content, xpath):
	selector = etree.HTML(content)
	return selector.xpath(xpath)

# 传入URL和XPath表达式的字典，获取游戏官网数据
def getOfficalData(url, xpath_dict):
	data_list = []
	html = get_html(url)
	titles = xpath_filter(html, xpath_dict['title'])
	hrefs = xpath_filter(html, xpath_dict['href'])
	# 遍历列表hrefs，构造绝对的URL
	i = 0
	while i < len(hrefs):
		hrefs[i] = parse.urljoin(url, hrefs[i])
		i = i + 1
	try:
		dates = xpath_filter(html, xpath_dict['date'])
		data = {}
		i = 0
		while i < len(titles):
			data = {'title': titles[i], 'href': hrefs[i], 'date': dates[i]}
			data_list.append(data)
			i = i + 1
	# 部分竞品网站新闻不包含日期数据，需捕获KeyError错误
	except KeyError:
		print('传入字典中未找到date信息')
		data = {}
		i = 0
		while i < len(titles):
			data = {'title': titles[i], 'href': hrefs[i]}
			data_list.append(data)
			i = i + 1
	return(data_list)


def miniworld():
	url = 'https://www.mini1.cn'
	xpath_dict = {
		'title': '//div[@class="tab-content-item active"]//a[@class="title"]/text()',
		'href': '//div[@class="tab-content-item active"]//a[@class="title"]/@href',
		'date': '//div[@class="tab-content-item active"]//span[@class="date"]/text()',
	}
	return getOfficalData(url, xpath_dict)


def trove():
	url = 'http://bzsj.game.360.cn/main.html'
	xpath_dict = {
		'title': '//div[@class="tabUnit"][1]//span[@class="title"]/text()',
		'href': '//div[@class="tabUnit"][1]//ul[@class="newsList"]//a/@href',
		'date': '//div[@class="tabUnit"][1]//a/span[@class="date"]/text()',
	}
	return getOfficalData(url, xpath_dict)


def portal_knights():
	url = 'https://csm.duoyi.com/news/'
	xpath_dict = {
		'title': '//div[@class="news-list"]//a/text()',
		'href': '//div[@class="news-list"]//a/@href',
	}
	return getOfficalData(url, xpath_dict)


def create_magic():
	url = 'http://sm.yingxiong.com/info/list_64_1.html'
	xpath_dict = {
		'title': '//ul[@class="lis news-li-1 show"]//a/text()',
		'href': '//ul[@class="lis news-li-1 show"]//a/@href',
		'date': '//ul[@class="lis news-li-1 show"]//span/text()',
	}
	return getOfficalData(url, xpath_dict)


def content_write(head, data_list):
	head = '## %s\n' % head
	table_head = '| 标题 | 链接 | 日期 |\n| :--- | :--- | :--- |\n'
	table = ''
	try:
		for i in data_list:
			date = i['date']
			table_row = '| %s | %s | %s |\n' % (i['title'], i['href'], i['date'])
			table = table + table_row
	except KeyError:
		for i in data_list:
			table_row = '| %s | %s | %s |\n' % (i['title'], i['href'], '\\')
			table = table + table_row	
	content = head + table_head + table
	return content


def md_write():
	with open('竞品监控速报.md', 'a+', encoding='utf-8') as f:
		current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		news_head = '# 沙盒竞品新闻速报(%s)\n' % current_time
		f.write(news_head)
		f.write(content_write('迷你世界', miniworld()))
		f.write(content_write('宝藏世界', trove()))
		f.write(content_write('传送门骑士', portal_knights()))
		f.write(content_write('创造与魔法', create_magic()))	


print('\n%s\n%s\n%s\n%s\n' % (miniworld(), trove(), portal_knights(), create_magic()))
md_write()
