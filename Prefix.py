import re
from sets import Set

class Prefix(object):
	prefixRe = "([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})/([0-9]{1,2})"
	prefixFmt = "{}.{}.{}.{}/{}"

	# Given a prefix in string form, return its value and prefix length
	# value is read as bitwise little-endian for comparison reasons
	@staticmethod
	def parseStr(string):
		match = re.search(Prefix.prefixRe, string)
		val = 0
		for octet in xrange(4):
			remaining = int(match.group(octet))
			bit = 0
			while remaining:
				if remaining >= 2**(7-bit):
					val += 2**bit * 2**(8*octet)
				remaining -= 2**(7-bit)
				bit += 1

		length = int(match.group(4))

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
		return (self.value % 2**minLen) - (other.value % 2**minLen)

	def __str__(self):
		octets = []
		for octet in xrange(4):
			val = 0
			for bit in xrange(8):
				if self.value | (2**(8*octet + bit)):
					val += 2**(7 - bit)
			octets.append(val)

		return Prefix.prefixFmt.format(*octets, self.length)