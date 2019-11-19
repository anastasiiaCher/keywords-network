import scholarly
import csv
import unicodecsv as csv2

step = 0
names = []
names2 = []
with open('authors.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        names.append(row["Name"])


with open('pubs2013.csv', 'wb') as f:
    writer = csv2.writer(f)
    writer.writerow(['AUTHOR', 'YEAR', 'TITLE', 'ABSTRACT'])
    for name in names:
        search_query = scholarly.search_author(name)
        for author in search_query:
            for interest in author.interests:
                if interest.lower() == 'digital humanities':
                    author = author.fill()
                    pubs = [pub.bib['title'] for pub in author.publications]
                    step += 1
                    step2 = 0
                    print(step, author.name)
                    for pub in author.publications:
                        if 'year' in list(pub.bib.keys()):
                            if pub.bib['year'] == 2013:
                                step2 += 1
                                pub_title = pub.fill().bib['title']
                                search_pub = scholarly.search_pubs_query(pub_title)
                                pub_info = next(search_pub)
                                if 'abstract' in list(pub_info.bib.keys()):
                                    print ("{:<5} {:<70}".format(step2,  pub_info.bib['title']))
                                    print ('ABSTRACT', '\n', pub_info.bib['abstract'])
                                    writer.writerow([name,
                                                     pub.bib['year'],
                                                     pub_info.bib['title'],
                                                     pub_info.bib['abstract']])