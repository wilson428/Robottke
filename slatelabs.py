#some utility functions for various labs projects

import urllib
import os
import re

#returns a list of elements in list A not in list B.
#Similar to concept of "set difference," or A\B 
def difflist(listA, listB):
    listC = []
    if listA == None or listB == None:
        return []
    if len(listB) > len(listA):
        listA,listB = listB,listA
    for A in listA:
        if A not in listB:
            listC.append(A)
        #else:
            #print "removed",A
    return listC

#resolves shortened links
def follow_url(url):
    resp = urllib.urlopen(url)
    if resp.getcode() == 200:
       url = resp.url    
    return url

#http://code.activestate.com/recipes/577027-find-file-in-subdirectory/
def findInSub(filename, subdirectory=''):
    if subdirectory:
        path = subdirectory
    else:
        path = os.getcwd()
    for root, dirs, names in os.walk(path):
        if filename in names:
            #return os.path.join(root, filename)
            return True
    #raise 'File not found'
    return False

def unescape(s):
    s = s.replace("&amp;", "&")

    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&quot;", '"')


    # this has to be last:
    s = s.replace("&amp;", "&")
    return s

html_entites = re.compile('(&amp;amp;|&amp;|&quot;)')
clutter_chars = re.compile('([\!\;\:\*\(\)\ ,"\?])|(^\')|(\'$)|(\...$)|(\.$)')

def clean_word(word):
    word = word.lower()
    word = html_entites.sub("", word)
    word = clutter_chars.sub("", word)
    return word
