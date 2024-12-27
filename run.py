import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="MarkItDown Converter",
    layout="wide",
    initial_sidebar_state="expanded"  # 默认展开侧边栏
)

# 导入并运行主应用
from markitdown_demo.app import init_ui
init_ui() 