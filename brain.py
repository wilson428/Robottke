import sqlite3
from urlparse import urlparse
from slatelabs import clean_word

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#conn = sqlite3.connect('kottke.db')
#conn.row_factory = dict_factory
#c = conn.cursor()

def analyze_words(content, threshold):
    keys = content["keywords"]
    print keys
    score = 0
    for key in keys:
        c.execute("select frequency from 'tag-count' where tag = \"%s\"" % clean_word(key))
        r = c.fetchone()
        if r:
            if r["frequency"] > threshold:
                print key, r["frequency"]
                score = score+1
    return score

def analyze_source(url, name):
    score = 0
    c.execute("select frequency from hattips where name = '" + name + "'")
    r = c.fetchone()
    if r:
        print "Found hattip for " + name
        score = score + r["frequency"]
    c.execute("select frequency from sources where site = '" + urlparse(url).netloc + "'")
    if r:
        print "Found site freq for " + url
        score = score + r["frequency"]
    return score

#print analyze("nyc john", 25)
#conn.close()




