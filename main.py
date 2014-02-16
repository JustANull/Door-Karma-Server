from flask import Flask, request
from crossdomain import crossdomain
import db
import config
import json
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
        return json.dumps({'success': True})
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return json.dumps({'success': False})

@app.route('/fillKarma/<filluuid>/<uuid>/<name>/<platform>/<version>/<stoken>')
@crossdomain(origin='*')
def fillKarma(filluuid, uuid, name, platform, version, stoken):
    """complete a karma request row in the database and remove the karma from the active queue"""
    if stoken == secret:
        db.userFilled(filluuid, uuid, name, platform, version)
        del karmaTickets[uuid]
        return json.dumps({'success': True})
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return json.dumps({'success': False})

@app.route('/readyKarma/<uuid>/<name>/<stoken>')
@crossdomain(origin='*')
def readyKarma(uuid, name, stoken):
    if stoken == secret:
        karmaGivers[uuid]=name
        return json.dumps({'success': True})
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return json.dumps({'success': False})

@app.route('/unreadyKarma/<uuid>/<name>/<stoken>')
@crossdomain(origin='*')
def unreadayKarma(uuid, name, stoken):
    if stoken == secret:
        del karmaGivers[uuid]
        return json.dumps({'success': True})
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return json.dumps({'success': False})

@app.route('/userListKarma/<stoken>')
@crossdomain(origin='*')
def karmaTicketList(stoken):
    if stoken == secret:
        return json.dumps({'success': True, 'waiting': karmaTickets, 'ready': karmaGivers})
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return json.dumps({'success': False})

@app.route('/waitingPollKarma/<stoken>')
@crossdomain(origin='*')
def pollWaitingKarma(stoken):
    """these are the people who want karma, they need to know who is coming"""
    if stoken == secret:
        return json.dumps({'success': True})
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return json.dumps({'success': False})

@app.route('/readyPollKarma/<stoken>')
@crossdomain(origin='*')
def readyPoll(stoken):
    """these are the people that are ready to give karma, they get the list of people who want it"""
    if stoken == secret:
        return json.dumps({'success': True, 'waiting': karmaTickets})
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return json.dumps({'success': False})
        
@app.route('/messagePollKarma/<stoken>')
@crossdomain(origin='*')
def systemMessage(stoken):
    """this function is for sending system messages"""
    return sysMsg

@app.route('/killKarma/<name>/<uuid>/<stoken>')
@crossdomain(origin='*')
def killKarma(name, uuid):
    """pull the record out of the RAM table"""
    if stoken==secret:
        del karmaTickets[uuid]
        return json.dumps({'success': True})
    else:
        logging.warn("User {0} tried to get karma".format(name))
        return json.dumps({'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
