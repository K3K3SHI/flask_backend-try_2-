import mysql.connector
import mysql.connector.cursor
import os

def get_connection():
    connection = mysql.connector.connect(
        host='mysql.railway.internal',
        user='root',
        password='BVTSOpJDpqUiWaLTstJwrrwFxJewDzyi',  # <- use your actual Railway password
        database='railway',
        port=3306
    )
    return connection

def check_login(login, password):
    connection = get_connection()
    cursor = connection.cursor()
    recs = []
    print(login)
    cursor.execute("""Select login_name, password from user_master where login_name = %s """, (login,))
    recs = cursor.fetchall()
    print(recs)
    response = None
    if recs:
        password_in_db = recs[0][1]
        if password_in_db == password:
            response = { 'status': "OK",'user_role':  "CUSTOMER"}
        else:
            response = { 'status': "NOT_OK"}
    else:
        response = { 'status': "NOT_OK"}

    cursor.close()
    connection.close()
    return response

