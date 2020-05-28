from app import app
from app import draft, player, pack
import pandas as pd
from flask import render_template, jsonify, request, redirect, url_for

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
	return render_template('index.html')

@app.route('/queue')
def queue():
#should have a create draft button and a join draft form
	return render_template('queue.html')

@app.route('/draftviewer', methods=['GET', 'POST'])
def displaydraft():
	if request.form['submit'] != '':
		#initialize new player object if it doesn't exist, otherwise find player and draft ids
		playername = request.form['name'] #sanitize this here
		draftid = request.form['id']
		if draftid in alldrafts:
			DraftObj = alldrafts[draftid]
			if DraftObj.hasPlayer(playername):
				#"fail case" coding here -- player existed
				pass
			else:
				DraftObj.addPlayer(playername)
				print(alldrafts["TEST"])
				#RETURN SOMETHING TO PLAYER HERE?
		else:
			#"fail case" coding here -- draft didn't exist
			pass
		return render_template('draftviewer.html', draftid=draftid, player=playername) #other inputs here? I dunno, basically this should just display the main draft page.
	else: 
		return redirect('/lostandfound')

@app.route('/makepick', methods=['GET', 'POST'])
#here be a function that accepts incoming queries from players and returns a bunch of json
def makepick():
	if request.args['player'] != '':
		draftid = request.args['draftid']
		playername = request.args['player']
		num = int(request.args['pickid'])
		print(num)
		if draftid in alldrafts:
			try:
				DraftObj = alldrafts[draftid]
				output = DraftObj.handleIncoming(playername, num)
				return jsonify(output)
			except IndexError: #we get here if the player isn't in the draft
				pass
			except ValueError: #card not in pack!?!?!
				pass
		else:
		#draft not in alldrafts
			pass
	elif request.form['player'] != '':
		draftid = request.form['draftid']
		playername = request.form['player']
		num = int(request.form['pickid'])
		if draftid in alldrafts:
			try:
				DraftObj = alldrafts[draftid]
				output = DraftObj.handleIncoming(playername, num)
				return jsonify(output)
			except IndexError: #we get here if the player isn't in the draft
				pass
			except ValueError: #card not in pack!?!?!
				pass
		else:
		#draft not in alldrafts
			pass		
	else:
		return redirect('/queue')