import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage

from graphs.state import WriteArticleInput, WriteArticleOutput


def write_article_node(state: WriteArticleInput, config: RunnableConfig, runtime: Runtime[Context]) -> WriteArticleOutput:
    """
    title: 撰写完整文章
    desc: 根据选定标题和焦点关键词，撰写符合学术风格的完整markdown格式文章
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 读取大模型配置文件
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up_tpl = Template(_cfg.get("up", ""))
    
    # 渲染用户提示词
    user_prompt_content = up_tpl.render(
        selected_title=state.selected_title,
        focus_keyword=state.focus_keyword,
        product_name=state.product_name,
        reference_url=state.reference_url,
        reference_content=state.reference_content,
        reference_title=state.reference_title,
        keyword_positions=state.keyword_positions
    )
    
    # 初始化LLM客户端
    client = LLMClient(ctx=ctx)
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]
    
    # 调用大模型（长文本生成，需要更多tokens）
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.6),
        max_completion_tokens=llm_config.get("max_completion_tokens", 16384),
        thinking=llm_config.get("thinking", "disabled")
    )
    
    # 提取响应内容
    if isinstance(response.content, str):
        content_text = response.content
    elif isinstance(response.content, list):
        if response.content and isinstance(response.content[0], str):
            content_text = " ".join(response.content)
        else:
            text_parts = [item.get("text", "") for item in response.content if isinstance(item, dict) and item.get("type") == "text"]
            content_text = " ".join(text_parts)
    else:
        content_text = str(response.content)
    
    return WriteArticleOutput(full_article=content_text)
