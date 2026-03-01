from sqlalchemy import MetaData, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

metadata = Base.metadata

class LegalKnowledge(Base):
    """法律知识库表"""
    __tablename__ = "legal_knowledge"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    title = Column(String(500), nullable=False, comment="知识标题")
    content = Column(Text, nullable=False, comment="知识内容")
    category = Column(String(100), nullable=True, comment="分类（如：劳动法、民法、刑法等）")
    file_name = Column(String(255), nullable=True, comment="原始文件名")
    file_key = Column(String(500), nullable=True, comment="对象存储文件键")
    tags = Column(String(500), nullable=True, comment="标签，多个标签用逗号分隔")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

