from app import app
from flask import render_template, jsonify, request, redirect 

current_state = {'draft_key': '7162', 'my_name': 'bekka', 'my_status': 1, 'drafters': ['squigs', 'ada', 'bekka'], 'status': [1, 2, 1], 'packno': 1, 'total_packs': 3, 'cards_per_pack': 15, 'time_remaining': 10, 'chosen_cards': [113], 'chosen_df': '{"card":{"113":"Vile Manifestation"},"color":{"113":"B"},"cost":{"113":"{1}{B}"},"creature":{"113":1},"scryfall":{"113":"https:\\/\\/img.scryfall.com\\/cards\\/normal\\/front\\/7\\/1\\/7160bc31-bdfa-4654-9d69-95ee2a5fe870.jpg?1562803268"},"mtgo":{"113":64644}}', 'current_pack': [113], 'current_df': '{"card":{"113":"Vile Manifestation"},"color":{"113":"B"},"cost":{"113":"{1}{B}"},"creature":{"113":1},"scryfall":{"113":"https:\\/\\/img.scryfall.com\\/cards\\/normal\\/front\\/7\\/1\\/7160bc31-bdfa-4654-9d69-95ee2a5fe870.jpg?1562803268"},"mtgo":{"113":64644}}'}

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/enterdraft', methods=['POST'])
def newplayer():
	# name stored under request.form['name']. this should add the player to the current draft (I could have this post the draft ID too if useful).
	return redirect('/draft')


@app.route('/queue')
def queue():
	#should define players = list of current players, id = draft id 
	return render_template('queue.html', players=players, id=id)

@app.route('/draftviewer', methods=['GET', 'POST'])
def displaydraft():
	return render_template('draftviewer.html') #other inputs here? I dunno, basically this should just display the main draft page.

@app.route('/makepick', methods=['GET', 'POST'])
#here be a function that accepts incoming queries from players and returns a bunch of json
def makepick():
	return jsonify(current_state)