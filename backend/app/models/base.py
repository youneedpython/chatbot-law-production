"""
models/base.py
- SQLAlchemy Declarative Base 정의
"""


from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass