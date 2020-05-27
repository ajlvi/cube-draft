from pack import *
from player import *
from random import shuffle, sample
import pandas as pd

class Draft:
	def __init__(self, cube, packs, cardsper, intended=8, scheme="random"):
		"""
		To initialize the draft we need a cube to create packs from -- I'm
		assuming this will come to us as a pandas dataframe -- as well as how
		many packs to make, how many cards to make in each pack, a scheme for
		how to make the packs, and the number of players intended.
		"""
		self.packs = makePacks(cube, packs*intended, cardsper)
		self.intended = intended
		self.cards_per_pack = cardsper
		self.players = []
		self.handles = []
		self.currentPack = 0
		self.fullyDrafted = 0
	
	def __repr__(self):
		out = f"A cube draft involving {self.handles}."
		for Person in self.players:
			if Person.hasPack():
				out += f"\n{Person.getname()} is picking from {Person.getActive()}."
			else:
				out += f"\n{Person.getname()} isn't picking and has picked {Person.getChosen()}."
		return out
	
	def addPlayer(self, handle):
		"""Player is a string representing the handle of the human."""
		if handle not in self.handles:
			self.players.append(Player(handle))
		else:
			i = 2
			while handle + str(i) in self.handles: i += 1
			self.players.append(Player(handle + str(i))
	
	def startDraft(self):
		"""
		All the things that need to happen to get the draft underway.
		We need to randomize the players and give them their packs.
		"""
		shuffle(self.players); shuffle(self.packs)
		self.handles = [Person.getname() for Person in self.players]
		assert len(self.packs) % len(self.players) == 0
		packsper = int(len(self.packs) / len(self.players))
		for i in range(len(self.players)):
			self.players[i].takeUnopened(self.packs[i*packsper:(i+1)*packsper])
		self.nextPack() #will increment currentPack to 1, everyone opens pack
	
	def lookupByHandle(self, handle):
		"""
		self.handles is updated in the startDraft method to map correctly
		to the list of players after randomization.
		"""
		return self.players[self.handles.index(handle)]
	
	def readyForNextPack(self):
		"""Decides if we're ready for the next pack."""
		return self.fullyDrafted == len(self.players)
		
	def nextPack(self):
		"""Moves everyone onto the next pack."""
		for Person in self.players:
			Person.startNewPack()
		self.currentPack += 1
		self.fullyDrafted = 0
	
	def successor(self, handle):
		increment = (-1)**self.currentPack
		return self.players[(self.handles.index(handle) + increment)%len(self.players)]
	
	def makePick(self, handle, num):
		"""
		I'm expecting to receive handles from the end users.
		"""
		PlayerObj = self.players[self.handles.index(handle)]
		usedPack = PlayerObj.draftCard(num)
		if len(usedPack) == 0:
			self.fullyDrafted += 1
			if self.readyForNextPack(): self.nextPack()
		else:
			nextPlayer = self.successor(handle)
			nextPlayer.receivePack(usedPack)
	
	def autoPick(self, handle):
		"""
		Auto-picking for delinquent players. We're doing this by picking
		randomly, so that white doesn't get cut by auto-drafters.
		"""
		PlayerObj = self.players[self.handles.index(handle)]
		theirPack = PlayerObj.getActive()
		card = sample(theirPack.getCards(), 1)
		self.makePick(handle, card)
	
	def status(self, handle)
		"""
		Decides what the status of given player is.
		The returned value is an integer. The interpretation is as follows:
		--- A positive integer indicates "picking, plus X packs in queue."
		    So 1 means "picking and no packs in queue," etc.
		--- A returned value of 0 means the player is waiting for a pack.
		If the player is delinquent, this method will force them to make a pick,
		then reassess.
		"""
		PlayerObj = self.players[self.handles.index(handle)]
		if playerObj.isDelinquent(): #autopicking
			self.autoPick(handle)
			return self.status(handle)
		if PlayerObj.hasPack():
			return PlayerObj.queueLen() + 1
		else: return 0



def makePacks(cube, packs, cardsper, scheme="random"):
	"""
	Creates [packs] many packs each with [cardsper] cards in them from
	the [cube]. The [cube] object is assumed to be a pandas dataframe.
	Note that [packs] is TOTAL, not PER PLAYER.
	
	If the scheme is "random", the list of cards is shuffled
	and cut into segments and returned. If the scheme is "Adam", do what
	Adam typically does to make his cube (deal out colors to each pack).
	Right now "Adam" only works for 3x15 (8-man), 4x11 (6-man), and 5x9.
	"""
	if scheme == "random":
		pool = cube.sample(packs * cardsper)
		packidxs = [Pack(sorted(list(pool[i*cardsper:(i+1)*cardsper].index))) for i in range(packs)]
		return packidxs
	elif scheme == "Adam":
		#note, slightly unsatisfyingly, I couldn't use cube["color"].unique() here.
		if (packs, cardsper) == (24, 15):
			stock = {"W": 43, "U": 43, "B": 43, "R": 43, "G": 43, \
					 "ally": 35, "enemy": 35, 'other': 37, 'land': 38}
		elif (packs, cardsper) == (24, 11):
			stock = {"W": 31, "U": 31, "B": 31, "R": 31, "G": 31, \
					 "ally": 26, "enemy": 26, 'other': 28, 'land': 29}
		else: return makePacks(cube, packs, cardsper, "random")
		pool = []
		for color in ["W", "U", "B", "R", "G", "ally", "enemy", "other", "land"]:
			slice = cube[cube["color"] == color]
			pool.append(list(slice.sample(stock[color]).index))
		return divvy(pool, packs)
		
def divvy(cats, packs):
	"""
	Takes lists of segments and sprays them.
	"""
	packlists = [ [] for i in range(packs) ]
	pak = 0 #where the next element goes
	while len(cats) > 0 :
		current = cats.pop()
		for card in current:
			packlists[pak].append(card)
			pak = (pak + 1)%len(packlists)
	return [sorted(pack) for pack in packlists]