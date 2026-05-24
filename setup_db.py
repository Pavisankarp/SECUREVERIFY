import mysql.connector

def reset_db():
    conn = mysql.connector.connect(host="localhost", user="root", password="admin")
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS document_verification")
    cursor.execute("USE document_verification")
    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute("""
        CREATE TABLE documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            reg_no VARCHAR(50) NOT NULL,
            doc_type VARCHAR(50) NOT NULL,
            hash VARCHAR(64) NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Database reset successfully.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_db()