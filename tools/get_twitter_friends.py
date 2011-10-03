#!/usr/bin/python

#gets the Twitter info of whomever the handle fed to the function handles

import sqlite3
import urllib2, urllib
import simplejson

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

c.execute("create table if not exists friends(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE, screen_name VARCHAR(50) DEFAULT \"\", frequency INTEGER NOT NULL DEFAULT 0, follower text, most_recent INTEGER)")

def getFollows(names):
    names = names.split(",")
    for name in names:
        #returns twitter ids of all people [name] follows
        url = 'http://api.twitter.com/1/friends/ids.json?screen_name=%s' % name
        friends = simplejson.load(urllib2.urlopen(url))
        for friend_id in friends:
            print friend_id           
            c.execute('''insert or ignore into friends (user_id, follower, most_recent) VALUES (?,?,0)''', (friend_id, name))
        conn.commit()

    #now get their screen names. 
    gap = 100
    offset = 0
    while 1==1:
        query = "select * from friends limit %d offset %d" % (gap, offset)
        response = c.execute(query)
        friends = response.fetchall()
        #loop until last batch of 100, since twitter API only takes 100 at a time
        if len(friends) == 0:
            break
        else:
            ids = ''
            for friend in friends:
                ids += str(friend["user_id"])+','
                url = 'http://api.twitter.com/1/users/lookup.json?include_entities=1&user_id=%s' % ids    
            #call to Twitter API
            try:
                r = urllib.urlopen(url).read()
            except URLError, e:
                print e.reason
                break
            users = simplejson.loads(r)
            #print users
            for user in users:
                handle = user["screen_name"]
                print handle
                #get frequency of hattips eventually to measure authority
                #c.execute("select frequency from tip where name = '" + handle + "'")
                #r = c.fetchone()
                #freq = r["frequency"]
                c.execute('''update friends set screen_name = ? where user_id = ?''', (handle, user["id_str"]))
            conn.commit()
        offset = offset + gap
    conn.close()


getFollows("jkottke,kottke")
    
