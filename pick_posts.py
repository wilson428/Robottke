#The selection algorithm
#extremely weak and arbitrary at the moment

import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def clear():
    conn = sqlite3.connect("kottke.db")
    conn.row_factory = dict_factory
    c = conn.cursor()        
    m = c.execute("select * from candidates").fetchall()
    for g in m:
        c.execute("update candidates set robotke = 0 where id = %d" % g["id"])
        conn.commit()
    conn.close()

def display_robotke():
    #k = Kottke_post.objects.all()
    #r = Candidate_post.objects.all()
    conn = sqlite3.connect("kottke.db")
    conn.row_factory = dict_factory
    c = conn.cursor()        

    p = []
    count = 0
    do = 0
    #m = c.execute("select * from candidates where word_score > 0 and source_score > 0")
    m = c.execute("select * from candidates where word_score > 1").fetchall()
    m.sort(key=lambda h: (len(h["tags"].split(","))*10+len(h["body_tags"].split(","))), reverse=True)
    for g in m:
        print g["title"], g["word_score"]
        if len(g["tags"].split(",")) > 1:
                c.execute("update candidates set robotke = 1 where id = %d" % g["id"])
                conn.commit()
                count = count+1
        if count > 20:
                break
        #p.append(g)
    #p = Context(p)
    conn.close()
    #return render_to_response('robotke.html', {'candidate_posts' : p}, context_instance=RequestContext(request))

clear()
display_robotke()
