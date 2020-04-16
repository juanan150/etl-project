#%%

import pandas as pd
import matplotlib

clean_elcolombiano = pd.read_csv('clean_elcolombiano_2020_03_31_articles.csv')
#clean_elpais = pd.read_csv('clean_elpais_2020_03_29_articles.csv')

print(clean_elcolombiano.describe())
#print(clean_elpais.describe())

#print(clean_elpais.loc[clean_elpais['n_tokens_title'] == 2])

#clean_elpais['n_tokens_title'].plot(style='k.')
clean_elcolombiano['n_tokens_title'].plot(style='r.')

# %%
clean_elpais['n_tokens_body'].plot(style='k.')
clean_elcolombiano['n_tokens_body'].plot(style='r.')

# %%

all_newspaper = pd.concat([clean_elpais,clean_elcolombiano])

grouped = all_newspaper.groupby('newspaper_uid')

grouped.hist()

#%%

grouped['n_tokens_body'].agg(['min','mean','max'])

# %%

print(clean_elcolombiano.loc[clean_elcolombiano['n_tokens_body'] == 1])

clean_elcolombiano['url'].value_counts

# %%
