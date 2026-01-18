"""
SQLAlchemy declarative base for JD-Xi Editor database models.

This module provides the declarative base that all ORM models should inherit from.
"""

from sqlalchemy.orm import declarative_base

# Create declarative base for all models
Base = declarative_base()
