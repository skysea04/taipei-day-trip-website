import mysql.connector
from config import Config
import json

db = mysql.connector.connect(
        host='localhost',
        user = Config.mysql_user,
        password = Config.mysql_password,
        database='taipei_trip'
    )

cursor = db.cursor()

##  select函式使用方法：看要找什麼就在參數寫x='x' 
##  範例
##  db_select('user', username='ply', password='ply')
def db_select(table, **kargs):
    sql=f'SELECT * FROM {table} WHERE'
    for key in kargs:
        sql += f" { key } = \'{ kargs[key] }\' and "
    sql = sql[:-5]   
    cursor.execute(sql)
    user = cursor.fetchone()
    if not user:
        return None
    userData = dict(zip(cursor.column_names, user))
    return userData

##  insert函式使用方法：看要找什麼就在參數寫x='x'
##  範例
##  db_insert('user', name='澎澎', username='ply', password='ply')
def db_insert(table, **kargs):
    sql =f'INSERT INTO {table} '
    column = '('
    value = '('

    for key in kargs:
        column += key + ','
        value += f"\'{kargs[key]}\',"
    
    column = column[:-1] + ')'
    value = value[:-1] + ')'
    sql += column + ' VALUES ' + value
    # print(sql)
    cursor.execute(sql)
    db.commit()


def select_attraction(sql):
	cursor.execute(sql)
	result = cursor.fetchall()
	# attrs為本次搜尋所有景點資料的陣列
	attraction_list = []
	for attr in result:
		temp_attr = dict(zip(cursor.column_names, attr))
		temp_attr['images'] = json.loads(attr[9])
		attraction_list.append(temp_attr)
	
	return attraction_list
