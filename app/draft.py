from app.pack import *
from app.player import *
from random import shuffle, randrange
import pandas as pd

class Draft:
	def __init__(self, cube, packs, cardsper, intended=8, scheme="random"):
		"""
		To initialize the draft we need a cube to create packs from -- I'm
		assuming this will come to us as a pandas dataframe -- as well as how
		many packs to make, how many cards to make in each pack, a scheme for
		how to make the packs, and the number of players intended.
		
		This method returns the key to be stored in a dictionary of drafts.
		"""
		self.packs = makePacks(cube, packs*intended, cardsper)
		self.cube = cube
		self.intended = intended
		self.total_packs = packs
		self.cards_per_pack = cardsper
		self.players = []
		self.handles = []
		self.currentPack = 0
		self.fullyDrafted = 0
		self.key = makeKey()

	def __repr__(self):
		out = f"A cube draft involving {self.handles}."
		for Person in self.players:
			if Person.hasPack():
				out += f"\n{Person.getname()} is picking from {Person.getActive()}."
			else:
				out += f"\n{Person.getname()} isn't picking and has picked {Person.getChosen()}."
		return out
	
	def addPlayer(self, handle):
		"""handle is a string representing the handle of the human."""
		if self.currentPack == 0:
			if handle not in self.handles:
				self.players.append(Player(handle))
				self.handles.append(handle)
				if len(self.handles) == self.intended: self.startDraft() #fine for now
		
	def hasPlayer(self, handle): return handle in self.handles
	
	def whatPackIsIt(self, handle): return self.currentPack
	
	def getKey(self): return self.key

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
		print(f"player {handle} is picking card {num}.")
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
		card = theirPack.randomCard()
		self.makePick(handle, card)
	
	def status(self, handle):
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
		if PlayerObj.isDelinquent(): #autopicking
			self.autoPick(PlayerObj.getname())
			return self.status(PlayerObj.getname())
		if PlayerObj.hasPack():
			return PlayerObj.queueLen() + 1
		else: return 0
		
	def statusCheck(self):
		"""A "global" version of status, for assessing the whole draft."""
		output = []
		for handle in self.handles:
			PlayerObj = self.players[self.handles.index(handle)]
			if PlayerObj.isDelinquent():
				self.status(handle); return self.statusCheck()
			else:
				output.append(self.status(handle))
		return output

	def handleIncoming(self, handle, num):
		"""
		This is the function which interfaces with the end user -- it receives the
		data from the page and it outputs everything that we want to give back.
		[num] is nonnegative if this function call includes making a pick.
		For a pure status update, -1 gets passed in.
		
		This returns a dictionary which still needs to be JSONnified.
		"""
		print(f"Player {handle} is ppinging with card-id {num}.")
	#if HANDLE not here -- raise IndexError
	#if CARD not here -- raise ValueError
		if num >= 0: self.makePick(handle, num)
		stat = self.statusCheck()
		PlayerObj = self.players[self.handles.index(handle)]
		chosen_cards = PlayerObj.getChosen()
		chosen_df = self.cube.loc[PlayerObj.getChosen()].to_json()
		if PlayerObj.getActive() != None:
			current_pack = PlayerObj.getActive().getCards()
			current_df = self.cube.loc[current_pack].to_json()
			time_remaining = PlayerObj.timeLeft()
		else:
			current_pack = None
			current_df = None
			time_remaining = 0
		outdict = {"draft_key": self.key, "drafters": self.handles,\
			"status": stat, "my_name": handle, "my_status": self.status(handle), \
			"packno": self.currentPack, "total_packs": self.total_packs, \
			"cards_per_pack": self.cards_per_pack, "time_remaining": time_remaining,\
			"chosen_cards": chosen_cards, "chosen_df": chosen_df,\
			"current_pack": current_pack, "current_df": current_df}
		return outdict


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
	
def makeKey():
	"""
	Returns a random four-character string.
	"""
	return hex(randrange(16**3, 16**4)).split('x')[1].upper()