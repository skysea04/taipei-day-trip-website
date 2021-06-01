from flask import *
import os
from dotenv import load_dotenv
from models import db

load_dotenv()
mysql_user = os.getenv("mysql_user")
mysql_password = os.getenv("mysql_password")
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["SECRET_KEY"] = os.urandom(24).hex()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_user}:{mysql_password}@localhost:3306/taipei_trip"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping":True}

db.init_app(app)

from api.attraction import appAttraction
from api.booking import appBooking
from api.order import appOrder
from api.user import appUser

#Api
app.register_blueprint(appAttraction, url_prefix='/api')
app.register_blueprint(appBooking, url_prefix='/api')
app.register_blueprint(appOrder, url_prefix='/api')
app.register_blueprint(appUser, url_prefix='/api')

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
@app.route('/member')
def memeber():
	return render_template("member.html")

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=3000, debug=True)