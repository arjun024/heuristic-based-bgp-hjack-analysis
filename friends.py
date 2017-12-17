# reads CAIDA as-relationships and as-organizations data, and
# determines "friends" of each AS, defined as connected neighbors
# and ASes of the same organization
import pprint

class FriendsMap(object):
	# takes the path to the as-organizations file
	# and the path to the as-relationships file
	def __init__(self, organizationPath, relationshipsPath):
		self.friends = {}
		with open(relationshipsPath, 'r') as relsFile:
			for line in relsFile:
				if line[0] == '#':
					continue
				parsed = line.split('|')
				try:
					as1 = int(parsed[0])
					as2 = int(parsed[1])
				except:
					continue
				if as1 not in self.friends:
					self.friends[as1] = set([as2])
				else:
					self.friends[as1].add(as2)
				if as2 not in self.friends:
					self.friends[as2] = set([as1])
				else:
					self.friends[as2].add(as1)
		orgs = {}
		with open(organizationPath, 'r') as orgsFile:
			for line in orgsFile:
				if line[0] == '#':
					continue
				parsed = line.split('|')
				try:
					asn = int(parsed[0])
					org = parsed[3]
				except:
					continue
				if org not in orgs:
					orgs[org] = set([asn])
				else:
					orgs[org].add(asn)
		for siblings in orgs.values():
			if len(siblings) < 2:
				continue
			for asn in siblings:
				if asn not in self.friends:
					self.friends[asn] = siblings - set([asn])
				else:
					self.friends[asn] |= (siblings - set([asn]))


	def __call__(self, asn):
		try:
			return self.friends[asn]
		except KeyError:
			return []

	def show(self):
		pprint.pprint(self.friends)

if __name__ == '__main__':
	FriendsMap('data/20170401.as-org2info.txt', 'data/20170901.as-rel2.txt')