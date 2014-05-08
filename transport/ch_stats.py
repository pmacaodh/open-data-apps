# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 21:08:40 2014

@author: paul
"""

import pandas as pd
import numpy as np

xlfile = 'su-d-01.02.02.01.15clean.xls'
df = pd.read_excel(xlfile,'2012',index_col=0)

district_ix = df.index.map(lambda s: '>>' in s)
kanton_ix = df.index.map(lambda s: '- ' in s)
town_ix = df.index.map(lambda s: '......' in s)

clean_index = lambda s: s.replace('>> ','').replace('- ','').replace('......','')
df.index = df.index.map(clean_index)



def plot_kanton_pop():
    pop = df['Population']
    kanton_pop = pop[kanton_ix].copy()
    kanton_pop.sort()
    kanton_pop.div(1000).plot(kind='barh',title='Kantonal Population (m)')

def plot_district_pop():
    pop = df['Population']
    district_pop = pop[district_ix].copy()
    district_pop.sort()
    district_pop.head(20).div(1000).plot(kind='barh',title='District Population (000s)')

def kantonal_towns_data(kanton='Zurich'):
    pop = df['Population']
    count = pop.reset_index()
    kstarts = count[kanton_ix].index.values.astype(int).tolist()
    kends = kstarts[1:] + [len(pop)]

    zurich_ix = range(kstarts[0],kends[0])
    zurich_ix = count.index.map(lambda x:x in zurich_ix)
    zurich_town_ix = np.logical_and(zurich_ix, town_ix)
    return df.ix[zurich_town_ix]

def get_zh_origins(data):
    zh_origins = [town[5:] for town in data.index.values]
    bad_towns = ['Kyburg','Schlatt (ZH)','Lindau']
    zh_origins = filter(lambda x: x not in bad_towns,zh_origins)
    return zh_origins