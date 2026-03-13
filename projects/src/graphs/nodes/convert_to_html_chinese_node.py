import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage

from graphs.state import ConvertToHtmlChineseInput, ConvertToHtmlChineseOutput

def convert_to_html_chinese_node(state: ConvertToHtmlChineseInput, config: RunnableConfig, runtime: Runtime[Context]) -> ConvertToHtmlChineseOutput:
    """
    title: 转换为HTML格式（中文）
    desc: 将中文文章转换为符合规范的HTML格式，保留标题序号
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
        article_content=state.chinese_article
    )
    
    # 初始化LLM客户端
    client = LLMClient(ctx=ctx)
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]
    
    # 调用大模型
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-2-0-pro-260215"),
        temperature=llm_config.get("temperature", 0.0),
        max_completion_tokens=llm_config.get("max_completion_tokens", 16384),
        thinking=llm_config.get("thinking", "disabled")
    )
    
    # 提取响应内容
    if isinstance(response.content, str):
        chinese_html_article = response.content
    elif isinstance(response.content, list):
        if response.content and isinstance(response.content[0], str):
            chinese_html_article = " ".join(response.content)
        else:
            text_parts = [item.get("text", "") for item in response.content if isinstance(item, dict) and item.get("type") == "text"]
            chinese_html_article = " ".join(text_parts)
    else:
        chinese_html_article = str(response.content)
    
    # 确保HTML是连续的（移除可能的换行符）
    chinese_html_article = chinese_html_article.replace('\n', '').replace('\r', '')
    
    return ConvertToHtmlChineseOutput(chinese_html_article=chinese_html_article)
