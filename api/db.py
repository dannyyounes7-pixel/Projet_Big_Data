"""
Database Connection and Query Utilities
"""
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import yaml
from typing import List, Dict, Any


class DatabaseConnection:
    """PostgreSQL connection pool manager"""
    
    def __init__(self, config_path: str = 'config/api.yaml'):
        """Initialize connection pool"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        db_config = config['database']
        
        # Parse connection string
        # Format: postgresql://user:password@host:port/database
        conn_str = db_config['url']
        parts = conn_str.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_port_db = parts[1].split('/')
        host_port = host_port_db[0].split(':')
        
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=db_config.get('pool_size', 10),
            user=user_pass[0],
            password=user_pass[1],
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            database=host_port_db[1]
        )
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool"""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self):
        """Get cursor from connection"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results as list of dicts
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of dictionaries (column_name: value)
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
    
    def execute_one(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """
        Execute SELECT query and return single result
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Dictionary (column_name: value) or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def close(self):
        """Close all connections in pool"""
        if self.connection_pool:
            self.connection_pool.closeall()


# Global database instance
db = None


def get_db() -> DatabaseConnection:
    """Get database instance (singleton)"""
    global db
    if db is None:
        db = DatabaseConnection()
    return db
