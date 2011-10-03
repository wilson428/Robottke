#!/usr/bin/python

#creates a table of tag coincidences

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

c.execute('CREATE TABLE IF NOT EXISTS "tag_ngrams" (id INTEGER PRIMARY KEY AUTOINCREMENT, "tag1" TEXT, "tag2" TEXT, "frequency" INTEGER)')

html_entites = re.compile('(&amp;amp;|&amp;|&quot;)')
clutter_chars = re.compile('([\!\;\:\*\(\)\,"\?])|(^\')|(\'$)|(\...$)|(\.$)')

def clean_word(word):
    word = word.lower()
    word = html_entites.sub("", word)
    word = clutter_chars.sub("", word)
    return word
            
r = c.execute("select * from kottke")

for post in r.fetchall():
    tags = post["tags"].split(",")
    tags.remove("")
    print post["id"]
    for i in range(0, len(tags)):
        tag1 = clean_word(tags[i])
        #print tag1
        for ii in range(i+1, len(tags)):
            tag2 = clean_word(tags[ii])
            r = c.execute("select id,frequency from tag_ngrams where tag1=? and tag2=? or tag1=? and tag2=?", (tag1,tag2,tag2,tag1)).fetchone()
            if r:
                c.execute("update tag_ngrams set frequency = ? where id = ?", (r['frequency']+1, r['id']))
            else:
                c.execute("insert into tag_ngrams (tag1, tag2, frequency) values (?,?,?)", (tag1,tag2,1))
            conn.commit()
    
    #c.execute('''update sources set name = ? where id = ?''', (name, source["id"]))

conn.commit()    
conn.close()
