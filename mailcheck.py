#!/usr/bin/python

import imaplib

class mailMsg():
	def __init__(self, data):
		lines = data.splitlines()
		n = len(lines)

		self.Received = []

		# Process header
		i = 0
		while i < n:
			l = lines[i]
			if l[:9] == 'Received:':
				rcv = []
				rcv.append(l[10:])
				inew = i
				while True:
					inew += 1
					lsub = lines[inew]

					if lsub[0] == '\t':
						rcv.append(lsub[1:])
					else:
						break
				i = inew - 1

				self.Received.append(rcv)

			if l[:5] == 'From:':
				self.From = l[6:]

			if l[:3] == 'To:':
				self.To = l[4:]

			if l[:8] == 'Subject:':
				self.Subject = l[9:]

			if l[:7] == 'Sender:':
				self.Sender = l[8:]

			if l[:13] == 'Content-Type:':
				self.Content_Type = l[14:].split(';')[0]
				if self.Content_Type.find('multipart') == -1:
					self.multipart = False
				else:
					self.multipart = True
					self.boundary = lines[i + 1].split('"')[1]

			# End of header, start of body(s)
			if l == '':
				break

			
			i += 1

		if self.multipart:
			dataparts = data.split('--' + self.boundary)[1:-1]
			self.body = []
			for part in dataparts:
				self.body.append(mailBody(part))
		else:
			i += 1
			body = ''
			while i < n:
				body += lines[i] + '\r\n'
				i += 1

			self.body = [mailBody(body)]
			
class mailBody():
	def __init__(self, text):
		self.text = text

class mailUser():
	
	def __init__(self, username, password, server, address, ssl = True):
		self.username = username
		self.password = password
		self.host = server
		self.address = address
		self.ssl = ssl
		self.connected = False

	def connect(self):

		if self.ssl:
			self.imap = imaplib.IMAP4_SSL(self.host)			
			
		else:
			self.imap = imaplib.IMAP4(self.host)

		self.imap.login(self.username, self.password)

		self.connected = True

	def getlast(self):
		
		if not(self.connected):
			self.connect()

		mcount = int(self.imap.select()[1][0])

		status, data = self.imap.fetch(mcount, '(RFC822)')

		msgdata = data[0][1]

		return mailMsg(msgdata)
