import dublintraceroute
import pprint
import time
from py2neo import authenticate, Graph, Node, Relationship, NodeSelector, PropertyDict
from py2neo.ogm import *


# set up authentication parameters
authenticate("localhost:7474", "neo4j", "neo4j")

# connect to authenticated graph database
graph = Graph("http://localhost:7474/db/data/")

#graph.schema.create_uniqueness_constraint("Host","ip")

dest = '8.8.8.8'

dublin = dublintraceroute.DublinTraceroute(dest, npaths=3)
d = dublin.traceroute()
pprint.pprint(d)

tx = graph.begin()

# Test for and build Target Node
if graph.find_one("Target", "ip", dest) is not None:
    z = graph.find_one("Target", "ip", dest)
    z["last"] = time.time()
#    graph.push(z)
    tx.merge(z)
    print("found Target")
else:
    z = Node("Target", ip=dest, time=time.time())
    tx.merge(z)
    print("Target not found")

tx.commit()

# loop through each flow creating Nodes
for flow in d['flows'].keys():
    for hop, results in enumerate(d['flows'][flow]):
        tx = graph.begin()
        print(">"+'\n')
        print(d['flows'][flow][hop]['is_last'])
        if d['flows'][flow][hop]['received'] is not None:
            print(d['flows'][flow][hop]['flowhash'])
            print(d['flows'][flow][hop]['received']['ip']['src'])
            print(d['flows'][flow][hop]['sent']['ip']['ttl'])
            print(d['flows'][flow][hop]['received']['timestamp'])
            ip = d['flows'][flow][hop]['received']['ip']['src']
            if graph.find_one("Host", "ip", ip) is not None:
                a = graph.find_one("Host", "ip", ip)
                a["last"] = time.time()
                graph.push(a)
                print("found a")
            else:
                a = Node("Host", ip=ip, last=time.time())
                tx.merge(a)
                print("a not found")
# Build paths to dest with hop
        if d['flows'][flow][hop]['received'] is not None:
            az = Relationship(a, "PATH", z)
            az["hop"] = d['flows'][flow][hop]['sent']['ip']['ttl']
            print(tx.exists(az))
            print(az)
            tx.merge(az)
        tx.commit()

# Build Connections
        tx = graph.begin()
        if hop > 0:
            if d['flows'][flow][hop]['received'] is not None:
                if d['flows'][flow][(hop-1)]['received'] is not None:
                    ip = d['flows'][flow][(hop-1)]['received']['ip']['src']
                    if graph.find_one("Host", "ip", ip) is not None:
                        b = graph.find_one("Host", "ip", ip)
                        print("found b")
                    else:
                        print("build b")
                        b = Node("Host", ip=ip)
    #
                    print(a)
                    print(b)
    #
                    ba = Relationship(b, "Link", a)
                    print(tx.exists(ba))
                    print(ba)
                    tx.merge(ba)
        tx.commit()

#    print(results['flows'][flow][2])
#    pprint.pprint(d['flows'][code])
