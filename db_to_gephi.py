import csv, sqlite3
import networkx as nx
from operator import itemgetter
import unicodecsv as csv2
import pandas as pd
import community


con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("CREATE TABLE texts (text, text_id);")
cur.execute("CREATE TABLE keywords (word, text_id);")


texts = []
words = []

with open('2_abs_keywords2013.csv','r', encoding='utf-8') as fin:
    dr = csv.DictReader(fin)
    for row in dr:
        words.append(row["KEYWORDS"])
        texts.append(row["TEXT"])


texts_fin = []
for i in range(0,len(texts)-1):
    texts_fin.append((texts[i], 'text' + str(i)))

list_of_int =[]
ks = []
for i in range(0, len(words)-1):
    words[i] = words[i].lower()
    words[i] = words[i].split(',')
    for k in words[i]:
        k = k.replace(" '", "")
        k = k.replace("['", "")
        k = k.replace("']", "")
        k = k.replace("'", "")
        ks.append(k)
    list_of_int.append(ks)
    ks = []

words_fin = []
for i in range(0,len(list_of_int)):
    for word in list_of_int[i]:
        words_fin.append((word, 'text' + str(i)))


cur.executemany("INSERT INTO texts (text, text_id) "
                "VALUES (?, ?);",
                texts_fin)
cur.executemany("INSERT INTO keywords (word, text_id) "
                "VALUES (?, ?);",
                words_fin)
con.commit()
sql1 = "SELECT word, " \
       "COUNT(word) AS cnt " \
       "FROM keywords " \
       "GROUP BY word " \
       "ORDER BY cnt " \
       "DESC;"
cur.execute(sql1)
to_print = cur.fetchall()
uniq_words = []
pairs = []
for row in to_print:
    uniq_words.append(row[0])

sql2 = "SELECT a.word a, b.word b, " \
       "COUNT(*) cnt " \
       "FROM keywords a " \
       "JOIN keywords b " \
       "ON b.text_id = a.text_id AND b.word > a.word " \
       "GROUP BY a.word, b.word " \
       "ORDER BY cnt " \
       "DESC;"
cur.execute(sql2)
occ = cur.fetchall()

pairs = []
weighted = []

for row in occ:
    pairs.append((row[0], row[1]))
    weighted.append((row[0], row[1], row[2]))

lables = ['point1', 'point2', 'count']
nodes_df = pd.DataFrame.from_records(weighted, columns=lables)

G = nx.Graph()
G.add_weighted_edges_from(weighted)
G.remove_node("digital humanities")
node_and_degree = G.degree()
(largest_hub, degree) = sorted(node_and_degree, key=itemgetter(1))[-1]

hub_ego = nx.ego_graph(G, largest_hub)

print (nx.info(G))
density = nx.density(G)
print("Network density:", density)
if nx.is_connected(G):
    print("Connectivity: True")
    print("Network diameter: ", nx.diameter(G))
else:
    print("Connectivity: False")
triadic_closure = nx.transitivity(G)
print("Triadic closure (transitivity):", triadic_closure)

degree_dict = dict(G.degree(G.nodes()))
nx.set_node_attributes(G, degree_dict, 'degree')
sorted_degree = sorted(degree_dict.items(), key=itemgetter(1), reverse=True)
print("Top 25 nodes by degree:")
for d in sorted_degree[:25]:
    print(d)

print ("Node Connectivity: ", nx.node_connectivity(G))
print ("K-component Structure: ", nx.k_components(G))

print("To centrality...")

print("Calculating betweenness centrality...")
betweenness_dict = nx.betweenness_centrality(G, normalized=True)

print("Calculating eigenvector centrality...")
eigenvector_dict = nx.eigenvector_centrality(G)

print("Betweenness centrality...")
nx.set_node_attributes(G, betweenness_dict, 'betweenness')
print("Eigenvector centrality...")
nx.set_node_attributes(G, eigenvector_dict, 'eigenvector')
print("Sorting betweenness...")
sorted_betweenness = sorted(betweenness_dict.items(), key=itemgetter(1), reverse=True)
sorted_eigenvector = sorted(eigenvector_dict.items(), key=itemgetter(1), reverse=True)

print("Top 25 nodes by betweenness centrality:")
for b in sorted_betweenness[:25]:
    print(b)

print("Top 25 nodes by eigenvector centrality:")
for b in sorted_eigenvector[:25]:
    print(b)

communities = community.best_partition(G)

print (community.modularity(communities, G))

nx.set_node_attributes(G, communities, 'modularity')
class0 = [n for n in G.nodes() if G.node[n]['modularity'] == 1]
class0_betw = {n:G.node[n]['betweenness'] for n in class0}
class0_sorted_by_betw = sorted(class0_betw.items(), key=itemgetter(1), reverse=True)
print("Modularity Class 0 Sorted by betweenness Centrality:")
for node in class0_sorted_by_betw[:5]:
    print("Name:", node[0], "| Betweenness Centrality:", node[1])

class0_eig = {n:G.node[n]['eigenvector'] for n in class0}
class0_sorted_by_eigenvector = sorted(class0_eig.items(), key=itemgetter(1), reverse=True)
print("Modularity Class 0 Sorted by Eigenvector Centrality:")
for node in class0_sorted_by_eigenvector[:5]:
    print("Name:", node[0], "| Eigenvector Centrality:", node[1])

class0_deg = {n:G.node[n]['degree'] for n in class0}
class0_sorted_by_deg = sorted(class0_deg.items(), key=itemgetter(1), reverse=True)
print("Modularity Class 0 Sorted by Degree Centrality:")
for node in class0_sorted_by_eigenvector[:5]:
    print("Name:", node[0], "| Degree Centrality:", node[1])

modularity = {}
for k,v in communities.items():
    if v not in modularity:
        modularity[v] = [k]
    else:
        modularity[v].append(k)

with open('clusters.csv', 'wb') as f:
    writer = csv2.writer(f)
    writer.writerow(["CLUSTER", "NUM OF KWORDS", "KEYWORDS"])
    for k, v in modularity.items():
        if len(v) > 9:
            writer.writerow([str(k), len(v), v])

nx.write_gexf(G, 'network2013.gexf')

cur.close()
con.close()
