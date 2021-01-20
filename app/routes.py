from app import app
from app import draft, player, pack, cube_parse, redis_client
import pandas as pd
from flask import render_template, jsonify, request, redirect, url_for, escape
import time ; import os
import json 
import redis
import boto3
s3_client = boto3.client("s3")

#url = 'app/static/cube.csv'
#cube = pd.read_csv(url)

@app.route('/')
@app.route('/index')
def index():
	return redirect('/queue')

@app.route('/queue', methods=['GET', 'POST'])
def queue():
	msg = ''
	playername = ''
	draftid = ''
	hiddenform = ''
	draftcreated = ''
	resultmsg = ''
	ins = []
	outs = []
	updated = False
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
		if request.args['invalidname'] == 'blank':
			msg = 'Please enter a valid name.<span class="draft-parameters">(Names cannot be blank.)</span>'
		else:
			msg = 'Please enter a valid name.<span class="draft-parameters">(Names cannot include the special characters >, <, &, ;, &#92;, or ".)</span>'
	elif 'draftcreated' in request.args:
		if request.args['draftcreated'] == 'yes':
			r = redis_client
			draftidbit = request.args['key'].encode()
			snapshot = json.loads(r.get(draftidbit))
			draftcreated = 'Draft has been created with ID ' + request.args['key'] + ' <span class="draft-parameters">[parameters: ' + snapshot['cube_id'] + ', ' + str(snapshot['intended']) + ', ' + str(snapshot['total_packs']) + ', ' + str(snapshot['cards_per_pack']) + ', ' + snapshot['scheme'] + ']</span>'
		else:
			draftcreated = 'Something went wrong. Try again!'
	elif 'submit' in request.form:
		lines = request.form['lines']
		passcode = request.form['passcode']
		deltas = cube_parse.makeCSV(lines, passcode)
		if deltas['cards'] == -1:
			resultmsg = "There was an issue with the passcode. Please try again."
		elif len(deltas['skips']) == 0:
			resultmsg = f"Success! All {str(deltas['cards'])} cards in .dek file stored as cube."
			updated = True
		else:
			resultmsg = "There was an issue with the following IDs:"
			for mtgoid in deltas['skips']:
				resultmsg += f" {mtgoid}, "
			resultmsg = resultmsg[:-2]
			updated = True
		ins = deltas['ins']
		outs = deltas['outs']
	return render_template('queue.html', msg=msg, playername=playername, draftid=draftid, hiddenform=hiddenform, draftcreated=draftcreated, resultmsg=resultmsg, ins=ins, outs=outs, updated=updated)

@app.route('/draftviewer', methods=['GET', 'POST'])
def displaydraft():
	r = redis_client
	if 'submit' in request.form:
		#initialize new player object if it doesn't exist, otherwise find player and draft ids
		playername = request.form['name'].strip().replace("'", "\'")
		badchars = ['<', '>', ';', '&', '"', '\\']
		draftid = request.form['id'].upper().strip()
		draftidbit = draftid.encode()
		if r.exists(draftidbit):
			snapshot = json.loads(r.get(draftidbit))
			cubeid = snapshot['cube_id']
			cubeidbit = cubeid.encode()
			cube = pd.read_json(r.get(cubeidbit))
			DraftObj = draft.rebuildDraft(snapshot, cube)
			if playername == '':
				url = '/queue?invalidname=blank&id='+draftid
				return redirect(url)
			elif any([c in playername for c in badchars]):
				url = '/queue?invalidname=yes&id='+draftid
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
		playername = request.args['player']
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
						pipe.watch(draftid)
						snapshot = json.loads(r.get(draftid))
						cubeid = snapshot['cube_id']
						cubeidbit = cubeid.encode()
						cube = pd.read_json(r.get(cubeidbit))
						DraftObj = draft.rebuildDraft(snapshot, cube)
						output = DraftObj.handleIncoming(playername, num, cog)
						newsnapshot = json.dumps(DraftObj.export())
						pipe.multi()
						pipe.set(draftid, newsnapshot)
						pipe.execute()
						pickMade = True
#						print(time.time()); print(DraftObj) #debug line
						return jsonify(output) 
					except redis.WatchError: #there was a collision! try again
						print('watch error!!!')
						pass
			except IndexError: #we get here if the player isn't in the draft
				return 'https://ajlvi-cube-draft.herokuapp.com/queue'
			except (ValueError, AttributeError) as e: #card not in pack -- happens with rapid double-selects
				#check whether the card being picked is the most recent pick by the player
				if DraftObj.lookupByHandle(playername).getChosen()[-1] == num:
					print('Duplicate pick!!')
					output = DraftObj.handleIncoming(playername, -1, cog)
					return jsonify(output)
				else:
					return 'https://ajlvi-cube-draft.herokuapp.com/lostandfound'
		else:
		#draft not in alldrafts
			return 'https://ajlvi-cube-draft.herokuapp.com/queue'
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
						cubeid = snapshot['cube_id']
						cubeidbit = cubeid.encode()
						cube = pd.read_json(r.get(cubeidbit))
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
				return 'https://ajlvi-cube-draft.herokuapp.com/queue'
			except ValueError: #card not in pack!?!?!
				#check whether the card being picked is the most recent pick by the player
				if DraftObj.lookupByHandle(playername).getChosen()[-1] == num:
					print('duplicate pick!!')
					output = DraftObj.handleIncoming(playername, -1, cog)
					return jsonify(output)
				else:
					return 'https://ajlvi-cube-draft.herokuapp.com/queue'
		else:
		#draft not in alldrafts
			return 'https://ajlvi-cube-draft.herokuapp.com/queue'
		
@app.route('/lostandfound')
def lostandfound():
	return render_template('lostandfound.html')
	
@app.route('/newdraft', methods=['POST'])
def newdraft():
	r = redis_client
	if 'submit' in request.form:
		if 'cubes' in request.form:
			if request.form['cubes'] == 'ada':
				fname = 'ajlvi_cube.csv'
				cubeid = 'ajlvi'
			elif request.form['cubes'] == "andrew":
				fname = 'andrew_cube.csv'
				cubeid = 'andrew'
			elif request.form['cubes'] == "felix":
				fname = 'felix_cube.csv'
				cubeid = 'felix'
			elif request.form['cubes'] == "rich":
				fname = 'rich_cube.csv'
				cubeid = 'rich'
			elif request.form['cubes'] == "sfvc":
				fname = 'sfvc_cube.csv'
				cubeid = 'sfvc'
			elif request.form['cubes'] == "cnc":
				fname = 'sfvc_cube.csv'
				cubeid = 'cnc'
#			elif request.form['cubes'] == 'jacob':
#				fname = 'jacob_cube.csv'
#				cubeid = 'jacob'
			else:
				return redirect('/queue?draftcreated=no')
		else:
			return redirect('/queue?draftcreated=no')
		cubefile = s3_client.download_file("cube-draft-csvs", fname, "temp.csv")
		cube = pd.read_csv("temp.csv"); os.remove("temp.csv")

		newdraft = draft.Draft(cube, cubeid, int(request.form['packs']), int(request.form['cards']), int(request.form['players']), request.form['packmethod'])
		newdraftkey = newdraft.getKey()
		draftdict = json.dumps(newdraft.export())
		cubedict = cube.to_json()
		r.set(cubeid, cubedict)
		r.set(newdraftkey, draftdict)
		url = '/queue?draftcreated=yes&key='+newdraftkey
		return redirect(url)
	else:
		return redirect('/queue?draftcreated=no')
		
@app.route('/pickhistory', methods=['GET'])
def pickhistory():
	r = redis_client
	if 'player' in request.args:
		draftid = request.args['draftid'].upper().strip() #should be some sort of error handling if no draft id specified
		playername = request.args['player']
		return render_template('pickhistory.html', playername=playername, draftid=draftid)
		
@app.route('/renderhistory', methods=['GET', 'POST'])
def renderhistory():
	r = redis_client
	if 'player' in request.args:
		draftid = request.args['draftid'].encode() #should be some sort of error handling if no draft id specified
		playername = request.args['player']
		snapshot = json.loads(r.get(draftid)) #should be some sort of error handling if draftid not in database
		cubeid = snapshot['cube_id']
		cubeidbit = cubeid.encode()
		cube = pd.read_json(r.get(cubeidbit))
		DraftObj = draft.rebuildDraft(snapshot, cube)
		output = DraftObj.draftHistory(playername)
		return jsonify(output)
		