import mysql.connector
import json
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

def add_product(name, details, image_url, seller_id, price, category, stock, brand, color):
    conn = get_connection()
    cursor = conn.cursor()
    query = """INSERT INTO products
        (name, details, image_url, seller_id, price, category, stock, brand, color)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (name, details, image_url, seller_id, price, category, stock, brand, color))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    query = """SELECT id, name, details, image_url, seller_id ,price, category, stock, brand, color 
               FROM products"""
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "details": row[2],
            "image": row[3],
            "seller_id": row[4],
            "price": row[5],
            "category": row[6],
            "stock": row[7],
            "brand": row[8],
            "color": row[9]
        })
    return products




def register_user(login_name, password, first_name, last_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """INSERT INTO user_master
            (login_name, password, first_name, last_name)
            VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (login_name, password, first_name, last_name))
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "login_name": login_name,
            "first_name": first_name,
            "last_name": last_name
        }
    except Exception as e:
        return {
            "error": str(e)
        }


def update_order_status(order_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE orders SET status=%s WHERE id=%s"
    cursor.execute(query, (new_status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def get_product_by_id(id):
    conn = get_connection()
    cursor = conn.cursor()
    query = """SELECT id, name, details, image_url,seller_id,price, category, stock, brand, color
               FROM products WHERE id = %s"""
    cursor.execute(query, (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "details": row[2],
            "image": row[3],
            "seller_id": row[4],
            "price": row[5],
            "category": row[6],
            "stock": row[7],
            "brand": row[8],
            "color": row[9]
        }
    return None

def insert_order(user_id, items, address, total_price, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (user_id, items, address, total_price, status) VALUES (%s, %s, %s, %s, %s)",
        (user_id, json.dumps(items), address, total_price, status)
    )

    conn.commit()
    order_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return order_id

def get_orders_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM orders WHERE user_id=%s ORDER BY order_time DESC", (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_user_products(seller_id):
    products = []
    query = """SELECT id, name, details, image_url,seller_id, price, category, stock, brand, color
               FROM products WHERE seller_id = %s"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (seller_id,))
                for row in cursor.fetchall():
                    products.append({
                        "id": row[0],
                        "name": row[1],
                        "details": row[2],
                        "image": row[3],
                        "seller_id": row[4],
                        "price": row[5],
                        "category": row[6],
                        "stock": row[7],
                        "brand": row[8],
                        "color": row[9]
                    })
    except Exception as e:
        print("Database error:", e)
    return products
