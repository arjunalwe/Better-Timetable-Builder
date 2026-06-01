from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

pool = ConnectionPool(conninfo=DB_URL, open=True)

# with pool.connection() as conn:
#     with conn.cursor() as cur:
#         cur.execute("""
#                     CREATE TABLE IF NOT EXISTS bronze(
#                         id VARCHAR(30) PRIMARY KEY,
#                         course VARCHAR(8),
#                         ttb_json JSONB,
#                         acorn_json JSONB, 
#                         status VARCHAR(20) DEFAULT 'PENDING',
#                         updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
#                     )
#                     """)
#         conn.commit()