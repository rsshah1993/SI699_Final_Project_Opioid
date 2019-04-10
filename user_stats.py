#Make dataset of Reddit user statistics by week 

import glob
import json
import pandas as pd
import datetime
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

filenames = glob.glob("20??-??")

s=""
cols = ['author','body','id','parent_id','score','subreddit','created_utc']
typings = {'author':"str",'body':"str",'id':"str",'parent_id':"str",'score':"float",
           'subreddit':"str","created_utc":"int"}
df=pd.DataFrame(columns=cols).astype(typings)
for filename in filenames:       
     with open(filename, "r") as f:
        s="["+f.read().replace("}","},")[:-2]+"]"
        d = json.loads(s)
        df2 = pd.DataFrame(d,columns=cols).astype(typings)
        df=pd.concat([df, df2],ignore_index=True)
df['timestamps']=df['created_utc'].apply(datetime.datetime.utcfromtimestamp)

df=df[(df.author!="[deleted]") & (df.author!="AutoModerator")]
name_dict = df.loc[:,["id","author"]].set_index("id").to_dict()["author"]

df["parent_author"]=df.parent_id.apply(lambda x:name_dict[x[3:]] if x[3:] in name_dict.keys() else np.nan)
df=df[~df.parent_author.isna()]

week_list = [g.reset_index() for n, g in df.set_index('timestamps').groupby(pd.TimeGrouper('W'))]

num_users="week,year,newcomer,proportion\n"

s=set([])

for i,v in enumerate(week_list):
    if len(v)>0:
        l = [name for name in v.author.values if name not in s]
        year = str(v.timestamps.iloc[0].year)
        if len(s)==0:
            sss = len(l)
        else:
            sss = len(s)
        proportion = len(l)/sss
        num_users += "{},{},{},{}\n".format(str(i),year,str(len(l)),str(proportion))
        s.update(l)

f=open("newcomer.csv","w")
f.write(num_users)
f.close()