#Make dataset of Reddit network statistics by week

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

def make_network(f):
    ndf=f.loc[:,["author","parent_author"]]

    ndf=ndf.groupby(["author","parent_author"]).count()
    ndf = ndf.reset_index(level=['author', 'parent_author'])
    return(nx.from_pandas_edgelist(ndf, source="author", target="parent_author"))

def network_stats(g,gname,week):
    num_users = len(g.nodes())
    num_connections = len(g.edges())

    density = nx.density(g)
    avg_clustering_coef = nx.clustering(g).values()
    avg_clustering_coef = sum(avg_clustering_coef)/num_users
    # in_degree = nx.in_degree_centrality(g)
    # out_degree = nx.out_degree_centrality(g)  
    # closeness = nx.closeness_centrality(g)  

    gn = nx.algorithms.community.centrality.girvan_newman(g)
    communities=tuple(sorted(c) for c in next(gn))
    communities = sorted(communities,reverse=True,key=len)
    num_com=len(communities)
    avg_com_size=num_users/num_com
    biggest_com = len(communities[0])
    
    return("{},{},{},{},{},{},{},{},{}".format(str(week),gname,str(num_users),str(num_connections),str(density),str(avg_clustering_coef),str(num_com),str(avg_com_size),str(biggest_com)))

s="week,status,num_users,num_connections,density,avg_clustering_coef,year,num_com,avg_com_size,biggest_com\n"

for i in range(len(week_list)):
    if len(week_list[i])>0:
        g = make_network(week_list[i])

        gname=""
        if week_list[i].timestamps.apply(lambda x: True if (datetime.date(2016, 7, 22) == x.date()) else False).any():
            gname="during"
        elif not (datetime.datetime(2016, 7, 22) < week_list[i].timestamps).any():
            gname="before"
        else:
            gname="after"

        year = str(week_list[i].timestamps.iloc[0].year)

        s+=network_stats(g,gname,i)+","+year+"\n"

f=open("network_stats_weekly2.csv","w")
f.write(s)
f.close()