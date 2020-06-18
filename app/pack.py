from random import sample

class Pack:	
	"""A pack object!?"""	
	def __init__(self, cardnums):
		"""When it's created it needs to know what cards belong in it.
		The Draft class which is making packs will be in charge of that.
		"""
		self.cards = cardnums
		
	def __repr__(self):	return f"Pack with cards {self.cards}"
	
	def __len__(self): return len(self.cards)
		
	def getCards(self): return self.cards
	
	def hasCard(self, num): return num in self.cards
	
	def randomCard(self): return sample(self.cards, 1)[0]
	
	def chooseCard(self, num):
		"""
		Take a card out of the pack.
		"""
		if self.hasCard(num): self.cards.remove(num)
		else: raise ValueError(f"Card {num} wasn't in pack...")
		
	def replaceCard(self, taken, putback):
		"""
		Removes [[taken]] and puts in [[putback]]. This is used for Cogwork Librarians.
		"""
		assert taken in self.cards
		self.cards[self.cards.index(taken)] = putback