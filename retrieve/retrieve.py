"""
Divyesh Chitroda, d151@umbc.edu
CampusId: GW92650

CMSC 676 – Information Retrieval
Homework 4
"""

import html2text as h2t
import os, codecs, sys, time, math

args = len(sys.argv)
if args < 2:
    print("At least 1 argument required: query")
    exit()

wscoring = False
if sys.argv[1] == "wt":
    wscoring = True
    if args < 4:
        print("At least 2 argument required: weight query")
        exit()

# read stopwords.txt file to get list of stopwords
stfile = open("stopwords.txt", "r")
stopwordslist = stfile.read()
stopwordslist = stopwordslist.replace("'", "")
stopwordslist = stopwordslist.split("\n")

def escape(word):
    # list of escape characters, unwanted characters
    escapeChars = ["\n","\t","\r",",",".","-","_","'",'"',"`","[","]","(",")","?","|","*",
        ";","!","{","}",">","$","=","%","#","+","<","&","\\","0","1","2","3","4","5","6","7","8","9"]
    
    for esc in escapeChars:
        word = word.replace(esc, " ")
    
    word = word.strip().lower()
    if len(word) and word not in stopwordslist:
        return word

wqarr = {}

if wscoring:
    for i in range(3,args,2):
        word = escape(sys.argv[i])
        if word:
            wqarr[word] = float(sys.argv[i-1])
else:
    for i in range(1,args):
        word = escape(sys.argv[i])
        if word:
            wqarr[word] = 1

fr = open(os.path.join("out", "postings.txt"), "r",  encoding="ascii", errors="ignore")
postings = fr.read()
fr.close()

fr = open(os.path.join("out", "index.txt"), "r",  encoding="ascii", errors="ignore")
index = fr.read()
fr.close()

postings = postings.split("\n")
index = index.split("\n")

result = {}

for tok, weight in wqarr.items():
    if tok in index:
        idx = index.index(tok)
        posts = int(index[idx + 1])
        offset = int(index[idx + 2])
        doclist = postings[offset:offset + posts]
        for entry in doclist:
            [doc, idf] = entry.split("\t")
            if doc not in result:
                result[doc] = 0
            result[doc] += float(idf) * weight

sorted_res = sorted(result.items(), key=lambda kv: kv[1], reverse=True)
filtered_res = list(filter(lambda kv: kv[1] > 0, sorted_res))
if len(filtered_res):
    count = min(10, len(filtered_res))
    for i in range(count):
        print(filtered_res[i][0], filtered_res[i][1])
else:
    print("query not found.")
    