import apnsclient
import gcmclient
import logging

class PhoneType:
	Android, Apple = range(2)

class PushServer:
	def __init__(self, apnsKey, gcmKey):
		self.apnsClients = list()
		self.gcmClients = list()
		logging.info("Initializing GCM client")
		self.gcm = gcmclient.GCM(gcmKey)
		logging.info("No APNS client supported")
		#self.apnsSession = apnsclient.Session()
		#self.apns = self.apnsSession.get_connection("push_sandbox", cert_file = apnsKey)

	def broadcast(self, val):
		logging.info("Broadcasting {0}".format(val))
		try:
			logging.debug("Sending GCM messages")
			gcmResults = self.gcm.send(gcmclient.JSONMessage(self.gcmClients, {'data': val}))
		except gcmclient.GCMAuthenticationError, e:
			logging.critical("Unable to auth with GCM")
			raise e
		logging.debug("APNS unsupported; Here we would send APNS")
		#apnsResults = apnsclient.APNs(self.apns).send(apnsclient.Message(self.apnsClients, alert = val))

	#Michael tells me I can assume phoneType will be a member of the class PhoneType
	def registerClient(self, phoneType, UUID):
		if phoneType == PhoneType.Android:
			if self.gcmClients.count(UUID) == 0:
				self.gcmClients.append(UUID)
		elif phoneType == PhoneType.Apple:
			if self.apnsClients.count(UUID) == 0:
				self.apnsClients.append(UUID)

	def unregisterClient(self, phoneType, UUID):
		if phoneType == PhoneType.Android:
			if self.gcmClients.count(UUID) > 0:
				self.gcmClients.remove(UUID)
		elif phoneType == PhoneType.Apple:
			if self.apnsClients.count(UUID) > 0:
				self.apnsClients.remove(UUID)
