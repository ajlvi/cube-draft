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
	
	def chooseCard(self, num):
		"""
		Take a card out of the pack.
		"""
		if self.hasCard(num): self.cards.remove(num)
		else: raise ValueError(f"Card {num} wasn't in pack...")