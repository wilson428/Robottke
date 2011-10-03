#!/usr/bin/python

#for sites in the sources database that don't have a name,
#uses the domain name

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

r = c.execute("select * from sources where name = ''")

for source in r.fetchall():
    name = urlparse(source["domain"]).netloc
    name = name.replace("www.", "")
    name = name.replace(".com", "")
    name = name.replace(".co.uk", "")
    print name
    
    c.execute('''update sources set name = ? where id = ?''', (name, source["id"]))

conn.commit()    
conn.close()
