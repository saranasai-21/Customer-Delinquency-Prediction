# db.py

import sqlite3

conn = sqlite3.connect(
    "predictions.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions(

id INTEGER PRIMARY KEY AUTOINCREMENT,

customer_id INTEGER,

risk TEXT,

probability REAL,

recommendation TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()


def save_prediction(
        customer_id,
        risk,
        probability,
        recommendation):

    cursor.execute(

        """
        INSERT INTO predictions(
        customer_id,
        risk,
        probability,
        recommendation
        )

        VALUES(?,?,?,?)

        """,

        (
            customer_id,
            risk,
            probability,
            recommendation
        )
    )

    conn.commit()