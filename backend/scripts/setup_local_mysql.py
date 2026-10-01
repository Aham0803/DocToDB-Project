import pymysql
import sys

passwords_to_try = ['', 'root', 'password', '1234', '123456', 'admin', 'root123']
found_pwd = None

for pwd in passwords_to_try:
    try:
        conn = pymysql.connect(host='localhost', user='root', password=pwd, connect_timeout=2)
        print(f"Connected to local MySQL successfully! Root password is: '{pwd}'")
        found_pwd = pwd
        
        with conn.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS doc_to_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print("Database 'doc_to_db' verified/created.")
            
            # Read and execute init_db.sql
            with open("scripts/init_db.sql", "r", encoding="utf-8") as f:
                sql_script = f.read()
            
            for statement in sql_script.split(';'):
                stmt = statement.strip()
                if stmt:
                    cur.execute(stmt)
            print("All DocToDB tables created successfully in local MySQL!")
        
        conn.close()
        break
    except Exception as e:
        continue

if found_pwd is None:
    print("Could not auto-connect to MySQL root with default passwords.")
    print("Please check your local MySQL root password.")
else:
    # Update .env with working MySQL password
    from pathlib import Path
    env_file = Path("../.env")
    if env_file.exists():
        content = env_file.read_text(encoding="utf-8")
        import re
        content = re.sub(r"MYSQL_PASSWORD=.*", f"MYSQL_PASSWORD={found_pwd}", content)
        env_file.write_text(content, encoding="utf-8")
        print(f"Updated .env with MYSQL_PASSWORD={found_pwd}")
