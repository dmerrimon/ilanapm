"""
Debug endpoint to check database configuration
"""

from fastapi import APIRouter
import os
from database.connection import DB_TYPE, DATABASE_URL

router = APIRouter()


@router.get("/debug/db-config")
async def get_db_config():
    """Get current database configuration (for debugging)"""
    return {
        "db_type": DB_TYPE,
        "database_url_set": DATABASE_URL is not None,
        "database_url_prefix": DATABASE_URL[:20] if DATABASE_URL else None,
        "env_vars": {
            "DATABASE_URL": "SET" if os.getenv("DATABASE_URL") else "NOT SET",
        }
    }
