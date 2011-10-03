#collects candidate posts for Robottke
#both from popular hattip sites and twitter

import json, StringIO, sqlite3
import feedparser
import urllib, re
from time import gmtime, strftime
from slatelabs import *
from lxml.html import etree, HTMLParser, tostring
from lxml.html.clean import clean_html, Cleaner
from librarian import *
import simplejson
from time import strftime, strptime
from datetime import datetime, date, timedelta
from dateutil.parser import parse
import sys

parser = etree.HTMLParser()

PREFIX = ''

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect(PREFIX + "kottke.db")
conn.row_factory = dict_factory
c = conn.cursor()

c.execute ('CREATE TABLE IF NOT EXISTS "candidates" ("id" INTEGER PRIMARY KEY ,"url" text, "title" TEXT, "source" text,"source_name" TEXT, "keywords" TEXT NOT NULL DEFAULT "", "key_tags" TEXT, "body_tags" TEXT NOT NULL DEFAULT "", "timestamp" datetime)')

THRESHOLD = 3
MAX_AGE = 3
MIN_SOURCE_FREQUENCY = 15
MIN_TIP_FREQUENCY = 5
NUM_ITEMS = 5

#commits each item in an RSS feed

#goes through sites JK commonly links to
def get_sources():
    response = c.execute('''select * from sources where rss != "" and tip_frequency > ?''', str(MIN_SOURCE_FREQUENCY))
    for site in response.fetchall():
        name = site["name"]
        print name
        extract_links(site["rss"], name, site["last"], NUM_ITEMS)

def get_tips():
    response = c.execute('''select * from sources where rss != "" and tip_frequency > ?''', str(MIN_TIP_FREQUENCY))
    for site in response.fetchall():
        name = site["name"]
        print name
        extract_links(site["rss"], name, site["last"], NUM_ITEMS)

#'last' is the date of the item in the RSS feed most recently visited
#meant to avoid scanning same pages again and again
def extract_links(url, name, last, limit=-1):  
    rss = feedparser.parse(url)
    if limit==-1 or limit > len(rss.entries):
        limit = len(rss.entries)
    content1 = {}
    content2 = {}

    #update the most recent story we hit
    try:
        c.execute("update sources set last = '%s' where rss = '%s'" % (rss.entries[0].date, url))
        conn.commit()
    except:
        print "nothing in feed"
        return

    #This extracts content from a page while extracting as few extraneous links as possible
    #to do this, we go through the RSS feed and diff each item against the next, ideally eliminating boilerplate links
    for i in range(0, limit):
        if rss.entries[i].date == last:
            print "no new entries for ", name
            return
        print "reading " + rss.entries[i].link + " from " + url
        age = how_old(rss.entries[i].date).days
        #print "age", age
        #visit_page, in librarian.py, optionally saves the entire html of each page it visits for archiving use
        if age < MAX_AGE:
            if content2 == {}:
                content1 = visit_page(rss.entries[0].link,"articles/"+name,True)
            else:                
                content1 = content2
            if i == len(rss.entries):
                content2 = visit_page(rss.entries[0].link,"articles/"+name,True)
            else:
                content2 = visit_page(rss.entries[i+1].link,"articles/"+name,True)
            if content1["links"] != [] and content1["links"] != []:
                #add this page as a candidate post. Comment out following line if only want to use this as a source for other links
                #brackets around name note that this was not located from a different site
                commit_link(rss.entries[i].link, "["+name+"]", rss.entries[i].link, parse(rss.entries[i].date, ignoretz=True))
                unique_links = difflist(content1["links"], content2["links"])
                #print "unique links",unique_links
                print "found " + str(len(unique_links)) + " unique links"
                for link in unique_links:
                    #if it's not from the same site and has a path (we typically don't want homepage links)
                    #print urlparse(link).path
                    if urlparse(link).netloc != urlparse(rss.feed.link).netloc and urlparse(link).path != '/' and urlparse(link).path != '':
                        try:
                            print link
                            commit_link(link, name, rss.entries[i].link, parse(rss.entries[i].date, ignoretz=True))
                        except UnicodeEncodeError as e:
                            print e
        #else:
            #print "too old"

#Takes various date formats and returns the elapsed time
def how_old(timestamp):
    now = datetime.now()
    then = parse(timestamp, ignoretz=True)
    return now - then

#we need a function to consolodate links that are found from two different locations and someone add weight to their authority and preserve sourcing
'''
def consolodate():
    m = c.execute("select * from candidates where word_score > 0 and source_score > 0")
    for link in m.fetchall():
        d = c.execute("select * from candidates where url = \"%s\"", link["url"])
        r = d.fetchone()
        if r != None:
            new_source_score = d["source_score"] + link["source_score"]
           
            c.execute("update candidates set 
'''

def get_tags(content):
    #compare to tags
    content["key_tags"] = ""
    try:
        keywords = ",".join(content["keywords"]).lower()+" "+content["title"].lower()
    except:
        keywords = ",".join(content["keywords"]).lower()
    keywords = list(set(re.split("[, -]+", keywords)))
    for word in keywords:
        c.execute("select frequency from 'tags' where tag = \"%s\"" % clean_word(word))
        r = c.fetchone()
        if r:
            if r["frequency"] > THRESHOLD:
                if content["key_tags"] == "":
                    content["key_tags"] = word+" (%d)" % r["frequency"]
                else:
                    content["key_tags"] = content["key_tags"] + ", " +word+" (%d)" % r["frequency"]

    content["body_tags"] = ""
    bodywords = list(set(content["body"].split(" ")))
    for word in bodywords:
        c.execute("select frequency from 'tags' where tag = \"%s\"" % clean_word(word))
        r = c.fetchone()
        if r:
            if r["frequency"] > THRESHOLD:
                if content["body_tags"] == "":
                    content["body_tags"] = word+" (%d)" % r["frequency"]
                else:
                    content["body_tags"] = content["body_tags"] + ", " +word+" (%d)" % r["frequency"]
    return content

def commit_link(url, source_name, source, date): 
    c.execute("select * from candidates where url=\"%s\" and source_name=\"%s\"" % (url, source_name))
    r = c.fetchone()
    #print url, r
    if r != None:
        print "Already have that link from that source", url
        return False

    content = visit_page(url, "articles/"+source_name, True)
    if not content:
        return False
    content = get_tags(content)
    print content

    #when the algorithm is better developed, it may make sense to compute here

    if content["url"] and content["url"] != "":
        try:
            c.execute("insert into candidates (url, title, source, source_name, keywords, key_tags, body_tags, timestamp) VALUES (?,?,?,?,?,?,?,?)", (content["url"], content["title"], source, source_name, ",".join(content["keywords"]), content["key_tags"], content["body_tags"], date.strftime("%b %d, %Y %I:%M %p")))
            conn.commit()
            return True
        except:
            return False
    else:
        print "no url!", content["url"]
        return False



#----------------------------------    

#retrieve all links from JK's Twitter followees
def twitter_links():
    gap = 50
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
                r = urllib2.urlopen(url).read()
            except URLError, e:
                print e.reason
                break
            users = simplejson.loads(r)
            #print users
            for user in users:
                #if user's json profile contains a tweet
                if user.get("status") != None:
                    tweet = user.get("status")
                    query = "select * from friends where user_id=%s" % user["id_str"]
                    u = c.execute(query).fetchone()
                    #if a new tweet
                    if tweet["id_str"] != str(u["most_recent"]):
                        #update most recent tweet for that user
                        c.execute('''update friends set most_recent = ? where user_id = ?''', (tweet["id_str"], user["id_str"]))
                        extract_twitter_links(tweet, user)
                else:
                    print "no tweet"
            offset = offset + gap

def extract_twitter_links(tweet, user):
    try:
        links = tweet["entities"]["urls"] #[0]["expanded_url"].split(",")
    except IndexError as strerror:
        print "no link ({0})".format(strerror)
        return
    for link in links:
        url = link['expanded_url']
        if url == None:
            url = link['url']
        #print url,user["screen_name"]
        commit_link(url, "@"+user['screen_name'], tweet['id'], parse(tweet['created_at'], ignoretz=True))
        conn.commit()

twitter_links()
#get_sources()
#get_tips()

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "twitter":
        twitter_links()
        conn.close()
    elif cmd == "sources":
        get_sources()
        conn.close()
    elif cmd == "tips":
        get_tips()
        conn.close()
