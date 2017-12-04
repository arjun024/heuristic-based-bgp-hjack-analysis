#!/usr/bin/env python
from collections import Counter

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
#stream.add_interval_filter(1503631454, 1503631454)
stream.add_interval_filter(1503631454, 1503631954)
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

# Given an origin AS and list of all origin ASes, detect if it's a hijacker or not
def detect_hijack(sample_as, as_list):
	# with little info, we can't detect a hijack
	if len(as_list) < 3:
		return False
	# If majority of elements in the list have the same value and
	# the sample element has a different value, it could be a hijack
	counter = Counter(as_list)
	if counter.most_common()[0][1] <= len(as_list) / 2:
		# No majority element
		return False
	if counter.most_common()[0][0] == sample_as:
		# Most common is the sample: not the hijacker
		return False
	return True


def analyze(forest):
	for high_level_node in forest.roots:
		as_origins = []

		# collect all as origin values
		for astree in high_level_node.root.announcements:
			as_origins.append(int(astree.AS))
		for child in high_level_node.children:
			for astree in child.announcements:
				as_origins.append(int(astree.AS))

		# mark
		for astree in high_level_node.root.announcements:
			if detect_hijack(int(astree.AS), as_origins):
				astree.is_a_hijack = True
				print 'Hijacker: %d' % astree.AS
				print 'All origins: ' + str(as_origins)

		for child in high_level_node.children:
			for astree in child.announcements:
				if detect_hijack(int(astree.AS), as_origins):
					astree.is_a_hijack = True
					print 'Hijacker: %d' % astree.AS
					print 'All origins: ' + str(as_origins)


def main():
	tree = build_tree()
	#print str(tree)
	analyze(tree)


if __name__ == '__main__':
	main()

