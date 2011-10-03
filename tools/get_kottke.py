#scans kottke archives and gathers relevant data.
#Probably not important to run this often

import urllib2 
import sqlite3
import re
from datetime import datetime

from BeautifulSoup import BeautifulSoup

prefix = '../'

conn = sqlite3.connect(prefix + 'kottke.db')
c = conn.cursor()
t = datetime.now()

months = {"Jan" : "01", "Feb" : "02", "Mar" : "03", "Apr" : "04", "May" : "05", "Jun" : "06", "Jul" : "07", "Aug" : "08", "Sep" : "09", "Oct" : "10", "Nov" : "11", "Dec" : "12" }

# Create table
c.execute("create table if not exists kottke(id INTEGER PRIMARY KEY AUTOINCREMENT, title blob, url blob, published blob, source blob, videos blob, tags blob, hattip blob)")

#year (98,99,0-9,10,11) and month (1-12) to beginning crawling
year = 7
month = 1

while year != 11 or month != 10: #inelegent, but update to stop at current month
   syear = str(year)
   if year < 10:
      syear = "0" + syear 
   smonth = str(month)
   if month < 10:
      smonth = "0" + smonth 
   url = "http://kottke.org/" + syear + "/" + smonth + "/"
   print "<-----------------------" + url
   soup = BeautifulSoup(urllib2.urlopen(url))
   for entry in soup.findAll('div', { "class" : "post" }):
      try:
         title = entry.h3.contents[0]
      except:
         title = entry.h2.contents[0]
      urlf = title['href']
      head = unicode(title.contents[0])      
      #print head
      body = entry.findAll('p')
      bodytext = ""
      for p in body:
         bodytext = bodytext + str(p)
      #print bodytext
      links = ""
      hattip = ""        

      try:
         for link in re.findall("<a href=\"(.+?)\"", bodytext):
            ht = re.findall("\(via <a href=\""+link+"\">(.+?)</a>", bodytext)
            if ht:
               hattip = ht[0] + "<" + link + ">"
            else:
               links = links + link + ","
      except:
         print "unbalanced"
      meta = entry.findAll('div', {"class" : "meta"})
      ls = re.findall("<a href=\"(.+?)\"", str(meta[0]))
            
      tags=""
      for tag in ls:
         if tag[0:5] == "/tag/":
            tags = tags + tag[5:] + ","
      d = re.findall("title=\"permanent link\">([a-zA-Z0-9,_ ]+)</a>", str(meta[0]))
      dt = re.split(" +", d[0])
      dmonth = months[dt[0]]
      dyear = dt[2]
      day = dt[1][:-1]
      if len(day) == 1:
         day = "0" + day           
      dat = dyear + "-" + dmonth + "-" + day

      videos = ''
      for video in re.findall("src=\"http://www.youtube.com/v/([a-zA-Z0-9_]+)", bodytext):
         videos = videos + "http://youtube.com/v/" + video + ","
      for video in re.findall("src=\"http://player.vimeo.com/video/([0-9]+)", bodytext):
         videos = videos + "http://player.vimeo.com/video/" + video + ","

      try:
         c.execute("insert into kottke(title, url, published, source, videos, tags, hattip) values (?,?,?,?,?,?,?)", (head, urlf, dat, links, videos, tags, hattip))
         #print ''
      except:
         print "bad character"
      #f.write("added " + head + "\n")
      conn.commit()

   month = month + 1
   if month == 13:
      month = 1
      year = year+1

c.close()
#f.close()
