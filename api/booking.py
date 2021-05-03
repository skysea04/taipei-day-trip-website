from flask import *
import sys
sys.path.append("..")
from mysql_connect import cursor, db, db_insert, db_select

appBooking = Blueprint('appBooking', __name__)

@appBooking.route('/booking', methods=["GET"])
def get_booking():
    return 0


@appBooking.route('/booking', methods=["POST"])
def post_booking():
    try:
        if 'user' in session:
            user_id = session["user"]["id"]
            booking = request.json
            attraction_id = booking["attractionId"]
            date = booking["date"]
            time = booking["time"]
            price = booking["price"]
            if attraction_id and date and ((time == 'morning' and price == 2000) or (time == 'afternoon' and price == 2500)):
                # 建立行程成功
                db_insert("booking", user_id=user_id, attraction_id=attraction_id, date=date, time=time, price=price)
                data = {"ok": True}
                return jsonify(data)
            # 輸入內容有誤
            data = {
                "error": True,
                "message": "行程建立失敗，輸入不正確或其他原因"
            }
            return jsonify(data), 400
        # 沒有登入
        data = {
            "error": True,
            "message": "未登入系統，行程建立失敗"
        }
        return jsonify(data), 403
    # 伺服器（資料庫）連線失敗
    except:
        data = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(data), 500


@appBooking.route('/booking', methods=["DELETE"])
def delete_booking():
    return 0
