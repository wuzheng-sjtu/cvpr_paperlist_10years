#!/usr/bin/python
#-*- coding:utf-8 -*-
__author__ = 'Zheng Wu'

import os, sys
import re
import urllib2
from collections import OrderedDict
# add UTF-8 support
reload(sys)
sys.setdefaultencoding('utf-8')

# 2015 2016 are not available
YEARS = xrange(2007, 2015) + xrange(2017, 2018)
this_dir = os.path.dirname(__file__)
# header for pass crawler test
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def process_title(title):
	# process the titles to a specific format
	pattern = re.compile('\([\s\S]*?\)')
	title = re.sub(pattern, '', title)
	title = title.replace('\n', ' ')
	title = title.strip()
	return title

for year in YEARS:
	YEAR_PATH = os.path.join(this_dir, 'CVPR{:d}'.format(year))
	if not os.path.exists(YEAR_PATH):
		os.mkdir(os.path.join(YEAR_PATH))
	paper_list_dir = os.path.join(YEAR_PATH, 'paper_list.txt')
	# get URL for each conference
	_URL = 'http://www.cvpapers.com/cvpr{:d}.html'.format(year)
	page = urllib2.urlopen(_URL).read()
	re_str = '<dt>([\s\S]*?)</dt>'
	pattern = re.compile(re_str)

	# construct a paper dict: {name: citation}
	papers = {}
	titles = re.findall(pattern, page)
	num_titles = 0
	for title in titles:
		# get rid of \n
		num_titles += 1
		print 'getting citation of paper: {:d}/{:d}'.format(num_titles, len(titles))
		title = process_title(title)
		search_title = title.replace(' ', '+')
		citation_url = 'https://d.ggkai.men/extdomains/scholar.google.com/scholar?hl=en-US&as_sdt=0%2C5&q='+search_title+'&btnG='
		print citation_url
		#citation_page = urllib2.urlopen(citation_url).read()
		req = urllib2.Request(citation_url, headers=hdr)
		try:
			citation_page = urllib2.urlopen(req).read()
			#citation_page = unicode()
		except urllib2.HTTPError, e:
			print e.fp.read()

		citation_pattern = re.compile('Cited by (.*?)</a>')
		citations = re.findall(citation_pattern, citation_page)
		# sometimes return multiple citations or 0 citations
		if len(citations) == 0:
			print 'Citation not found!'
			paper_citation = 0
		else:
			paper_citation = int(citations[0])

		papers[title] = paper_citation

	# Sort the dict by number of citations
	sorted_papers = OrderedDict(sorted(papers.items(), key=lambda x: x[1]), reversed=False)
	f = open(os.path.join(YEAR_PATH, 'paper_list.txt'), 'wb')
	for k, v in sorted_papers.items():
		if k=='reversed':
			continue
		f.write('Title: {:s}\nCitations: {:d}\n\n'.format(k, v))
	f.close()


	