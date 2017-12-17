#!/usr/bin/env python
from collections import Counter

from _pybgpstream import BGPStream, BGPRecord, BGPElem
from PrefixForest import PrefixForest
import pprint, argparse
from friends import FriendsMap

parser = argparse.ArgumentParser(description='Download a file over HTTP.')
parser.add_argument('file', metavar='F', default='&%*None', help='File to write output to.')
file = parser.parse_args().file

stream = BGPStream()
rec = BGPRecord()

# Consider RIPE RRC 10 only
stream.add_filter('collector','rrc11')

# Time interval:
#stream.add_interval_filter(1503631454, 1503631454)
stream.add_interval_filter(1503631454, 1503635054)
#stream.add_interval_filter(1503631454, 1506252254)
print("sampling interval: 1 hour")
# Start the stream
stream.start()

as_reliability_map = {}

def analyze_conflicts(conflicts):
	# arg0: List[Node]
	pass

friendsMap = FriendsMap('data/20170401.as-org2info.txt', 'data/20170901.as-rel2.txt')

counter = {
	'all_announcements' : 0,
	'all_conflicts': 0,
	'hijacks': 0
}

def build_tree():
	tree = PrefixForest()
	init = True
	while(stream.get_next_record(rec)):
		if init:
			init = False
			start_time = rec.time
			day = 0
		elif rec.time - day*24*60*60 > start_time:
			print 'Day ' + str(day)
			day += 1
		# Print the record information only if it is not a valid record
		if rec.status != "valid":
			continue
		elem = rec.get_next_elem()
		while(elem):
			counter['all_announcements'] += 1
			# Interested only in announcements for the timebeing
			if elem.type == 'A':
				prefixNode = tree.unsanitizedInsert(elem)
				if prefixNode:
					counter['all_conflicts'] += 1
					if detect_hijack(prefixNode, elem.time):
						counter['hijacks'] += 1
			elif elem.type == 'W':
				tree.withdraw(elem.peer_asn, elem.fields['prefix'])
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


def detect_hijack(prefixNode, time):
	# identify the new announcement tree
	announcements = prefixNode.announcementTrees()
	for tree in announcements:
		if tree.time == time:
			new = tree
			break
	else:
		raise KeyError('No announcement found under prefix ' + str(prefixNode.value()) + ' at time ' + str(time))

	# check if the new announcement is a hijack, if not, return False
	for tree in announcements:
		# if the AS is neighbors with an AS legitimately announcing the same prefix, it's not a hijack
		if not tree.is_a_hijack and tree.AS in friendsMap(new.AS):
			return False

	# if it is a hijack, mark it as such
	new.is_a_hijack = True

	# mark ASes that are advertising a hijack as unreliable, and the others as reliable
	for tree in announcements:
		mark(tree)
	return True

def mark(astree, gullible=False):
	gullible = gullible or astree.is_a_hijack
	if as_reliability_map.get(astree.AS) is None:
		as_reliability_map[astree.AS] = {
			'gullible': 0,
			'appeared': 0,
			'reliability_score': 0
		}
	if gullible:
		as_reliability_map[astree.AS]['gullible'] += 1
	as_reliability_map[astree.AS]['appeared'] += 1
	# recalc the score
	appearances = as_reliability_map[astree.AS]['appeared']
	gullible_apprearances = as_reliability_map[astree.AS]['gullible']
	as_reliability_map[astree.AS]['reliability_score'] = (appearances - gullible_apprearances) / float(appearances)
	for child in astree.children:
		mark(child, gullible)


def analyze():
	output = '**********\n'
	output += str(counter) + '\n'
	output += 'Hijacks per announcement: %f %%\n' % (counter['hijacks'] * 100 / float(counter['all_announcements']))
	output += 'Hijacks per overlap: %f %%\n' % (counter['hijacks'] * 100 / float(counter['all_conflicts']))
	output += '**********\n'
	output += str(sorted(as_reliability_map.items(), key=lambda (k, v): v['reliability_score']))

	if file == '&%*None':
		print output
	else:
		with open(file, 'w') as f:
			f.write(output)

def main():
	tree = build_tree()
	#print str(tree)
	analyze()


if __name__ == '__main__':
	main()

