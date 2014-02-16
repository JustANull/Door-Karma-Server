from flask import Flask, request
from crossdomain import crossdomain
import db
import config
import logging

logging.basicConfig(level=logging.DEBUG)

conf = config.getConfig()

app = Flask(__name__)
db = db.DoorKarmaDatabase(conf["db"]["host"], conf["db"]["user"], conf["db"]["pass"], conf["db"]["db"], conf["db"]["table"])
secret=conf["karmaServer"]["secret"]

karmaTickets = {}
karmaGivers = {}

sysMsg = "you got the sysMsg, prepare to be delta'd"

@app.route('/')
@crossdomain(origin='*')
def hello_world():
    logging.debug("someone called hello world")
    return 'Hello World!'

@app.route('/requestKarma/<uuid>/<name>/<platform>/<version>/<stoken>')
@crossdomain(origin='*')
def requestKarma(uuid, platform, version, name, stoken):
    """request karma from the server"""
    if stoken == secret:
        logging.debug("attempting to request karma for {0}".format(name))
        db.userRequest(uuid, name, platform, version)
        karmaTickets[uuid]=name
        logging.info("Karma requested for {0}".format(name))
        return "KARMA IN QUEUE"
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return "NOT AUTHORIZED"

@app.route('/fillKarma/<filluuid>/<uuid>/<name>/<platform>/<version>/<stoken>')
@crossdomain(origin='*')
def fillKarma(filluuid, uuid, name, platform, version, stoken):
    """complete a karma request row in the database and remove the karma from the active queue"""
    if stoken == secret:
        logging.debug("{0} is trying to fill {1}'s door karma".format(filluuid, uuid))
        db.userFilled(filluuid, uuid, name, platform, version)
        del karmaTickets[uuid]
        logging.info("Door karma filled by {0}".format(name))
        return "karma filled"
    else:
        logging.warn("User {0} tried to fill karma".format(name))
        return "NOT AUTHORIZED"

@app.route('/readyKarma/<uuid>/<name>/<stoken>')
@crossdomain(origin='*')
def readyKarma(uuid, name, stoken):
    if stoken == secret:
        karmaGivers[uuid]=name
        logging.info("{0} checked in to provide door karma.".format(name))
        return "karma engaged"
    else:
        logging.warn("User {0} tried to provide karma".format(name))
        return "NOT AUTHORIZED"

@app.route('/unreadyKarma/<uuid>/<name>/<stoken>')
@crossdomain(origin='*')
def unreadayKarma(uuid, name, stoken):
    if stoken == secret:
        del karmaGivers[uuid]
        logging.info("{0} asked for the karma giver's list".format(name))
        return "your heart is coal"
    else:
        logging.warn("User {0} tried to not provide karma".format(name))
        return "NOT AUTHORIZED"

@app.route('/userListKarma/<stoken>')
@crossdomain(origin='*')
def karmaTicketList(stoken):
    """the people who provide karma need to know who wants it"""
    if stoken == secret:
        logging.info("{0} asked for the list of karma recipients".format(name))
        return str(karmaTickets) + " " + str(karmaGivers)
    else:
        logging.warn("User {0} tried to list karma requests".format(name))
        return "NOT AUTHORIZED"

@app.route('/waitingPollKarma/<stoken>')
@crossdomain(origin='*')
def pollWaitingKarma(stoken):
    """these are the people who want karma, they need to know who is coming"""
    if stoken == secret:
        logging.info("Someone outside asked if anyone was coming.")
        return "someone is coming"
    else:
        logging.warn("User {0} tried to get karma givers list".format(name))
        return "NOT AUTHORIZED"

@app.route('/readyPollKarma/<stoken>')
@crossdomain(origin='*')
def readyPoll(stoken):
    """these are the people that are ready to give karma, they get the list of people who want it"""
    if stoken == secret:
        logging.info("Karma giver wanted an update on possible recipients")
        return str(karmaTickets)
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return "NOT AUTHORIZED"
        
@app.route('/messagePollKarma/<stoken>')
@crossdomain(origin='*')
def systemMessage(stoken):
    """this function is for sending system messages"""
    logging.info("The system message was sent")
    return sysMsg

@app.route('/killKarma/<name>/<uuid>/<stoken>')
@crossdomain(origin='*')
def killKarma(name, uuid):
    """pull the record out of the RAM table"""
    if stoken==secret:
        logging.info("Removing {0} from the karma request list".format(name))
        del karmaTickets[uuid]
        return "ticket removed"
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return "NOT AUTHORIZED"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
