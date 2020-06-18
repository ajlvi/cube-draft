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
		self.opentime = 0 #refreshes each time a pack is opened

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
	
	def setChosen(self, l): self.chosen = l
	def setActive(self, ap): self.activePack = ap
	def setUnopened(self, u): self.unopened = u
	def setQueue(self, q): self.queue = q
	def setTime(self, t): self.opentime = t

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
		"""Says `yes` presently if you're more than three seconds beyond the limit."""
		if self.hasPack(): return self.timeLeft() < -3
		return False
		
	def pullFromQueue(self):
		assert self.activePack == None
		self.activePack = self.queue[0]
		self.queue = self.queue[1:]
		self.opentime = time()

	def startNewPack(self):
		assert self.activePack == None
		self.activePack = self.unopened[0]
		self.unopened = self.unopened[1:]
		self.opentime = time()

	def receivePack(self, pack):
		if self.activePack == None: 
			self.activePack = pack
			self.opentime = time()
		else: self.queue.append(pack)
		
	def draftCard(self, num):
		"""
		This method only handles non-Cogwork picks.
		"""
		self.activePack.chooseCard(num)
		self.chosen.append(num)
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
		self.activePack.swapCard(num, cogwork)
		self.opentime += 10