from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

_pool = None
_pool_pid = None

def get_db_pool(db_url: str=DB_URL) -> ConnectionPool:
    global _pool, _pool_pid
    current_pid = os.getpid()
    
    if _pool is None or _pool_pid != current_pid:
        if _pool is not None:
            _pool.close() 
            
        _pool = ConnectionPool(conninfo=db_url, open=True)
        _pool_pid = current_pid
        
    return _pool