"""
Divyesh Chitroda, d151@umbc.edu
CampusId: GW92650

CMSC 676 – Information Retrieval
Homework 2
"""

import html2text as h2t
import os, codecs, sys, time, math

# check for command line arguments, must have input and output directory path
if len(sys.argv) != 3:
    print("2 arguments required: input and output directory path.")
    exit()

# get input directory
inpath = sys.argv[1]
# get output directory
outpath = sys.argv[2]

if not os.path.exists(outpath):
    os.mkdir(outpath)

# list of escape characters, unwanted characters
escapeChars = ["\n","\t","\r",",",".","-","_","'",'"',"`","[","]","(",")","?","|","*",";","!","{","}",">","$","=","%","#","+","<","&","\\","0","1","2","3","4","5","6","7","8","9"]

# read stopwords.txt file to get list of stopwords
stfile = open("stopwords.txt", "r")
stopwordslist = stfile.read()
stopwordslist = stopwordslist.replace("'", "")
stopwordslist = stopwordslist.split("\n")

# Record class to store fixed length entry in the index file
class Record:
    def __init__(self, word, postings, offset):
        self.word = word
        self.postings = postings
        self.offset = offset

# get all files in the input folder
files  = os.listdir(inpath)

# select files in batches
for batch in [10, 20, 40, 80, 100, 200, 300, 400, 500]:
    doc_freq = {}
    freq_dist = {}
    tf = {}

    # file counter
    idx=0

    # get programs start time
    prev = time.time()
    print("Preprocessing:")
    # iterate through all the files in input directory
    for file in files:
        # if number of files processed == batch size
        if idx == batch:
            break

        # check for html files only
        if file.endswith(".html"):
            # open the file with ascii encoding and ignore encoding errors
            fr = open(os.path.join(inpath, file), "r",  encoding="ascii", errors="ignore")
            # read html content of the file
            html = fr.read()
            # extract text from html using html parser
            text_maker = h2t.HTML2Text()
            text_maker.ignore_links = True
            text_maker.ignore_images = True
            text_maker.images_to_alt = True
            text_maker.protect_links = True
            text_maker.ignore_anchors = True
            text_maker.inline_links = False
            text = text_maker.handle(html)
            # replace all unwanted characters from escape sequence with whitespace character
            for esc in escapeChars:
                text = text.replace(esc, " ")
            
            # split text string into tokens using whitespace
            tokens = text.split(' ')

            # contains token frequency for each file
            freq_dist[file] = {}
            # contains term frequency weight of tokens for each file
            tf[file] = {}

            # iterate all tokens and create hashmap with frequency and document count
            for i in tokens:
                # lower case all characters
                i = i.lower()
                # ignore empty tokens and stopwords
                if len(i) > 1 and i not in stopwordslist:
                    # create frequency distrbution hashmap
                    if i in freq_dist[file]:
                        freq_dist[file][i] += 1
                    else:
                        freq_dist[file][i] = 1

                    # create document frequency hashmap
                    if i not in doc_freq:
                        doc_freq[i] = set()
                    doc_freq[i].add(file)

            for i in freq_dist[file]:
                # calculate term frequency weights, tf = f(d,w)/|D|
                wordtf = freq_dist[file][i]/len(tokens)
                tf[file][i] = wordtf

            # increment file counter
            idx += 1

    # find elapsed CPU time of files proccessed
    print(time.time() - prev)

    # total number of documents
    collection = idx

    # get programs start time
    prev = time.time()

    print("Calculate weights:")
    # calculate and store tf-idf weights of tokens
    tfidf = {}
    for file in freq_dist:
        # conatins tf-idf for each token
        tokens = freq_dist[file]
        tfidf[file] = {}
        for tok in tokens:
            # calculate idf = |c|/df(w)
            idf = math.log(collection/len(doc_freq[tok]))
            # calculate tfidf = tf(d,w) * idf(w)
            tfidf[file][tok] = tf[file][tok] * idf

    # find elapsed CPU time of tfidf calculation
    print(time.time() - prev)

    index = []
    postings = []

    # get programs start time
    prev = time.time()

    print("Indexing:")
    for tok in doc_freq:
        docs = doc_freq[tok]
        record = Record(tok, len(docs), len(postings) + 1)
        index.append(record)
        for doc in docs:
            weight = tfidf[doc][tok]
            postings.append((doc, weight))

    # create postings.txt file
    fn_posting = os.path.join(outpath, "postings") +".txt"
    fw = codecs.open(fn_posting, 'w', encoding='ascii',errors="ignore")
    for doc, tfidf in postings:
        # store (document, weight) pairs for each token
        fw.write(doc + "\t" + str(tfidf) + "\n")
    # close file
    fw.close()

    # create index.txt file
    fn_index = os.path.join(outpath, "index") +".txt"
    fw = codecs.open(fn_index, 'w', encoding='ascii',errors="ignore")
    for record in index:
        # store (word, # documents, start position in postings file) records
        fw.write(record.word + "\n" + str(record.postings) + "\n" + str(record.offset) + "\n")
    # close file
    fw.close()

    # find elapsed CPU time and file sizes in KBs of index and postings file
    print(time.time() - prev, os.path.getsize(fn_index)/1024, os.path.getsize(fn_posting)/1024)