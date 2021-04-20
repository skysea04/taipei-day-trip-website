from flask import *
from mysql_connect import cursor, db, select_attraction

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True


# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")


#Api
@app.route('/api/attractions')
def api_attractions():
	if request.args.get('page'):
		page = int(request.args.get('page'))
		if request.args.get('keyword'):
			keyword =request.args.get('keyword')
			attraction_list = select_attraction(page, f"SELECT * FROM attraction WHERE name like '%{keyword}%' ")
			if len(attraction_list)>0:
				attractions = {
					"nextPage": page+1,
					"data": attraction_list
				}
				return jsonify(attractions)
		else:
			[attraction_list, last_page] = select_attraction(page, "SELECT * FROM attraction")
			
			attractions = {
				"nextPage": None if last_page else page+1,
				"data": attraction_list
			}
			return jsonify(attractions)
	return {
		"error": True,
		"message": "伺服器內部錯誤"
	}, 500

@app.route('/api/attraction/<int:attractionId>')
def api_attraction(attractionId):
	if attractionId:
		cursor.execute(f"SELECT * FROM attraction where id={attractionId}")
		attr = cursor.fetchone()
		if attr:
			attraction = {
				"data": dict(zip(cursor.column_names, attr))
			}
			attraction['data']['images'] = json.loads(attr[9])
			return attraction
		return {
			"error": True,
			"message": "景點編號不正確"
		}, 400
	return {
		"error": True,
		"message": "伺服器內部錯誤"
	}, 500


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=3000)