from flask import *
import sys
sys.path.append("..")
from mysql_connect import cursor, db

appOrder = Blueprint('appOrder', __name__)