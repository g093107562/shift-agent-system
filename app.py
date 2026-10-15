import streamlit as st
import os
import json
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

DB_FILE = "leave_database.json"

# 💾 雲端永久儲存讀取函式（支援跨年月獨立儲存）
def load_leaves_from_disk():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    
    # 預設初始假表（僅保留 10 月示範資料，11月起保持乾淨獨立）
    initial_data = {}
    oct_default = {
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
    for k, v in oct_default.items():
        initial_data[f"2026_{k}"] = v
    return initial_data

def save_leaves_to_disk(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"存檔失敗: {e}")

st.title("🏢 企業級 24/7 永續排假與輪班 AI Agent 系統")
st.markdown("🔒 **多年月獨立雲端資料庫已啟動**：各月份排假完全隔離，重新整理網頁永不丟失！")

# 初始化 Session State
if "daily_leaves" not in st.session_state:
    st.session_state.daily_leaves = load_leaves_from_disk()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！各月份假表已完全獨立隔離。您可以安心選擇年份與月份進行排假與查詢！"}
    ]

# 側邊欄：色彩圖例
with st.sidebar:
    st.header("🎨 人員專屬色彩圖例")
    for name, color in DEFAULT_PERSON_COLORS.items():
        st.markdown(f'<span style="background-color:{color}; color:white; padding:4px 10px; border-radius:4px; font-weight:bold;">{name}</span>', unsafe_allow_html=True)

# 1. 控制台
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
                d_key = f"{year_num}_{month_num}/{day}"
                st.markdown(f"**{month_num}/{day}**")
                off_people = list(set(st.session_state.daily_leaves.get(d_key, [])))
                if off_people:
                    for p in off_people:
                        c = DEFAULT_PERSON_COLORS.get(p, "#888888")
                        st.markdown(f'<div style="background-color:{c}; color:white; padding:2px 4px; border-radius:3px; font-size:11px; margin-bottom:2px; text-align:center;">{p} 休</div>', unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:gray; font-size:10px;'>尚無排假</div>", unsafe_allow_html=True)

st.markdown("---")

# 2. 雙欄
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("👤 員工自助排假區")
    all_staff_names = list(DEFAULT_PERSON_COLORS.keys())
    current_user = st.selectbox("選擇您的身分（排假人）", all_staff_names, key="active_user_select")
    
    user_info = EMPLOYEE_DEPT_GROUP.get(current_user, {})
    current_dept = user_info.get('dept')
    current_group = user_info.get('group')
    st.info(f"📌 當前身分：**{current_user}** | 所屬部門：{current_dept} | 班別：{current_group}")
    
    with st.form("self_leave_form"):
        _, num_days_in_month = calendar.monthrange(year_num, month_num)
        all_month_keys = [f"{year_num}_{month_num}/{d}" for d in range(1, num_days_in_month + 1)]
        all_month_display = [f"{month_num}/{d}" for d in range(1, num_days_in_month + 1)]
        
        same_group_colleagues = [
            name for name, info in EMPLOYEE_DEPT_GROUP.items() 
            if info["dept"] == current_dept and info["group"] == current_group and name != current_user
        ]
        
        colleagues_off_days = set()
        for dk, d_disp in zip(all_month_keys, all_month_display):
            day_off_list = st.session_state.daily_leaves.get(dk, [])
            for c_name in same_group_colleagues:
                if c_name in day_off_list:
                    colleagues_off_days.add(d_disp)
        
        available_display_days = [d for d in all_month_display if d not in colleagues_off_days]
        
        current_user_leaves = []
        for dk, d_disp in zip(all_month_keys, all_month_display):
            if current_user in st.session_state.daily_leaves.get(dk, []):
                current_user_leaves.append(d_disp)
                
        valid_default_leaves = [d for d in current_user_leaves if d in available_display_days]
        
        selected_user_off = st.multiselect(
            f"勾選【{current_user}】想休假的 {year_num}年{selected_month_str} 日期：", 
            options=available_display_days, 
            default=valid_default_leaves
        )
        
        submit_user_leave = st.form_submit_button(f"🚀 提交【{current_user}】在 {year_num}年{selected_month_str} 的排假")
        
        if submit_user_leave:
            for dk, d_disp in zip(all_month_keys, all_month_display):
                if dk not in st.session_state.daily_leaves:
                    st.session_state.daily_leaves[dk] = []
                
                if d_disp in available_display_days:
                    if d_disp in selected_user_off:
                        if current_user not in st.session_state.daily_leaves[dk]:
                            st.session_state.daily_leaves[dk].append(current_user)
                    else:
                        if current_user in st.session_state.daily_leaves[dk]:
                            st.session_state.daily_leaves[dk].remove(current_user)
            
            save_leaves_to_disk(st.session_state.daily_leaves)
            st.success(f"🎉 成功！【{current_user}】在 {year_num}年{selected_month_str} 總共排了 {len(selected_user_off)} 天假，已永久存檔！")
            st.rerun()

    # 🤝 跨部門代班與同組換班/調假機制
    st.markdown("---")
    st.subheader("🤝 跨部門代班與同組換班/調假機制")
    st.markdown("如果想和同組夥伴在同一天休假，或需進行輪班調假，可透過暖惒部門支援代班：")
    
    with st.form("substitute_form"):
        target_disp_date = st.selectbox("選擇需要調假/代班的日期", [f"{month_num}/{d}" for d in range(1, num_days_in_month + 1)], key="sub_date")
        target_db_key = f"{year_num}_{target_disp_date}"
        
        current_day_off = st.session_state.daily_leaves.get(target_db_key, [])
        st.write(f"📅 **{target_disp_date} 目前休假名單**：{', '.join(current_day_off) if current_day_off else '無'}")
        
        warm_early_staff = [name for name, info in EMPLOYEE_DEPT_GROUP.items() if info["dept"] == "暖惒" and info["group"] == "早班"]
        helper_person = st.selectbox("指派【暖惒】支援代班人員", warm_early_staff)
        
        action_type = st.radio("選擇調班/代班動作", ["申請同日休假（需暖惒代班支援）", "與已休假人員換班/調假"])
        
        sub_btn = st.form_submit_button("執行調假/代班申請")
        if sub_btn:
            if target_db_key not in st.session_state.daily_leaves:
                st.session_state.daily_leaves[target_db_key] = []
                
            if action_type == "申請同日休假（需暖惒代班支援）":
                if current_user not in st.session_state.daily_leaves[target_db_key]:
                    st.session_state.daily_leaves[target_db_key].append(current_user)
                save_leaves_to_disk(st.session_state.daily_leaves)
                st.success(f"✅ 已成功送出並永久存檔！【{target_disp_date}】由【{helper_person}（暖惒）】跨部門支援代班，【{current_user}】順利休假！")
                st.rerun()
            else:
                off_colleagues_on_day = [p for p in current_day_off if p in same_group_colleagues]
                if off_colleagues_on_day:
                    target_colleague = off_colleagues_on_day[0]
                    st.session_state.daily_leaves[target_db_key].remove(target_colleague)
                    if current_user not in st.session_state.daily_leaves[target_db_key]:
                        st.session_state.daily_leaves[target_db_key].append(current_user)
                    save_leaves_to_disk(st.session_state.daily_leaves)
                    st.success(f"✅ 換班成功並永久存檔！在【{target_disp_date}】由【{current_user}】與【{target_colleague}】成功調換班別！")
                    st.rerun()
                else:
                    if current_user not in st.session_state.daily_leaves[target_db_key]:
                        st.session_state.daily_leaves[target_db_key].append(current_user)
                    save_leaves_to_disk(st.session_state.daily_leaves)
                    st.success(f"✅ 已成功完成並永久存檔 {target_disp_date} 的調假申請！")
                    st.rerun()

with col2:
    st.header("💬 AI Agent 智慧互動區")
    
    chat_container = st.container(height=450)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])
                
    user_input = st.chat_input("請在此輸入查詢指令（例如：琪11月休幾天？、11/5誰休假）...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        query_text = user_input.strip()
        reply = ""
        
        matched_person = None
        for name in DEFAULT_PERSON_COLORS.keys():
            if name in query_text:
                matched_person = name
                break
                
        matched_month = None
        m_match = re.search(r'(\d{1,2})\s*月', query_text)
        if m_match:
            matched_month = int(m_match.group(1))
        else:
            matched_month = month_num

        date_match = re.search(r'(\d{1,2})/(\d{1,2})', query_text)

        if matched_person and ("幾天" in query_text or "休假" in query_text or "幾號" in query_text or "哪天" in query_text or not date_match):
            person_off_dates = []
            prefix = f"{year_num}_{matched_month}/"
            for d_key, off_list in st.session_state.daily_leaves.items():
                if d_key.startswith(prefix) and matched_person in off_list:
                    day_part = d_key.split('/')[1]
                    person_off_dates.append(f"{matched_month}/{day_part}")
            
            person_off_dates.sort(key=lambda x: int(x.split('/')[1]))
            count = len(person_off_dates)
            
            if count > 0:
                reply = f"📊 **{year_num}年{matched_month}月【{matched_person}】排假統計結果**：\n\n"
                reply += f"🗓️ **休假總天數**：共 **{count}** 天\n"
                reply += f"🌴 **休假日期**：{', '.join(person_off_dates)}"
            else:
                reply = f"ℹ️ 【{matched_person}】在 **{year_num}年{matched_month}月** 目前沒有排休任何假哦！"

        elif date_match:
            month, day = date_match.groups()
            date_key = f"{year_num}_{month}/{day}"
            
            if date_key in st.session_state.daily_leaves:
                off_list = list(set(st.session_state.daily_leaves[date_key]))
                all_people = list(DEFAULT_PERSON_COLORS.keys())
                working_list = [p for p in all_people if p not in off_list]
                
                reply = f"📅 **{year_num}年 {month}/{day} 班表查詢結果**\n\n"
                reply += f"💼 **上班人員**：{', '.join(working_list) if working_list else '全員休假'}\n"
                reply += f"🌴 **休假人員**：{', '.join(off_list) if off_list else '無'}"
            else:
                reply = f"❌ 找不到 {year_num}年 {month}/{day} 的假表記錄（可能該月份尚未排假）。"
        else:
            reply = f"🤖 我是您的排班 AI 助理！我能幫您分析假表數據。\n\n試試看這樣問我：\n* 「琪{month_num}月休幾天？」\n* 「{month_num}/15 誰休假？」\n* 「安{month_num}月哪幾天休假？」"

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
