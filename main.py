#!/usr/bin/env python

from _pybgpstream import BGPStream, BGPRecord, BGPElem
from PrefixForest import PrefixForest
import pprint

# A node in the proverbial Tree
class Node():
	def __init__(self, prefix, origin, aspath):
		self.prefix = prefix
		self.origin = origin
		self.aspath = aspath
# placeholder
class Tree():
	@classmethod
	def insert(self, node):
		# returns the list of nodes that conflict if the insertion created a conflict
		return []
	@classmethod
	def delete(self, node):
		pass
	@classmethod
	def search(self, key, value):
		pass


stream = BGPStream()
rec = BGPRecord()

# Consider RIPE RRC 10 only
stream.add_filter('collector','rrc11')

# Time interval:
stream.add_interval_filter(1503631454, 1503631454)# 1503632022) #1503631546 1503631561
# Start the stream
stream.start()

def analyze_conflicts(conflicts):
	# arg0: List[Node]
	pass

def build_tree():
	tree = PrefixForest()
	while(stream.get_next_record(rec)):
		# Print the record information only if it is not a valid record
		if rec.status != "valid":
			continue
		elem = rec.get_next_elem()
		while(elem):
			# Interested only in announcements for the timebeing
			if elem.type != 'A':
				elem = rec.get_next_elem()
				continue
			tree.insert(elem)
			# fields = elem.fields
			# if not fields:
			# 	elem = rec.get_next_elem()
			# 	continue

			# prefix = fields.get('prefix', None)
			# if not prefix:
			# 	elem = rec.get_next_elem()
			# 	continue

			# aspath = fields.get('as-path', None)
			# if not aspath:
			# 	elem = rec.get_next_elem()
			# 	continue

			# # convert to list
			# aspath = aspath.split()
			# # originator of the announcement
			# origin = aspath[-1]
			# # Clean up AS path prepending and get a list of unique values
			# aspath_uniq = []
			# [aspath_uniq.append(x) for x in aspath if x not in aspath_uniq]

			# # Make a node and add to the tree
			# node = Node(prefix, origin, aspath)
			# # assumed to return a bool
			# conflicts = tree.insert(node)
			# if conflicts:
			# 	analyze_conflicts(conflicts)
			elem = rec.get_next_elem()
	return tree

def main():
	tree = build_tree()
	print str(tree)


if __name__ == '__main__':
	main()

