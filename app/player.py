from app.pack import *
from time import time

picktimes = {15: 75, 14: 70, 13: 65, 12: 60, 11: 55, 10: 50, 9: 45, 8: 40, 7: 35, 6: 30, 5: 25, 4: 20, 3: 15, 2: 10, 1: 5}

class Player:
	def __init__(self, handle):
		self.handle = handle
		self.queue = []
		self.chosen = []
		self.activePack = None
		self.unopened = []
		self.choices = [] #these are pairs ([pack], [chosen])
		self.opentime = 0 #refreshes each time a pack is opened
		self.delinquency = False
		
	def __repr__(self):
		out = f"Player {self.handle} participating in draft."
		out += f"\nI currently possess cards: {self.chosen}."
		if self.activePack != None: out += f"\nI am drafting from {self.activePack}."
		return out

	def getname(self): return self.handle
	def getChosen(self): return self.chosen
	def getActive(self): return self.activePack
	def getUnopened(self): return self.unopened
	def getQueue(self): return self.queue
	def getTime(self): return self.opentime
	def getDelinq(self): return self.delinquency
	
	def setChosen(self, l): self.chosen = l
	def setActive(self, ap): self.activePack = ap
	def setUnopened(self, u): self.unopened = u
	def setQueue(self, q): self.queue = q
	def setTime(self, t): self.opentime = t
	def setChoices(self, c): self.choices = c
	def setDelinq(self, d): self.delinquency = d

	def takeUnopened(self, packs):
		"""
		These are the unopened packs that come from the draft object.
		I'm expecting a list of Pack objects.
		"""
		self.unopened = packs

	def hasPack(self): return self.activePack != None
	
	def queueLen(self): return len(self.queue)
	
	def chosenLen(self): return len(self.chosen)
	
	def timeLeft(self):
		"""Returns -1 if we're waiting. Otherwise determines how much time
		should be left based on cards in active pack."""
		if not self.hasPack(): return -1
		return picktimes[len(self.activePack)] - (time() - self.opentime)
		
	def isDelinquent(self):
		"""Says `yes` presently if you're more than three seconds beyond the limit.
		   This is a test based on the status of the player; the delinquency variable
		   is keeping track of whether you were delinquent at your last pick."""
		if self.hasPack(): return self.timeLeft() < -3
		return False
		
	def pullFromQueue(self):
		#take the next pack from the queue and begin drafting from it.
		assert self.activePack == None
		self.activePack = self.queue[0]
		self.queue = self.queue[1:]
		self.opentime = time()
		self.choices.append( ([c for c in self.activePack.getCards()], []) )

	def startNewPack(self):
		#take the next pack from our stock of unopened packs and start drafting from it.
		assert self.activePack == None
		self.activePack = self.unopened[0]
		self.unopened = self.unopened[1:]
		self.opentime = time()
		self.choices.append( ([c for c in self.activePack.getCards()], []) )

	def receivePack(self, pack):
		#draft from the passed pack, or put it in the queue if busy.
		if self.activePack == None: 
			self.activePack = pack
			self.opentime = time()
			self.choices.append( ([c for c in self.activePack.getCards()], []) )
		else: self.queue.append(pack)
		
	def draftCard(self, num):
		"""
		This method only handles non-Cogwork picks.
		"""
		self.activePack.chooseCard(num)
		self.chosen.append(num)
		self.choices[-1][1].append(num)
		usedPack = self.activePack
		self.activePack = None
		if self.queueLen() != 0: self.pullFromQueue()
		return usedPack
		
	def cogworkPick(self, num, cogwork):
		"""
		This method replaces Cogwork Librarian in the list of chosen cards
		with the selected card [[num]]. I'm having the Draft object tell us
		which card is the librarian.
		"""
		assert cogwork in self.chosen
		self.chosen[self.chosen.index(cogwork)] = num
		self.activePack.replaceCard(num, cogwork)
		self.opentime += 10
		self.choices[-1][1].append(num)
	
	def draftAllCards(self):
		"""
		Draft every card from all packs. Used for sealed.
		"""
		for pack in self.unopened:
			for card in pack.getCards():
				self.chosen.append(card)
		self.chosen.sort()
		self.unopened = []
		
	def giveChoices(self): return self.choices
		
	def convertChoices(self, cube):
		"""
		This method will replace all the ID numbers in choices with corresponding MTGO IDs.
		The intention here is to change what's being stored into something that's resistant
		to changes in the cube composition. (Using cube indexes will cause eventual drift.)
		The parent draft object will run this on each user after the draft has ended.
		"""
		newchosen = []
		for tup in self.choices:
			newpack = [int(cube.loc[x]["mtgo"]) for x in tup[0]]
			newchoice = [int(cube.loc[x]["mtgo"]) for x in tup[1]]
			newchosen.append( (newpack, newchoice) )
		self.choices = newchosen