#!/usr/bin/python

#nuts and bolts of retrieving pages from websites

#from calais import Calais
import json, simplejson, StringIO
import re
from urlparse import urlparse
import feedparser
from lxml.html import etree, HTMLParser, tostring
from lxml.html.clean import clean_html, Cleaner
from lxml.html.diff import htmldiff
from time import gmtime, strftime
import os
import urllib, urllib2
from urllib2 import URLError
from slatelabs import *


#API_KEY = "p6q44cknxg28qzyvcwx48ufu"
#calais = Calais(API_KEY, submitter="slate labs")

parser = etree.HTMLParser()
cleaner = Cleaner(style=True, page_structure=True )

BANNED = ["www.amazon.com", "amazon.com", "flickr.com", "www.flickr.com"]

#takes url and returns resolved url, title, metatags, and body and body links
#optionally saves whole HTML to path

def visit_page(url,path="",save=False):
    content = {"title" : "", "url" : "", "keywords" : "", "links" : [], "body" : ""}
    if urlparse(url).netloc == "":
        #print "partial:", url
        return content
    
    if urlparse(url).netloc in BANNED:
        #print "banned:", url
        return content
    try:
        resp = urllib2.urlopen(url)
    except URLError as e:
        print e
        return content
    if resp.getcode() != 200:
        "Bad response: ",resp.getcode() 
        return content
    #resolves URL
    content["url"] = resp.url  
    html = resp.read()
    try:
        tree = etree.parse(StringIO.StringIO(html), parser)
    except:
        print "LXML error"
        return content
    content["title"] = tree.xpath("//title//text()")
    if len(content["title"]) > 0:
        content["title"] = content["title"][0].strip()
    content["links"] = tree.xpath("//body//@href")
    content["keywords"] = tree.xpath("//meta[@name='keywords']/@content")
    if content["keywords"] == "":
        content["keywords"] = tree.xpath("//meta[@name='Keywords']/@content")
        print "caught a case ",url
    #content["body"] = cleaner.clean_html(etree.tostring(tree.xpath("//body")[0]))
    body = cleaner.clean_html(etree.tostring(tree.xpath("//body")[0]))
    content["word_count"] = len(body.split(" "))

    #will save full html
    if save:
        filename = urllib.quote_plus(content["url"][0:60])+".txt"
        #filename.replace("http%3A%2F%2F", "")
                
        #if file doesn't already exist
        if not findInSub(filename,path):
            #make that day's path
            path = path + strftime("/%Y/%m/%d/", gmtime())
            if not os.path.exists(path):
                os.makedirs(path)
            f = open(path+filename, "w+")
            f.write(html)
            f.close()
            print "wrote " + path+filename
        else:
            print "already had " + filename
    return content

  
#get's the first item with a domain that matches the RSS url
#to avoid diffing all entries against an ad or sister site
#a better system would be to scan all of them and reduce by probability of repeat 
def get_first_index(rss):
    post1 = None
    post2 = None
    for i in range(1, len(rss.entries)):
        post1 = rss.entries[i-1].link
        post2 = rss.entries[i].link
        if urlparse(post1).netloc == urlparse(post2).netloc:
            break
    if not post1 or not post2:
        return -1
    else:
        return i

def diff_rss(url, name, limit=-1):  
    rss = feedparser.parse(url)
    links = {}
    #print rss
    if limit==-1 or limit > len(rss.entries):
        limit = len(rss.entries)
    first_index = get_first_index(rss)
    for i in range(first_index, limit+1):
        links[rss.entries[i].link] = []
        post1 = rss.entries[i-1].link
        if i == limit:
            post2 = rss.entries[first_index-1].link
        else:
            post2 = rss.entries[i].link
        print post2
        diffh = htmldiff(get_content(post1)["body"], get_content(post2)["body"])
        tree = etree.parse(StringIO.StringIO(diffh), parser)
        diff = tree.xpath("//ins//@href")
        for d in diff:
            if urlparse(d).netloc != urlparse(rss.feed.link).netloc and urlparse(d).path != '/':
                links[rss.entries[i].link].append(d)
    return links


'''
#returns json or raw version of OpenCalais tags
def get_tags(txt,typ="json"):
    try:
        result = calais.analyze(txt)
        if typ=="json":
            return json.dumps(result.raw_response, sort_keys=True, indent=4)
        else:
            return result.simplified_response
    except:
        return "Calais is busy"
'''


