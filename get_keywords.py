import pke
import nltk
import csv
import pandas as pd
import unicodecsv as csv2
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

file = open("stopwords.txt", "r")
for line in file:
    words = line.split(",")
stoplist = stopwords.words('english') + list(words)

def get_keywords(content):
    content = content.replace("-", "")
    if len(content) <= 500:
        NGraph = 8
        NStat = 5
    if 500 < len(content) < 1000:
        NGraph = 13
        NStat = 10
    if len(content) >= 1000:
        NGraph = 18
        NStat = 15

    PositionRank = []
    MultipartiteRank = []
    TFIDF = []
    TextRank = []

    # PKE - TF-IDF
    extractorTFIDF = pke.unsupervised.TfIdf()
    extractorTFIDF.load_document(input=content, language="en", normalization=None)
    extractorTFIDF.candidate_selection(n=4, stoplist=stoplist)
    df = pke.load_document_frequency_file(
        input_file='C:/Users/admin/Anaconda3/Lib/site-packages/pke/models/df-semeval2010.tsv.gz')
    extractorTFIDF.candidate_weighting(df=df)
    keyphrasesTFIDF = extractorTFIDF.get_n_best(n=NStat)
    for key in keyphrasesTFIDF:
        TFIDF.append(key[0])

    # PKE - TextRank
    pos = {'NOUN', 'PROPN', 'ADJ'}
    extractorTextRank = pke.unsupervised.TextRank()
    extractorTextRank.load_document(input=content, language='en', normalization=None)
    extractorTextRank.candidate_weighting(window=2, pos=pos, top_percent=0.33)
    keyphrasesTextRank = extractorTextRank.get_n_best(n=NGraph)
    for key in keyphrasesTextRank:
        TextRank.append(key[0])

    # PKE - PositionRank
    pos = {'NOUN', 'PROPN', 'ADJ'}
    grammar = "NP: {<ADJ>*<NOUN|PROPN>+}"
    extractorPositionRank = pke.unsupervised.PositionRank()
    extractorPositionRank.load_document(input=content, language='en', normalization=None)
    extractorPositionRank.candidate_selection(grammar=grammar, maximum_word_number=4)
    extractorPositionRank.candidate_weighting(window=2, pos=pos)
    keyphrasesPositionRank = extractorPositionRank.get_n_best(n=NGraph)
    for key in keyphrasesPositionRank:
        PositionRank.append(key[0])

    # PKE - MultipartiteRank
    extractorMultipartiteRank = pke.unsupervised.MultipartiteRank()
    extractorMultipartiteRank.load_document(input=content)
    pos = {'NOUN', 'PROPN', 'ADJ'}
    extractorMultipartiteRank.candidate_selection(pos=pos, stoplist=stoplist)
    extractorMultipartiteRank.candidate_weighting(alpha=3, threshold=0.95, method='average')
    keyphrasesMultipartiteRank = extractorMultipartiteRank.get_n_best(n=NGraph)
    for key in keyphrasesMultipartiteRank:
        MultipartiteRank.append(key[0])

    inter1 = set(PositionRank).intersection(set(MultipartiteRank))
    inter2 = set(TFIDF).intersection(set(TextRank))
    to_remove_fin = []
    to_add = []
    to_remove = []
    for elem1 in inter2:
        for elem2 in inter1:
            if (" " not in elem1) and (" " not in elem2) and (
                    lemmatizer.lemmatize(elem1) in lemmatizer.lemmatize(elem2)):
                to_remove_fin.append(elem2)
                to_remove.append(elem1)
                to_add.append(elem1)
            if (" " not in elem1) and (" " not in elem2) and (
                    lemmatizer.lemmatize(elem2) in lemmatizer.lemmatize(elem1)):
                to_remove_fin.append(elem2)
                to_remove.append(elem1)
                to_add.append(elem2)
            if (elem1 in elem2) and (' ' in elem1) and (elem1 != elem2):
                to_remove_fin.append(elem2)
            elif (elem1 in elem2) and (' ' not in elem1) and (elem1 != elem2):
                to_remove.append(elem1)
    to_remove = set(to_remove)
    for elem in to_remove:
        inter2.remove(elem)

    inter = set(inter1).union(set(inter2))
    inter = list(inter)

    new_inter = inter
    new_inter = new_inter + list(set(to_add))
    for i in range(0, len(inter)):
        count = 0
        poses = []
        tokens = [word for word in nltk.word_tokenize(inter[i]) if word not in stoplist]
        new_inter[i] = ' '.join(tokens)
        tags = list(nltk.pos_tag(tokens))
        for tag in tags:
            poses.append(tag[1])
        for pos in poses:
            if 'NN' in pos:
                count += 1
        if count == 0:
            to_remove_fin.append(new_inter[i])
        if len(poses) > 4:
            to_remove_fin.append(new_inter[i])
    to_remove_fin = list(set(to_remove_fin))
    new_inter = list(set(new_inter).difference(to_remove_fin))
    return new_inter

author = []
abstract = []
year = []
language = []
with open('2_abs_translated.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        abstract.append(row["TRANSLATED_ABSTRACT"])
        year.append(row["YEAR"])
        author.append(row["AUTHOR"])
        language.append(row["LANGUAGE"])

df = pd.DataFrame(
    {'Abstract': abstract,
     'Year': year,
     'Author': author,
     'Language': language})

df.sort_values("Abstract", inplace=True)
df.drop_duplicates(subset="Abstract", keep='first', inplace=True)

with open('2_abs_keywords2013.csv', 'wb') as f:
    writer = csv2.writer(f)
    writer.writerow(["AUTHOR", "YEAR", "LANGUAGE", "TEXT", "KEYWORDS"])
    for i in range(0, df.shape[0]):
        if df.iloc[i]["Year"] == '2013':
            keywords = get_keywords(df.iloc[i]["Abstract"])
            print(i + 1)
            print(df.iloc[i]["Abstract"])
            print(keywords)
            writer.writerow([df.iloc[i]["Author"],
                             df.iloc[i]["Year"],
                             df.iloc[i]["Language"],
                             df.iloc[i]["Abstract"],
                             keywords])