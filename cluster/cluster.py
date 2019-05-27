#%%
"""
Divyesh Chitroda, d151@umbc.edu
CampusId: GW92650

CMSC 676 – Information Retrieval
Homework 5
"""

import os
try:
	os.chdir(os.path.join(os.getcwd(), 'cluster'))
	print(os.getcwd())
except:
	pass

import html2text as h2t
import codecs, sys, time, math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

#%%
# check for command line arguments, must have input and output directory path
if len(sys.argv) != 3:
    print("2 arguments required: input and output directory path.")
    exit()

# get input directory
inpath = "files" #sys.argv[1]
# get output directory
outpath = "output" #sys.argv[2]

if not os.path.exists(outpath):
    os.mkdir(outpath)

# list of escape characters, unwanted characters
escapeChars = ["\n","\t","\r",",",".","-","_","'",'"',"`","[","]","(",")","?","|","*",";","!","{","}",">","$","=","%","#","+","<","&","\\","0","1","2","3","4","5","6","7","8","9"]
doc_freq = {}
freq_dist = {}
tf = {}

# get programs start time
prev = time.time()

# file counter
idx=0

# read stopwords.txt file to get list of stopwords
stfile = open("stopwords.txt", "r")
stopwordslist = stfile.read()
stopwordslist = stopwordslist.replace("'", "").lower()
stopwordslist = stopwordslist.split("\n")

# get all files in the input folder
files  = os.listdir(inpath)
print("Preprocessing:")
documents = {}
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
        text_maker.ignore_images = True
        text_maker.images_to_alt = True
        text_maker.protect_links = True
        text_maker.ignore_anchors = True
        text_maker.inline_links = False
        text = text_maker.handle(html)
        text = text.lower()
        # replace all unwanted characters from escape sequence with whitespace character
        for esc in escapeChars:
            text = text.replace(esc, " ")

        for stopwords in stopwordslist:
            text = text.replace(" " + stopwords + " ", " ")
        
        documents[file] = text

        # if len(documents.keys()) == 100:
        #     break

print(documents.keys())
#%%
# for file in freq_dist:
#     # conatins tf-idf for each token
#     tfidf = {}
#     tokens = freq_dist[file]
#     for tok in tokens:
#         # calculate idf = |c|/df(w)
#         idf = math.log(collection/len(doc_freq[tok]))
#         # calculate tfidf = tf(d,w) * idf(w)
#         tfidf[tok] = tf[file][tok] * idf

tfidf_vectorizer = TfidfVectorizer()
def cosine_similarity(d1, d2):
    if not len(d1.strip()) and not len(d2.strip()):
        return 0

    tfidf_matrix = tfidf_vectorizer.fit_transform([d1,d2])
    return ((tfidf_matrix * tfidf_matrix.T).A)[0,1]

cosine_similarity(documents["001.html"], documents["002.html"])

#%%
cos_sim_matrix = {}
for file1 in documents:
    print(file1)
    cos_sim_matrix[file1] = {}
    for file2 in documents:
        if file1 == file2:
            break
        cos_sim_matrix[file1][file2] = cosine_similarity(documents[file1], documents[file2])

#%%
def get_closest_clusters(data, inactive):
    max_num = -1
    maximum = (max_num, 0, 0)
    for d1 in data.keys():
        for d2 in data[d1].keys():
            if d1 not in inactive and d2 not in inactive and d1 != d2:
                score = data[d1][d2]
                if score > max_num:
                    max_num = score
                    maximum = (max_num, d1, d2)
    return maximum

def get_farthest_clusters(data, inactive):
    min_num = 5000
    minimum = (min_num, 0, 0)
    for d1 in data.keys():
        for d2 in data[d1].keys():
            if d1 not in inactive and d2 not in inactive and d1 != d2:
                score = data[d1][d2]
                if score < min_num:
                    min_num = score
                    minimum = (min_num, d1, d2)
    return minimum

print(get_closest_clusters(cos_sim_matrix, set()))
print(get_farthest_clusters(cos_sim_matrix, set()))

# (1.000000000000002, '420.html', '417.html')
# (0.0, '007.html', '006.html')

#%%
def init_centroids(files):
    centroids = {}
    for file in files:
        centroids[file] = [file]

    return centroids

#%%
def update_scores(data, clusters, cname, other):
    cluster1 = clusters[cname]
    cluster2 = clusters[other]
    documents = len(cluster1) + len(cluster2)
    score = 0
    for doc1 in cluster1:
        for doc2 in cluster2:
            if doc1 in data and doc2 in data[doc1]:
                score += data[doc1][doc2]
            if doc2 in data and doc1 in data[doc2]:
                score += data[doc2][doc1]

        data[cname][other] = score/documents

#%%
def kmeans_doc_cluster(clusters, data):
    inactive = set()
    total_clusters = len(clusters.keys())

    while total_clusters - len(inactive) - 1:
        cname = str(total_clusters)
        cosine_score, c1, c2 = get_closest_clusters(data, inactive)
        if cosine_score != -1:
            new_cluster = [c1, c2]
            inactive.update(new_cluster)
            clusters[cname] = new_cluster
            data[cname] = {}

            for cluster in clusters:
                if cluster not in inactive:
                    update_scores(data, clusters, cname, cluster)

            total_clusters += 1
        print(c1 + "+" + c2 + "--->" + cname + "::" + str(cosine_score))

#%%
centroids = init_centroids(documents)
kmeans_doc_cluster(centroids, cos_sim_matrix)

#%%
output_file = open(os.path.join(outpath, "cluster.json"),"w")
output_file.write(str(centroids).replace("'", '"'))
output_file.close()


#%%
