import mysql.connector
import json

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz"
}

DB_NAME = "uber_eats"

with open('uber_output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


def create_database(cursor):
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

def create_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant_all (
        id INT AUTO_INCREMENT PRIMARY KEY,
        
        restaurant_name VARCHAR(255),
        phone_number VARCHAR(50),
        
        product_category JSON,
        img TEXT,
        
        address TEXT,
        country VARCHAR(10),
        latitude DOUBLE,
        longitude DOUBLE,
        
        currency VARCHAR(10),
        delivery_time VARCHAR(50),
        rating FLOAT NULL,
        
        availability JSON,
        deliverable_distance VARCHAR(50),
        
        menu JSON
    )
    """)

def insert_data(cursor, conn, data):
    query = """
    INSERT INTO restaurant_all (
        restaurant_name, phone_number, product_category, img,
        address, country, latitude, longitude,
        currency, delivery_time, rating,
        availability, deliverable_distance, menu
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data['restaurant_name'],
        data['phone_number'],
        json.dumps(data['product_category']),
        data['img'],
        data['location']['address'],
        data['location']['country'],
        data['location']['latitude'],
        data['location']['longitude'],
        data['currency'],
        data['delivery_time'],
        data['rating'],
        json.dumps(data['availability']),
        data['deliverable_distance'],
        json.dumps(data['menu'])
    )

    cursor.execute(query, values)
    conn.commit()

def fetch_data(cursor):
    cursor.execute("SELECT * FROM restaurant_all")
    rows = cursor.fetchall()

    print("\nStored Data:\n")
    for row in rows:
        print(row)

def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        create_database(cursor)
        create_table(cursor)
        insert_data(cursor, conn, data)
        fetch_data(cursor)

        cursor.close()
        conn.close()

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()