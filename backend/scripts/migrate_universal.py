import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "doc_to_db.sqlite"))
print(f"Connecting to: {db_path}")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(documents)")
    cols = [r[1] for r in c.fetchall()]
    new_cols = [
        ("document_type", "VARCHAR(50) DEFAULT 'GENERAL_DOCUMENT'"),
        ("document_title", "VARCHAR(255)"),
        ("primary_entity", "VARCHAR(255)"),
        ("summary", "TEXT")
    ]
    for name, typ in new_cols:
        if name not in cols:
            print(f"Adding column {name}...")
            c.execute(f"ALTER TABLE documents ADD COLUMN {name} {typ}")
    conn.commit()
    c.execute("PRAGMA table_info(documents)")
    print("Final columns:", [r[1] for r in c.fetchall()])
    conn.close()
