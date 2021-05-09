from flask import *
import requests
import copy
import json
import sys
from datetime import date, timedelta
sys.path.append("..")
from mysql_connect import cursor, db, db_insert, db_select

appOrder = Blueprint('appOrder', __name__)

@appOrder.route('/order', methods = ["GET"])
def get_user_order():
    try:
        db.reconnect(attempts=1, delay=0)
        if "user" in session:
            user_id = session['user']['id']

            # 找尋所有該使用者的訂單
            cursor = db.cursor(dictionary=True)
            sql = f'SELECT name, address, images, date, time, price, order_number, refund FROM booking INNER JOIN attraction WHERE user_id={user_id} AND order_number IS NOT NULL AND booking.attraction_id=attraction.id ORDER BY booking.id DESC'
            cursor.execute(sql)
            bookings = cursor.fetchall()
            
            # 建立外層陣列、字典
            data_list = []
            order_data = {
                "orderNumber": "",
                "order": [],
                "refund": False
            }

            for booking in bookings:
                order = {
                    "price": booking["price"],
                    "attraction": {
                        "address": booking["address"],
                        "image": json.loads(booking["images"])[0],
                        "name": booking["name"]
                    },
                    "date": booking["date"].strftime("%Y-%m-%d"),
                    "time": booking["time"]
                }
                # 深拷貝！！避免參照都傳入最後一個booking的資料
                temp_data = copy.deepcopy(order_data)

                # 如果orderNumber和上一筆資料相同，多加入order行程的部分進入order array就好
                if temp_data["orderNumber"] == booking["order_number"]:
                    data_list.pop()
                    temp_data["order"].insert(0, order)
                # 建立一筆新的order_data
                else:
                    temp_data["order"].clear()
                    temp_data["orderNumber"] = booking["order_number"]
                    temp_data["order"].append(order)
                    temp_data["refund"] = booking["refund"]
                
                data_list.append(temp_data)
                order_data = temp_data
            
            if data_list == []:
                data_list = None

            data = {"data": data_list}
            return jsonify(data)
        # 沒有登入       
        data = {
            "error": True,
            "message": "未登入系統，操作失敗"
        }
        return jsonify(data), 403
    # 伺服器（資料庫）連線失敗
    except:
        data = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(data), 500
    
        

@appOrder.route('/order/<orderNumber>', methods=["GET"])
def get_order(orderNumber):
    try:
        db.reconnect(attempts=1, delay=0)
        if "user" in session:

            # 向TapPay獲取訂單資料
            order_body = json.dumps({
                "partner_key": 'partner_SwRrjaapkdWe1yKzV596Gr9HRTr9ymx9TossfP7XFooQ5t18nMlzhPFF',
                "filters": {
                    "rec_trade_id": orderNumber
                }
            })
            record_url = 'https://sandbox.tappaysdk.com/tpc/transaction/query'
            headers = {
                'Content-type': 'application/json',
                'x-api-key': 'partner_SwRrjaapkdWe1yKzV596Gr9HRTr9ymx9TossfP7XFooQ5t18nMlzhPFF'
            }
            response = requests.post(record_url, data=order_body, headers=headers)
            res = response.json()


            # 沒有這筆訂單的情況
            if res["number_of_transactions"] == 0:
                data = {
                    "data": None
                }
                return jsonify(data), 400
            
            # 有訂單的情況
            booking_list = []
            # 尋找每個order_number是orderNumber的order
            sql = f'SELECT booking.id, attraction_id, name, address, images, date, time, price FROM booking INNER JOIN attraction WHERE order_number="{orderNumber}" AND booking.attraction_id=attraction.id'
            cursor.execute(sql)
            bookings = cursor.fetchall()
            # 分別取得該order的booking資訊
            for booking in bookings:
        
                booking_dict = dict(zip(cursor.column_names, booking))
                booking_data = {
                    "id": booking_dict["id"],
                    "attraction": {
                        "id": booking_dict["attraction_id"],
                        "name": booking_dict["name"],
                        "address": booking_dict["address"],
                        "image": json.loads(booking_dict["images"])[0]
                    },
                    "date": booking_dict["date"].strftime("%Y-%m-%d"),
                    "time": booking_dict["time"]
                }
                # 將行程加入list
                booking_list.append(booking_data)

            order_record = res["trade_records"][0]
            data = {
                "data": {
                    "number": orderNumber,
                    "price": order_record["amount"],
                    "trip": booking_list,
                    "contact": {
                        "name": order_record["cardholder"]["name"],
                        "email": order_record["cardholder"]["email"],
                        "phone": order_record["cardholder"]["phone_number"]
                    },
                    "status": 1
                }
            }
            return jsonify(data)
        # 沒有登入       
        data = {
            "error": True,
            "message": "未登入系統，操作失敗"
        }
        return jsonify(data), 403
    # 伺服器（資料庫）連線失敗
    except:
        data = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(data), 500


@appOrder.route('/order', methods=["POST"])
def post_order():
    try:
        db.reconnect(attempts=1, delay=0)
        if "user" in session:
            user_id = session["user"]["id"]
            # 整理訂購資訊
            order = request.json
            prime = order["prime"]
            price = order["order"]["price"]
            name = order["order"]["contact"]["name"]
            email = order["order"]["contact"]["email"]
            phone = order["order"]["contact"]["phone"]
            trip_list = order["order"]["trip"]

            total_price = 0

            # 從資料庫確認訂購行程的總價格
            for trip in trip_list:
                booking = db_select("booking", id=trip["id"])
                total_price += booking["price"]
            
            # 沒有輸入內容、使用者更動總價格等輸入不正確的狀況
            if (prime == None) or (price != total_price) or (name == None) or (email == None) or (phone == None):
                data = {
                    "error": True,
                    "message": "訂單建立失敗，輸入不正確或其他原因"
                }
                return jsonify(data), 400
            
            # 建立訂單
            send_prime = json.dumps({
                "prime": prime,
                "partner_key": "partner_SwRrjaapkdWe1yKzV596Gr9HRTr9ymx9TossfP7XFooQ5t18nMlzhPFF",
                "merchant_id": "arcade0425_ESUN",
                "details":"一日遊行程",
                "amount": price,
                "cardholder": {
                    "phone_number": phone,
                    "name": name,
                    "email": email
                },
                "remember": False
            })

            # 將訂單傳送至TapPay並獲取回應
            pay_url = 'https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime'
            headers = {
                'Content-type': 'application/json',
                'x-api-key': 'partner_SwRrjaapkdWe1yKzV596Gr9HRTr9ymx9TossfP7XFooQ5t18nMlzhPFF'
            }
            response = requests.post(pay_url, data=send_prime, headers=headers)
            res = response.json()

            # 當回傳結果為付款成功時，回傳建立成功資訊
            if res["status"] == 0:
                for trip in trip_list:
                    # 建立變數
                    booking_id = trip["id"]
                    order_number=res["rec_trade_id"]

                    # 更動資料庫
                    sql = f'UPDATE booking SET order_number="{order_number}" WHERE id={booking_id}'
                    cursor.execute(sql)
                    db.commit()
                data = {
                    "data":{
                        "number": order_number,
                        "payment": {
                            "status": 0,
                            "message": "付款成功"
                        }
                    }
                }
                return jsonify(data)

            # TapPay回傳失敗資訊
            data = {
                "data":{
                    "number": order_number,
                    "payment": {
                        "status": res["status"],
                        "message": "付款失敗"
                    }
                }
            }
            return jsonify(data)

        # 沒有登入
        data = {
            "error": True,
            "message": "未登入系統，操作失敗"
        }
        return jsonify(data), 403

    # 伺服器（資料庫）連線失敗
    except:
        data = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(data), 500

@appOrder.route('/order', methods=["DELETE"])
def delete_order():
    try:
        if "user" in session:
            user_id = session["user"]["id"]
            order_number = request.json["orderNumber"]

            # 如果有任一行程三天內要出發，則不給退款
            three_days_later = date.today() + timedelta(days=3)
            cursor = db.cursor(dictionary=True)
            sql = f'SELECT date FROM booking WHERE order_number="{order_number}"'
            cursor.execute(sql)
            bookings = cursor.fetchall()
            for booking in bookings:
                if booking["date"] < three_days_later:
                    data = {
                        "error": True,
                        "message": "有行程超過退款期限囉，無法進行退款"
                    }
                    return jsonify(data), 400

            # 將退款要求傳送至TapPay並獲取回應
            send_refund = json.dumps({
                "partner_key": "partner_SwRrjaapkdWe1yKzV596Gr9HRTr9ymx9TossfP7XFooQ5t18nMlzhPFF",
                "rec_trade_id": order_number
            })
            refund_url = 'https://sandbox.tappaysdk.com/tpc/transaction/refund'
            headers = {
                'Content-type': 'application/json',
                'x-api-key': 'partner_SwRrjaapkdWe1yKzV596Gr9HRTr9ymx9TossfP7XFooQ5t18nMlzhPFF'
            }
            response = requests.post(refund_url, data=send_refund, headers=headers)
            res = response.json()

            # 若回傳退款成功資訊，更動資料庫內容，回傳成功退款訊息
            if res["status"] == 0:
                sql = f'UPDATE booking SET refund=true WHERE order_number="{order_number}"'
                cursor.execute(sql)
                db.commit()
                data = {
                    "ok": True,
                    "message": "退款成功！"
                }
                return jsonify(data)
            
            # 退款失敗
            data = {
                "error": True,
                "message": "退款失敗，若有問題請洽詢客服人員"
            }
            return jsonify(data), 400
            
        # 沒有登入
        data = {
            "error": True,
            "message": "未登入系統，操作失敗"
        }
        return jsonify(data), 403
    # 伺服器（資料庫）連線失敗
    except:
        data = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(data), 500