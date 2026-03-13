## 项目概述
- **名称**: SEO文章生成工作流
- **功能**: 根据产品信息和参考页面URL，自动生成符合谷歌SEO规范的学术风格内容营销文章，并输出中英文双语HTML格式文档
- **特性**: 支持从参考URL抓取实际产品信息，在文章中准确引用产品规格、技术参数等真实数据，自动翻译成中文

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| fetch_reference_content | `nodes/fetch_reference_content_node.py` | task | 抓取参考页面内容 | - | - |
| generate_titles | `nodes/generate_titles_node.py` | agent | 拟写SEO标题 | - | `config/generate_titles_cfg.json` |
| confirm_keywords | `nodes/confirm_keywords_node.py` | agent | 确认焦点关键词 | - | `config/confirm_keywords_cfg.json` |
| write_article | `nodes/write_article_node.py` | agent | 撰写学术风格文章 | - | `config/write_article_cfg.json` |
| convert_to_html | `nodes/convert_to_html_node.py` | agent | 转换为HTML格式（英文） | - | `config/convert_to_html_cfg.json` |
| translate_to_chinese | `nodes/translate_to_chinese_node.py` | agent | 翻译成中文 | - | `config/translate_to_chinese_cfg.json` |
| convert_to_html_chinese | `nodes/convert_to_html_chinese_node.py` | agent | 转换为HTML格式（中文） | - | `config/convert_to_html_chinese_cfg.json` |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
无子图

## 技能使用
- fetch_reference_content节点使用URL内容抓取技能（fetch-url）
- generate_titles、confirm_keywords、write_article、convert_to_html、translate_to_chinese、convert_to_html_chinese节点使用大语言模型技能（LLM）

## 工作流说明

### 核心流程
1. **抓取参考页面内容（fetch_reference_content）**
   - 输入：参考产品页面URL
   - 处理：从URL抓取页面的实际内容和标题
   - 输出：页面文本内容、页面标题

2. **拟写SEO标题（generate_titles）**
   - 输入：产品名称、参考URL、参考页面内容、语言
   - 处理：基于实际产品信息生成3个符合谷歌SEO规范的学术风格标题
   - 输出：3个备选标题列表

3. **确认焦点关键词（confirm_keywords）**
   - 输入：3个备选标题、产品名称、参考页面内容
   - 处理：基于产品信息选择最优标题，确定焦点关键词及SEO元数据
   - 输出：选定标题、焦点关键词、URL Slug、Meta描述、SEO标题

4. **撰写完整文章（write_article）**
   - 输入：选定标题、焦点关键词、产品信息、参考页面内容
   - 处理：基于实际产品规格和技术参数撰写学术风格文章
   - 输出：完整的文章（Abstract和Keywords无序号，从Introduction开始使用数字编号）

5. **并行处理（两个分支同时执行）**：
   - **分支1：转换为HTML格式（convert_to_html）**
     - 输入：英文文章
     - 处理：使用大模型将英文文章转换为符合规范的HTML格式
       - Abstract和Keywords → `<h2 style="all: revert;">`（无序号）
       - 一级标题（如"1. Introduction"）→ `<h2 style="all: revert;">1. Introduction</h2>`
       - 二级标题（如"1.1 Background"）→ `<h3 style="all: revert;">1.1 Background</h3>`
       - 三级标题（如"1.1.1 xxx"）→ `<h4 style="all: revert;">1.1.1 xxx</h4>`
       - 段落 → `<p>` 标签包裹
       - 表格 → 带样式的HTML表格
     - 输出：英文HTML格式文章

   - **分支2：翻译成中文（translate_to_chinese）**
     - 输入：英文文章
     - 处理：使用大模型将英文文章准确翻译成中文，保持原有结构和学术风格
       - Abstract → 摘要
       - Keywords → 关键词
       - Introduction → 引言
       - Background → 背景
       - 保留所有数字和单位（如"IPX7"、"1.2mm"等）
     - 输出：中文翻译文章

6. **转换为HTML格式（中文）（convert_to_html_chinese）**
   - 输入：中文文章
   - 处理：使用大模型将中文文章转换为符合规范的HTML格式
     - 摘要和关键词 → `<h2 style="all: revert;">`（无序号）
     - 一级标题（如"1. 引言"）→ `<h2 style="all: revert;">1. 引言</h2>`
     - 二级标题（如"1.1 背景"）→ `<h3 style="all: revert;">1.1 背景</h3>`
     - 三级标题（如"1.1.1 xxx"）→ `<h4 style="all: revert;">1.1.1 xxx</h4>`
     - 段落 → `<p>` 标签包裹
     - 表格 → 带样式的HTML表格
   - 输出：中文HTML格式文章

### 特性说明
- **双语输出**: 自动生成英文和中文两个版本的HTML文档
- **并行处理**: HTML转换和中文翻译并行执行，提高效率
- **标题规则**: Abstract和Keywords不显示序号，从正文（Introduction）开始使用数字编号
- **HTML规范**: 输出为单行连续字符串，无换行符，表格和标题符合指定样式规范

### SEO优化要求
- 标题长度：50-65字符（英文）
- 学术风格：采用"主标题：副标题"结构
- 必须包含：数字词、力量词、情感词
- 核心关键词前置，长尾词自然融入
- 关键词密度：1%-1.5%
- 关键词位置：摘要首句、引言末句、至少1个H2标题、结论段落

### 文章结构要求
1. 文章标题
2. 摘要（150-200字）
3. 关键词（5-8个）
4. 引言
5. 标准概述（至少2个二级标题）
6. 核心技术内容（至少3个二级标题）
7. 设备/产品工程设计要求
8. 产品工程实践（软性植入）
9. 讨论（选型建议或工程考量）
10. 结论

### 输入参数
- `product_name`: 产品名称或核心关键词（必填）
- `reference_url`: 参考产品页面URL（可选）
- `language`: 文章语言（默认English）

### 输出结果
- `title_options`: 3个备选SEO标题
- `focus_keyword`: 焦点关键词
- `url_slug`: 建议的URL Slug
- `meta_description`: 页面Meta描述
- `seo_title`: SEO标题
- `full_article`: 完整的学术风格文章（英文，Abstract和Keywords无序号）
- `html_article`: 转换后的HTML格式文章（英文）
- `chinese_article`: 中文翻译文章
- `chinese_html_article`: 转换后的HTML格式文章（中文）


