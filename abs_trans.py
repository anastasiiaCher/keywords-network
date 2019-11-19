import csv
import unicodecsv as csv2
from yandex_translate import YandexTranslate


translate = YandexTranslate('trnsl.1.1.20190121T190126Z.4346c6134e91b324.8f82d3afe2601c8a0c5a8caa0d0b180fb27355a7')

abstracts = []
titles = []
years = []
authors = []
with open('2_pubs2013.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        years.append(row["YEAR"])
        authors.append((row["AUTHOR"]))
        titles.append(row["TITLE"])
        abstracts.append(row["ABSTRACT"])

texts = []
for i in range(0, len(titles)):
    content = titles[i] + '. ' + abstracts[i]
    texts.append(content)

step = 1
translated = []
with open('2_abs_translated.csv', 'wb') as f:
    writer = csv2.writer(f)
    writer.writerow(["AUTHOR", "YEAR", "LANGUAGE", "ABSTRACT", "TRANSLATED_ABSTRACT"])
    for text in range(0, len(texts)):
        language = translate.detect(texts[text])
        if language != 'en':
            translation = translate.translate(texts[text], 'en')
            print(step, '\n',
                  'ABSTRACT: ', texts[text], '\n',
                  'LANGUAGE: ', language, '\n',
                  'TRANSLATION: ',translation['text'][0])
            writer.writerow([authors[text], years[text], language,
                             texts[text], translation['text'][0]])
        else:
            print(step, '\n',
                  'ABSTRACT: ', texts[text], '\n',
                  'LANGUAGE: ', language)
            writer.writerow([authors[text], years[text], language,
                             texts[text], texts[text]])
        step += 1




