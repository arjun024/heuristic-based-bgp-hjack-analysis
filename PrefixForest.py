import bisect, re
from Prefix import Prefix
from pprint import pformat

class PrefixForest(object):
	def __init__(self):
		# array of PrefixNodes
		self.roots = []
		self.size = 0

	# wraps insert for inserting unsanitized BGPStream data
	def unsanitizedInsert(self, element):
		try:
			Prefix.parseStr(element.fields['prefix'])
		except ValueError:
			return False
		asPath = element.fields['as-path']
		path = []
		if asPath:
			for step in asPath.split(" "):
				match = re.search('[0-9]+', step)
				path.append(int(match.group(0)))
		prefix = Prefix(element.fields['prefix'], path)
		return self.insert(prefix)

	# Returns True if a new conflict is introduced
	def insert(self, prefix):
		self.size += 1
		index = bisect.bisect_left(self.roots, prefix)
		if index == len(self.roots):
			self.roots.append(PrefixNode(prefix))
			return False
		if prefix == self.roots[index]:
			if prefix.length() >= self.roots[index].root.length():
				return self.roots[index].insert(prefix)
			else:
				flattened = []
				while index < len(self.roots) and self.roots[index] == prefix:
					flattened.append(self.roots[index].root)
					flattened.extend(self.roots[index].children)
					del self.roots[index]
				self.roots.insert(index, PrefixNode(prefix, flattened))
				return True
		else:
			self.roots.insert(index, PrefixNode(prefix))
			return False

	# withdraw an announcement of 'prefix' from 'origin'
	# returns True if the number of origins announcing a prefix changes
	def withdraw(self, origin, prefix):
		try:
			Prefix.parseStr(prefix)
		except ValueError:
			return False
		prefix = Prefix(prefix)
		try:
			index = bisect.bisect_left(self.roots, prefix)
		except ValueError:
			return False
		if index >= len(self.roots) or self.roots[index] != prefix:
			return False
		toInsert = self.roots[index].withdraw(origin, prefix)
		if toInsert:
			del self.roots[index]
			for node in toInsert:
				self.insert(node)
		return True

	def __str__(self):
		out = []
		for prefix in self.roots:
			out.append(prefix.pr())
		return pformat(out)

class PrefixNode(object):
	def __init__(self, prefix, children=[]):
		# root and children are Prefix objects
		self.root = prefix
		self.children = children[:]

	# Inserts a new prefix
	# Assumes self.children is very short, so brute force is best
	def insert(self, other):
		for child in self.children:
			if child.length() == other.length() and child == other:
				child.merge(other)
				return
		self.children.append(other)

	def withdraw(self, origin, prefix):
		if self.root == prefix:
			self.root.withdraw(origin)
			return self.children
		toDel = -1
		for i in xrange(len(self.children)):
			if self.children[i] == prefix and self.children[i].length() == prefix.length():
				if not self.children[i].withdraw(origin):
					# if no ASes are announcing a prefix, remove that prefix
					toDel = i
		if toDel >= 0:
			del self.children[toDel]
		return []

	# helper for constructing dict for __str__
	def pr(self):
		childStrs = []
		for child in self.children:
			assert(type(child) != type(self))
			childStrs.append(str(child))
		# return {str(self.root) : childStrs, 'announcement_root': str(self.root.announcements[0].AS)}
		return {str(self.root) : childStrs}

	def value(self):
		return self.root.value()

	def length(self):
		return self.root.length()

	def __str__(self):
		return pformat(self.pr())

	def __cmp__(self, other):
		try:
			return self.root.__cmp__(other.root)
		except AttributeError:
			return self.root.__cmp__(other)

	def __len__(self):
		return len(self.root)