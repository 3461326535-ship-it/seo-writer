import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage

from graphs.state import GenerateTitlesInput, GenerateTitlesOutput


def generate_titles_node(state: GenerateTitlesInput, config: RunnableConfig, runtime: Runtime[Context]) -> GenerateTitlesOutput:
    """
    title: 拟写SEO标题
    desc: 根据产品信息生成3个符合谷歌SEO规范的学术风格标题
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
        product_name=state.product_name,
        reference_url=state.reference_url,
        reference_content=state.reference_content,
        reference_title=state.reference_title,
        language=state.language
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
        temperature=llm_config.get("temperature", 0.7),
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
    
    # 解析提取3个标题（假设模型输出每行一个标题）
    title_options = []
    for line in content_text.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('-'):
            # 移除可能的编号前缀
            if line[0].isdigit():
                line = line.split('.', 1)[-1].strip()
            title_options.append(line)
    
    # 确保至少有3个标题
    while len(title_options) < 3:
        title_options.append(f"{state.product_name}: Technical Analysis and Evaluation ({len(title_options) + 1})")
    
    title_options = title_options[:3]
    
    return GenerateTitlesOutput(title_options=title_options)
