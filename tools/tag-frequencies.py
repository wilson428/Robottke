#counts frequency of words in titles or in tags in kottke posts

import sqlite3
import re

def counts(list):
    counts = {} 
    for item in list:
        if not item: continue
        if item in counts: counts[item] += 1
        else: counts[item] = 1
    return counts

def format_counts(counts):
    counts = list((counts[word], word) for word in counts)
    counts.sort(key = lambda a: -a[0])
    output = "\n".join("%d,%s" % c for c in counts)
    return output

html_entites = re.compile('(&amp;amp;|&amp;|&quot;)')
clutter_chars = re.compile('([\!\;\:\*\(\)\,"\?])|(^\')|(\'$)|(\...$)|(\.$)')
stopwords = None
#stopwords = open("stop-words.csv").read().split(",")
#print stopwords

def clean_word(word):
    word = word.lower()
    word = html_entites.sub("", word)
    word = clutter_chars.sub("", word)
    if stopwords!=None:
        if word not in stopwords:
            return word
    else:
        return word
        
def in_title(cursor, field):
    tag_rows = cursor.execute("SELECT %s FROM kottke" % field)
    tags_split = (t[0].split(",") for t in tag_rows)
    words = (clean_word(word) for l in tags_split for word in l)
    return words # returns generator

if __name__ == "__main__":
    conn = sqlite3.connect('../kottke.db')
    cursor = conn.cursor()
    f = open("tags-count.txt", "w+")
    f.write(format_counts(counts(in_title(cursor, "tags"))).encode('utf-8'))
    conn.close()
