from langchain.tools import tool, ToolRuntime
from storage.database.db import get_session
from storage.database.knowledge_manager import KnowledgeManager


@tool
def search_knowledge_base(query: str, runtime: ToolRuntime, category: str = "") -> str:
    """
    搜索知识库中的法律知识
    
    该工具用于检索知识库中的法律条文、案例分析、相关规定等内容。
    当用户询问法律问题时，优先使用此工具检索知识库中是否有相关内容。
    
    Args:
        query: 搜索关键词，例如"劳动合同法 违法解除"、"工伤认定标准"
        runtime: 运行时上下文
        category: 可选，知识分类，例如"劳动法"、"民法"、"刑法"等
    
    Returns:
        返回知识库中匹配的内容列表
    """
    try:
        db = get_session()
        try:
            manager = KnowledgeManager()
            
            # 搜索知识库
            results = manager.search_knowledge(
                db=db,
                query=query,
                category=category if category else None
            )
            
            if not results:
                # 知识库中没有相关内容
                return f"知识库中未找到与'{query}'相关的内容，建议使用联网搜索工具检索法律规定。"
            
            # 构建返回结果
            result_text = f"已在知识库中找到 {len(results)} 条相关内容：\n\n"
            
            for idx, knowledge in enumerate(results, 1):
                result_text += f"{idx}. 【{knowledge.title}】"
                # 使用 getattr 来避免 LSP 类型检查错误
                knowledge_category = getattr(knowledge, 'category', None)
                if knowledge_category:
                    result_text += f" ({knowledge_category})"
                result_text += "\n\n"
                
                # 截取内容的前500字作为摘要
                content_preview = knowledge.content[:500]
                if len(knowledge.content) > 500:
                    content_preview += "..."
                result_text += f"   {content_preview}\n"
                
                knowledge_tags = getattr(knowledge, 'tags', None)
                if knowledge_tags:
                    result_text += f"   标签：{knowledge_tags}\n"
                
                result_text += "\n"
            
            result_text += "\n【提示】以上内容来自知识库。如果需要更详细的法律条文或最新规定，建议结合联网搜索工具进行检索。"
            
            return result_text
            
        finally:
            db.close()
            
    except Exception as e:
        return f"检索知识库时发生错误：{str(e)}"


@tool
def get_knowledge_by_category(category: str, runtime: ToolRuntime) -> str:
    """
    根据分类获取知识库内容
    
    该工具用于获取特定法律分类下的所有知识内容。
    
    Args:
        category: 知识分类，例如"劳动法"、"民法"、"刑法"、"合同法"等
    
    Returns:
        返回该分类下的所有知识内容
    """
    try:
        db = get_session()
        try:
            manager = KnowledgeManager()
            
            # 根据分类获取知识
            results = manager.get_knowledge_by_category(db=db, category=category)
            
            if not results:
                return f"知识库中暂无'{category}'分类的内容。"
            
            # 构建返回结果
            result_text = f"知识库中'{category}'分类共有 {len(results)} 条内容：\n\n"
            
            for idx, knowledge in enumerate(results, 1):
                result_text += f"{idx}. {knowledge.title}\n"
                knowledge_tags = getattr(knowledge, 'tags', None)
                if knowledge_tags:
                    result_text += f"   标签：{knowledge_tags}\n"
                knowledge_updated = getattr(knowledge, 'updated_at', None)
                knowledge_created = getattr(knowledge, 'created_at', None)
                result_text += f"   更新时间：{knowledge_updated or knowledge_created}\n\n"
            
            result_text += "如需查看具体内容，请使用 search_knowledge_base 工具进行详细搜索。"
            
            return result_text
            
        finally:
            db.close()
            
    except Exception as e:
        return f"获取知识库分类内容时发生错误：{str(e)}"


@tool
def list_knowledge_categories(runtime: ToolRuntime) -> str:
    """
    列出知识库中的所有分类
    
    该工具用于查看知识库中有哪些法律知识分类。
    
    Returns:
        返回所有分类列表
    """
    try:
        db = get_session()
        try:
            manager = KnowledgeManager()
            
            # 获取所有知识
            all_knowledge = manager.get_all_knowledge(db=db, limit=1000)
            
            if not all_knowledge:
                return "知识库暂无内容。"
            
            # 统计分类
            category_count = {}
            for knowledge in all_knowledge:
                knowledge_category = getattr(knowledge, 'category', None)
                if knowledge_category:
                    category_count[knowledge_category] = category_count.get(knowledge_category, 0) + 1
            
            if not category_count:
                return "知识库中有内容但未设置分类。"
            
            # 构建返回结果
            result_text = "知识库中包含以下分类：\n\n"
            for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
                result_text += f"- {category} ({count} 条)\n"
            
            result_text += f"\n总计：{len(all_knowledge)} 条知识"
            
            return result_text
            
        finally:
            db.close()
            
    except Exception as e:
        return f"获取知识库分类时发生错误：{str(e)}"
