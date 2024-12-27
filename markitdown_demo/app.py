import streamlit as st
from pathlib import Path
import tempfile
from markitdown_demo.config.settings import (
    SUPPORTED_EXTENSIONS,
    MODEL_OPTIONS,
    MAX_FILES
)
from markitdown_demo.utils.file_handlers import cleanup_old_files, save_uploaded_file
from markitdown_demo.services.converter_service import ConverterService
from markitdown_demo.ui.components import (
    display_chat_interface,
    display_file_preview,
    display_webpage_preview,
    display_markdown_preview,
    display_welcome_section,
    get_client_ip,
    user_tracker
)
from markitdown_demo.ui.styles import get_global_styles

def init_ui():
    """初始化UI"""
    # 添加全局样式
    st.markdown(get_global_styles(), unsafe_allow_html=True)
    
    # 初始化全局对话状态和上传文件状态
    if 'current_chat_key' not in st.session_state:
        st.session_state.current_chat_key = None
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = {}
    if 'uploaded_files_dict' not in st.session_state:
        st.session_state.uploaded_files_dict = {}
    if 'file_paths_dict' not in st.session_state:
        st.session_state.file_paths_dict = {}
    
    # 控制面板 - 移动到侧边栏
    with st.sidebar:
        st.markdown('<h2 class="sidebar-title">Control Panel</h2>', unsafe_allow_html=True)
        
        # 文件上传
        uploaded_files = st.file_uploader(
            "选择文件",
            type=[ext[1:] for ext in SUPPORTED_EXTENSIONS],
            accept_multiple_files=True,
            help="支持的格式: " + ", ".join(SUPPORTED_EXTENSIONS) + "\n最多可上传10个文件"
        )
        
        # 检查上传文件数量并更新上传文件字典
        if uploaded_files:
            if len(uploaded_files) > MAX_FILES:
                st.error(f"一次最多只能上传{MAX_FILES}个文件")
                uploaded_files = uploaded_files[:MAX_FILES]
            
            # 更新上传文件字典并保存文件
            new_files_dict = {}
            new_paths_dict = {}
            for file in uploaded_files:
                file_path, file_url = save_uploaded_file(file)
                new_files_dict[file.name] = file
                new_paths_dict[file.name] = (file_path, file_url)
            
            st.session_state.uploaded_files_dict = new_files_dict
            st.session_state.file_paths_dict = new_paths_dict
        else:
            # 如果没���选择文件，清空上传文件字典和相关状态
            if st.session_state.uploaded_files_dict:
                # 删除已保存的文件
                for file_path, _ in st.session_state.file_paths_dict.values():
                    Path(file_path).unlink(missing_ok=True)
            
            st.session_state.uploaded_files_dict = {}
            st.session_state.file_paths_dict = {}
            if 'markdown_results' in st.session_state:
                st.session_state.markdown_results = {
                    k: v for k, v in st.session_state.markdown_results.items()
                    if k.startswith('http')  # 保留URL的结果
                }
            if 'chat_histories' in st.session_state:
                st.session_state.chat_histories = {
                    k: v for k, v in st.session_state.chat_histories.items()
                    if k.startswith('http')  # 保留URL的对话历史
                }
            if st.session_state.current_chat_key and not st.session_state.current_chat_key.startswith('http'):
                st.session_state.current_chat_key = None
        
        # URL输入
        st.markdown("### 或者输入网页URL")
        url_input = st.text_input(
            "网页URL",
            help="输入要转换的网页URL地址",
            placeholder="https://example.com"
        )
        
        # 模型选择
        selected_model = st.selectbox(
            "选择模型",
            options=list(MODEL_OPTIONS.keys()),
            help="选择用于转换的AI模型"
        )
        
        # 获取当前用户IP和剩余次数
        client_ip = get_client_ip()
        can_convert, remaining_converts = user_tracker.can_convert(client_ip)
        can_chat, remaining_chats = user_tracker.can_chat(client_ip)
        
        # 显示剩余次数
        st.info(f"剩余转换次数: {remaining_converts}")
        st.info(f"剩余对话次数: {remaining_chats}")
        
        # 转换按钮
        convert_button = st.button(
            "开始转换",
            disabled=not (
                len(st.session_state.uploaded_files_dict) > 0 or 
                (url_input and url_input.strip().startswith("http"))
            ),
            help="点击开始转换文档"
        )
    
    # 创建转换器服务
    converter = ConverterService(model=MODEL_OPTIONS[selected_model])
    
    # 判断是否有文件或URL
    has_content = bool(st.session_state.uploaded_files_dict or (url_input and url_input.strip()))
    
    # 如果点击了转换按钮，记录转换次数
    if convert_button and has_content:
        client_ip = get_client_ip()
        
        # 计算需要转换的新文件/URL数量
        new_items_count = 0
        
        # 检查URL是否需要转换
        if url_input and url_input.strip():
            if url_input not in st.session_state.get('markdown_results', {}):
                new_items_count += 1
        
        # 检查文件是否需要转换
        for file_name in st.session_state.uploaded_files_dict:
            if file_name not in st.session_state.get('markdown_results', {}):
                new_items_count += 1
        
        # 如果没有新的内容需要转换，直接显示已有结果
        if new_items_count == 0:
            st.info("所有内容已经转换过，直接显示已有结果")
        else:
            # 检查是否可以转换
            can_convert, remaining = user_tracker.can_convert(client_ip)
            if not can_convert:
                st.error("您的转换次数已用完，无法继续转换")
                return
            
            # 检查剩余次数是否足够
            if remaining < new_items_count:
                st.error(f"转换次数不足，需要 {new_items_count} 次，剩余 {remaining} 次")
                return
            
            # 记录转换次数
            success, remaining = user_tracker.record_convert(client_ip, new_items_count)
            if not success:
                st.error("转换次数不足，无法完成所有转换")
                return
            
            st.success(f"转换成功，剩余次数：{remaining}")
            print(f"记录转换: IP={client_ip}, 数量={new_items_count}")
    
    # 创建主容器
    main_container = st.container()
    
    with main_container:
        # 根据内容状态显示不同的界面
        if not has_content:
            # 显示欢迎界面
            display_welcome_section()
        else:
            # 显示预览界面
            preview_container = st.container()
            
            with preview_container:
                # 处理URL输入
                if url_input and url_input.strip():
                    st.markdown(f"### URL: {url_input}")
                    cols = st.columns(2)
                    
                    with cols[0]:
                        st.markdown('<p class="stHeader">URL Preview</p>', unsafe_allow_html=True)
                        display_webpage_preview(url_input)
                    
                    with cols[1]:
                        st.markdown('<p class="stHeader">Markdown Output</p>', unsafe_allow_html=True)
                        
                        # 显示已有的转换结果
                        if url_input in st.session_state.get('markdown_results', {}):
                            display_markdown_preview(st.session_state['markdown_results'][url_input])
                        
                        # 只在点击转换按钮且没有已有结果时进行新的转换
                        if convert_button and url_input not in st.session_state.get('markdown_results', {}):
                            try:
                                result = converter.convert_url(url_input)
                                if 'markdown_results' not in st.session_state:
                                    st.session_state['markdown_results'] = {}
                                st.session_state['markdown_results'][url_input] = result
                                st.session_state.current_chat_key = url_input
                                # 初始化新URL的对话历史
                                if url_input not in st.session_state.chat_histories:
                                    st.session_state.chat_histories[url_input] = []
                                st.success("URL转换成功")
                                display_markdown_preview(result)
                            except Exception as e:
                                st.error(f"URL转换失败: {str(e)}")
                
                # 处理已上传的文件
                if st.session_state.uploaded_files_dict:
                    for file_name, file in st.session_state.uploaded_files_dict.items():
                        st.markdown(f"### {file_name}")
                        cols = st.columns(2)
                        
                        with cols[0]:
                            st.markdown('<p class="stHeader">Document Preview</p>', unsafe_allow_html=True)
                            display_file_preview(file)
                        
                        with cols[1]:
                            st.markdown('<p class="stHeader">Markdown Output</p>', unsafe_allow_html=True)
                            
                            # 显示已有的转换结果
                            if file_name in st.session_state.get('markdown_results', {}):
                                display_markdown_preview(
                                    st.session_state['markdown_results'][file_name],
                                    file_name
                                )
                            
                            # 只在点击转换按钮且没有已有结果时进行新的转换
                            if convert_button and file_name not in st.session_state.get('markdown_results', {}):
                                try:
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp_file:
                                        tmp_file.write(file.getvalue())
                                        result = converter.convert_file(tmp_file.name, Path(file_name).suffix)
                                        
                                        if 'markdown_results' not in st.session_state:
                                            st.session_state['markdown_results'] = {}
                                        st.session_state['markdown_results'][file_name] = result
                                        st.session_state.current_chat_key = file_name
                                        # 初始化新文件的对话历史
                                        if file_name not in st.session_state.chat_histories:
                                            st.session_state.chat_histories[file_name] = []
                                        
                                        Path(tmp_file.name).unlink(missing_ok=True)
                                        st.success(f"文件 {file_name} 转换成功")
                                        display_markdown_preview(result, file_name)
                                except Exception as e:
                                    st.error(f"转换失败: {str(e)}")
                        st.markdown("---")
    
    # 在内容外显示全局对话界面
    if st.session_state.current_chat_key:
        display_chat_interface(st.session_state.current_chat_key)
    else:
        display_chat_interface(None)
    
    # 清理旧文件
    cleanup_old_files()

if __name__ == "__main__":
    init_ui() 