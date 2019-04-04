import gensim
from glob import glob
import pickle
from gensim.corpora.dictionary import Dictionary
import pandas as pd
import json
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import string
import pickle
import pandas as pd
import re
import string
from gensim import corpora
from gensim.models import CoherenceModel


##Disinclude stop words and punctuation
stop = set(nltk.corpus.stopwords.words('english'))
exclude = set(string.punctuation)

#Initialize lemmatizer
lemma = WordNetLemmatizer()
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

##Load in the data
search_path = "/scratch/si699w19_fluxm/roshah/Opioid/2016-??"
filenames = glob(search_path)
search_path2 = "/scratch/si699w19_fluxm/roshah/Opioid/2017-??"
filenames += glob(search_path2)
df=pd.DataFrame()
for filename in filenames:
     with open(filename, "r") as f:
        s="["+f.read().replace("}","},")[:-2]+"]"
        d = json.loads(s)
        df2 = pd.DataFrame(d)
        df2["year"]=filename
        df=pd.concat([df, df2],ignore_index=True)

##Delete rows where author no long existss
df = df[df['author']!= '[deleted]']

#Sample a proportion of the data because of how long it was taking to run
df = df.sample(frac = 1/20, random_state = 42)

#Create a list of just the comments
bodies = list(df['body'])

#clean all of the documents
doc_clean = [clean(doc).split() for doc in bodies]


#Model
dictionary = corpora.Dictionary(doc_clean)
doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]

Lda = gensim.models.ldamodel.LdaModel
ldamodel = Lda(doc_term_matrix, num_topics=3, id2word = dictionary, passes=500)

#Save Results
ldamodel.save('/scratch/si699w19_fluxm/roshah/text_analysis/lda_topic_model')
results = ldamodel.show_topics(num_topics=3, num_words=50, formatted = False)

with open('/scratch/si699w19_fluxm/roshah/text_analysis/topics.pkl', 'wb') as f:
    pickle.dump(results, f)
