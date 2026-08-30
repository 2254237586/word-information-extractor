# Word 文档重要事项智能提取系统

这是一个利用中文预训练 Transformer 模型，从 Word 文档中自动识别、抽取、合并并排序重要事项的本地 NLP 系统。项目面向大学生竞赛展示，同时保留了可运行性、可解释的离线降级能力以及后续迁移学习入口。

## 技术架构

```text
DOCX → python-docx 文本解析 → 清洗/中文分句
     → MacBERT 深层语义特征 → 重要性分类
     → 时间与槽位信息抽取 → embedding 余弦相似度去重
     → 优先级排序 → 控制台 / JSON / Markdown / Streamlit
```

默认预训练模型为 `hfl/chinese-macbert-base`。首次联网运行会由 Hugging Face 下载并缓存模型；以后使用本地缓存。MacBERT 的 `[CLS]` 768 维向量用于技术展示和相似事项合并。若 `models/important_message_model/` 存在，系统优先使用真实微调二分类模型；否则使用 MacBERT 表示加时间、动作、截止、地点等可解释规则评分。若模型包、网络或缓存不可用，系统明确记录警告并降级为规则分类和字符向量去重，仍能完成基本分析。

## 环境与安装

推荐 Windows 10/11、Python 3.10 或 3.11。CPU 可运行，检测到 CUDA 时自动使用 GPU。

```bash
cd word_information_extractor
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

默认安装提供轻量的规则降级模式和 Streamlit 界面。若需要 MacBERT、模型微调或
768 维语义向量，请安装完整机器学习依赖：

```bash
pip install -r requirements-ml.txt
```

第一次模型下载体积较大。无网络演示可增加 `--offline`；此时只读取本地 Hugging Face 缓存，缓存不存在则自动使用规则降级。

## 运行

命令行：

```bash
python main.py data/sample.docx
python main.py data/sample.docx --offline
```

结果写到 `data/output/tasks.json` 和 `data/output/summary.md`，JSON 使用 UTF-8 和 `ensure_ascii=False`。

Web 界面：

```bash
streamlit run app.py
```

页面支持上传 `.docx`、进度提示、优先级分组以及通过 expander 查看原文、置信度、段落位置和完整字段。

## 微调自己的分类模型

CSV 格式必须为：

```csv
text,label
实验报告周日22点前上传学习通,1
今天天气不错,0
```

其中 `0=普通，1=重要`。运行：

```bash
python training/train_classifier.py
```

脚本执行分层 `train_test_split(test_size=0.2, random_state=42)`、MacBERT fine-tuning、逐轮验证，按真实验证集 F1 选择最佳模型并保存到 `models/important_message_model/`。控制台输出 Accuracy、Precision、Recall、F1，`evaluation.json` 保存真实指标，不包含任何写死性能。

自带的 50 条平衡数据只用于流程测试。**真正训练时需要进一步增加人工标注数据，建议至少 1000~3000 条。**

## 目录说明

- `config/settings.py`：模型、阈值、训练参数和 CPU/GPU 设备。
- `src/document_reader.py`：读取 DOCX 段落与表格并保留来源。
- `src/text_preprocessor.py`：保守清洗、中文分句和位置追溯。
- `src/importance_classifier.py`：微调分类、MacBERT fallback 和 768 维 embedding。
- `src/time_parser.py`：中文日期、时刻与截止语义。
- `src/information_extractor.py`：可替换的混合槽位抽取接口。
- `src/task_merger.py`：embedding 余弦相似度合并并保留多来源。
- `src/task_ranker.py`：按置信度、截止、时间和完整度排序。
- `src/formatter.py`：控制台、JSON、Markdown 输出。
- `src/pipeline.py`：端到端编排。
- `training/`：数据集、指标、训练与最佳模型保存。
- `tests/`：文档、预处理和端到端离线测试。

## 测试

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -q
```

若需要重新生成示例 Word：

```bash
python scripts/generate_sample_docx.py
```

## 技术亮点

中文预训练语言模型 MacBERT、Transformer 深层语义特征、迁移学习和 Fine-tuning、真实二分类指标、768 维 `[CLS]` embedding、中文信息抽取、语义相似度去重、结构化任务自动整理，以及模型不可用时诚实且可解释的离线 fallback。

## 当前限制与扩展

第一版槽位抽取主要依赖规则，不等同于完整 UIE；复杂指代、跨段事项、农历日期和“下下周”等表达可能识别不准。相对时间当前保留原始文本，未结合文档创建时间转换为绝对日期。字符哈希向量仅是模型完全不可用时的运行保障，语义质量低于 MacBERT。下一步最值得做的是积累真实校园通知标注数据并微调分类器，同时把 `InformationExtractor` 后端替换为经过验证的中文 UIE/NER 模型。

## 安全与许可证

请勿把真实群聊、个人信息、凭据或私有模型权重提交到公开仓库。安全问题请按照
[`SECURITY.md`](SECURITY.md) 私下报告。本项目采用 [MIT License](LICENSE)。
