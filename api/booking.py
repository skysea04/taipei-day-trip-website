from flask import *
import sys
sys.path.append("..")
from mysql_connect import cursor, db, db_insert, db_select

appBooking = Blueprint('appBooking', __name__)

@appBooking.route('/booking', methods=["GET"])
def get_booking():
    try:
        db.reconnect(attempts=1, delay=0)
        if "user" in session:
            booking_list = []
            user_id = session["user"]["id"]
            sql = f'SELECT booking.id, attraction_id, name, address, images, date, time, price FROM booking INNER JOIN attraction WHERE user_id={user_id} AND pay=0 AND booking.attraction_id=attraction.id'
            cursor.execute(sql)
            bookings = cursor.fetchall()
            for booking in bookings:
                booking_data = dict(zip(cursor.column_names, booking))
                book_data = {
                    "id": booking_data["id"],
                    "attraction": {
                        "id": booking_data["attraction_id"],
                        "name": booking_data["name"],
                        "address": booking_data["address"],
                        "image": json.loads(booking_data["images"])[0]
                    },
                    "date": booking_data["date"].strftime("%Y-%m-%d"),
                    "time": booking_data["time"],
                    "price": booking_data["price"]
                }
                booking_list.append(book_data)

            data = {
                "data": booking_list
            }
            return jsonify(data)
                
        data = {
            "error": True,
            "message": "未登入系統，操作失敗"
        }
        return jsonify(data)
    except:
        data = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(data), 500


@appBooking.route('/booking', methods=["POST"])
def post_booking():
    try:
        db.reconnect(attempts=1, delay=0)
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
    try:
        db.reconnect(attempts=1, delay=0)
        if "user" in session:
            delete_id = request.json["id"]
            sql = f'DELETE FROM booking WHERE id={delete_id}'
            cursor.execute(sql)
            db.commit()
            data = {"ok": True}
            return jsonify(data)
        data = {
            "error": True,
            "message": "未登入系統，操作失敗"
        }
        return jsonify(data), 403
    except:
        data = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(data), 500
