from app import app
from app import draft, player, pack, redis_client
import pandas as pd
from flask import render_template, jsonify, request, redirect, url_for, escape
import json 

url = 'app/static/cube.csv'
cube = pd.read_csv(url)


testDict = {'key': 'DA50', 
'handles': ['bekka', 'ada', 'squiggs'], 
'intended': 3, 
'total_packs': 3, 
'cards_per_pack': 15, 
'scheme': 'random',
'currentPack': 1, 
'fullyDrafted': 0, 
'player_info': {'bekka': {'queue': [], 'unopened': [[83, 89, 98, 106, 216, 249, 262, 294, 322, 328, 362, 374, 382, 384, 415], [59, 74, 75, 123, 154, 167, 213, 226, 243, 247, 289, 331, 333, 373, 438]], 'chosen': [103], 'active': None, 'opentime': 1590763607.0334032},
'ada': {'queue': [], 'unopened': [[37, 65, 136, 164, 174, 240, 251, 264, 270, 321, 324, 326, 375, 420, 448], [33, 51, 129, 138, 144, 198, 237, 292, 301, 337, 348, 359, 364, 393, 439]], 'chosen': [], 'active': [14, 43, 55, 118, 130, 188, 211, 230, 256, 261, 311, 323, 344, 407, 417], 'opentime': 1590763607.0334032},
'squiggs': {'queue': [[8, 80, 115, 160, 161, 197, 245, 248, 281, 330, 343, 353, 391, 440]], 'unopened': [[40, 77, 96, 146, 158, 183, 187, 204, 218, 222, 238, 260, 266, 300, 400], [6, 9, 18, 23, 38, 87, 107, 199, 202, 239, 263, 312, 313, 342, 345]], 'chosen': [], 'active': [12, 88, 122, 170, 252, 253, 257, 268, 306, 310, 351, 383, 395, 416, 429], 'opentime': 1590763607.0334032}} }

@app.route('/')
@app.route('/index')
def index():
	return redirect('/queue')

@app.route('/queue', methods=['GET'])
def queue():
	msg = ''
	playername = ''
	draftid = ''
	hiddenform = ''
	if 'playerexists' in request.args:
		msg = 'There is already a player in that draft with that name. If it\'s you, submit the form again to rejoin. Otherwise, pick a different name!'
		playername = request.args['name']
		draftid = request.args['id']
		hiddenform = '<input type="hidden" name="rejoin" value="true" />'
	elif 'draftexists' in request.args:
		msg = 'The draft ID you have entered does not appear to exist. Doublecheck the ID and try again.'
		playername = request.args['name']
		draftid = request.args['id']
	elif 'draftcreated' in request.args:
		if request.args['draftcreated'] == 'yes':
			draftcreated = 'Draft has been created with ID ' + request.args['key']
	return render_template('queue.html', msg=msg, playername=playername, draftid=draftid, hiddenform=hiddenform, draftcreated=draftcreated)

@app.route('/draftviewer', methods=['GET', 'POST'])
def displaydraft():
	r = redis_client
	if 'submit' in request.form:
		#initialize new player object if it doesn't exist, otherwise find player and draft ids
		playername = request.form['name'] #sanitize this here
		draftid = request.form['id']
		draftidbit = draftid.encode()
		if r.exists(draftidbit):
			snapshot = json.loads(r.get(draftidbit))
			DraftObj = draft.rebuildDraft(snapshot, cube)
			if DraftObj.hasPlayer(playername):
				if 'rejoin' in request.form:
					pass
				else: 
					url = '/queue?playerexists=yes&name='+playername+'&id='+draftid
					return redirect(url)
			else:
				DraftObj.addPlayer(playername)
				newsnapshot = json.dumps(DraftObj.export())
				r.set(draftidbit, newsnapshot)
				#RETURN SOMETHING TO PLAYER HERE?
		else:
			#"fail case" coding here -- draft didn't exist
			url = '/queue?draftexists=no&name='+playername+'&id='+draftid
			return redirect(url)
		return render_template('draftviewer.html', draftid=draftid, player=playername) #other inputs here? I dunno, basically this should just display the main draft page.
	else: 
		return redirect('/lostandfound')

@app.route('/makepick', methods=['GET', 'POST'])
def makepick():
	r = redis_client
	if 'player' in request.args:
		draftid = request.args['draftid'].encode()
		playername = escape(request.args['player'])
		num = int(request.args['pickid'])
		print(num)
		if r.exists(draftid):
			try:
				snapshot = json.loads(r.get(draftid))
				DraftObj = draft.rebuildDraft(snapshot, cube)
				output = DraftObj.handleIncoming(playername, num)
				newsnapshot = json.dumps(DraftObj.export())
				r.set(draftid, newsnapshot)
				return jsonify(output)
			except IndexError: #we get here if the player isn't in the draft
				return redirect('/queue')
			except ValueError: #card not in pack!?!?!
				return redirect('/lostandfound')
		else:
		#draft not in alldrafts
			return redirect('/queue')
	elif 'player' in request.form:
		draftid = escape(request.form['draftid']).encode()
		playername = request.form['player']
		num = int(request.form['pickid'])
		print(draftid)
		if r.exists(draftid):
			try:
				snapshot = json.loads(r.get(draftid))
				DraftObj = draft.rebuildDraft(snapshot, cube)
				output = DraftObj.handleIncoming(playername, num)
				newsnapshot = json.dumps(DraftObj.export())
				r.set(draftid, newsnapshot)
				return jsonify(output)
			except IndexError: #we get here if the player isn't in the draft
				return redirect('/queue')
			except ValueError: #card not in pack!?!?!
				return redirect('/lostandfound')
		else:
		#draft not in alldrafts
			return redirect('/queue')		
	else:
		return redirect('/queue')
		
@app.route('/lostandfound')
def lostandfound():
	return render_template('lostandfound.html')
	
@app.route('/newdraft', methods=['POST'])
def newdraft():
	r = redis_client
	if 'submit' in request.form:
		newdraft = draft.Draft(cube, int(request.form['packs']), int(request.form['cards']), int(request.form['players']), request.form['packmethod'])
		newdraftkey = newdraft.getKey()
		draftdict = json.dumps(newdraft.export())
		r.set(newdraftkey, draftdict)
		url = '/queue?draftcreated=yes&key='+newdraftkey
		return redirect('url')
	else:
		return redirect('/queue?draftcreated=no')
		
		
