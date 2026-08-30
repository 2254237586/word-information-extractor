import tempfile
from pathlib import Path

import streamlit as st

from src.pipeline import ExtractionPipeline

st.set_page_config(page_title="Word 文档重要事项智能提取系统", page_icon="📌", layout="wide")
st.title("Word 文档重要事项智能提取系统")
uploaded = st.file_uploader("上传 Word 文件", type=["docx"])
if uploaded and st.button("开始分析", type="primary"):
    progress = st.progress(10, text="正在读取文档并加载模型……")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / uploaded.name
            path.write_bytes(uploaded.getvalue())
            result = ExtractionPipeline().run(path)
        progress.progress(100, text="分析完成")
        st.success(f"共读取 {result['total_sentences']} 个句子，识别重要内容 {result['important_sentences']} 条")
        icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        for task in result["tasks"]:
            with st.expander(f"{icons[task['priority']]} {task['event']}", expanded=task["priority"] == "high"):
                cols = st.columns(3)
                cols[0].metric("优先级", task["priority"])
                cols[1].metric("置信度", f"{task['importance_score']:.1%}")
                cols[2].metric("来源", f"段落 {task['paragraph_id'] + 1}")
                st.json(task)
    except Exception as exc:
        progress.empty()
        st.error(f"分析失败：{exc}")

