import argparse

import numpy as np
import spacy
import yaml
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer

from models import lstm_event
from util import data_generator, io

nlp = spacy.load('en_core_web_lg')


with open('config.yaml') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
parser = argparse.ArgumentParser(description='data related parameters')
parser.add_argument('--stride', type=int, default=3)
parser.add_argument('--predict_length', type=int, default=3)
args = parser.parse_args()
window = config['window']

news = io.load_news(embed='none')
corpus = news.loc[:'2013-04-11', 0].values  # 60%

vectorizer = CountVectorizer(binary=True, stop_words=stopwords.words('english'),
                             lowercase=True, min_df=3, max_df=0.9, max_features=128000)
x_train_onehot = vectorizer.fit_transform(corpus)
word2idx = {word: idx for idx, word in enumerate(vectorizer.get_feature_names())}
embeddings_index = np.zeros((len(vectorizer.get_feature_names()) + 1, 300))
for word, idx in word2idx.items():
    try:
        embedding = nlp.vocab[word].vector
        embeddings_index[idx] = embedding
    except:
        pass
word2idx = {word: idx for idx, word in enumerate(vectorizer.get_feature_names())}

x_train, x_test, y_train, y_test = data_generator.generate(window, future=True, news=False, train_percentage=0.6,
                                                           stride=5,  # args.stride,
                                                           predict_length=3,  # args.predict_length
                                                           )
lstm_event.train(x_train, y_train, x_test, y_test, time_steps=window, layer_shape=[128, 32],
                 learning_rate=0.0000001, epoch=5000, predict_length=args.predict_length,
                 embed=embeddings_index, vocab_size=len(vectorizer.get_feature_names()))