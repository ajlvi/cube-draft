from operator import itemgetter
import pandas as pd
from sys import argv
import os
import boto3
from botocore.exceptions import ClientError
s3_client = boto3.client("s3")

adam_backs = {"Pursuit of Knowledge": "https://i.imgur.com/f3v6QuK.png", "Write into Being": "https://i.imgur.com/s48jeOw.png", "Taigam's Strike": "https://i.imgur.com/41cLK5q.png", "Savage Punch": "https://i.imgur.com/MBE07lp.png", "Angelic Purge": "https://i.imgur.com/htIuV9C.png", "Trail of Mystery": "https://i.imgur.com/PsXVoU8.png", "The Mending of Dominaria": "https://i.imgur.com/g70POfW.png", "Burst Lightning": "https://c1.scryfall.com/file/scryfall-cards/normal/front/2/d/2dc16614-5cf8-444d-a5ae-cac25018af68.jpg?1562610949"}

adam_alt_art = {"Lhurgoyf": "https://c1.scryfall.com/file/scryfall-cards/normal/front/f/e/fee6d385-d44b-4f1a-beb1-13aeebde063e.jpg?1562943042", "Vexing Arcanix": "https://c1.scryfall.com/file/scryfall-cards/normal/front/0/c/0c9ea118-6a19-4e1b-aa5a-9b2729efc096.jpg?1562897452", "Pyrotechnics": "https://c1.scryfall.com/file/scryfall-cards/normal/front/2/6/2646284b-a94d-4c99-98d4-7becbb473e2b.jpg?1562858223", "Gamble": "https://c1.scryfall.com/file/scryfall-cards/normal/front/0/e/0ee0f160-7339-4d98-8a8c-f08889ee52f5.jpg?1562898053", "Greater Good": "https://c1.scryfall.com/file/scryfall-cards/normal/front/1/2/12befd35-2dc6-4852-a153-75b553042643.jpg?1562898942", "Cogwork Librarian": "https://c1.scryfall.com/file/scryfall-cards/normal/front/4/5/453de664-0f09-4772-a626-51d58d1173f3.jpg?1562864968", "Hanna, Ship's Navigator": "https://c1.scryfall.com/file/scryfall-cards/normal/front/8/3/83a4e48d-6452-4245-bdad-63fe3263550e.jpg?1562921669", "Stormbind": "https://c1.scryfall.com/file/scryfall-cards/normal/front/c/2/c2d5d91b-aeb4-4d7e-b748-77f9960da55f.jpg?1562931456", "Phalanx Leader": "https://c1.scryfall.com/file/scryfall-cards/normal/front/9/5/955d5107-5caf-45fc-8c6b-8383bbd220f3.jpg?1562636794"}

def makeRow(l, sc, adam=False):
	#output is card, color, cost, creature 1/0, image, mtgo, back
	#sc is my modified scryfall database from trim.
	mtgo = int(l.split("CatID=\"")[1].split("\"")[0])
	rawn = l.split("Name=\"")[1].split("\"")[0]
	sfall = sc[(sc["mtgo_id"] == mtgo) | (sc["mtgo_foil_id"] == mtgo)]
	if len(sfall) == 1:
		cardser = sfall.iloc[0]
		name = cardser["name"]
#		if name != rawn: print(f"Name mismatch? {name} {rawn}")
		if name == "Gilded Sentinel": name = "Cogwork Librarian"
		cost = cardser["mana_cost"]
		if cardser.isnull()["card_faces"]: #regular card
			image = cardser["normal_image"]
			if name in adam_alt_art: image = adam_alt_art[name]
			back = ''
			if "Eldrazi" in cardser["type_line"]:
				colors = parseColors(cardser["color_identity"])
#				print(f"Eldrazi! {rawn} {colors}")
			else: colors = parseColors(cardser["colors"])
		elif "/" in rawn or cardser["layout"] in ["adventure", "flip"]: #split or adventure
#			print(f"Split! {rawn}")
			image = cardser["normal_image"]
			back = ''
			colors = parseColors(cardser["colors"])
			if cardser["layout"] in ["adventure", "flip"]: #I don't want the other side of these
				name = name.split(" // ")[0]
				cost = cost.split(" // ")[0]
		else: #regular DFC
			name = name.split(" // ")[0]
			cf = eval(cardser['card_faces'])
			image = cf[0]["image_uris"]["normal"]
			back = cf[1]["image_uris"]["normal"]
			front_cost = cf[0]["mana_cost"]
			back_cost = cf[1]["mana_cost"]
			if back_cost != '':
				cost = f'{cf[0]["mana_cost"]} // {cf[1]["mana_cost"]}'
			else: cost = front_cost
			colors = parseColors(cf[0]["colors"])
#			colors = parseColors(cardser['card_faces'][0]["colors"] + cardser['card_faces'][1]["colors"])
		if "Creature" in cardser["type_line"]: is_creat = 1
		else: is_creat = 0
		if "Land" in cardser["type_line"].split("/")[0]:
			colors = "land"; cost = ''; is_creat = 2
		if adam and name in adam_backs: back = adam_backs[name]
	else:
		name = None; colors = None; cost = None; is_creat = None; image = None; back = None
		print(name, colors, cost, is_creat, image, mtgo, back)
	return (name, colors, cost, is_creat, image, mtgo, back)

def parseColors(col):
	out = ""
	for color in ["W", "U", "B", "R", "G"]:
		if color in col: out += color
	if out == "": return "other"
	else: return out

def cmc(row):
	if str(row[2]) == "nan": return 0
	cost = row[2].split("/")[0]
	tot = 0
	for ch in cost: 
		if ch.isdigit(): tot += int(ch)
		elif ch in ["W", "U", "B", "R", "G"]: tot +=1
	return tot

def color_key(row):
	clist = ["W", "U", "B", "R", "G", "WU", "UB", "BR", "RG", "WG", "WB", "BG", "UG", "UR", "WR", "WUB", "UBR", "BRG", "WRG", "WUG", "WBR", "URG", "UBG", "WBG", "WUR", "WUBR", "WUBG", "WURG", "WBRG", "UBRG", "WUBRG", "other", "land"]
	return clist.index(row[1])
	
def creat_sort(row): return 1-row[3]
	
def arrange(rows):
	rows = sorted(rows, key=itemgetter(0)) #sort by name
	rows = sorted(rows, key=cmc) #sort by CMC
	rows = sorted(rows, key=creat_sort) #sort by creatures/non
	rows = sorted(rows, key=color_key) #sort by color identity
	return rows
	
def makeTestTable(rows):
	f = open("check-table.html", 'w')
	f.write("<html><head><title>Test table</title></head><body><table>\n")
	for i in range(len(rows)):
		if i%5 == 0:
			if i > 0: f.write("</tr>\n")
			f.write("<tr>")
		f.write(f'<td><img src="{rows[i][4]}" width=244 height=340></td>')
	f.write("\n</tr></table></body></html>")

def output_df(rows):
	df = pd.DataFrame.from_records(rows, columns=["card", "color", "cost", "creature", "scryfall", "mtgo", "back"])
	for pair in ["WU", "UB", "BR", "RG", "WG"]:
		df["color"] = df["color"].replace(pair, "ally")
	for pair in ["WR", "UR", "UG", "BG", "WB"]:
		df["color"] = df["color"].replace(pair, "enemy")
	for more in ["WUB", "UBR", "BRG", "WRG", "WUG", "WBR", "URG", "UBG", "WBG", "WUR", "WUBR", "WUBG", "WURG", "WBRG", "UBRG", "WUBRG"]:
		df["color"] = df["color"].replace(more, "other")
	return df

def makeCSV(lines, key='', table=False):
	#assuming lines comes from a .dek file
	lines = lines.split("\n")
	adam = False
	if key == "ajlv!i": csvname = "ajlvi_cube"; adam=True
	elif key == "AjeEight": csvname = "andrew_cube"
	elif key == "Gr3zes": csvname = "felix_cube"
	elif key == "R!chCali": csvname = "rich_cube"
	elif key == "SFVC++": csvname = "sfvc_cube"
	else: #password issue
		return {"cards": -1, "skips": [], "outs": [], "ins": []}
	
	#make old cube for comparison
	try:
		old_file = s3_client.download_file("cube-draft-csvs", f"{csvname}.csv", "temp.csv")
		old_cube = pd.read_csv("temp.csv")
	except ClientError:
		old_cube = pd.DataFrame(columns=["card"])

	#do the things
	sfall = pd.read_csv("app/static/scryfall-trimmed.csv")
	rows = [makeRow(i, sfall, adam) for i in lines[4:-1]]
	skips = [r[5] for r in rows if r[0] == None]
	rows = [r for r in rows if r[0] != None]
	srows = arrange(rows)
	new_cube_df = output_df(srows)
	new_cube_df.to_csv(f"{csvname}.csv", header=True, index=False)
	s3_client.upload_file(f"{csvname}.csv", "cube-draft-csvs", f"{csvname}.csv")
	if "temp.csv" in os.listdir("."): os.remove("temp.csv")
	os.remove(f"{csvname}.csv")

#	put some information in the logs
	if len(skips) != 0:
		for skip in skips:
			mtgo = str(skip)
			rel = [line for line in lines if mtgo in line]
			for l in rel: print(f"{mtgo}  {l.strip()}")
	print(f"Done! .csv created from cube with {len(srows)} cards.")
#	if table: makeTestTable(srows)

	#determine card deltas
	outs = [a for a in old_cube["card"].unique() if a not in new_cube_df["card"].unique()]
	ins = [a for a in new_cube_df["card"].unique() if a not in old_cube["card"].unique()]
	return {"cards": len(srows), "skips": skips, "outs": outs, "ins": ins}

if __name__ == '__main__':
	if len(argv) == 3: makeCSV(argv[1], argv[2])
	if len(argv) == 4 and argv[3] == "table": makeCSV(argv[1], argv[2], True)
