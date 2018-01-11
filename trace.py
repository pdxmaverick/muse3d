import dublintraceroute
import pprint
from py2neo import authenticate, Graph, Node, Relationship, NodeSelector, PropertyDict
from py2neo.ogm import *


# set up authentication parameters
authenticate("localhost:7474", "neo4j", "P0rsch3")

# connect to authenticated graph database
graph = Graph("http://localhost:7474/db/data/")

# graph.schema.create_uniqueness_constraint("host","ip")

#class Host(GraphObject):
#    __primarykey__ = "ip"
#    ip = Property()
#    last = Property()
#    ttl = Property()
#    path = RelatedTo("Host")


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
            ip = d['flows'][flow][hop]['received']['ip']['src']
            ttl = d['flows'][flow][hop]['sent']['ip']['ttl']
            last = d['flows'][flow][hop]['received']['timestamp']
            a = Node("Host", ip=ip, ttl=ttl, last=last)
            a.__primarykey__ = a[ip]

            tx.merge(a)
        if d['flows'][flow][hop]['is_last'] is False:
            if d['flows'][flow][hop]['received'] is not None:
                if d['flows'][flow][(hop+1)]['received'] is not None:
                    ip = d['flows'][flow][(hop+1)]['received']['ip']['src']
                    b = Node("Host", ip=ip)
                    b.__primarykey__ = b[ip]
#                    a.path = d['flows'][flow][(hop+1)]['received']['ip']['src']
                    print(a)
                    print(b)
#                    tx.merge(a)
#                    b.path = a
#                    graph.push(b)
#                    tx.create(ba)

            ab = Relationship(a, "PATH", b)
            print(ab)
            tx.merge(ab)
tx.commit()

#    print(results['flows'][flow][2])
#    pprint.pprint(d['flows'][code])
