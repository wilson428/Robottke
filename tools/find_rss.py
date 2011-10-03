#!/usr/bin/python

#IN PROGRESS
#finds the RSS feed for sites in the database.
#not all sites to this the same way, so you have to try a bunch of patterns

#import twitter as twitterapi
import sqlite3
import urllib2
import simplejson
import re
import sys
from urlparse import urlparse
from cStringIO import StringIO
from lxml.html import etree, parse

#PREFIX = '/home/wilsonc/cron/'
PREFIX = '../'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect(PREFIX + 'kottke.db')
conn.row_factory = dict_factory
c = conn.cursor()

#c.execute("create table hattips(id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(25), domain varchar(25) UNIQUE, rss varchar(50), frequency INTEGER)")

def rss_search():
    r = c.execute('''select * from tips where rss=""''').fetchall()
    
    for line in r:
        source = line["domain"]
        #print source
        try:
            response = urllib2.urlopen(source).read()
            tree = etree.parse(StringIO(response), etree.HTMLParser())
            root = tree.getroot()

            feed = tree.xpath("//link[@type='application/rss+xml']")
            if feed == []:
                feed = tree.xpath("//a[text()='RSS']")
                if feed == []:
                    feed = tree.xpath("//a[@href='/feed/']")
                    if feed == []:
                        feed = tree.xpath("//a[@href='"+source+"/feed/']")
                        if feed == []:
                            feed = tree.xpath("//a[@href='/feeds/']")
                            if feed == []:
                                feed = tree.xpath("//a[@href='"+source+"/feeds/']")
                        
            if feed != []:
                print feed[0]
                rss = feed[0].get("href")
                if urlparse(rss).netloc != "" and urlparse(rss).netloc != "/":
                    print rss
                    c.execute('''update tips set rss = ? where domain = ?''', (rss,source))            
                    conn.commit()
                else:
                    rss_feed = source + rss
                    print rss_feed
                    c.execute('''update tips set rss = ? where domain = ?''', (rss_feed,source))            
                    conn.commit()
                    
        except IOError:
            print "bad call",source

rss_search()
    
conn.commit()
conn.close()
