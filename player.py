from pack import *

class Player:	
	def __init__(self, handle):
		self.handle = handle
		self.queue = []
		self.chosen = []
		self.activePack = None
		self.unopened = []

	def __repr__(self):
		out = f"Player {self.handle} participating in draft."
		out += f"\nI currently possess cards: {self.chosen}."
		return out

	def getname(self): return self.handle
	
	def getChosen(self): return self.chosen

	def getActive(self): return self.activePack
	
	def takeUnopened(self, packs):
		"""
		These are the unopened packs that come from the draft object.
		I'm expecting a list of Pack objects.
		"""
		self.unopened = packs

	def hasPack(self): return self.activePack != None
	
	def queueLen(self): return len(self.queue)
	
	def chosenLen(self): return len(self.chosen)
		
	def pullFromQueue(self):
		assert self.activePack == None
		self.activePack = self.queue[0]
		self.queue = self.queue[1:]

	def startNewPack(self):
		assert self.activePack == None
		self.activePack = self.unopened[0]
		self.unopened = self.unopened[1:]

	def receivePack(self, pack):
		if self.activePack == None: self.activePack = pack
		else: self.queue.append(pack)
		
	def draftCard(self, num, cogwork=False):
		"""
		Later we can try to add support for Cogwork Librarian here,
		but for now we're just going to append cards to the end of the
		list of picked objects.
		"""
		self.activePack.chooseCard(num)
		self.chosen.append(num)
		usedPack = self.activePack
		self.activePack = None
		if self.queueLen() != 0: self.pullFromQueue()
		return usedPack