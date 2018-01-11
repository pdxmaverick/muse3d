import dublintraceroute
import pprint
from py2neo import authenticate, Graph, Node, Relationship, NodeSelector, PropertyDict
from py2neo.ogm import *


# set up authentication parameters
authenticate("localhost:7474", "neo4j", "P0rsch3")

# connect to authenticated graph database
graph = Graph("http://localhost:7474/db/data/")

#graph.schema.create_uniqueness_constraint("host","ip")

class Host(GraphObject):
    __primarykey__ = "ip"
    ip = Property()
    last = Property()
    ttl = Property()
    path = RelatedTo("Host")


dublin = dublintraceroute.DublinTraceroute('8.8.8.8', npaths=1)
d = dublin.traceroute()

pprint.pprint(d)

tx = graph.begin()

for flow in d['flows'].keys():
    for hop, results in enumerate(d['flows'][flow]):
        print(">"+'\n')
        print(d['flows'][flow][hop]['is_last'])
        if d['flows'][flow][hop]['received'] is not None:
            print(d['flows'][flow][hop]['flowhash'])
            print(d['flows'][flow][hop]['received']['ip']['src'])
            print(d['flows'][flow][hop]['sent']['ip']['ttl'])
            print(d['flows'][flow][hop]['received']['timestamp'])
            a = Host()
            a.ip = d['flows'][flow][hop]['received']['ip']['src']
            a.ttl = d['flows'][flow][hop]['sent']['ip']['ttl']
            a.last = d['flows'][flow][hop]['received']['timestamp']
            tx.merge(a)
        if d['flows'][flow][hop]['is_last'] is False:
            if d['flows'][flow][hop]['received'] is not None:
                if d['flows'][flow][(hop+1)]['received'] is not None:
                    a.path = d['flows'][flow][(hop+1)]['received']['ip']['src']
                    print(a.ip)
                    print(a.path)
                    tx.merge(a)
#                    b.path = a
#                    graph.push(b)
#                    tx.create(ba)

#            ab = Relationship(a, "KNOWS", b)
#            tx.create(ab)
tx.commit()

#    print(results['flows'][flow][2])
#    pprint.pprint(d['flows'][code])
