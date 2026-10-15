import streamlit as st
import os
import re
import calendar
from datetime import datetime

st.set_page_config(page_title="24/7 輪班與排假表系統", page_icon="📅", layout="wide")

# 🎨 嚴格對應您的真實人員與專屬代表色與部門
DEFAULT_PERSON_COLORS = {
    "琪": "#9b59b6",       # 紫色 (常銘 - 早班)
    "安": "#f1c40f",       # 黃色 (常銘 - 早班)
    "淵": "#1abc9c",       # 藍綠色 (常銘 - 夜班)
    "Benson": "#795548",   # 灰帶點咖 (常銘 - 早班)
    "萱": "#3498db",       # 淡藍色 (暖惒 - 早班)
    "聖": "#2c3e50",       # 綻藍色 (暖惒 - 早班)
    "慈": "#e74c3c",       # 紅色 (暖惒 - 夜班)
    "孟": "#e91e63"        # 粉色 (暖惒 - 夜班)
}

# 員工所屬部門與班別對照
EMPLOYEE_DEPT_GROUP = {
    "琪": {"dept": "常銘", "group": "早班"},
    "安": {"dept": "常銘", "group": "早班"},
    "淵": {"dept": "常銘", "group": "夜班"},
    "Benson": {"dept": "常銘", "group": "早班"},
    "萱": {"dept": "暖惒", "group": "早班"},
    "聖": {"dept": "暖惒", "group": "早班"},
    "慈": {"dept": "暖惒", "group": "夜班"},
    "孟": {"dept": "暖惒", "group": "夜班"}
}

st.title("🏢 企業級 24/7 永續排假與輪班 AI Agent 系統")
st.markdown("本系統已修復語法錯誤，並完美支援全員自助排假、跨部門代班與同組協調機制！")

# 初始化 Session State
if "daily_leaves" not in st.session_state:
    st.session_state.daily_leaves = {
        "10/1": ["萱", "安", "Benson", "孟"],
        "10/2": ["聖", "安", "Benson", "孟"],
        "10/3": ["聖", "淵", "安", "慈"],
        "10/4": ["萱", "淵", "慈", "琪"],
        "10/5": ["萱", "安", "Benson", "孟"],
        "10/6": ["聖", "安", "Benson", "孟"],
        "10/7": ["聖", "安", "淵", "慈"],
        "10/8": ["聖", "琪", "淵", "慈"],
        "10/9": ["聖", "琪", "Benson", "孟"],
        "10/10": ["萱", "琪", "Benson", "孟"],
        "10/11": ["萱", "淵", "慈", "琪"],
        "10/12": ["萱", "淵", "慈", "安"],
        "10/13": ["聖", "淵", "慈", "安"],
        "10/14": ["聖", "琪", "Benson", "孟"],
        "10/15": ["聖", "琪", "Benson", "孟"],
        "10/16": ["安", "萱", "Benson", "慈"],
        "10/17": ["安", "萱", "淵", "慈"],
        "10/18": ["淵", "琪", "孟", "聖"],
        "10/19": ["淵", "琪", "孟", "聖"],
        "10/20": ["萱", "琪", "Benson", "慈"],
        "10/21": ["萱", "安", "Benson", "慈"],
        "10/22": ["孟", "安", "Benson", "聖"],
        "10/23": ["孟", "安", "淵", "聖"],
        "10/24": ["萱", "琪", "淵", "慈"],
        "10/25": ["萱", "琪", "淵", "慈"],
        "10/26": ["萱", "淵", "安", "孟"],
        "10/27": ["淵", "安", "聖", "慈"],
        "10/28": ["琪", "淵", "聖", "慈"],
        "10/29": ["萱", "琪", "Benson", "孟"],
        "10/30": ["萱", "琪", "Benson", "孟"],
        "10/31": ["琪", "Benson", "孟", "聖"]
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！系統語法已修正，請隨時切換身分排假或進行代班協調。"}
    ]

# 側邊欄：色彩圖例
with st.sidebar:
    st.header("🎨 人員專屬色彩圖例")
    for name, color in DEFAULT_PERSON_COLORS.items():
        st.markdown(f'<span style="background-color:{color}; color:white; padding:4px 10px; border-radius:4px; font-weight:bold;">{name}</span>', unsafe_allow_html=True)

# 1. 永續排假與月曆檢視控制台
st.markdown("---")
st.header("📅 永續排假與月曆檢視控制台")

years_list = list(range(2026, 2036))
c_year, c_month = st.columns(2)
with c_year:
    selected_year = st.selectbox("選擇全域年份", years_list, index=0, key="global_year")
with c_month:
    selected_month_str = st.selectbox("選擇全域月份", [f"{m}月" for m in range(1, 13)], index=9, key="global_month")

month_num = int(selected_month_str.replace("月", ""))
year_num = selected_year

st.markdown(f"### 🗓️ {year_num}年 {selected_month_str} 每日排假一覽表")

week_days = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"]
header_cols = st.columns(7)
for idx, day_name in enumerate(week_days):
    with header_cols[idx]:
        st.markdown(f"<div style='text-align: center; font-weight: bold; color: #555;'>{day_name}</div>", unsafe_allow_html=True)

cal = calendar.Calendar(firstweekday=6)
month_days = list(cal.itermonthdays2(year_num, month_num))
weeks = [month_days[i:i+7] for i in range(0, len(month_days), 7)]

for week in weeks:
    cols = st.columns(7)
    for idx, (day, weekday) in enumerate(week):
        with cols[idx]:
            if day == 0:
                st.markdown("<div style='color:lightgray;'>-</div>", unsafe_allow_html=True)
            else:
                d_key = f"{month_num}/{day}"
                st.markdown(f"**{d_key}**")
                off_people = list(set(st.session_state.daily_leaves.get(d_key, [])))
                if off_people:
                    for p in off_people:
                        c = DEFAULT_PERSON_COLORS.get(p, "#888888")
                        st.markdown(f'<div style="background-color:{c}; color:white; padding:2px 4px; border-radius:3px; font-size:11px; margin-bottom:2px; text-align:center;">{p} 休</div>', unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:gray; font-size:10px;'>尚無排假</div>", unsafe_allow_html=True)

st.markdown("---")

# 2. 左右雙欄：員工自助排假 + 暖惒代班／換班協調機制
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("👤 員工自助排假與代班協調區")
    
    # 選擇身分
    all_staff_names = list(DEFAULT_PERSON_COLORS.keys())
    current_user = st.selectbox("選擇您的身分（排假人）", all_staff_names, key="active_user_select")
    
    user_info = EMPLOYEE_DEPT_GROUP.get(current_user, {})
    st.info(f"📌 當前身分：**{current_user}** | 所屬部門：{user_info.get('dept')} |
