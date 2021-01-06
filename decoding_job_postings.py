# -*- coding: utf-8 -*-
"""Decoding Job Postings.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1D_O7p3RlbVw9729DOCeorzhV36MU_3JM
"""

#Dependencies
import pandas as pd
import glob
import numpy as np
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from wordcloud import WordCloud
import matplotlib.pyplot as plt

#Open the html files
all_files = []

files = glob.glob('/content/drive/MyDrive/html_job_postings/*')
for file_name in files:
  with open(file_name, 'r') as f:
    contents = f.read()
    all_files.append(contents)

print(f"Loaded {len(all_files)} HTML files.")

all_html = []

for html in all_files:
  soup = bs(html)
  all_html.append(soup)
print(all_html[1])

posting = {'Title': [], 'Body': []}

for soup in all_html:
  posting['Title'].append(soup.title.text)
  posting['Body'].append(soup.body.text)

df_new = pd.DataFrame(posting)
summary = df_new.describe()
print(summary)

all_bullets = []
for soup in all_html:
  new_bullets = []
  for bullet in soup.find_all('li'):
    new_bullets.append(bullet.text.strip())
  all_bullets.append(new_bullets)

df_new['Bullets'] = all_bullets
df_new['Bullets'] = df_new['Bullets'].apply(tuple, 1)
print(df_new.Bullets)

print(df_new)

df_new.head()

df_new.drop_duplicates(inplace=True)
df_new.shape

df_new = df_new[df_new['Title'].str.contains('(Data Science)|(Data Scientist)', case = False)]
df_new

#df_new.to_csv('step1.csv')
#df_new = pd.read_csv(df_name, converters={'column_name': eval})

resume = open('/content/drive/MyDrive/resume.txt', 'r').read()
print(resume)

vectorizer = TfidfVectorizer(stop_words='english')

text = df_new.Body.values.tolist() + [resume]
tf_matrix = vectorizer.fit(text)
tf_matrix = tf_matrix.transform(text)
print(tf_matrix.shape)

num_posts, title_size = tf_matrix.shape
print(f"Our collection of {num_posts} job postings contain a total of "
      f"{title_size} unique titles")

cosine_similarities = cosine_similarity(tf_matrix[:-1] , tf_matrix[-1])
cosine_similarities.shape

df_new['Relevant'] = cosine_similarities
df_sorted = df_new.sort_values(by='Relevant', ascending = False)
df_sorted.reset_index(inplace=True, drop=True)
df_sorted.shape

most_similar = df_sorted.iloc[:100].copy()
most_similar[most_similar['Title'].str.contains('(data scientist)|(data science)', case=False)].shape
most_similar.head()

#df_sorted.to_pickle('step2'.pk)

bullet_points = []
for sublist in most_similar['Bullets']:
  for item in sublist:
    bullet_points.append(item)
len(bullet_points)

bullet_vector = TfidfVectorizer(stop_words='english')
similar_skills = bullet_vector.fit_transform(bullet_points)
similar_skills.shape

svd_object = TruncatedSVD(n_components=100)
svd_transform_matrix = svd_object.fit_transform(similar_skills)
svd_transform_matrix.shape

svd_norm_matrix = Normalizer().fit_transform(svd_transform_matrix)
svd_norm_matrix.shape

svd_cosine_similarity = svd_norm_matrix[:-1] @ svd_norm_matrix[-1].T
svd_cosine_similarity.shape

k_means_model = KMeans(n_clusters=6)
clusters = k_means_model.fit(svd_norm_matrix)
clusters_label = pd.DataFrame({'Cluster': clusters.labels_})
clusters_label.head()

