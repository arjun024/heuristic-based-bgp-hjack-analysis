import re
from sets import Set
from socket import inet_aton, inet_ntoa
from struct import pack, unpack

class Prefix(object):
	prefixRe = "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/([0-9]{1,2})"

	# Given a prefix in string form, return its value and prefix length
	@staticmethod
	def parseStr(string):
		match = re.search(Prefix.prefixRe, string)
		value = unpack("!I", inet_aton(match.group(1)))

		length = int(match.group(2))

		return value, length

	def __init__(self, prefix, asPath=None):
		value, length = Prefix.parseStr(prefix)
		self.value = value
		self.length = length
		self.announcements = {}
		if asPath:
			self.addAnnouncement(asPath)

	# Record an announcement of this prefix
	# Returns True if a new conflict is introduced
	def addAnnouncement(self, asPath):
		if asPath[-1] in self.announcements:
			self.announcements[asPath[-1]] = self.announcements[asPath[-1]].update(asPath)
		else:
			self.announcements[asPath[-1]] = Set(asPath)
			return len(self) > 1

		return False

	# withdraw an annouoncement of this prefix from 'origin'
	# returns the new number of announcing ASes
	def withdraw(self, origin):
		del self.announcements[origin]
		return len(self)

	# Merge two prefix objects with the same prefix into one
	# Returns True if a new conflict is introduced
	def merge(self, other):
		if self.value != other.value or self.length != other.length:
			raise AssertionError("Trying to merge two prefix objects with different prefixes")
		newConflict = False
		for origin in other.announcements:
			newConflict = newConflict or self.addAnnouncement(other.announcements[origin])
		return newConflict

	# length is defined as the number of ASes announcing this exact prefix
	def __len__(self):
		return len(self.announcements)

	# In order to detect competing announcements, two prefixes are
	# considered equal if one contains the other
	def __cmp__(self, other):
		minLen = min(self.length, other.length)
		return (self.value >> 2**minLen) - (other.value >> 2**minLen)

	def __str__(self):
		return inet_ntoa(pack("!I",self.value)) + '/' + str(self.length)
