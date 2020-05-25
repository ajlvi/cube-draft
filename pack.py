class Pack:	
	"""A pack object!?"""
	cards = []
	
	def __init__(self, cardnums):
		"""When it's created it needs to know what cards belong in it.
		The Draft class which is making packs will be in charge of that.
		"""
		self.cards = cardnums
		
	def __repr__(self):	return f"Pack with cards {self.cards}"
		
	def getCards(self): return self.cards
	
	def htmlCode(self): 
		"""This will ultimately be where the images are found and laid out.
		I'm imagining we'll have something like
			<div>currentPack.htmlCode()</div>
		in our site-building function. I haven't worked on this yet."""
		raise NotImplementedError
	
	def hasCard(self, num): return num in self.cards
	
	def chooseCard(self, num):
		"""I'm not 100% sure whether we want this method to return
		anything. For now it doesn't, but we can revisit this.
		"""
		if self.hasCard(num): self.cards.remove(num)
		else: raise ValueError(f"Card {num} wasn't in pack...")