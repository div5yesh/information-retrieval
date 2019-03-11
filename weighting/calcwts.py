"""
Divyesh Chitroda, d151@umbc.edu
CampusId: GW92650

CMSC 676 – Information Retrieval
Homework 2
"""

import html2text as h2t
import os, codecs, sys, time, math
import numpy as np

# check for command line arguments, must have input and output directory path
if len(sys.argv) != 3:
    print("2 arguments required: input and output directory path.")
    exit()

# get input directory
inpath = sys.argv[1]
# get output directory
outpath = sys.argv[2]

# list of escape characters, unwanted characters
escapeChars = ["\n","\t","\r",",",".","-","_","'",'"',"`","[","]","(",")","?","|","*",";","!","{","}",">","$","=","%","#","+","<","&","\\","0","1","2","3","4","5","6","7","8","9"]
freq_dist = {}
doc_freq = {}
filetokens = {}

# get programs start time
prev = time.time()

# file counter
idx=0

tf = {}

stfile = open("stopwords.txt", "r")
stopwordslist = stfile.read()
stopwordslist = stopwordslist.replace("'", "")
stopwordslist = stopwordslist.split("\n")

files  = os.listdir(inpath)

# iterate through all the files in input directory
for file in files:
    # check for html files only
    if file.endswith(".html"):
        # open the file with ascii encoding and ignore encoding errors
        fr = open(os.path.join(inpath, file), "r",  encoding="ascii", errors="ignore")
        # read html content of the file
        html = fr.read()
        # extract text from html using html parser
        text_maker = h2t.HTML2Text()
        text_maker.ignore_links = True
        # text_maker.ignore_images = True
        text_maker.images_to_alt = True
        text_maker.protect_links = True
        # text_maker.ignore_anchors = True
        # text_maker.inline_links = False
        text = text_maker.handle(html)
        # replace all unwanted characters from escape sequence with whitespace character
        for esc in escapeChars:
            text = text.replace(esc, " ")
        
        # split text string into tokens using whitespace
        tokens = text.split(' ')

        # # contains unique set of tokens for each file
        filetokens[file] = {}
        tf[file] = {}

        # iterate all tokens and create hashmap with frequency count
        for i in tokens:
            # lower case all characters
            i = i.lower()
            # ignore empty characters
            if len(i) > 1 and i not in stopwordslist:
                # add to list of corresponding file
                if i in filetokens[file]:
                    filetokens[file][i] += 1
                else:
                    filetokens[file][i] = 1

                # create frequency distrbution hashmap
                if i in freq_dist:
                    freq_dist[i] = freq_dist[i] + 1
                else:
                    freq_dist[i] = 1

                if i in doc_freq:
                    if file not in doc_freq[i]:
                        doc_freq[i].append(file)
                else:
                    doc_freq[i] = [file]

        for i in filetokens[file]:
            wordtf = filetokens[file][i]/len(tokens)
            tf[file][i] = wordtf

        # find elapsed CPU time at every 100th file
        if idx in [10, 20, 40, 80, 100, 200, 300, 400, 500]:
            print(time.time() - prev)
        
        # increment file counter
        idx+=1

collection = idx

for file in filetokens:
    tfidf = {}
    tokens = filetokens[file]
    for tok in tokens:
        idf = math.log(collection/len(doc_freq[tok]))
        tfidf[tok] = tf[file][tok] * idf

    fw = codecs.open(os.path.join(outpath, file) +".txt", 'w', encoding='ascii',errors="ignore")
    sortedvals = sorted(tfidf.items(), key=lambda kv: kv[1], reverse=True)
    for tok, tfidf in sortedvals:
        fw.write(tok + " " + str(tfidf) + "\n")

    fw.close()