from app import app
from app import draft, player, pack
import pandas as pd
from flask import render_template, jsonify, request, redirect, url_for, escape

url = 'app/static/cube.csv'
cube = pd.read_csv(url)

current_state = {'draft_key': '7162', 'my_name': 'bekka', 'my_status': 1, 'drafters': ['squigs', 'ada', 'bekka'], 'status': [1, 2, 1], 'packno': 1, 'total_packs': 3, 'cards_per_pack': 15, 'time_remaining': 10, 'chosen_cards': [113], 'chosen_df': '{"card":{"113":"Vile Manifestation"},"color":{"113":"B"},"cost":{"113":"{1}{B}"},"creature":{"113":1},"scryfall":{"113":"https:\\/\\/img.scryfall.com\\/cards\\/normal\\/front\\/7\\/1\\/7160bc31-bdfa-4654-9d69-95ee2a5fe870.jpg?1562803268"},"mtgo":{"113":64644}}', 'current_pack': [113], 'current_df': '{"card":{"113":"Vile Manifestation"},"color":{"113":"B"},"cost":{"113":"{1}{B}"},"creature":{"113":1},"scryfall":{"113":"https:\\/\\/img.scryfall.com\\/cards\\/normal\\/front\\/7\\/1\\/7160bc31-bdfa-4654-9d69-95ee2a5fe870.jpg?1562803268"},"mtgo":{"113":64644}}'}

alldrafts = {}

DTest = draft.Draft(cube, 3, 15, intended=3, scheme="Adam")
DTest.addPlayer("ada")
DTest.addPlayer("squiggs")
DTest.key = "TEST"
alldrafts["TEST"] = DTest

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
	return render_template('queue.html', msg=msg, playername=playername, draftid=draftid, hiddenform=hiddenform)

@app.route('/draftviewer', methods=['GET', 'POST'])
def displaydraft():
	if 'submit' in request.form:
		#initialize new player object if it doesn't exist, otherwise find player and draft ids
		playername = request.form['name'] #sanitize this here
		draftid = request.form['id']
		if draftid in alldrafts:
			DraftObj = alldrafts[draftid]
			if DraftObj.hasPlayer(playername):
				if 'rejoin' in request.form:
					pass
				else: 
					url = '/queue?playerexists=yes&name='+playername+'&id='+draftid
					return redirect(url)
			else:
				DraftObj.addPlayer(playername)
				#RETURN SOMETHING TO PLAYER HERE?
		else:
			#"fail case" coding here -- draft didn't exist
			url = '/queue?draftexists=no&player='+playername+'id='+draftid
			return redirect(url)
		return render_template('draftviewer.html', draftid=draftid, player=playername) #other inputs here? I dunno, basically this should just display the main draft page.
	else: 
		return redirect('/lostandfound')

@app.route('/makepick', methods=['GET', 'POST'])
def makepick():
	if 'player' in request.args:
		draftid = request.args['draftid']
		playername = escape(request.args['player'])
		num = int(request.args['pickid'])
		print(num)
		if draftid in alldrafts:
			try:
				DraftObj = alldrafts[draftid]
				output = DraftObj.handleIncoming(playername, num)
				return jsonify(output)
			except IndexError: #we get here if the player isn't in the draft
				return redirect('/queue')
			except ValueError: #card not in pack!?!?!
				return redirect('/lostandfound')
		else:
		#draft not in alldrafts
			return redirect('/queue')
	elif 'player' in request.form:
		draftid = escape(request.form['draftid'])
		playername = request.form['player']
		num = int(request.form['pickid'])
		if draftid in alldrafts:
			try:
				DraftObj = alldrafts[draftid]
				output = DraftObj.handleIncoming(playername, num)
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