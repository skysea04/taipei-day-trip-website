import mysql.connector
from config import Config
import json

db = Config.db

cursor = db.cursor()

##  select函式使用方法：看要找什麼就在參數寫x='x' 
##  範例
##  db_select(username='ply', password='ply')
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
##  db_insert(name='澎澎', username='ply', password='ply')
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
    print(sql)
    cursor.execute(sql)
    db.commit()


def select_attraction(page, sql):
	cursor.execute(sql)
	result = cursor.fetchall()
	# attrs代表所有的景點資料
	attrs = []
	for attr in result:
		temp_attr = dict(zip(cursor.column_names, attr))
		temp_attr['images'] = json.loads(attr[9])
		attrs.append(temp_attr)
		
	attrs_len = len(attrs)	
	attraction_list = []
	first_index = page * 12
	
	if attrs_len - first_index <=12:
		for i in range(first_index, attrs_len):
			attraction_list.append(attrs[i])
	else:
		for i in range(first_index, first_index + 12):
			attraction_list.append(attrs[i])
	
	return attraction_list
