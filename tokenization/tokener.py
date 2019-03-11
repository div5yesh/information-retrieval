"""
Divyesh Chitroda, d151@umbc.edu
CampusId: GW92650

CMSC 676 – Information Retrieval
Homework 1
"""

import html2text as h2t
import os, codecs, sys, time

# check for command line arguments, must have input and output directory path
if len(sys.argv) != 3:
    print("2 arguments required: input and output directory path.")
    exit()

# get input directory
inpath = sys.argv[1]
# get output directory
outpath = sys.argv[2]

# list of escape characters, unwanted characters
escapeChars = ["\n","\t","\r",",",".","/","-","_","'",'"',"`","[","]","(",")","?",":","|","*",";","!","{","}",">","$","=","%","#","+","<","&","\\","0","1","2","3","4","5","6","7","8","9"]
freq_dist = {}

# get programs start time
prev = time.time()

# file counter
idx=0

# iterate through all the files in input directory
for file in os.listdir(inpath):
    # check for html files only
    if file.endswith(".html"):
        # open the file with ascii encoding and ignore encoding errors
        fr = open(os.path.join(inpath, file), "r",  encoding="ascii", errors="ignore")
        # read html content of the file
        html = fr.read()
        # extract text from html using html parser
        text = h2t.html2text(html)
        # replace all unwanted characters from escape sequence with whitespace character
        for esc in escapeChars:
            text = text.replace(esc, " ")
        
        # split text string into tokens using whitespace
        tokens = text.split(' ')

        # contains unique set of tokens for each file
        filetokens = set()

        # iterate all tokens and create hashmap with frequency count
        for i in tokens:
            # ignore empty characters
            if len(i) > 0:
                # lower case all characters
                i = i.lower()
                # add to list of corresponding file 
                filetokens.add(i)
                # create frequency distrbution hashmap
                if i in freq_dist:
                    freq_dist[i] = freq_dist[i] + 1
                else:
                    freq_dist[i] = 1

        # write tokens to file with corresponding html filename 
        fw = codecs.open(os.path.join(outpath, file) +".txt", 'w', encoding='ascii',errors="ignore")
        for i in filetokens:
            fw.write(i+"\n")
        
        # close the file
        fw.close()

    # find elapsed CPU time at every 100th file
    if idx % 100 == 0:
        print(time.time() - prev)
    
    # increment file counter
    idx+=1

# sort tokens alphabetically  
sortedKeys = sorted(freq_dist.items(), key=lambda kv: kv[0])
# sort tokens according to frequency of tokens in descending order
sortedvals = sorted(freq_dist.items(), key=lambda kv: kv[1], reverse=True)

# save alphabetically sorted frequency distribution to file dist_tokens.txt
ffw = codecs.open("dist_tokens.txt", 'w', encoding='ascii',errors="ignore")
for i in sortedKeys:
    ffw.write(i[0] + " " + str(i[1]) +"\n")
ffw.close()

# save frequency sorted frequency distribution to file dist_freq.txt
ffw = codecs.open("dist_freq.txt", 'w', encoding='ascii',errors="ignore")
for i in sortedvals:
    ffw.write(i[0] + " " + str(i[1]) + "\n")
ffw.close()