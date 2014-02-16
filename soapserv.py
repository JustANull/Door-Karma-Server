from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer
import db
import logging

class SOAPServer:
    def __init__(self, dbhost, dbusername, dbpassword, dbname, dbtablename, soapPort, soapLoc, soapAct, soapName, securekey):
        """init a database connection in the server's namespace"""
        logging.info("Opening connection to the database")
        self.db = db.DoorKarmaDatabase(dbhost, dbusername, dbpassword, dbname, dbtablename)
        logging.info("Database connection open")
        self.soapPort = soapPort
        self.soapLoc = soapLoc
        self.soapAct = soapAct
        self.soapName = soapName
        self.secureKey = securekey
        self.usersAvail={}
        
        self.DoorMan = SoapDispatcher(
            'DoorMan',
            location = self.soapLoc,
            action = self.soapAct,
            namespace = self.soapName,
            prefix="ns0",
            trace = True,
            ns = True)
        
        # register the user function
        self.DoorMan.register_function('letmein', self.letmein,
                                     returns={'UberString':str},
                                     args={'user':str, 'door':str, 'reason':str});
        

    def letmein(user, door, reason):
        "test function to let people in"
        return "I'll let in " + user + " at the " + door + " because " + reason
    
    def needKarma(name, platform, version, UUID, key):
        "put the request into the database, and push the notification out to the lounge"
        logging.info("{0} wants in!".format(name))
        self.db.userRequest(name, platform, version, UUID)
        return True
        

    def cancelKarma(name, UUID, key):
        """remove the karma request"""
        return True

    def fillKarma(fillfor, name, platform, version, UUID, key):
        """fill in the database entry and remove the request from the active RAM table"""
        self.db.userFilled(fillfor, name, platform, UUID, key)
        return True

    def checkin(platform, UUID, key):
        """add a user to the push list and send messages to them"""
        del self.usersAvail[UUID]
        return True

    def checkout(UUID, key):
        """remove a user from the push list and stop sending messages to them"""
        self.usersAvail.remove(UUID)
        return True

    def karmaWaiting():
        """return true if there is a person who has requested karma"""
        return True

    def beginServe(self):
        print "Starting server..."
        self.httpd = HTTPServer(("", 8008), SOAPHandler)
        self.httpd.dispatcher = self.DoorMan
        self.httpd.serve_forever()

if __name__ == "__main__":
    theserver = SOAPServer("enterprise.local", "santiago", "cole", "doorKarma", "events", 8008, "http://localhost:8008/", "http://localhost:8008/", "http://foo/", "pass")
    theserver.beginServe()
