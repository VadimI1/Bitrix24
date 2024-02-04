import sqlite3

from fast_bitrix24 import Bitrix
import gspread
import time


FILE_JSON = 'bitriks-413311-b6a6348d8b48.json'
TABLE = "bitriks"
WEBHOOK = "https://b24-g21v7o.bitrix24.ru/rest/1/87ss39nqwrd2scs4/"

b = Bitrix(WEBHOOK)


deal_order = b.get_all(
    'crm.deal.list',
    params={
        'select': ['*', 'UF_*'],
        'filter': {'CLOSED': 'N'}
})


deal_client = b.list_and_get(
    'crm.contact'
)


list = []
for i in deal_order:
    for j in deal_client:
        if i["CONTACT_ID"] == deal_client[str(j)]["ID"]:
            list.append([deal_client[str(j)]["SECOND_NAME"] + " " + deal_client[str(j)]["NAME"] + " " + deal_client[str(j)]["LAST_NAME"],
                         deal_client[str(j)]["PHONE"][0]["VALUE"], i["COMMENTS"]])


# file = open("bitriks.db.sql", "r", encoding='utf-8')
# build_db = file.read()
# file.close()

connector = sqlite3.connect('bitrik24.db')
cursor = connector.cursor()

#cursor.executescript(build_db)

sql_services = cursor.execute("SELECT * FROM Orders")
repeat = []
flag = True
for row in sql_services:
    repeat.append(row)

for i in list:
    if not repeat:
        cursor.execute(f"INSERT INTO Orders (Name, Phone, Comment)"
                       f"VALUES ('{i[0]}', '{i[1]}', '{i[2]}')")
    else:
        for j in repeat:
            if j[1] == i[0] and j[2] == int(i[1][1::]) and j[3] == i[2]:
                flag = False
                break
        if flag:
            cursor.execute(f"INSERT INTO Orders (Name, Phone, Comment)"
                           f"VALUES ('{i[0]}', '{i[1]}', '{i[2]}')")
        flag = True



#проверка на сохранения в БД
sql_services = cursor.execute("SELECT * FROM Orders")
list = []
for row in sql_services:
    list.append(row)
    print(row)

connector.commit()
cursor.close()
connector.close()


gc = gspread.service_account(filename=FILE_JSON)

sh = gc.open(TABLE)
worksheet = sh.get_worksheet(0)

worksheet.update('A1', 'ФИО')
worksheet.update('B1', 'Номер телефона')
worksheet.update('C1', 'Комментарий')

for i in list:
    worksheet.update('A' + str(i[0] + 1), i[1])
    worksheet.update('B' + str(i[0] + 1), i[2])
    worksheet.update('C' + str(i[0] + 1), i[3])
    time.sleep(2.5)
