import os
from typing import Optional
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from cozeloop.decorator import observe
from coze_coding_utils.runtime_ctx.context import Context, default_headers


class WebItem:
    """Web搜索结果项模型"""
    def __init__(self, **kwargs):
        self.id = kwargs.get("Id")
        self.sort_id = kwargs.get("SortId")
        self.title = kwargs.get("Title")
        self.site_name = kwargs.get("SiteName")
        self.url = kwargs.get("Url")
        self.snippet = kwargs.get("Snippet")
        self.summary = kwargs.get("Summary")
        self.content = kwargs.get("Content")
        self.publish_time = kwargs.get("PublishTime")
        self.logo_url = kwargs.get("LogoUrl")
        self.rank_score = kwargs.get("RankScore")
        self.auth_info_des = kwargs.get("AuthInfoDes")
        self.auth_info_level = kwargs.get("AuthInfoLevel")


@observe
def _web_search_internal(
    ctx: Context,
    query: str,
    search_type: str = "web_summary",
    count: int = 10,
    need_content: bool = True,
    need_url: bool = True,
    need_summary: bool = True,
    sites: Optional[str] = None,
) -> tuple[list[WebItem], str, dict]:
    """
    内部函数：调用联网搜索API
    
    Args:
        ctx: 上下文对象
        query: 搜索查询词
        search_type: 搜索类型
        count: 返回条数
        need_content: 是否需要正文
        need_url: 是否需要URL
        need_summary: 是否需要摘要
        sites: 指定搜索站点
    
    Returns:
        tuple[web_items, summary, result_dict]
    """
    import requests
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_BASE_URL")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    headers.update(default_headers(ctx))
    
    request = {
        "Query": query,
        "SearchType": search_type,
        "Count": count,
        "Filter": {
            "NeedContent": need_content,
            "NeedUrl": need_url,
            "Sites": sites,
        },
        "NeedSummary": need_summary,
    }
    
    try:
        response = requests.post(
            f'{base_url}/api/search_api/web_search',
            json=request,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        response_metadata = data.get("ResponseMetadata", {})
        result = data.get("Result", {})
        
        if response_metadata.get("Error"):
            raise Exception(f"web_search 失败: {response_metadata.get('Error')}")

        web_items = []
        if result.get("WebResults"):
            web_items = [WebItem(**item) for item in result.get("WebResults", [])]
        
        summary = ""
        if result.get("Choices"):
            summary = result.get("Choices", [{}])[0].get("Message", {}).get("Content", "")
        
        return web_items, summary, result
    except requests.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except Exception as e:
        raise Exception(f"web_search 失败: {str(e)}")
    finally:
        if 'response' in locals():
            response.close()


@tool
def search_legal_articles(query: str, runtime: ToolRuntime) -> str:
    """
    搜索法律条文和相关规定
    
    该工具用于检索与用户案件相关的法律规定、法条、司法解释等内容。
    
    Args:
        query: 法律问题或关键词，例如"劳动合同法 违法解除赔偿"、"民法典 侵权责任"
    
    Returns:
        返回搜索到的法律条文摘要和相关内容
    """
    ctx = runtime.context
    
    try:
        web_items, summary, result = _web_search_internal(
            ctx=ctx,
            query=query,
            search_type="web_summary",
            count=10,
            need_content=True,
            need_url=True,
            need_summary=True,
            sites=None  # 可以指定特定的法律网站，如"npc.gov.cn|court.gov.cn"
        )
        
        if not web_items and not summary:
            return f"未搜索到与'{query}'相关的法律规定，请尝试更具体的关键词。"
        
        # 构建返回结果
        result_text = f"已为您搜索到与'{query}'相关的法律规定：\n\n"
        
        # 添加搜索摘要（如果有）
        if summary:
            result_text += f"【搜索摘要】\n{summary}\n\n"
        
        # 添加详细搜索结果
        result_text += "【详细条文】\n"
        for idx, item in enumerate(web_items[:5], 1):  # 最多返回前5条
            result_text += f"\n{idx}. {item.title}\n"
            result_text += f"   站点：{item.site_name or '未知'}\n"
            if item.snippet:
                result_text += f"   摘要：{item.snippet}\n"
            if item.summary:
                result_text += f"   精准摘要：{item.summary}\n"
            if item.url:
                result_text += f"   来源：{item.url}\n"
        
        return result_text
        
    except Exception as e:
        return f"搜索法律条文时发生错误：{str(e)}"


@tool  
def search_specific_law(law_name: str, specific_article: str, runtime: ToolRuntime) -> str:
    """
    搜索特定法律的特定条文
    
    该工具用于检索具体法律中的具体条文内容。
    
    Args:
        law_name: 法律名称，例如"劳动合同法"、"民法典"
        specific_article: 条文关键词或编号，例如"第38条"、"违法解除"、"赔偿标准"
    
    Returns:
        返回该法律条文的具体内容
    """
    ctx = runtime.context
    
    # 构建搜索查询
    query = f"{law_name} {specific_article}"
    
    try:
        web_items, summary, result = _web_search_internal(
            ctx=ctx,
            query=query,
            search_type="web_summary",
            count=8,
            need_content=True,
            need_url=True,
            need_summary=True,
            sites=None
        )
        
        if not web_items and not summary:
            return f"未找到《{law_name}》关于'{specific_article}'的条文内容。"
        
        result_text = f"已为您检索《{law_name}》关于'{specific_article}'的相关条文：\n\n"
        
        if summary:
            result_text += f"【条文摘要】\n{summary}\n\n"
        
        result_text += "【条文详情】\n"
        for idx, item in enumerate(web_items[:3], 1):
            result_text += f"\n{idx}. {item.title}\n"
            if item.content and len(item.content) < 500:
                result_text += f"   条文内容：{item.content}\n"
            elif item.summary:
                result_text += f"   条文内容：{item.summary}\n"
            if item.url:
                result_text += f"   完整来源：{item.url}\n"
        
        return result_text
        
    except Exception as e:
        return f"检索法律条文时发生错误：{str(e)}"
