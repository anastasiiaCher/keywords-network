import csv
import re
from yandex_translate import YandexTranslate


translate = YandexTranslate('trnsl.1.1.20190121T190126Z.4346c6134e91b324.8f82d3afe2601c8a0c5a8caa0d0b180fb27355a7')

interests = []
with open('authors.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        interests.append(row["Interests"])

keywords = []
for i in range(0, len(interests)):
    keywords.append(interests[i].split(','))

print("{:<5} {:<25} {:<10} {:<25}".format('#', 'KEYWORD', 'LANGUAGE', 'TRANSLATION'))

translated = []
step = 1
for i in range(0, len(keywords)):
    for k in range(0, len(keywords[i])):
        keywords[i][k] = re.sub("' | '", "", keywords[i][k])
        keywords[i][k] = keywords[i][k].replace("'", "")
        keywords[i][k] = keywords[i][k].replace('"', "")
        keywords[i][k] = keywords[i][k].replace("[", "")
        keywords[i][k] = keywords[i][k].replace("]", "")
        keywords[i][k] = keywords[i][k].lower().lstrip()
        language = translate.detect(keywords[i][k])
        if language != 'en':
            translation = translate.translate(keywords[i][k], 'en')
            print("{:<5} {:<25} {:<10} {:<25}".format(step,
                                                      keywords[i][k],
                                                      language,
                                                      translation['text'][0]))
            translated.append(translation['text'][0])
            step += 1
        else:
            translated.append(keywords[i][k])

with open('translated_keywords.csv', 'w', encoding="utf-8", newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_NONE)
    writer.writerow(['KEYWORD'])
    if translated != []:
        for i in translated:
            writer.writerow([i])