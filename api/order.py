from flask import *
import requests, copy, json, sys, re
from datetime import date, timedelta, datetime
sys.path.append("..")
import os
from dotenv import load_dotenv
from models import Attraction, Booking, db

load_dotenv()
partner_key = os.getenv("partner_key")
appOrder = Blueprint('appOrder', __name__)

@appOrder.route('/order', methods = ["GET"])
def get_user_order():
    try:
        if "user" in session:
            user_id = session['user']['id']

            # 找尋所有該使用者的訂單
            bookings = Booking.query\
                .join(Attraction, Attraction.id==Booking.attraction_id)\
                .add_columns(Booking.date, Booking.time, Booking.price, Booking.order_number, Booking.refund, Attraction.name, Attraction.address, Attraction.images)\
                .filter(Booking.user_id == user_id)\
                .filter(Booking.pay.is_(True))\
                .order_by(Booking.id.desc())\
                .all()
            
            # 建立外層陣列、字典
            data_list = []
            order_data = {
                "orderNumber": "",
                "order": [],
                "refund": False
            }

            for booking in bookings:
                booking = booking._asdict()
                order = {
                    "price": booking["price"],
                    "attraction": {
                        "address": booking["address"],
                        "image": booking["images"][0],
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
        if "user" in session:
            # 向TapPay獲取訂單資料
            order_body = json.dumps({
                "partner_key": partner_key,
                "filters": {
                    "order_number": orderNumber
                }
            })
            record_url = 'https://sandbox.tappaysdk.com/tpc/transaction/query'
            headers = {
                'Content-type': 'application/json',
                'x-api-key': partner_key
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
            bookings = Booking.query\
                .join(Attraction, Attraction.id==Booking.attraction_id)\
                .add_columns(Booking.id, Booking.attraction_id, Booking.date, Booking.time, Booking.price, Attraction.name, Attraction.address, Attraction.images)\
                .filter(Booking.order_number == orderNumber)\
                .all()

            # 分別取得該order的booking資訊
            for booking in bookings:
                booking = booking._asdict()
                booking_data = {
                    "id": booking["id"],
                    "attraction": {
                        "id": booking["attraction_id"],
                        "name": booking["name"],
                        "address": booking["address"],
                        "image": booking["images"][0]
                    },
                    "date": booking["date"].strftime("%Y-%m-%d"),
                    "time": booking["time"]
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
        if "user" in session:
            # 整理訂購資訊
            order = request.json
            prime = order["prime"]
            price = order["order"]["price"]
            name = order["order"]["contact"]["name"]
            email = order["order"]["contact"]["email"]
            phone = order["order"]["contact"]["phone"]
            trip_list = order["order"]["trip"]
            total_price = 0
            order_number = datetime.now().strftime('%Y%m%d%H%M%S%f')

            # 從資料庫確認訂購行程的總價格
            for trip in trip_list:
                booking = Booking.query.filter_by(id=trip["id"]).first().as_dict()
                total_price += booking["price"]
            
            # 沒有輸入內容、使用者更動總價格等輸入不正確的狀況
            if (prime == None) or (price != total_price) or (name == None) or (email == None) or  not bool(re.match(r"\A09[0-9]{8}\b", phone)):
                data = {
                    "error": True,
                    "message": "訂單建立失敗，輸入不正確或其他原因"
                }
                return jsonify(data), 400
            
            
            for trip in trip_list:
                # 建立變數
                booking_id = trip["id"]
                # 新增order_number
                update_booking = Booking.query.filter_by(id=booking_id).first()
                update_booking.order_number = order_number
                db.session.commit()
            
            # 建立訂單
            send_prime = json.dumps({
                "prime": prime,
                "partner_key": partner_key,
                "merchant_id": "arcade0425_ESUN",
                "order_number": order_number,
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
                'x-api-key': partner_key
            }
            response = requests.post(pay_url, data=send_prime, headers=headers)
            res = response.json()
            rec_trade_id=res["rec_trade_id"]

            orders = Booking.query.filter_by(order_number=order_number).all()

            # 當回傳結果為付款成功時，回傳建立成功資訊
            if res["status"] == 0:
                for order in orders:
                    order.rec_trade_id = rec_trade_id
                    order.pay = True
                    db.session.commit()

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
            for order in orders:
                order.rec_trade_id = rec_trade_id
                db.session.commit()
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
            # rec_trade_id = ''

            # 如果有任一行程三天內要出發，則不給退款
            three_days_later = date.today() + timedelta(days=3)
            bookings = Booking.query.filter_by(order_number=order_number).all()
            for booking in bookings:
                rec_trade_id = booking.rec_trade_id
                if booking.date < three_days_later:
                    data = {
                        "error": True,
                        "message": "有行程超過退款期限囉，無法進行退款"
                    }
                    return jsonify(data), 400

            # 將退款要求傳送至TapPay並獲取回應
            send_refund = json.dumps({
                "partner_key": partner_key,
                "rec_trade_id": rec_trade_id
            })
            refund_url = 'https://sandbox.tappaysdk.com/tpc/transaction/refund'
            headers = {
                'Content-type': 'application/json',
                'x-api-key': partner_key
            }
            response = requests.post(refund_url, data=send_refund, headers=headers)
            res = response.json()

            # 若回傳退款成功資訊，更動資料庫內容，回傳成功退款訊息
            if res["status"] == 0:
                update_bookings = Booking.query.filter_by(order_number=order_number).all()
                for booking in update_bookings:
                    booking.refund = True
                    db.session.commit()
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