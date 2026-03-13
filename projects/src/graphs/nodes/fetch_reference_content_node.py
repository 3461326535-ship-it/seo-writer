from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk.fetch import FetchClient

from graphs.state import FetchReferenceInput, FetchReferenceOutput


def fetch_reference_content_node(state: FetchReferenceInput, config: RunnableConfig, runtime: Runtime[Context]) -> FetchReferenceOutput:
    """
    title: 抓取参考页面内容
    desc: 从参考URL抓取产品页面的实际内容，用于后续文章生成
    integrations: URL内容抓取
    """
    ctx = runtime.context
    
    # 初始化FetchClient
    client = FetchClient(ctx=ctx)
    
    # 如果没有提供URL，返回空内容
    if not state.reference_url or state.reference_url.strip() == "":
        return FetchReferenceOutput(
            reference_content="",
            reference_title=""
        )
    
    # 抓取URL内容
    try:
        response = client.fetch(url=state.reference_url)
        
        # 检查是否成功
        if response.status_code != 0:
            # 抓取失败，返回空内容
            return FetchReferenceOutput(
                reference_content="",
                reference_title=""
            )
        
        # 提取文本内容
        text_content = "\n".join(
            item.text for item in response.content if item.type == "text"
        )
        
        # 获取页面标题
        page_title = response.title if response.title else ""
        
        return FetchReferenceOutput(
            reference_content=text_content,
            reference_title=page_title
        )
    except Exception as e:
        # 发生异常，返回空内容
        return FetchReferenceOutput(
            reference_content="",
            reference_title=""
        )
