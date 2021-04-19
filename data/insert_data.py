import urllib.request as req
import json
import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='taipei_trip'
)

cursor = db.cursor()
url = 'taipei-attractions.json'

with open(url, mode='r', encoding='utf-8') as response:
    data = json.load(response)
data = data['result']['results']
data_length = len(data)

for i in range(data_length):
    attr = data[i]
    # 將img們挑出來變成陣列
    imgs = attr['file'].split('http:')
    img_len = len(imgs)
    img_list = []
    for j in range(1, img_len):
        img_format = imgs[j][-4:]
        if img_format == '.jpg' or img_format == '.JPG' or img_format == '.png':
            img_url = 'http:'+imgs[j]
            img_list.append(img_url)

    sql = 'INSERT INTO attraction (name, category, description, address, transport, mrt, latitude, longitude, images) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    val = (attr['stitle'], attr['CAT2'], attr['xbody'], attr['address'], attr['info'], attr['MRT'], attr['latitude'], attr['longitude'], json.dumps(img_list))
    cursor.execute(sql, val)
    db.commit()


            
