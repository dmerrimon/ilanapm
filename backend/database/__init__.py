"""Database module for feedback storage"""

from .connection import get_db_connection, init_db

__all__ = ["get_db_connection", "init_db"]
