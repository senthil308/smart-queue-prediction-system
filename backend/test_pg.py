import psycopg2
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    print("CONNECTION_SUCCESS")
    
    # Check if database exists
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='smart_queue_db'")
    if not cur.fetchone():
        print("DB_MISSING, creating smart_queue_db...")
        cur.execute("CREATE DATABASE smart_queue_db")
        print("DB_CREATED")
    else:
        print("DB_EXISTS")
    
    conn.close()
except Exception as e:
    print(f"CONNECTION_ERROR_DETAILS: {e}")
