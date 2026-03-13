from typing import List, Optional
from pydantic import BaseModel, Field


class GlobalState(BaseModel):
    """全局状态定义"""
    # 输入参数
    product_name: str = Field(..., description="产品名称或核心关键词")
    reference_url: str = Field(default="", description="参考产品页面URL")
    language: str = Field(default="English", description="文章语言")
    
    # 内容抓取：参考页面的实际内容
    reference_content: str = Field(default="", description="从参考URL抓取的页面内容")
    reference_title: str = Field(default="", description="参考页面标题")
    
    # 第一步输出：标题列表
    title_options: List[str] = Field(default=[], description="生成的3个备选标题")
    
    # 第二步输出：焦点关键词及SEO信息
    selected_title: str = Field(default="", description="选定的标题")
    focus_keyword: str = Field(default="", description="焦点关键词")
    url_slug: str = Field(default="", description="建议的URL Slug")
    meta_description: str = Field(default="", description="页面Meta描述")
    seo_title: str = Field(default="", description="SEO标题")
    keyword_positions: str = Field(default="", description="关键词在文章中的最佳位置说明")
    
    # 第三步输出：完整文章和HTML
    full_article: str = Field(default="", description="完整的阿拉伯数字编号格式文章")
    html_article: str = Field(default="", description="转换后的HTML格式文章（英文）")
    chinese_article: str = Field(default="", description="中文翻译文章")
    chinese_html_article: str = Field(default="", description="转换后的HTML格式文章（中文）")


class GraphInput(BaseModel):
    """工作流的输入"""
    product_name: str = Field(..., description="产品名称或核心关键词")
    reference_url: str = Field(default="", description="参考产品页面URL（可选）")
    language: str = Field(default="English", description="文章语言（默认English）")


class GraphOutput(BaseModel):
    """工作流的输出"""
    title_options: List[str] = Field(..., description="3个备选SEO标题")
    focus_keyword: str = Field(..., description="焦点关键词")
    url_slug: str = Field(..., description="建议的URL Slug")
    meta_description: str = Field(..., description="页面Meta描述")
    seo_title: str = Field(..., description="SEO标题")
    full_article: str = Field(..., description="完整的阿拉伯数字编号格式文章（英文）")
    html_article: str = Field(..., description="转换后的HTML格式文章（英文）")
    chinese_article: str = Field(..., description="中文翻译文章")
    chinese_html_article: str = Field(..., description="转换后的HTML格式文章（中文）")


# ========== 节点0: 抓取参考内容 ==========
class FetchReferenceInput(BaseModel):
    """抓取参考内容节点输入"""
    reference_url: str = Field(..., description="参考产品页面URL")


class FetchReferenceOutput(BaseModel):
    """抓取参考内容节点输出"""
    reference_content: str = Field(..., description="从参考URL抓取的页面内容")
    reference_title: str = Field(default="", description="参考页面标题")


# ========== 节点1: 拟写SEO标题 ==========
class GenerateTitlesInput(BaseModel):
    """拟写标题节点输入"""
    product_name: str = Field(..., description="产品名称或核心关键词")
    reference_url: str = Field(default="", description="参考产品页面URL")
    reference_content: str = Field(default="", description="从参考URL抓取的页面内容")
    reference_title: str = Field(default="", description="参考页面标题")
    language: str = Field(default="English", description="文章语言")


class GenerateTitlesOutput(BaseModel):
    """拟写标题节点输出"""
    title_options: List[str] = Field(..., description="生成的3个备选标题，每个标题需符合SEO规范")


# ========== 节点2: 确认焦点关键词 ==========
class ConfirmKeywordsInput(BaseModel):
    """确认关键词节点输入"""
    title_options: List[str] = Field(..., description="3个备选标题")
    product_name: str = Field(..., description="产品名称或核心关键词")
    reference_content: str = Field(default="", description="从参考URL抓取的页面内容")
    reference_title: str = Field(default="", description="参考页面标题")


class ConfirmKeywordsOutput(BaseModel):
    """确认关键词节点输出"""
    selected_title: str = Field(..., description="选定的标题")
    focus_keyword: str = Field(..., description="焦点关键词")
    url_slug: str = Field(..., description="建议的URL Slug")
    meta_description: str = Field(..., description="页面Meta描述")
    seo_title: str = Field(..., description="SEO标题")
    keyword_positions: str = Field(..., description="关键词在文章中的最佳位置说明")


# ========== 节点3: 撰写完整文章 ==========
class WriteArticleInput(BaseModel):
    """撰写文章节点输入"""
    selected_title: str = Field(..., description="选定的标题")
    focus_keyword: str = Field(..., description="焦点关键词")
    product_name: str = Field(..., description="产品名称或核心关键词")
    reference_url: str = Field(default="", description="参考产品页面URL")
    reference_content: str = Field(default="", description="从参考URL抓取的页面内容")
    reference_title: str = Field(default="", description="参考页面标题")
    keyword_positions: str = Field(..., description="关键词在文章中的最佳位置说明")


class WriteArticleOutput(BaseModel):
    """撰写文章节点输出"""
    full_article: str = Field(..., description="完整的阿拉伯数字编号格式文章")


# ========== 节点4: 转换为HTML格式 ==========
class ConvertToHtmlInput(BaseModel):
    """转换为HTML节点输入"""
    full_article: str = Field(..., description="完整的阿拉伯数字编号格式文章")


class ConvertToHtmlOutput(BaseModel):
    """转换为HTML节点输出"""
    html_article: str = Field(..., description="转换后的HTML格式文章")


# ========== 节点5: 翻译成中文 ==========
class TranslateToChineseInput(BaseModel):
    """翻译成中文节点输入"""
    full_article: str = Field(..., description="完整的英文文章")


class TranslateToChineseOutput(BaseModel):
    """翻译成中文节点输出"""
    chinese_article: str = Field(..., description="中文翻译文章")


# ========== 节点6: 转换为HTML格式（中文） ==========
class ConvertToHtmlChineseInput(BaseModel):
    """转换为HTML节点输入（中文）"""
    chinese_article: str = Field(..., description="中文文章")


class ConvertToHtmlChineseOutput(BaseModel):
    """转换为HTML节点输出（中文）"""
    chinese_html_article: str = Field(..., description="转换后的HTML格式文章（中文）")
