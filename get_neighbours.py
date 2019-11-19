import networkx as nx
import operator


G = nx.read_gexf("network2013.gexf",
                 node_type = None, relabel = False, version = '1.2draft')

neighs = G.neighbors("digital journalism")
print ("Neighbours of GIS node:")
nodes = []
for n in neighs:
    if n in G:
        betweenness = nx.get_node_attributes(G, 'degree')
        nodes.append([n, betweenness[n]])

nodes.sort(key=operator.itemgetter(1), reverse=True)
for n in range(0, len(nodes)):
    print (n+1, nodes[n][0], G['digital journalism'][nodes[n][0]]['weight'])

