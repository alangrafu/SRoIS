from bottle import response, request
import commands
import socket
import re
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib import URIRef, Literal


appPort=15151
host = "http://%s:%d/" % (str(socket.gethostname()), appPort)
hostUri = host+"host"

## Needs to be improved
def __serialization(g=None):
  if g is None:
    return ""
  return g.serialize(format="n3")

#Gets what type of service this process is running
def __getServiceType(pid=0, g=None):
  if pid > 0 or g is None:
    return
  ##Add triples to the graph
  ##For example, that URI for that PID is of rdf:type :SparqlEndpoint
  return


app = bottle.app()
app.debug=True
@app.route('/services')
def sohowServices():
    g = Graph()
    S = Namespace("http://tw.rpi.edu/srs/")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
    result = commands.getoutput('netstat -tnap|egrep "LISTEN"')
    table = (result.split("\n"))[1:]
    for row in table:
      pairPidProcess = re.search('\d+\/\w+', str(row))
      processPortMatch = re.search('\d+\.\d+\.\d+\.\d+:\d+', str(row))
      if processPortMatch != None:
        processPort = ''.join(str(processPortMatch.group(0)).split(":")[1:])
        processPid, processName = str(pairPidProcess.group(0)).split("/")
        serviceUri = host+"pid/"+processPid
        g.add((URIRef(serviceUri), RDF['type'], S['Service']))
        g.add((URIRef(serviceUri), S['runningPort'], Literal(processPort, datatype=XSD['integer'])))
        g.add((URIRef(serviceUri), S['runningHost'], URIRef(hostUri)))
        __getServiceType(processPid, g)

    response.content_type = 'text/turtle'
    g.add((URIRef(hostUri), RDF['type'], S['Host']))
    return __serialization(g)

bottle.run(app=app,host='0.0.0.0',port=appPort)
