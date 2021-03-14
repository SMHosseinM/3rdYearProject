import pandas as pd
df = pd.read_csv('./datasets/dataset-cooking.csv')
df = df.sample(frac=1)

# ****************

col = ['text', 'class']
df = df[col]
df = df[pd.notnull(df['text'])]
df.columns = ['query', 'query-class']

df['category_id'] = df['query-class'].factorize()[0]
category_id_df = df[['query-class', 'category_id']].drop_duplicates().sort_values('category_id')
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['category_id', 'query-class']].values)

# ****************
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression

X_train, X_test, y_train, y_test = train_test_split(df['query'], df['query-class'], random_state = 20)
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

# clf = LogisticRegression(multi_class='multinomial', solver='lbfgs').fit(X_train_tfidf, y_train)

# SVM model
from sklearn.svm import SVC
from sklearn.multiclass import OneVsOneClassifier

svm = OneVsOneClassifier(SVC(kernel='linear')).fit(X_train_tfidf, y_train)
