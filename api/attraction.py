from flask import *
import sys
sys.path.append("..")
from models import Attraction

appAttraction = Blueprint('appAttraction', __name__)

def select_attraction(first_index, keyword=None):
	if keyword == None:
		result = Attraction.query.limit(12).offset(first_index).all()
	else:
		result = Attraction.query.filter(Attraction.name.like(f'%{keyword}%')).limit(12).offset(first_index).all()
	# attrs為本次搜尋所有景點資料的陣列
	attraction_list = []
	for attr in result:
		temp_attr = {c.name: getattr(attr, c.name) for c in attr.__table__.columns}
		attraction_list.append(temp_attr)
	
	return attraction_list

@appAttraction.route('/attractions')
def api_attractions():
	try:
		if request.args.get('page'):
			page = int(request.args.get('page'))
			first_index = page * 12
			next_page = page + 1

			# 有keyword
			if request.args.get('keyword'):
				keyword =request.args.get('keyword')
				attraction_list = select_attraction(first_index, keyword)
				next_page_list = select_attraction(first_index, keyword)
				#如果下一頁的陣列是空值，代表本次的搜尋是最後一頁，next_page返回null
				if len(next_page_list) == 0:
					next_page = None
				attractions = {
					"nextPage": next_page,
					"data": attraction_list
				}
				return jsonify(attractions)
			
			# 沒有keyword
			else:
				attraction_list = select_attraction(first_index)
				next_page_list = select_attraction(first_index+12)
				#如果下一頁的陣列是空值，代表本次的搜尋是最後一頁，next_page返回null
				if len(next_page_list) == 0:
					next_page = None
				attractions = {
					"nextPage": next_page,
					"data": attraction_list
				}
				return jsonify(attractions)

	# 伺服器（資料庫）連線失敗			
	except:
		return {
			"error": True,
			"message": "伺服器內部錯誤"
		}, 500

@appAttraction.route('/attraction/<int:attractionId>')
def api_attraction(attractionId):
	try:
		if attractionId:
			attr = Attraction.query.filter_by(id=attractionId).first().as_dict()
			# 有資料時，回傳景點資料
			if attr:
				attraction = {
					"data": attr
				}
				return attraction
			# 景點編號錯誤
			return {
				"error": True,
				"message": "景點編號不正確"
			}, 400
	# 伺服器（資料庫）連線失敗
	except:
		return {
			"error": True,
			"message": "伺服器內部錯誤"
		}, 500
