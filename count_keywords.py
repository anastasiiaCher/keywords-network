import csv
from operator import itemgetter
import re
import unicodecsv as csv2

keywords = []
words = []
with open('2_translated_keywords.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        keywords.append(row["KEYWORD"].lower().split(','))

for i in range(0, len(keywords)):
    for k in range(0, len(keywords[i])):
        keywords[i][k] = re.sub("' | '|  ’| –", "", keywords[i][k])
        keywords[i][k] = keywords[i][k].replace("'", "")
        keywords[i][k] = keywords[i][k].replace('"', "")
        keywords[i][k] = keywords[i][k].replace("[", "")
        keywords[i][k] = keywords[i][k].replace("]", "")
        keywords[i][k] = keywords[i][k].replace(' ”', "")
        keywords[i][k] = keywords[i][k].replace('“ ', "")
        keywords[i][k] = keywords[i][k].replace(' ’', "")
        keywords[i][k] = keywords[i][k].replace(' — ', "")
        keywords[i][k] = keywords[i][k].replace(' )', "")
        keywords[i][k] = keywords[i][k].replace('( ', "")
        keywords[i][k] = keywords[i][k].replace(')', "")
        keywords[i][k] = keywords[i][k].replace('(', "")
        keywords[i][k] = keywords[i][k].replace('.', "")
        words.append(keywords[i][k])

print ('TOTAL: ', len(words))
print ('UNIQUE: ', len(set(words)))

count = [[x, words.count(x)] for x in set(words)]
count = sorted(count, key=itemgetter(1), reverse=True)

print ("{:<8} {:<50} {:<10}".format('#', 'KEYWORD', 'OCCURRENCES'))
with open('tally_keywords.csv', 'wb') as f:
    writer = csv2.writer(f)
    writer.writerow(["KEYWORD", "OCCURRENCES"])
    for i in range(0, len(set(words))):
        print ("{:<8} {:<50} {:<10}".format(i + 1, count[i][0], count[i][1]))
        writer.writerow([count[i][0], count[i][1]])