from app.pack import *
from app.player import *
from random import shuffle, randrange, choices
import pandas as pd

class Draft:
	def __init__(self, cube, cubename, packs, cardsper, intended=8, scheme="random"):
		"""
		To initialize the draft we need a cube to create packs from -- I'm
		assuming this will come to us as a pandas dataframe -- as well as how
		many packs to make, how many cards to make in each pack, a scheme for
		how to make the packs, and the number of players intended.
		
		This method returns the key to be stored in a dictionary of drafts.
		"""
		self.cube = cube
		if "Cogwork Librarian" in cube["card"].values:
			self.cogworkIdx = int(cube[cube["card"] == "Cogwork Librarian"].index[0])
		else: self.cogworkIdx = -1
		self.scheme = scheme
		self.intended = intended
		self.total_packs = packs
		self.cards_per_pack = cardsper
		self.players = []
		self.handles = []
		self.currentPack = 0
		self.fullyDrafted = 0
		self.key = makeKey()
		self.cubename = cubename

	def __repr__(self):
		out = f"A cube draft involving {self.handles}."
		for Person in self.players:
			if Person.hasPack():
				out += f"\n{Person.getname()} is picking from {Person.getActive()}."
			else:
				out += f"\n{Person.getname()} isn't picking and has picked {Person.getChosen()}."
		return out
	
	def addPlayer(self, handle):
		"""handle is a string representing the handle of the human.
		   In the interest of avoiding funny business, new players are processed
		   pre-draft only. This also auto-fires the draft when ready."""
		if self.currentPack == 0:
			if handle not in self.handles:
				self.players.append(Player(handle))
				self.handles.append(handle)
				if len(self.handles) == self.intended: self.startDraft() #fine for now
		
	def hasPlayer(self, handle): return handle in self.handles
	
	def whatPackIsIt(self, handle): return self.currentPack
	
	def getKey(self): return self.key
	def getScheme(self): return self.scheme
	def getPackData(self): return (self.intended, self.total_packs, self.cards_per_pack)

	def setKey(self, k): self.key = k
	def setHandles(self, hs): self.handles = hs
	def setFully(self, f): self.fullyDrafted = f
	def setCurrent(self, c): self.currentPack = c
	def setPlayer(self, Pl): self.players.append(Pl)

	def startDraft(self):
		"""
		All the things that need to happen to get the draft underway.
		We need to randomize the players and give them their packs.
		"""
		if self.cards_per_pack == 90 and self.scheme != "random":
			self.startSealed(); return
		packstock = makePacks(self.cube, self.total_packs*self.intended, self.cards_per_pack, self.scheme)
		shuffle(self.players); shuffle(packstock)
		self.handles = [Person.getname() for Person in self.players]
		assert len(packstock) % len(self.players) == 0
		packsper = int(len(packstock) / len(self.players))
		for i in range(len(self.players)):
			self.players[i].takeUnopened(packstock[i*packsper:(i+1)*packsper])
		self.nextPack() #will increment currentPack to 1, everyone opens pack
	
	def startSealed(self):
		"""
		All the things that need to happen to get a sealed pool underway.
		We need to randomize the players and give them their packs.
		Then each player picks every card in all their packs and the "draft" ends.
		I'm expecting each player will ping and discover all their cards.
		"""
		packstock = sealedPacks(self.cube, self.scheme)
		shuffle(self.players); shuffle(packstock)
		self.handles = [Person.getname() for Person in self.players]
		assert len(self.handles) <= 5
		packsper = 6		
		for i in range(len(self.players)):
			self.players[i].takeUnopened(packstock[i*packsper:(i+1)*packsper])
			self.players[i].draftAllCards()
		self.fullyDrafted = 1; self.currentPack = 1
		
	def lookupByHandle(self, handle):
		"""
		self.handles is updated in the startDraft method to map correctly
		to the list of players after randomization.
		"""
		return self.players[self.handles.index(handle)]
	
	def readyForNextPack(self):
		"""Decides if we're ready for the next pack."""
		return (self.fullyDrafted == len(self.players)) and (self.currentPack < self.total_packs)
	
	def nextPack(self):
		"""Moves everyone onto the next pack."""
		for Person in self.players:
			Person.startNewPack()
		self.currentPack += 1
		self.fullyDrafted = 0
	
	def successor(self, handle):
		increment = (-1)**self.currentPack
		return self.players[(self.handles.index(handle) + increment)%len(self.players)]
	
	def makePick(self, handle, num, cogwork):
		"""
		I'm expecting to receive handles from the end users.
		"""
		print(f"player {handle} is picking card {num}.")
		PlayerObj = self.players[self.handles.index(handle)]
		if cogwork:
			PlayerObj.cogworkPick(num, self.cogworkIdx)
		else:
			usedPack = PlayerObj.draftCard(num)
			if len(usedPack) == endPackNumber(self): #player has finished with this pack
				self.fullyDrafted += 1
				if len(PlayerObj.getUnopened()) == 0: #this should mean they're done drafting
					PlayerObj.convertChoices(self.cube)
				if self.readyForNextPack(): self.nextPack()
			else:
				nextPlayer = self.successor(handle)
				usedPack.sortCards() #to rearrange a replaced Librarian, if needed
				nextPlayer.receivePack(usedPack)
	
	def autoPick(self, handle):
		"""
		Auto-picking for delinquent players. We're doing this by picking
		randomly, so that white doesn't get cut by auto-drafters.
		"""
		PlayerObj = self.players[self.handles.index(handle)]
		theirPack = PlayerObj.getActive()
		card = theirPack.randomCard()
		PlayerObj.setDelinq(True)
		self.makePick(handle, card, False)
	
	def hasCogwork(self):
		for handle in self.handles:
			PlayerObj = self.players[self.handles.index(handle)]
			if self.cogworkIdx in PlayerObj.getChosen():
				return handle
		return None
	
	def status(self, handle):
		"""
		Decides what the status of given player is.
		The returned value is an integer. The interpretation is as follows:
		--- A positive integer indicates "picking, plus X packs in queue."
		    So 1 means "picking and no packs in queue," etc.
		--- A returned value of 0 means the player is waiting for a pack.
		If the player is delinquent, this method will force them to make a pick,
		then reassess.
		--- A returned value of -N-1 means "delinquent with N packs in queue."
		    So a -1 means "not picking and delinquent."
		"""
		PlayerObj = self.players[self.handles.index(handle)]
		if PlayerObj.isDelinquent(): #autopicking -- delinq is set in autoPick
			self.autoPick(PlayerObj.getname())
			return -1 * self.status(PlayerObj.getname()) -1 #rerun status; may/may not have pack
		if PlayerObj.hasPack():
			if PlayerObj.getDelinq(): return -1 * (PlayerObj.queueLen() + 1) - 1
			else: return PlayerObj.queueLen() + 1
		else: 
			if PlayerObj.getDelinq(): return -1
			else: return 0

	def statusCheck(self):
		"""A "global" version of status, for assessing the whole draft."""
		output = []
		for handle in self.handles:
			PlayerObj = self.players[self.handles.index(handle)]
			output.append(self.status(handle)) #doesn't this already handle delinquency?
#			if PlayerObj.isDelinquent():
#				self.status(handle); return self.statusCheck()
#			else:
		return output

	def handleIncoming(self, handle, num, cogwork=False):
		"""
		This is the function which interfaces with the end user -- it receives the
		data from the page and it outputs everything that we want to give back.
		[num] is nonnegative if this function call includes making a pick.
		For a pure status update, -1 gets passed in.
		
		This returns a dictionary which still needs to be JSONnified.
		"""
		print(f"Player {handle} is pinging with card-id {num}.")
	#if HANDLE not here -- raise IndexError
	#if CARD not here -- raise ValueError
		PlayerObj = self.players[self.handles.index(handle)]
		if num >= 0: # a "legit" pick, so we'll set delinq to False
			self.makePick(handle, num, cogwork)
			PlayerObj.setDelinq(False)
		stat = self.statusCheck()
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
			"current_pack": current_pack, "current_df": current_df, \
			"scheme": self.scheme, "has_cogwork": self.hasCogwork(), \
			"thrown_picks": endPackNumber(self), "cube_id": self.cubename }
		return outdict
		
	def export(self):
		"""
		Returns enough information as a dictionary so that self can be rebuilt.
		I'm not exporting the cube -- that will need to be specified on each
		import call.
		"""
		d = {}
		d["key"] = self.key
		d["handles"] = self.handles
		d["intended"] = self.intended
		d["total_packs"] = self.total_packs
		d["cards_per_pack"] = self.cards_per_pack
		d["currentPack"] = self.currentPack
		d["fullyDrafted"] = self.fullyDrafted
		d["scheme"] = self.scheme
		d["cube_id"] = self.cubename
		playd = {}
		for handle in self.handles:
			PlayerObj = self.players[self.handles.index(handle)]
			hd = {}
			hd["queue"] = [P.getCards() for P in PlayerObj.getQueue()]
			hd["unopened"] = [P.getCards() for P in PlayerObj.getUnopened()]
			hd["chosen"] = PlayerObj.getChosen()
			hd["choices"] = PlayerObj.giveChoices()
			hd["delinq"] = PlayerObj.getDelinq()
			if PlayerObj.getActive() == None: hd["active"] = None
			else: hd["active"] = PlayerObj.getActive().getCards()
			hd["opentime"] = PlayerObj.getTime()
			playd[handle] = hd
		d["player_info"] = playd
		return d
		
	def draftHistory(self, handle):
		PlayerObj = self.players[self.handles.index(handle.replace("&#39;", "'"))]
		raw_choices = PlayerObj.giveChoices()
		out_dict = {"packs": {}, "picks": {}, "seen_df": '', "tot_packs": self.total_packs, "pack_size": self.cards_per_pack, "tossed": endPackNumber(self), "my_name": handle }
		allCardsSeen = []
		sfall = pd.read_csv("app/static/scryfall-trimmed.csv")
		for i in range(len(raw_choices)):
			out_dict["packs"][i] = raw_choices[i][0]
			out_dict["picks"][i] = raw_choices[i][1]
			for card in raw_choices[i][0]:
				if card not in allCardsSeen: allCardsSeen.append(card)
#		out_dict["seen_df"] = self.cube.loc[allCardsSeen][["scryfall", "card", "cost", "creature"]].to_json()
		out_df = sfall[(sfall["mtgo_id"].isin(allCardsSeen)) | (sfall["mtgo_foil_id"].isin(allCardsSeen))].copy()
		out_df.loc[:, "creature"] = out_df["type_line"].apply(lambda s: int("Creature" in s)).copy()
		out_df = out_df.rename({"name": "card"}, axis='columns')
		out_df.loc[:, "scryfall"] = out_df.apply(lambda row: trimImage(row), axis=1)
		out_df.loc[:, "mtgo_index"] = out_df.apply(lambda row: MTGOidfy(row, allCardsSeen), axis=1)
		out_df.loc[:, "cost"] = out_df.apply(lambda row: findManaCost(row), axis=1)
		out_df.set_index("mtgo_index", drop=True, inplace=True)
		out_dict["seen_df"] = out_df[["scryfall", "card", "cost", "creature"]].to_json()
		return out_dict
	
def trimImage(row):
	#for scryfall.
	if len(str(row.normal_image)) >= 4: return row.normal_image
	else: return eval(row["card_faces"])[0]["image_uris"]["normal"]
	
def MTGOidfy(row, seen):
	if row.mtgo_id in seen: return int(row.mtgo_id)
	elif row.mtgo_foil_id in seen: return int(row.mtgo_foil_id)
	raise ValueError("MTGO ID weirdness")
	
def findManaCost(row):
	if row.layout == "transform": return eval(row.card_faces)[0]["mana_cost"]
	else: return row.mana_cost

def endPackNumber(draf):
	if draf.getScheme() == "Adam" and draf.getPackData() in [(6, 4, 13), (4, 6, 9)]:
		return 2
	return 0

def rebuildDraft(d, cube):
	"""
	Takes the information of an exported dictionary d and a cube df and
	rebuilds a draft object from it.
	"""
	newD = Draft(cube, d["cube_id"], d["total_packs"], d["cards_per_pack"], d["intended"], d["scheme"])
	newD.setKey(d["key"])
	newD.setHandles(d["handles"])
	newD.setCurrent(d["currentPack"])
	newD.setFully(d["fullyDrafted"])
	for hand in d["handles"]:
		Pl = Player(hand)
		Pl.setQueue([Pack(l) for l in d["player_info"][hand]["queue"]])
		Pl.setUnopened([Pack(l) for l in d["player_info"][hand]["unopened"]])
		Pl.setChosen(d["player_info"][hand]["chosen"])
		Pl.setTime(d["player_info"][hand]['opentime'])
		Pl.setChoices(d["player_info"][hand]["choices"])
		Pl.setDelinq(d["player_info"][hand]["delinq"])
		if d["player_info"][hand]["active"] == None:
			Pl.setActive(d["player_info"][hand]["active"])
		else:
			Pl.setActive(Pack(d["player_info"][hand]["active"]))
		newD.setPlayer(Pl)
	return newD

def makePacks(cube, packs, cardsper, scheme="random"):
	"""
	Creates [packs] many packs each with [cardsper] cards in them from
	the [cube]. The [cube] object is assumed to be a pandas dataframe.
	Note that [packs] is TOTAL, not PER PLAYER.
	
	If the scheme is "random", the list of cards is shuffled
	and cut into segments and returned. If the scheme is "Adam", do what
	Adam typically does to make his cube (deal out colors to each pack).
	Right now "Adam" only works for 3x15 (8-man), 4x11/13 (6-man), and 5x9/11.
	"""
	if scheme == "random":
		pool = cube.sample(packs * cardsper)
		packidxs = [Pack(sorted(list(pool[i*cardsper:(i+1)*cardsper].index))) for i in range(packs)]
		return packidxs
#	elif scheme == "cogtest":
#		cog = cube[cube["card"] == "Cogwork Librarian"].index[0]
#		pool = cube.sample(packs * cardsper)
#		if cog not in pool.index: pool = cube.loc[list(pool.index[:-1]) + [cog]]
#		packidxs = [Pack(sorted(list(pool[i*cardsper:(i+1)*cardsper].index))) for i in range(packs)]
#		return packidxs

#	elif scheme == "Adam" and len(cube) == 450:
		#note, slightly unsatisfyingly, I couldn't use cube["color"].unique() here.
#		if (packs, cardsper) == (24, 15):
#			stock = {"W": 43, "U": 43, "B": 43, "R": 43, "G": 43, \
#					 "ally": 35, "enemy": 35, 'other': 37, 'land': 38}
#		elif (packs, cardsper) == (21, 15): #seven people
#			stock = {"W": 37, "U": 37, "B": 37, "R": 37, "G": 37, \
#					 "ally": 32, "enemy": 32, 'other': 32, 'land': 34}
#		elif (packs, cardsper) == (24, 13): #six with tosses
#			stock = {"W": 37, "U": 37, "B": 37, "R": 37, "G": 37, \
#					 "ally": 30, "enemy": 30, 'other': 33, 'land': 34}
#		elif (packs, cardsper) == (24, 11): #six without tosses
#			stock = {"W": 31, "U": 31, "B": 31, "R": 31, "G": 31, \
#					 "ally": 26, "enemy": 26, 'other': 28, 'land': 29}
#		elif (packs, cardsper) == (24, 9): #four with tosses
#			stock = {"W": 26, "U": 26, "B": 26, "R": 26, "G": 26, \
#					 "ally": 20, "enemy": 20, 'other': 22, 'land': 24}
#		else: return makePacks(cube, packs, cardsper, "random")
#		pool = []
#		for color in ["W", "U", "B", "R", "G", "ally", "enemy", "other", "land"]:
#			slice = cube[cube["color"] == color]
#			pool.append(list(slice.sample(stock[color]).index))
#		return divvy(pool, packs)
		
#		stock = {"W": 43, "U": 43, "B": 43, "R": 43, "G": 43, \
#				 "ally": 34, "enemy": 34, 'other': 38, 'land': 39}

	elif scheme == "Adam": #21.01.18 now works for any parameters
		stocksize = packs * cardsper
		#if the cube has 360 cards, let's not try to randomly hit the right configuration
		if len(cube) == 360 and stocksize == 360:
			stock = {x : len(cube[cube["color"] == x]) for x in ["W", "U", "B", "R", "G", "ally", "enemy", "other", "land"]}
		else: #giving up on doing this for 360/360 since we'd have to run perfect
			stock = {}
			mono = min( [ int( stocksize/len(cube) * len(cube[cube["color"] == x])) for x in ["W", "U", "B", "R", "G"] ] )
			for color in ["W", "U", "B", "R", "G"]: stock[color] = mono
			multi = min( [ int( stocksize/len(cube) * len(cube[cube["color"] == x])) for x in ["ally", "enemy"] ] )
			for color in ["ally", "enemy"]: stock[color] = multi
			lands = int( (stocksize/len(cube)) * len(cube[cube["color"] == "land"]))
			other = int( (stocksize/len(cube)) * len(cube[cube["color"] == "other"]))
			stock["land"] = lands; stock["other"] = other
			total = sum([stock[a] for a in stock])
			acceptable = False
			while not acceptable:
				teststock = dict(stock)
				if total < stocksize:
					for addl in choices(list(stock), k=stocksize-total): teststock[addl] += 1
				if not any([teststock[a] > len(cube[cube["color"] == a]) for a in teststock]):
					acceptable = True; stock = teststock
			print(f"Mono: {mono}  Multi: {multi}  Other: {other}  Lands: {lands}")
			print(f"Making packs with {stock}.")
		pool = []
		for color in ["W", "U", "B", "R", "G", "ally", "enemy", "other", "land"]:
			slice = cube[cube["color"] == color]
			pool.append(list(slice.sample(stock[color]).index))
		return divvy(pool, packs)
	
	else: return makePacks(cube, packs, cardsper, "random")

def sealedPacks(cube, scheme):
	"""
	Makes packs for sealed. The idea is to create color-balanced ("ada style")
	packs from the whole cube, then divvy the entire cube. We'll give six packs
	to each player elsewhere.
	"""
	colors = ["W", "U", "B", "R", "G", "ally", "enemy", "other", "land"]
	pool = []
	if scheme == "Adam" and len(cube) == 450: #broken now
		stock = {"W": 53, "U": 53, "B": 53, "R": 53, "G": 53, \
				"ally": 45, "enemy": 45, 'other': 48, 'land': 47}
	else:
		total = 450
		stock = {}
		
		mono = int( (450/len(cube)) * len(cube[cube["color"].isin(["W", "U", "B", "R", "G"])])/5)
		total -= mono*5
		print(f"Taking {mono} of each color, {total} to go.")
		for color in ["W", "U", "B", "R", "G"]: stock[color] = mono
		
		multi = int( (450/len(cube)) * len(cube[cube["color"] == "ally"]))
		total -= multi*2
		print(f"Taking {multi} allies and enemies, {total} to go.")
		for color in ["ally", "enemy"]: stock[color] = multi
		
		lands = int( (450/len(cube)) * len(cube[cube["color"] == "land"]))
		other = int( (450/len(cube)) * len(cube[cube["color"] == "other"]))
		total -= lands; total -= other
		print(f"Taking {lands} lands and {other} other, {total} to go.")
		stock["land"] = lands; stock["other"] = other
		
		for addl in choices(list(stock), k=total): stock[addl] += 1
#	print(stock)
	for color in colors:
		slice = cube[cube["color"] == color]
		pool.append(list(slice.sample(stock[color]).index))
	return divvy(pool, 30)

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
	return [Pack(sorted(pack)) for pack in packlists]

def makeKey():
	"""
	Returns a random four-character string.
	"""
	return hex(randrange(16**3, 16**4)).split('x')[1].upper()