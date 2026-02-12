
import sqlite3
import os

DB_PATH = r"C:\Users\gaelf\AppData\Local\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\LocalState\sessions\9C420243DA164BCA9E1F3D1643923DD4474850FB\contacts.db"

def inspect_db(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    
    print(f"=== Inspecting {os.path.basename(path)} ===")
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", [t[0] for t in tables])
        
        for table in tables:
            tname = table[0]
            print(f"\n--- Table: {tname} ---")
            cursor.execute(f"PRAGMA table_info({tname});")
            columns = cursor.fetchall()
            print("Columns:", [c[1] for c in columns])
            
            # Search for 'label' or 'creation' in any text column
            # (Just a sample for now)
            try:
                cursor.execute(f"SELECT * FROM {tname} LIMIT 5;")
                rows = cursor.fetchall()
                for r in rows:
                    print(r)
            except:
                pass
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_db(DB_PATH)
