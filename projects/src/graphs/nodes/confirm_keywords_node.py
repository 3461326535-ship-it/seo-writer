import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage

from graphs.state import ConfirmKeywordsInput, ConfirmKeywordsOutput


def confirm_keywords_node(state: ConfirmKeywordsInput, config: RunnableConfig, runtime: Runtime[Context]) -> ConfirmKeywordsOutput:
    """
    title: 确认焦点关键词
    desc: 从备选标题中选择最优标题，并确认焦点关键词及SEO相关信息
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
        title_options=state.title_options,
        product_name=state.product_name,
        reference_content=state.reference_content,
        reference_title=state.reference_title
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
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.5),
        max_completion_tokens=llm_config.get("max_completion_tokens", 4096),
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
    
    # 解析提取关键词信息（假设模型输出JSON格式）
    import re
    
    # 默认值
    selected_title = state.title_options[0] if state.title_options else state.product_name
    focus_keyword = state.product_name
    url_slug = state.product_name.lower().replace(' ', '-').replace('_', '-')
    meta_description = f"Comprehensive analysis of {state.product_name}. Learn about technical specifications, applications, and selection criteria."
    seo_title = f"{selected_title} | LISUN"
    keyword_positions = "Include in abstract first sentence, introduction last sentence, at least one H2 heading, and conclusion paragraph."
    
    # 尝试从响应中提取结构化信息
    try:
        # 查找JSON格式的输出
        json_match = re.search(r'\{[\s\S]*\}', content_text)
        if json_match:
            json_data = json.loads(json_match.group())
            if 'selected_title' in json_data:
                selected_title = json_data['selected_title']
            if 'focus_keyword' in json_data:
                focus_keyword = json_data['focus_keyword']
            if 'url_slug' in json_data:
                url_slug = json_data['url_slug']
            if 'meta_description' in json_data:
                meta_description = json_data['meta_description']
            if 'seo_title' in json_data:
                seo_title = json_data['seo_title']
            if 'keyword_positions' in json_data:
                keyword_positions = json_data['keyword_positions']
    except Exception:
        pass
    
    return ConfirmKeywordsOutput(
        selected_title=selected_title,
        focus_keyword=focus_keyword,
        url_slug=url_slug,
        meta_description=meta_description,
        seo_title=seo_title,
        keyword_positions=keyword_positions
    )
