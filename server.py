import bottle
from bottle import response
import commands
import socket
import re
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib import URIRef, Literal


appPort=15151
host = "http://%s:%d/" % (str(socket.gethostname()), appPort)
hostUri = host+"host"

app = bottle.app()
app.debug=True
@app.route('/services')
def sohowServices():
    g = Graph()
    EX = Namespace("http://example.org/")
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
        g.add((URIRef(serviceUri), RDF['type'], EX['Service']))
        g.add((URIRef(serviceUri), EX['runningPort'], Literal(processPort, datatype=XSD['integer'])))
        g.add((URIRef(serviceUri), EX['runningHost'], URIRef(hostUri)))

    response.content_type = 'text/turtle'
    g.add((URIRef(hostUri), RDF['type'], EX['Host']))
    return g.serialize(format="n3")

bottle.run(app=app,host='0.0.0.0',port=appPort)
