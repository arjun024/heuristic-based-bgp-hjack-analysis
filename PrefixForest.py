import bisect
from Prefix import Prefix
from pprint import pformat

class PrefixForest(object):
	def __init__(self):
		self.roots = []
		self.size = 0

	# Returns True if a new conflict is introduced
	def insert(self, element):
		try:
			Prefix.parseStr(element.fields['prefix'])
		except ValueError:
			return False
		self.size += 1
		prefix = Prefix(element.fields['prefix'], element.fields['as-path'].split(" "))
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
	# returns the new number of origins announcing the prefix
	def withdraw(self, origin, prefix):
		try:
			index = bisect.index(self.roots, prefix)
		except ValueError:
			return 0
		return self.roots[index].root.withdraw(origin)

	def __str__(self):
		out = []
		for prefix in self.roots:
			out.append(prefix.pr())
		return pformat(out)

class PrefixNode(object):
	def __init__(self, prefix, children=[]):
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