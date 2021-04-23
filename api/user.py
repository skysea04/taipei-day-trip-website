from flask import *
import sys
sys.path.append("..")
from mysql_connect import cursor, db

appUser = Blueprint('appUser', __name__)