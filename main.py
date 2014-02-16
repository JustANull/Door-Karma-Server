from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer

def adder(a,b):
    "Add two values"
    return a+b

def letmein(user, door, reason):
    "test function to let people in"
    return "I'll let in " + user + " at the " + door + " because " + reason

dispatcher = SoapDispatcher(
    'my_dispatcher',
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/', # SOAPAction
    namespace = "http://example.com/sample.wsdl", prefix="ns0",
    trace = True,
    ns = True)

# register the user function
dispatcher.register_function('Adder', adder,
                             returns={'AddResult': int}, 
                             args={'a': int,'b': int})

dispatcher.register_function('letmein', letmein,
                             returns={'UberString':str},
                             args={'user':str, 'door':str, 'reason':str});

print "Starting server..."
httpd = HTTPServer(("", 8008), SOAPHandler)
httpd.dispatcher = dispatcher
httpd.serve_forever()
