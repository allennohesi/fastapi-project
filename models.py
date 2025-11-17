from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base


class User(Base):
    __tablename__ = "user_tbl"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.first_name} {self.last_name})>"


class AuthToken(Base):
    __tablename__ = "auth_token"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_tbl.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    
    def __repr__(self):
        return f"<AuthToken(id={self.id}, user_id={self.user_id})>"
