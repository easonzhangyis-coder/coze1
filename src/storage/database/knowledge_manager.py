from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from storage.database.shared.model import LegalKnowledge


# --- Pydantic Models ---
class KnowledgeCreate(BaseModel):
    """创建知识库记录的输入模型"""
    title: str = Field(..., description="知识标题")
    content: str = Field(..., description="知识内容")
    category: Optional[str] = Field(None, description="分类（如：劳动法、民法、刑法等）")
    file_name: Optional[str] = Field(None, description="原始文件名")
    file_key: Optional[str] = Field(None, description="对象存储文件键")
    tags: Optional[str] = Field(None, description="标签，多个标签用逗号分隔")


class KnowledgeUpdate(BaseModel):
    """更新知识库记录的输入模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None


# --- Manager Class ---
class KnowledgeManager:
    """知识库管理类"""

    def create_knowledge(self, db: Session, knowledge_in: KnowledgeCreate) -> LegalKnowledge:
        """创建知识库记录"""
        knowledge_data = knowledge_in.model_dump()
        db_knowledge = LegalKnowledge(**knowledge_data)
        db.add(db_knowledge)
        try:
            db.commit()
            db.refresh(db_knowledge)
            return db_knowledge
        except Exception:
            db.rollback()
            raise

    def get_knowledge_by_id(self, db: Session, knowledge_id: int) -> Optional[LegalKnowledge]:
        """根据ID获取知识库记录"""
        return db.query(LegalKnowledge).filter(LegalKnowledge.id == knowledge_id).first()

    def get_knowledge_by_category(self, db: Session, category: str) -> List[LegalKnowledge]:
        """根据分类获取知识库记录"""
        return db.query(LegalKnowledge).filter(LegalKnowledge.category == category).all()

    def search_knowledge(self, db: Session, query: str, category: Optional[str] = None) -> List[LegalKnowledge]:
        """搜索知识库（支持标题和内容模糊搜索）"""
        search_query = db.query(LegalKnowledge)
        
        # 构建搜索条件
        conditions = []
        if query:
            conditions.append(LegalKnowledge.title.ilike(f"%{query}%"))
            conditions.append(LegalKnowledge.content.ilike(f"%{query}%"))
        
        if category:
            conditions.append(LegalKnowledge.category == category)
        
        if conditions:
            # 如果有搜索词，使用 OR 连接标题和内容的搜索，AND 连接分类
            query_conditions = []
            if query:
                query_conditions.append(or_(*conditions[:2]))
            if category:
                query_conditions.append(LegalKnowledge.category == category)
            
            from sqlalchemy import and_
            search_query = search_query.filter(and_(*query_conditions))
        
        return search_query.order_by(LegalKnowledge.created_at.desc()).limit(10).all()

    def update_knowledge(self, db: Session, knowledge_id: int, knowledge_in: KnowledgeUpdate) -> Optional[LegalKnowledge]:
        """更新知识库记录"""
        db_knowledge = self.get_knowledge_by_id(db, knowledge_id)
        if not db_knowledge:
            return None
        
        update_data = knowledge_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_knowledge, field):
                setattr(db_knowledge, field, value)
        
        db.add(db_knowledge)
        try:
            db.commit()
            db.refresh(db_knowledge)
            return db_knowledge
        except Exception:
            db.rollback()
            raise

    def delete_knowledge(self, db: Session, knowledge_id: int) -> bool:
        """删除知识库记录"""
        db_knowledge = self.get_knowledge_by_id(db, knowledge_id)
        if not db_knowledge:
            return False
        
        db.delete(db_knowledge)
        try:
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise

    def get_all_knowledge(self, db: Session, skip: int = 0, limit: int = 100) -> List[LegalKnowledge]:
        """获取所有知识库记录"""
        return db.query(LegalKnowledge).order_by(LegalKnowledge.created_at.desc()).offset(skip).limit(limit).all()
