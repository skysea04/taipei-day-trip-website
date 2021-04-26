from flask import *
import sys
sys.path.append("..")
from mysql_connect import cursor, db

appBooking = Blueprint('appBooking', __name__)