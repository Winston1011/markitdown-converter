def get_global_styles():
    return """
        <style>
        /* 全局样式优化 */
        .main {
            padding: 1rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* 按钮样式优化 */
        .stButton button {
            width: 100%;
            background-color: #2563eb;
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
        }
        .stButton button:hover {
            background-color: #1d4ed8;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        }
        .stButton button:active {
            transform: translateY(0);
        }
        
        /* 标题和文本样式优化 */
        .stHeader {
            font-size: 1.2rem;
            color: #1f2937;
            margin-bottom: 1rem;
            font-weight: 600;
            letter-spacing: -0.025em;
        }
        
        /* 文件上传组件优化 */
        div[data-testid="stFileUploader"] {
            margin-bottom: 1rem;
            padding: 1rem;
            border: 2px dashed #e5e7eb;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #2563eb;
            background-color: rgba(37, 99, 235, 0.05);
        }
        
        /* 标题样式优化 */
        h1 {
            margin-top: 0.5rem !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.5rem !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #111827;
            border-bottom: 2px solid #e5e7eb;
        }
        
        /* 分割线样式 */
        hr {
            margin: 1rem 0 !important;
            border-color: #e5e7eb;
        }
        
        /* 输入框和选择框样式优化 */
        div.stTextInput, div.stSelectbox {
            padding-bottom: 1rem;
        }
        div.stTextInput input, div.stSelectbox select {
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            padding: 0.5rem;
            transition: all 0.2s ease;
        }
        div.stTextInput input:focus, div.stSelectbox select:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        /* 标签样式优化 */
        label {
            font-size: 1rem !important;
            padding-bottom: 0.4rem !important;
            color: #4b5563;
            font-weight: 500;
        }
        
        /* 侧边栏样式优化 */
        .sidebar-title {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            margin-bottom: 1.5rem !important;
            color: #111827 !important;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e5e7eb;
        }
        
        /* 介绍文本样式优化 */
        .intro-text {
            color: #4b5563;
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 2.5rem;
            padding: 1rem;
            background-color: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
        }

        /* 空状态样式 */
        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 2rem auto;
            max-width: 600px;
            border: 1px solid #e5e7eb;
        }
        
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1.5rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .empty-state h3 {
            color: #111827;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            margin-bottom: 1rem !important;
            border: none !important;
        }
        
        .empty-state p {
            color: #6b7280;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        .empty-state-tips {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .tip-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #4b5563;
            font-size: 1rem;
            background-color: #f9fafb;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .tip-item:hover {
            transform: translateY(-2px);
            background-color: #f3f4f6;
        }
        
        .tip-icon {
            font-size: 1.2rem;
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        </style>
    """

def get_chat_styles():
    return """
        <style>
        /* 聊天容器样式优化 */
        .chat-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #ffffff;
            border-radius: 16px 16px 0 0;
            padding: 24px;
            margin: 0;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
            z-index: 1000;
            max-height: 60vh;
            overflow-y: auto;
            transition: all 0.3s ease;
            display: none;  /* 默认隐藏 */
        }
        
        /* 当有聊天内容时显示容器 */
        .chat-container:not(:empty) {
            display: block;
        }
        
        /* 聊天头部样式优化 */
        .chat-header {
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f3f4f6;
            position: sticky;
            top: 0;
            background-color: #ffffff;
            z-index: 1001;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        /* 聊天消息样式优化 */
        .chat-message {
            margin: 16px 0;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
            animation: fadeIn 0.3s ease;
        }
        
        /* 用户消息样式 */
        .user-message {
            background-color: #2563eb;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        
        /* 助手消息样式 */
        .assistant-message {
            background-color: #f3f4f6;
            color: #1f2937;
            margin-right: auto;
            border-bottom-left-radius: 4px;
        }
        
        /* 聊天输入区域样式优化 */
        .chat-input {
            position: sticky;
            bottom: 0;
            background-color: #ffffff;
            padding: 16px 0;
            border-top: 2px solid #f3f4f6;
            margin-top: 24px;
            z-index: 1001;
        }
        
        .chat-input input {
            border-radius: 24px;
            border: 2px solid #e5e7eb;
            padding: 12px 20px;
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        
        .chat-input input:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        /* 主内容区域样式 */
        .main-content {
            margin-bottom: 0;  /* 移除底部边距 */
            padding-bottom: 2rem;
        }
        
        /* 动画效果 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
    """

def get_webpage_card_styles():
    return """
        <style>
        /* 网页卡片样式优化 */
        .webpage-card {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #ffffff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        
        .webpage-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* 网页标题样式 */
        .webpage-title {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 12px;
            color: #111827;
            line-height: 1.4;
        }
        
        /* 网页域名样式 */
        .webpage-domain {
            color: #6b7280;
            font-size: 0.95em;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        /* 网页描述样式 */
        .webpage-description {
            color: #4b5563;
            line-height: 1.6;
            font-size: 1rem;
            padding-top: 8px;
            border-top: 1px solid #f3f4f6;
        }
        </style>
    """ 