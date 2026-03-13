from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)
from graphs.nodes.fetch_reference_content_node import fetch_reference_content_node
from graphs.nodes.generate_titles_node import generate_titles_node
from graphs.nodes.confirm_keywords_node import confirm_keywords_node
from graphs.nodes.write_article_node import write_article_node
from graphs.nodes.convert_to_html_node import convert_to_html_node
from graphs.nodes.translate_to_chinese_node import translate_to_chinese_node
from graphs.nodes.convert_to_html_chinese_node import convert_to_html_chinese_node

# 创建状态图，指定工作流的入参和出参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("fetch_reference_content", fetch_reference_content_node)
builder.add_node("generate_titles", generate_titles_node, metadata={"type": "agent", "llm_cfg": "config/generate_titles_cfg.json"})
builder.add_node("confirm_keywords", confirm_keywords_node, metadata={"type": "agent", "llm_cfg": "config/confirm_keywords_cfg.json"})
builder.add_node("write_article", write_article_node, metadata={"type": "agent", "llm_cfg": "config/write_article_cfg.json"})
builder.add_node("convert_to_html", convert_to_html_node, metadata={"type": "agent", "llm_cfg": "config/convert_to_html_cfg.json"})
builder.add_node("translate_to_chinese", translate_to_chinese_node, metadata={"type": "agent", "llm_cfg": "config/translate_to_chinese_cfg.json"})
builder.add_node("convert_to_html_chinese", convert_to_html_chinese_node, metadata={"type": "agent", "llm_cfg": "config/convert_to_html_chinese_cfg.json"})

# 设置入口点
builder.set_entry_point("fetch_reference_content")

# 添加边（线性流程）
builder.add_edge("fetch_reference_content", "generate_titles")
builder.add_edge("generate_titles", "confirm_keywords")
builder.add_edge("confirm_keywords", "write_article")
# write_article后有两个并行分支：转换为HTML（英文）和翻译成中文
builder.add_edge("write_article", "convert_to_html")
builder.add_edge("write_article", "translate_to_chinese")
# 两个并行分支后汇聚到中文HTML转换
builder.add_edge(["convert_to_html", "translate_to_chinese"], "convert_to_html_chinese")
builder.add_edge("convert_to_html_chinese", END)

# 编译图
main_graph = builder.compile()
