#IN PROGRESS
#meant to extract just the unique content of a page by diffing it against
#a similar page on the site
#doesn't really work yet

import urllib2
from lxml.html import etree, HTMLParser, tostring
from lxml.html.clean import clean_html, Cleaner
from lxml.html.diff import htmldiff
import StringIO
from urlparse import urlparse
from ngram import NGram
parser = etree.HTMLParser()
from librarian import *

#reads a page 
def smart_read(url):
    resp = urllib2.urlopen(url)
    #resolve url
    url = resp.url
    domain = urlparse(url).netloc
    path = urlparse(url).path
    
    html = resp.read()
    tree = etree.parse(StringIO.StringIO(html), parser)
    links = tree.xpath("//body//@href")
    nmax = 0
    for link in links:
        if urlparse(link).netloc == domain:
            ng = NGram.compare(urlparse(link).path,path)
            #print link,ng
            if ng > nmax and ng < 1:
                nmax = ng
                mirror = link
    diffh = htmldiff(visit_page(url)["body"], visit_page(mirror)["body"])
    tree = etree.parse(StringIO.StringIO(diffh), parser)
    diff = tree.xpath("//ins//text()")
    for d in diff:
        print d

smart_read('http://www.huffingtonpost.com/2011/09/26/romneys-recived-56000-plu_n_981619.html')
