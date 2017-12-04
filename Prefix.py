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
		try:
			val = unpack("!I", inet_aton(match.group(1)))[0]
		except AttributeError:
			raise ValueError(string + " does not match an IP address")

		lengthVal = int(match.group(2))

		return val, lengthVal

	def __init__(self, prefix, asPath=None):
		val, lengthVal = Prefix.parseStr(prefix)
		self.val = val
		self.lengthVal = lengthVal
		self.announcements = []
		if asPath:
			path = []
			for step in asPath.split(" "):
				match = re.search('[0-9]+', step)
				path.append(int(match.group(0)))
			self.addAnnouncement(path)

	# Record an announcement of this prefix
	# Returns True if a new conflict is introduced
	def addAnnouncement(self, asPath):
		# return False by default=
		ret = False

		origin = ASTreeNode(asPath[-1])
		for root in self.announcements:
			if origin == root:
				current = root
				break
		else:
			if len(self.announcements) > 0:
				# A new conflict is introduced, so True will be returned
				ret = True
			self.announcements.append(origin)
			current = origin

		# if the first AS on the path is repeated, traffic engineering is being used,
		# so start the path at the last occurance of the origin
		index = asPath.index(asPath[-1])

		while index >= 0:
			step = ASTreeNode(asPath[index])
			for child in current.children:
				if step == child:
					current = child
					break
			else:
				current.children.append(step)
			index -= 1

		return ret

	# Recursively merge announcement forests
	# Returns True if a new conflict is introduced
	def mergeTrees(self, forest):
		# Return False by default
		ret = False

		for newChild in forest:
			for destChild in self.announcements:
				if destChild == newChild:
					Prefix.mergeNodes(destChild, newChild)
					break
			else:
				# If the new forest has a new origin, a conflict is
				# introduced, so return True
				ret = True
				self.announcements.append(newChild)

		return ret

	# Helper function for mergeTrees
	# information from newNode is added to destNode
	@staticmethod
	def mergeNodes(destNode, newNode):
		for newChild in newNode.children:
			for destChild in destNode.children:
				if destChild == newChild:
					Prefix.mergeNodes(destChild, newChild)
					break
			else:
				destNode.children.append(newChild)

	# withdraw an annouoncement of this prefix from 'origin'
	# returns the new number of announcing ASes
	def withdraw(self, origin):
		for root in self.announcements:
			if root == origin:
				self.announcements.remove(origin)
		return len(self)

	# Merge two prefix objects with the same prefix into one
	# Returns True if a new conflict is introduced
	def merge(self, other):
		if self.value() != other.value() or self.length() != other.length():
			raise AssertionError("Trying to merge two prefix objects with different prefixes")
		return self.mergeTrees(other.announcements)

	# getter for self.value
	def value(self):
		return self.val

	# getter for self.length
	def length(self):
		return self.lengthVal

	# length is defined as the number of ASes announcing this exact prefix
	def __len__(self):
		return len(self.announcements)

	# In order to detect competing announcements, two prefixes are
	# considered equal if one contains the other
	def __cmp__(self, other):
		minLen = min(self.length(), other.length())
		return (self.value() >> (32-minLen)) - (other.value() >> (32-minLen))

	def __str__(self):
		return inet_ntoa(pack("!I", self.value())) + '/' + str(self.length())

class ASTreeNode(object):
	def __init__(self, AS):
		self.AS = AS
		self.children = []
		# This field is manipulated by the analyzer if it believes this corresponds to a hijack
		# Initially set to False
		self.is_a_hijack = False

	def __cmp__(self, other):
		try:
			return int(self.AS) - int(other.AS)
		except AttributeError:
			return int(self.AS) - int(other)

	def __str__(self):
		return str(self.AS)