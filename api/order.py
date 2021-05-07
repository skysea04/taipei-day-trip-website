from flask import *
import requests
import json
import sys
sys.path.append("..")
from mysql_connect import cursor, db, db_insert, db_select

appOrder = Blueprint('appOrder', __name__)

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
            sql = f'SELECT * FROM orders where order_number="{orderNumber}"'
            cursor.execute(sql)
            orders = cursor.fetchall()
            # 分別取得該order的booking資訊
            for order in orders:
                sql = f'SELECT booking.id, attraction_id, name, address, images, date, time, price FROM booking INNER JOIN attraction WHERE booking.id={order[2]} AND booking.attraction_id=attraction.id'
                cursor.execute(sql)
                booking = cursor.fetchone()
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
            # 整理訂購資訊
            order = request.json
            prime = order["prime"]
            price = order["order"]["price"]
            name = order["order"]["contact"]["name"]
            email = order["order"]["contact"]["email"]
            phone = order["order"]["contact"]["phone"]

            total_price = 0

            # 從資料庫確認訂購行程的總價格
            for i in range(len(order["order"]["trip"])):
                booking = db_select("booking", id=order["order"]["trip"][i]["id"])
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
                for trip in order["order"]["trip"]:
                    # 建立變數
                    booking_id = trip["id"]
                    order_number=res["rec_trade_id"]

                    # 更動資料庫
                    sql = f'UPDATE booking SET pay=1 WHERE id={booking_id}'
                    cursor.execute(sql)
                    db.commit()
                    db_insert("orders", order_number=order_number, booking_id=booking_id)
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

