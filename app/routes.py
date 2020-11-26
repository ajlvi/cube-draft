from app import app
from app import draft, player, pack, redis_client
import pandas as pd
from flask import render_template, jsonify, request, redirect, url_for, escape
import json 
import redis

cube = ''

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
	draftcreated = ''
	if 'playerexists' in request.args:
		msg = 'There is already a player in that draft with that name. If it\'s you, submit the form again to rejoin. Otherwise, pick a different name!'
		playername = request.args['name']
		draftid = request.args['id']
		hiddenform = '<input type="hidden" name="rejoin" value="true" />'
	elif 'draftexists' in request.args:
		msg = 'The draft ID you have entered does not appear to exist. Doublecheck the ID and try again.'
		playername = request.args['name']
		draftid = request.args['id']
	elif 'invalidname' in request.args:
		draftid = request.args['id']
		msg = 'Please enter a valid name. (Names cannot be blank.)'
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
		draftid = request.form['id'].upper().strip()
		draftidbit = draftid.encode()
		if r.exists(draftidbit):
			snapshot = json.loads(r.get(draftidbit))
			DraftObj = draft.rebuildDraft(snapshot, cube)
			if playername == '':
				url = '/queue?invalidname=blank&id='+draftid
				return redirect(url)
			elif DraftObj.hasPlayer(playername):
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
		draftid = request.args['draftid'].upper().strip().encode()
		playername = escape(request.args['player'])
		num = int(request.args['pickid'])
		if 'isCogwork' in request.args:
			if request.args['isCogwork'] == 'yes':
				cog = True
			else:
				cog = False
		else:
			cog = False
		if r.exists(draftid):
			try:
				pipe = r.pipeline() #we need to watch the draft id to make sure there aren't collisions
				pickMade = False
				while not pickMade:
					try:
						snapshot = json.loads(r.get(draftid))
						pipe.watch(draftid)
						DraftObj = draft.rebuildDraft(snapshot, cube)
						output = DraftObj.handleIncoming(playername, num, cog)
						newsnapshot = json.dumps(DraftObj.export())
						pipe.multi()
						pipe.set(draftid, newsnapshot)
						pipe.execute()
						pickMade = True
						return jsonify(output) 
					except redis.WatchError: #there was a collision! try again
						print('watch error!!!')
						pass
			except IndexError: #we get here if the player isn't in the draft
				return redirect('/queue')
			except ValueError: #card not in pack!?!?!
				return redirect('/lostandfound')
		else:
		#draft not in alldrafts
			return redirect('/queue')
	elif 'player' in request.form:
		draftid = escape(request.form['draftid']).upper().strip().encode()
		playername = request.form['player']
		num = int(request.form['pickid'])
		if 'isCogwork' in request.form:
			if request.form['isCogwork'] == 'yes':
				cog = True
			else:
				cog = False
		else:
			cog = False
		print(draftid)
		if r.exists(draftid):
			try:
				pipe = r.pipeline() #we need to watch the draft id to make sure there aren't collisions
				pickMade = False
				while not pickMade:
					try:
						snapshot = json.loads(r.get(draftid))
						pipe.watch(draftid)
						DraftObj = draft.rebuildDraft(snapshot, cube)
						output = DraftObj.handleIncoming(playername, num, cog)
						newsnapshot = json.dumps(DraftObj.export())
						pipe.multi()
						pipe.set(draftid, newsnapshot)
						pipe.execute()
						pickMade = True
						return jsonify(output) 
					except redis.WatchError: #there was a collision! try again
						print('watch error!!!')
						pass
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
	global cube
	r = redis_client
	if 'submit' in request.form:
		if request.form['cubes'] == 'ada':
			url = 'app/static/cube.csv'
		elif request.form['cubes'] == 'jason':
			url = 'app/static/jason_cube.csv'
		#as a failsafe for now let's default to ada's cube
		else:
			url = 'app/static/cube.csv'
		cube = pd.read_csv(url)
		newdraft = draft.Draft(cube, int(request.form['packs']), int(request.form['cards']), int(request.form['players']), request.form['packmethod'])
		newdraftkey = newdraft.getKey()
		draftdict = json.dumps(newdraft.export())
		r.set(newdraftkey, draftdict)
		url = '/queue?draftcreated=yes&key='+newdraftkey
		return redirect(url)
	else:
		return redirect('/queue?draftcreated=no')
		
		
