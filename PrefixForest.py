from bisect import bisect_left, insort
from Prefix import Prefix

class PrefixForest(object):
	def __init__(self):
		self.roots = []
		self.size = 0

	# Returns True if a new conflict is introduced
	def insert(self, element):
		self.size += 1
		prefix = Prefix(element.fields['prefix'], element.fields['as-path'].split(" "))
		newNode = PrefixTreeNode(prefix)
		index = bisect_left(self.roots, newNode)
		if index == len(self.roots):
			self.roots.append(newNode)
			return False
		if newNode == self.roots[index]:
			if newNode.prefix.length >= self.roots[index].prefix.length:
				return self.roots[index].insert(newNode)
			else:
				ret = newNode.insert(self.roots[index])
				self.roots[index] = newNode
				return ret
		else:
			insort(self.roots, prefix)
			return False

	def withdraw(self, origin, prefix):
		

class PrefixTreeNode(object):
	def __init__(self, prefix):
		self.prefix = prefix
		self.left = None
		self.right = None

	# Insert a new prefix somewhere into the tree
	# Returns True if a new conflict is introduced
	def insert(self, other):
		# This function should only be called on nodes with prefixes
		# at least as long as this one's
		assert(self.prefix.length <= other.prefix.length)

		# This function should only be called on nodes
		# with competing prefixes
		assert(self.prefix == other.prefix)

		if self.prefix.length == other.prefix.length:
			# If the prefixes are exactly the same, merge them
			return self.prefix.merge(other.prefix)
		elif other.prefix.value | 2**self.prefix.length:
			# Otherwise insert the new node into the tree
			# on the right if the next bit is 1
			if self.right:
				if self.right.prefix.length > other.prefix.length:
					other.insert(self.right)
					self.right = other
					return True
				return self.right.insert(other)
			else:
				self.right = other
				return True
		else:
			#on the left if the next bit is 0
			if self.left:
				if self.left.prefix.length > other.prefix.length:
					other.insert(self.left)
					self.left = other
					return True
				return self.left.insert(other)
			else:
				self.left = other
				return True

	def __str__(self):
		return str(self.prefix)

	def __cmp__(self, other):
		return self.prefix.__cmp__(other.prefix)

	def __len__(self):
		return len(self.prefix)