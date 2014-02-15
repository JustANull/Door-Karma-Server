import logging
import MySQLdb

logging.basicConfig(level=logging.DEBUG)

#I do not claim to write beautiful code
def fixFormatString(fmt):
	final = ""
	inc = 0
	for part in fmt.split('%s'):
		final += part + '\'{' + str(inc) + '}\''
		inc += 1
	return final[:-len(str('\'{'+str(inc - 1)+'}\''))]

#Michael has signed off on not sanitizing inputs
class DoorKarmaDatabase:
	def __init__(self, host, username, password, dbname, tablename):
		logging.info("Initializing database connection")
		try:
			self.db = MySQLdb.connect(host, username, password, dbname)
			logging.debug("Connected; Acquiring cursor")
			self.cur = self.db.cursor()
			logging.debug("Selecting database...")
			self.cur.execute("USE {0};".format(dbname))
			logging.debug("Successfully selected")
		except MySQLdb.OperationalError, e:
			logging.critical("Database error: {0}".format(str(e)))
			raise e
		self.tablename = tablename
		self.fromnameToID = dict()

	def userRequest(self, fromname, submitterPlatform, submitterVersion):
		logging.info("User {0} ({1}::{2}) requested".format(
			fromname, submitterPlatform, submitterVersion))
		cmd = "INSERT INTO " + self.tablename + " (rFrom, platSubType, platSubVer) VALUES(%s, %s, %s);"
		try:
			logging.debug("About to execute \n{0}".format(fixFormatString(cmd).format(fromname, submitterPlatform, submitterVersion)))
			self.cur.execute(cmd, (fromname, submitterPlatform, submitterVersion))
			logging.debug("Successfully executed; Committing")
			self.db.commit()
			logging.debug("Committed")
		except MySQLdb.OperationalError, e:
			logging.debug("Commit failed; Rolling back")
			self.db.rollback()
			logging.critical("Database error: {0}".format(str(e)))
			raise e
		self.fromnameToID[fromname] = self.db.insert_id()

	def userFilled(self, fromname, byname, fillerPlatform, fillerVersion):
		#WARNING: PROVIDE PROPER COLUMN NAMES
		cmd = "UPDATE " + self.tablename + " SET rFill=%s, tFill=%s, platFillType=%s, platFillVer=%s WHERE eventNumber=%s;"
		try:
			logging.debug("About to execute \"{0}\"".format(fixFormatString(cmd).format(byname, time.time(), fillerPlatform, fillerVersion, self.fromnameToID[fromname])))
			self.cur.execute(cmd, (byname, time.time(), fillerPlatform, fillerVersion, self.fromnameToID[fromname]))
		except MySQLdb.OperationalError, e:
			logging.critical("Database error: {0}".format(str(e)))
			raise e

if __name__ == "__main__":
	obj = None
	try:
		obj = DoorKarmaDatabase("enterprise.local", "santiago", "cole", "doorKarma", "events")
		#obj.cur.execute('INSERT INTO events (rFrom, platSubType, platSubVer) VALUES("Michael Aldridge", "OSX", "whocares");')
		obj.userRequest("Michael Aldridge", "OSX", "whocares")
	except Exception, e:
		obj.db.close()
		raise e
