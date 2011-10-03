#!/usr/bin/python

#scans kottke database and collects frequencies of sources and hattips

#import twitter as twitterapi
import sqlite3
import urllib2
import simplejson
import re
import sys
from urlparse import urlparse

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

c.execute('CREATE TABLE IF NOT EXISTS "sources" ("id" INTEGER PRIMARY KEY ,"name" varchar(25) NOT NULL DEFAULT "","domain" varchar(50) NOT NULL UNIQUE, "rss" varchar(50) NOT NULL DEFAULT "","link_frequency" INTEGER NOT NULL DEFAULT 0, "tip_frequency" INTEGER NOT NULL DEFAULT 0, "last" TEXT NOT NULL  DEFAULT "")')
c.execute('CREATE TABLE IF NOT EXISTS "tips" ("id" INTEGER PRIMARY KEY ,"name" varchar(25) NOT NULL DEFAULT "","domain" varchar(50) NOT NULL, "rss" varchar(50) NOT NULL DEFAULT "", "frequency" INTEGER NOT NULL DEFAULT 0, "last" TEXT NOT NULL  DEFAULT "")')

personals = ["www.twitter.com","twitter.com","blogspot.com", "typepad.com", "wordpress.com", "tumblr.com", "www.tumblr.com", "www.stellar.io", "stellar.io"]

def get_sources():
    domains = {}
    c.execute('''select * from kottke''')
    for post in c.fetchall():
        links = post["source"].split(",")
        for link in links:
            domain = urlparse(link).scheme + "://" + urlparse(link).netloc
            if urlparse(link).netloc in personals:
                domain = link
            if domain != 'http://kottke.org':
                try:
                    domains[domain] = domains[domain]+1
                except:
                    domains[domain] = 1
    for key, value in sorted(domains.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        if value >= 3:
            print key + " - " + str(value)
            c.execute('''insert or ignore into sources (domain, link_frequency) values (?,?)''', (key, value))         
    conn.commit()

def get_hattips():
    domains = {}
    names = {}
    c.execute('''select * from kottke where hattip !=\'\'''')
    for post in c.fetchall():
        ht = re.match('(.+)<(.+)>', post["hattip"])
        try:
            nm = ht.group(1)
            url = urlparse(ht.group(2)).scheme + "://" + urlparse(ht.group(2)).netloc               
            if urlparse(ht.group(2)).netloc in personals:
                url = ht.group(2)
                #print url

            #print nm+"\t"+url
            try:
                domains[nm] = domains[nm]+1
            except:
                domains[nm] = 1
                names[nm] = url
        except:
            print "no good on " + post["hattip"]

    for key, value in sorted(domains.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        print key + " - " + str(value) + " - " + names[key]
        c.execute('''insert into tips (name, domain, frequency) values (?,?,?)''', (key, names[key], value))         
        conn.commit()

#this does NOT delete repeats, where kottke cited the same blog by different names ("marginal revolution" vs. "mr").
#it just gives all repeats the frequency of their combined tips. This is because I like to go in and choose the version of the name I like best
def consolidate():
    r = c.execute("select *, COUNT(domain) as num, SUM(frequency) as total from tips group by domain having num > 1")
    for dupe in r.fetchall():
        c.execute('''update tips set frequency = ? where domain = ?''', (dupe["total"], dupe["domain"]))
        print dupe["name"]
    conn.commit()


#get_hattips()
#get_sources()
#consolidate()        
conn.close()
