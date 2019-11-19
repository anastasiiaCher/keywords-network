import scholarly
import unicodecsv as csv


search_query = scholarly.search_keyword('digital_humanities')

step = 0
with open('authors.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Interests'])
    if search_query != []:
        for i in search_query:
            writer.writerow([i.name, i.interests])
            step += 1
            print (step, i.name, '\n', i.interests)






