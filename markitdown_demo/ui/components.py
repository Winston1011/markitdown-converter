import streamlit as st
from pathlib import Path
import tempfile
from markitdown_demo.utils.file_handlers import (
    display_pdf,
    get_webpage_info,
    handle_xml_file,
    handle_excel_file,
    handle_text_file,
    save_uploaded_file
)
from markitdown_demo.utils.audio_utils import get_audio_info
from markitdown_demo.services.openai_service import chat_with_content
from markitdown_demo.ui.styles import get_chat_styles, get_webpage_card_styles
from markitdown_demo.utils.file_handlers import save_uploaded_file
from markitdown_demo.utils.user_tracker import UserTracker
import socket
from urllib.request import urlopen
import json
from markitdown_demo.services.converter_service import ConverterService

# 初始化用户追踪器（全局单例）
user_tracker = UserTracker()

def get_client_ip():
    """获取客户端IP地址"""
    try:
        # 使用 Streamlit 的实验性功能获取请求信息
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        if ctx is None:
            print("ctx is None")
            return "unknown"
        
        headers = st.context.headers
        
        # 按优先级尝试不同的请求头
        headers_to_check = [
            'X-Forwarded-For',
            'X-Real-IP',
            'CF-Connecting-IP',
            'True-Client-IP',
            'X-Client-IP',
            'Remote-Addr'
        ]

        if headers:
            for header in headers_to_check:
                ip = headers.get(header)
                if ip:
                    if header == 'X-Forwarded-For':
                        ip = ip.split(',')[0].strip()
                    # print(f"IP地址来源: {header}, 值: {ip}")
                    return ip.strip()

        return 'unknown'
        
    except Exception as e:
        print(f"获取IP地址时出错: {str(e)}")
        return 'unknown'

def display_chat_interface(content_key):
    """显示对话界面"""
    st.markdown(get_chat_styles(), unsafe_allow_html=True)
    
    # 检查是否有转换结果
    has_content = content_key is not None and 'markdown_results' in st.session_state and content_key in st.session_state['markdown_results']
    
    if has_content:
        # 创建固定在底部的聊天容器
        chat_container = st.container()
        
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # 聊天头部
            st.markdown('<div class="chat-header">', unsafe_allow_html=True)
            st.markdown("### 💬 文档对话助手")
            
            # 获取当前用户IP和剩余对话次数
            client_ip = get_client_ip()
            can_chat, remaining_chats = user_tracker.can_chat(client_ip)
            st.info(f"剩余对话次数: {remaining_chats}")
            
            # 如果有多个文件，显示文件选择下拉框
            available_files = []
            if 'markdown_results' in st.session_state:
                available_files = [k for k in st.session_state['markdown_results'].keys()]
            
            if len(available_files) > 1:
                selected_file = st.selectbox(
                    "选择要对话的文档",
                    options=available_files,
                    index=available_files.index(content_key) if content_key in available_files else 0,
                    format_func=lambda x: f"{'🌐 ' if x.startswith('http') else '📄 '}{x}"
                )
                if selected_file != content_key:
                    st.session_state.current_chat_key = selected_file
                    content_key = selected_file
                    has_content = True
            elif content_key:
                st.info(f"当前对话文档: {content_key}")
            else:
                st.warning("请先转换文档后再开始对话")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 初始化聊天历史
            if 'chat_histories' not in st.session_state:
                st.session_state.chat_histories = {}
            
            # 如果content_key改变，清空对应的聊天历史
            if 'last_content_key' not in st.session_state:
                st.session_state.last_content_key = None
            
            if content_key != st.session_state.last_content_key:
                if content_key in st.session_state.chat_histories:
                    st.session_state.chat_histories[content_key] = []
                st.session_state.last_content_key = content_key
            
            # 显示聊天消息
            messages_container = st.container()
            with messages_container:
                if has_content and content_key in st.session_state.chat_histories:
                    for message in st.session_state.chat_histories[content_key]:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
            
            # 添加聊天输入区域
            st.markdown("""
            <style>
                /* 输入框容器样式 */
                .chat-input-container {
                    display: flex;
                    align-items: center;
                    background-color: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 24px;
                    padding: 0.5rem 1rem;
                    margin: 1rem 0;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }
                
                /* 输入框样式 */
                .chat-input-container input {
                    flex: 1;
                    border: none !important;
                    background: transparent !important;
                    padding: 0.5rem !important;
                    box-shadow: none !important;
                }
                
                /* 发送按钮样式 */
                .chat-input-container .send-button {
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 0.5rem 1rem;
                    font-size: 0.9rem;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                
                .chat-input-container .send-button:hover {
                    background-color: #1d4ed8;
                }
                
                .chat-input-container .send-button:disabled {
                    background-color: #9ca3af;
                    cursor: not-allowed;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # 使用列布局创建输入框和按钮的组合
            input_container = st.empty()
            
            # 初始化或获取输入框的key
            if 'chat_input_key' not in st.session_state:
                st.session_state.chat_input_key = 0
            
            # 创建输入框
            with input_container:
                prompt = st.text_input(
                    "聊天输入",
                    key=f"chat_input_{st.session_state.chat_input_key}",
                    disabled=not has_content or not can_chat,
                    placeholder="请输入您的问题，按回车发送" if can_chat else "对话次数已用完",
                    label_visibility="collapsed"
                )
            
            # 处理用户输入
            if prompt and has_content:
                # 检查是否可以对话
                if not can_chat:
                    st.error("您的对话次数已用完，无法继续对话")
                    return
                
                # 记录对话次数
                success, remaining = user_tracker.record_chat(get_client_ip())
                if not success:
                    st.error("对话次数不足")
                    return
                
                st.success(f"对话成功，剩余次数：{remaining}")
                
                # 保存当前输入
                current_prompt = prompt
                
                # 初始化当前文档的聊天历史（如果不存在）
                if content_key not in st.session_state.chat_histories:
                    st.session_state.chat_histories[content_key] = []
                
                # 处理消息
                st.session_state.chat_histories[content_key].append({"role": "user", "content": current_prompt})
                
                with messages_container:
                    with st.chat_message("user"):
                        st.markdown(current_prompt)
                
                doc_content = st.session_state['markdown_results'].get(content_key, "")
                
                with messages_container:
                    with st.chat_message("assistant"):
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        response_stream = chat_with_content(doc_content, current_prompt)
                        
                        if isinstance(response_stream, str):
                            st.error(response_stream)
                            return
                        
                        for chunk in response_stream:
                            if chunk.choices[0].delta.content is not None:
                                full_response += chunk.choices[0].delta.content
                                response_placeholder.markdown(full_response + "▌")
                        
                        response_placeholder.markdown(full_response)
                        
                        st.session_state.chat_histories[content_key].append(
                            {"role": "assistant", "content": full_response}
                        )
                
                # 更新输入框的key来清空
                st.session_state.chat_input_key += 1
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_file_preview(uploaded_file):
    """显示文件预览"""
    # 检查是否是新上传的文件
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()
    
    # 使用文件名和大小的组合作为唯一标识
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # 只有当文件未被处理过时才记录
    if file_id not in st.session_state.processed_files:
        user_tracker.record_file_upload(get_client_ip(), uploaded_file.size)
        st.session_state.processed_files.add(file_id)
    
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    try:
        # 首先保存文件到 files 目录
        file_path, file_url = save_uploaded_file(uploaded_file)
        
        if file_extension in ['.mp3', '.wav']:
            # 直接使用已保存的文件路径，不再创建临时文件
            audio_info = get_audio_info(file_path)
            st.audio(uploaded_file, format=f'audio/{file_extension[1:]}')
            
            if audio_info:
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    st.markdown("**📊 基本信息**")
                    st.write(f"文件格式：{audio_info['format']}")
                    st.write(f"文件大小：{audio_info['filesize']}")
                    st.write(f"时长：{audio_info['duration']}")
                    st.write(f"比特率：{audio_info['bitrate']}")
                
                with info_col2:
                    st.markdown("**🎵 音频参数**")
                    st.write(f"采样率：{audio_info['sample_rate']}")
                    st.write(f"声道数：{audio_info['channels']}")
                    st.write(f"编码：{audio_info['encoding']}")
                    st.write(f"MIME类型：{audio_info['mime_type']}")
                
                with info_col3:
                    st.markdown("**📝 元数据**")
                    st.write(f"标题：{audio_info['title']}")
                    st.write(f"艺术家：{audio_info['artist']}")
                    st.write(f"专辑：{audio_info['album']}")
                    st.write(f"流派：{audio_info['genre']}")
                
                st.markdown("**⏰ 时间信息**")
                time_col1, time_col2 = st.columns(2)
                with time_col1:
                    st.write(f"创建时间：{audio_info['created_date']}")
                with time_col2:
                    st.write(f"修改时间：{audio_info['modified_date']}")
        
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            st.image(uploaded_file, use_container_width=True)
        
        elif file_extension in ['.doc', '.docx', '.ppt', '.pptx', '.xlsx', '.xls']:
            preview_url = f"https://view.officeapps.live.com/op/view.aspx?src={file_url}"
            st.markdown(
                f'<iframe src="{preview_url}" width="100%" height="600px" frameborder="0"></iframe>',
                unsafe_allow_html=True
            )
        
        elif file_extension == '.pdf':
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                img, total_pages = display_pdf(tmp_file.name)
                if img:
                    st.image(img, caption="第 1 页", use_container_width=True)
                    if total_pages > 1:
                        st.info(f"仅显示第1页，整文档共{total_pages}页")
                Path(tmp_file.name).unlink(missing_ok=True)
        
        elif file_extension == '.xml':
            xml_content = handle_xml_file(uploaded_file.getvalue())
            st.code(xml_content, language='xml')
        
        elif file_extension == '.xlsx':
            df = handle_excel_file(uploaded_file)
            st.dataframe(df, use_container_width=True)
        
        elif file_extension == '.txt':
            text_content = handle_text_file(uploaded_file.getvalue())
            st.text_area("文件内容", text_content, height=400)
        
        else:
            st.info(f"文件 {uploaded_file.name} 暂不支持预览")
        
    except Exception as e:
        st.error(f"预览错误: {str(e)}")

def display_webpage_preview(url):
    """显示网页预览"""
    st.markdown(get_webpage_card_styles(), unsafe_allow_html=True)
    try:
        webpage_info = get_webpage_info(url)
        
        st.markdown(f"""
            <div class="webpage-card">
                <div class="webpage-title">{webpage_info['title']}</div>
                <div class="webpage-domain">🌐 {webpage_info['domain']}</div>
                <div class="webpage-description">{webpage_info['description']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**网页状态：**")
        st.code(f"""
状态: {webpage_info['status_code']}
内容类型: {webpage_info['content_type']}
        """)
        
        st.markdown(f"[🔗 在新窗口中打开]({url})")
        
    except Exception as e:
        st.error(f"预览失败: {str(e)}")
        st.markdown(f"[🔗 直接访问链接]({url})")

def display_markdown_preview(content, file_name=None):
    """显示Markdown预览"""
    with st.expander("查看转换结果", expanded=True):
        if file_name:
            st.download_button(
                "下载完整 Markdown",
                content,
                file_name=f"{Path(file_name).stem}.md",
                mime="text/markdown"
            )
        
        st.markdown(content, unsafe_allow_html=True) 

def display_welcome_section():
    """显示欢迎部分，包括标题和介绍"""
    # 记录用户访问
    user_tracker.record_visit(get_client_ip())
    
    # 获取用户统计信息
    user_stats = user_tracker.get_user_stats(get_client_ip())
    
    # 创建一个容器来控制垂直位置
    welcome_container = st.container()
    
    # 添加一些空行来调整垂直位置
    for _ in range(3):
        st.write("")
    
    with welcome_container:
        # 标题部分
        st.markdown("""
            <h1 style="text-align: center; font-size: 3rem; font-weight: 800; color: #1f2937; margin-bottom: 2rem;">
                MarkItDown Converter
            </h1>
        """, unsafe_allow_html=True)
        
        # 介绍文本
        st.markdown("""
            <div style="max-width: 800px; margin: 0 auto; text-align: center; color: #6b7280; font-size: 1.1rem; line-height: 1.6; margin-bottom: 2rem;">
                Converter可视化工具基于微软开源的<a href="https://github.com/microsoft/markitdown" style="color: #2563eb; text-decoration: none;">MarkItDown</a>工具，
                能够将各种格式的文档（包括PDF、Word、PPT等）转换为结构化Markdown格式。
            </div>
        """, unsafe_allow_html=True)
        
        # 特点列表
        features = [
            ("📁", "支持多种文件格式", "Mp3、Wav、URL、PDF、Word、PPT、Excel、图片等"),
            ("🤖", "智能AI转换", "使用先进的GPT模型进行内容理解和转换"),
            ("👁️", "实时预览", "支持原文档和转换结果的双���实时预览"),
            ("📝", "保持格式", "自动保存文档的标题、列表、表格等重要格式"),
            ("💬", "对话模式", "支持与转换后的Markdown内容进行对话"),
            ("🔄", "批量处理", "支持多个文件同时上传和批量转换处理")
        ]
        
        # 计算需要的行数
        num_features = len(features)
        num_rows = (num_features + 2) // 3  # 向上取整
        
        # 使用行列布局显示特点
        for row in range(num_rows):
            cols = st.columns(3)
            for col in range(3):
                idx = row * 3 + col
                if idx < num_features:
                    icon, title, desc = features[idx]
                    with cols[col]:
                        st.markdown(f"""
                            <div style="
                                background-color: white;
                                padding: 1.5rem;
                                border-radius: 12px;
                                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                                margin-bottom: 1rem;
                                transition: transform 0.2s;
                                height: 100%;
                                min-height: 180px;
                                display: flex;
                                flex-direction: column;
                                justify-content: flex-start;
                            ">
                                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                                <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">{title}</div>
                                <div style="color: #6b7280; font-size: 0.9rem;">{desc}</div>
                            </div>
                        """, unsafe_allow_html=True) 
        
        # 在特点列表下方添加用户统计信息
        st.markdown("""
            <div style="
                max-width: 800px;
                margin: 2rem auto;
                padding: 1rem;
                background-color: #f8fafc;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            ">
                <h3 style="color: #1f2937; font-size: 1.2rem; margin-bottom: 0.5rem; text-align: center;">
                    📊 您的使用统计
                </h3>
                <div style="text-align: center; margin-bottom: 1rem; color: #6b7280; font-size: 0.9rem;">
                    IP地址：{ip_address}
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; color: #2563eb; font-weight: 600;">
                            {visit_count}
                        </div>
                        <div style="color: #6b7280; font-size: 0.9rem;">
                            访问次数
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; color: #2563eb; font-weight: 600;">
                            {chat_count}
                        </div>
                        <div style="color: #6b7280; font-size: 0.9rem;">
                            对话次数
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; color: #2563eb; font-weight: 600;">
                            {file_count}
                        </div>
                        <div style="color: #6b7280; font-size: 0.9rem;">
                            上传文件数
                        </div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; color: #2563eb; font-weight: 600;">
                            {convert_count}
                        </div>
                        <div style="color: #6b7280; font-size: 0.9rem;">
                            转换次数
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; color: #2563eb; font-weight: 600;">
                            {total_size}
                        </div>
                        <div style="color: #6b7280; font-size: 0.9rem;">
                            累计上传大小
                        </div>
                    </div>
                </div>
            </div>
        """.format(
            ip_address=get_client_ip(),
            visit_count=user_stats["visit_count"],
            chat_count=user_stats["chat_count"],
            file_count=user_stats["file_count"],
            convert_count=user_stats["convert_count"],
            total_size=user_tracker.format_file_size(user_stats["total_file_size"])
        ), unsafe_allow_html=True) 

def convert_files(files, model):
    """转换文件"""
    converter = ConverterService(model=model)
    return converter.convert_files(files, ip=get_client_ip()) 