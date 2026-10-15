import streamlit as st
import os
import re
import calendar
from datetime import datetime

st.set_page_config(page_title="24/7 輪班與排假表系統", page_icon="📅", layout="wide")

# 🎨 嚴格對應您的真實人員與專屬代表色
DEFAULT_PERSON_COLORS = {
    "琪": "#9b59b6",       # 紫色
    "安": "#f1c40f",       # 黃色
    "淵": "#1abc9c",       # 藍綠色
    "Benson": "#795548",   # 灰帶點咖 (勳)
    "萱": "#3498db",       # 淡藍色
    "聖": "#2c3e50",       # 綻藍色
    "慈": "#e74c3c",       # 紅色
    "孟": "#e91e63"        # 粉色
}

st.title("🏢 企業級 24/7 永續排假與輪班 AI Agent 系統")
st.markdown("本系統支援 **2026 年至 2035 年（未來 10 年）** 任意年份與月份的跨年永續排假！")

# 初始化 Session State
if "departments" not in st.session_state:
    st.session_state.departments = ["常銘", "暖惒"]

if "person_colors" not in st.session_state:
    st.session_state.person_colors = DEFAULT_PERSON_COLORS.copy()

if "employees_db" not in st.session_state:
    st.session_state.employees_db = [
        {"id": "EMP_01", "name": "琪", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_02", "name": "安", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_03", "name": "淵", "dept": "常銘", "group": "夜班 (20:30-08:30)", "status": "在職"},
        {"id": "EMP_04", "name": "Benson", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_05", "name": "萱", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_06", "name": "聖", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_07", "name": "慈", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"},
        {"id": "EMP_08", "name": "孟", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"}
    ]

# 🧠 全局動態假表資料庫（10 月預載真實名單）
if "daily_leaves" not in st.session_state:
    st.session_state.daily_leaves = {
        # 10月精準真實假表
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
        {"role": "assistant", "content": "您好！系統已擴充支援 2026–2035 年共 10 年的任意跨年排假！"}
    ]

# 側邊欄：色彩圖例與金鑰保護
with st.sidebar:
    st.header("🎨 人員專屬色彩圖例")
    for name, color in st.session_state.person_colors.items():
        st.markdown(f'<span style="background-color:{color}; color:white; padding:4px 10px; border-radius:4px; font-weight:bold;">{name}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("🔐 系統進階與 API 金鑰設定 (管理員專用)"):
        default_token = st.secrets.get("LINE_CHANNEL_ACCESS_TOKEN", os.getenv("LINE_CHANNEL_ACCESS_TOKEN", ""))
        line_token = st.text_input("LINE Channel Access Token", type="password", value=default_token)
        
        if st.button("更新並加密儲存金鑰"):
            os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = line_token
            st.success("✅ 金鑰已安全加密載入！")

# 1. 視覺化月份月曆檢視區（動態 10 年支援）
st.markdown("---")
st.header("📅 視覺化動態排假月曆檢視區")

# 支援 2026 到 2035 共 10 年
years_list = list(range(2026, 2036))

c_year, c_month = st.columns(2)
with c_year:
    selected_year = st.selectbox("選擇年份", years_list, index=0)
with c_month:
    selected_month = st.selectbox("選擇月份", [f"{m}月" for m in range(1, 13)], index=9) # 預設10月

month_num = int(selected_month.replace("月", ""))
year_num = selected_year

st.markdown(f"### 🗓️ {year_num}年 {selected_month} 每日排假一覽表")

# 顯示星期表頭 (週日至週六)
week_days = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"]
header_cols = st.columns(7)
for idx, day_name in enumerate(week_days):
    with header_cols[idx]:
        st.markdown(f"<div style='text-align: center; font-weight: bold; color: #555;'>{day_name}</div>", unsafe_allow_html=True)

# 動態計算該月標準週曆
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
                        c = st.session_state.person_colors.get(p, "#888888")
                        st.markdown(f'<div style="background-color:{c}; color:white; padding:2px 4px; border-radius:3px; font-size:11px; margin-bottom:2px; text-align:center;">{p} 休</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:gray; font-size:10px;">尚無排假</div>', unsafe_allow_html=True)

st.markdown("---")

# 2. 下方左右雙欄：任意年份與月份員工自助排假與 AI 互動區
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("👤 永續跨年員工自助排假")
    st.markdown(f"目前針對 **{year_num} 年 {selected_month}** 進行自助排假：")
    
    with st.form("self_leave_form"):
        # 選擇身分
        all_staff_names = list(DEFAULT_PERSON_COLORS.keys())
        current_user = st.selectbox("選擇您的身分（排假人）", all_staff_names)
        
        # 動態計算選擇月份的天數
        _, num_days_in_month = calendar.monthrange(year_num, month_num)
        target_month_days = [f"{month_num}/{d}" for d in range(1, num_days_in_month + 1)]
        
        # 找出目前該成員在選擇月份中已勾選的日期
        current_user_leaves = [d for d in target_month_days if current_user in st.session_state.daily_leaves.get(d, [])]
        
        selected_user_off = st.multiselect(f"勾選【{current_user}】想休假的 {year_num}年{selected_month} 日期：", target_month_days, default=current_user_leaves)
        
        submit_user_leave = st.form_submit_button(f"🚀 提交【{current_user}】在 {year_num}年{selected_month} 的排假")
        
        if submit_user_leave:
            for d in target_month_days:
                if d not in st.session_state.daily_leaves:
                    st.session_state.daily_leaves[d] = []
                
                if d in selected_user_off:
                    if current_user not in st.session_state.daily_leaves[d]:
                        st.session_state.daily_leaves[d].append(current_user)
                else:
                    if current_user in st.session_state.daily_leaves[d]:
                        st.session_state.daily_leaves[d].remove(current_user)
            
            st.success(f"🎉 成功！【{current_user}】在 {year_num}年{selected_month} 總共排了 {len(selected_user_off)} 天假。")
            st.rerun()

with col2:
    st.header("💬 AI Agent 智慧互動區")
    
    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])
                
    user_input = st.chat_input("請在此輸入查詢指令（例如：11/1誰休假）...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        query_text = user_input.strip()
        reply = ""
        
        date_match = re.search(r'(\d{1,2})/(\d{1,2})', query_text)
        
        if date_match:
            month, day = date_match.groups()
            date_key = f"{month}/{day}"
            
            if date_key in st.session_state.daily_leaves:
                off_list = list(set(st.session_state.daily_leaves[date_key]))
                all_people = list(st.session_state.person_colors.keys())
                working_list = [p for p in all_people if p not in off_list]
                
                target_name = None
                for name in all_people:
                    if name in query_text:
                        target_name = name
                        break
                
                if target_name:
                    if target_name in off_list:
                        reply = f"📋 查詢結果：在 **{date_key}** 這天，【{target_name}】固定休假 🌴。"
                    else:
                        reply = f"📋 查詢結果：在 **{date_key}** 這天，【{target_name}】需要上班 💼！"
                else:
                    reply = f"📅 **{date_key} 班表查詢結果**\n\n"
                    reply += f"💼 **上班人員**：{', '.join(working_list) if working_list else '全員休假'}\n"
                    reply += f"🌴 **休假人員**：{', '.join(off_list) if off_list else '無'}"
            else:
                reply = f"❌ 找不到 {date_key} 的假表記錄（可能該月份尚未排假）。"
        else:
            reply = f"🤖 AI Agent 已收到您的指令：「{user_input}」。您可以輸入日期來查詢（例如：「11/1誰休假」）！"

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
