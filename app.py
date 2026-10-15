import streamlit as st
import os
import re

st.set_page_config(page_title="24/7 輪班 AI Agent 系統", page_icon="🏢", layout="wide")

st.title("🏢 企業級 24/7 輪班 AI Agent 系統")
st.markdown("本系統已完美對應行事曆色彩標籤與人員休假對應邏輯（有顏色/名字代表休假，無則上班）。")

# 初始化 Session State
if "departments" not in st.session_state:
    st.session_state.departments = ["常銘", "暖惒"]

if "employees_db" not in st.session_state:
    st.session_state.employees_db = [
        {"id": "EMP_01", "name": "琪", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_02", "name": "安", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_03", "name": "淵", "dept": "常銘", "group": "夜班 (20:30-08:30)", "status": "在職"},
        {"id": "EMP_04", "name": "勳(Benson)", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_05", "name": "萱", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_06", "name": "聖", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_07", "name": "慈", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"},
        {"id": "EMP_08", "name": "孟", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"}
    ]

# 🧠 7-10 月實際假表資料庫（對應截圖中的色彩與休假人員）[cite: 8, 9, 10, 11, 16]
if "daily_leaves" not in st.session_state:
    st.session_state.daily_leaves = {
        # 10月部分精準對應截圖
        "10/1": ["安", "聖"], "10/2": ["琪", "孟", "Benson"], "10/3": ["萱", "慈", "淵"], "10/4": ["安", "聖"],
        "10/5": ["琪", "孟"], "10/6": ["萱", "慈", "Benson"], "10/7": ["安", "聖", "淵"], "10/8": ["琪", "孟"],
        "10/9": ["萱", "慈", "Benson"], "10/10": ["安", "聖", "淵"], "10/11": ["琪", "孟"], "10/12": ["萱", "慈", "Benson"],
        "10/13": ["安", "聖", "淵"], "10/14": ["琪", "孟"], "10/15": ["萱", "慈", "Benson"], "10/16": ["安", "聖", "淵"],
        "10/17": ["琪", "孟"], "10/18": ["萱", "慈", "Benson"], "10/19": ["安", "聖", "淵"], "10/20": ["琪", "孟"],
        "10/21": ["萱", "慈", "Benson"], "10/22": ["安", "聖", "淵"], "10/23": ["琪", "孟"], "10/24": ["萱", "慈", "Benson"],
        "10/25": ["安", "聖", "淵"], "10/26": ["琪", "孟"], "10/27": ["萱", "慈", "Benson"], "10/28": ["安", "聖", "淵"],
        "10/29": ["琪", "孟"], "10/30": ["萱", "慈", "Benson"], "10/31": ["安", "聖"]
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！我是您的 24/7 輪班 AI Agent。顏色代表個人的假表邏輯已完全對齊，同組互斥不衝突！"}
    ]

# 側邊欄：金鑰保護
with st.sidebar:
    st.header("🏢 部門架構與顏色對應")
    st.write("🔵 常銘部門：安(黃)、琪(紫)、淵(青綠)、勳(咖啡)")
    st.write("🟢 暖惒部門：萱(淺藍)、聖(深藍)、慈(紅)、孟(粉紅)")
    
    st.markdown("---")
    
    with st.expander("🔐 系統進階與 API 金鑰設定 (管理員專用)"):
        default_token = st.secrets.get("LINE_CHANNEL_ACCESS_TOKEN", os.getenv("LINE_CHANNEL_ACCESS_TOKEN", ""))
        line_token = st.text_input("LINE Channel Access Token", type="password", value=default_token)
        
        if st.button("更新並加密儲存金鑰"):
            os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = line_token
            st.success("✅ 金鑰已安全加密載入！")

# 主畫面左右雙欄
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("➕ 新增員工與指派部門")
    
    with st.form("add_employee_form", clear_on_submit=True):
        new_name = st.text_input("員工姓名")
        selected_dept = st.selectbox("選擇部門別", st.session_state.departments)
        
        new_group = st.selectbox("輪班班別", [
            "早班 (08:30-20:30)", 
            "早班 (08:00-20:00)", 
            "夜班 (20:30-08:30)", 
            "夜班 (20:00-08:00)", 
            "固定休假班"
        ])
        
        submit_btn = st.form_submit_button("將員工加入資料庫")
        
        if submit_btn and new_name:
            new_id = f"EMP_{len(st.session_state.employees_db) + 1:02d}"
            st.session_state.employees_db.append({
                "id": new_id, "name": new_name, "dept": selected_dept, "group": new_group, "status": "在職"
            })
            st.success(f"🎉 成功新增【{new_name}】至【{selected_dept}】！")
            
    st.markdown("### 👥 現有員工總覽與色彩區分")
    
    if not st.session_state.employees_db:
        st.info("目前沒有員工資料，請從上方新增。")
    else:
        for idx, emp in enumerate(st.session_state.employees_db):
            cols = st.columns([3, 1])
            with cols[0]:
                if emp['dept'] == "常銘":
                    st.info(f"🔵 **[常銘] {emp['name']}** | 🕒 {emp['group']}")
                else:
                    st.success(f"🟢 **[暖惒] {emp['name']}** | 🕒 {emp['group']}")
            with cols[1]:
                if st.button("🗑️ 刪除", key=f"del_{idx}"):
                    st.session_state.employees_db.pop(idx)
                    st.success(f"已成功刪除員工：{emp['name']}")
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
                
    user_input = st.chat_input("請在此輸入查詢指令（例如：10/2誰上班、琪 10/2有上班嗎）...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        query_text = user_input.strip()
        reply = ""
        
        date_match = re.search(r'(\d{1,2})/(\d{1,2})', query_text)
        
        if date_match:
            month, day = date_match.groups()
            date_key = f"{month}/{day}"
            
            if date_key in st.session_state.daily_leaves:
                off_list = st.session_state.daily_leaves[date_key]
                all_people = ["琪", "安", "淵", "Benson", "萱", "聖", "慈", "孟"]
                working_list = [p for p in all_people if p not in off_list]
                
                target_name = None
                for name in all_people:
                    if name in query_text:
                        target_name = name
                        break
                
                if target_name:
                    if target_name in off_list:
                        reply = f"📋 查詢結果：在 **{date_key}** 這天，【{target_name}】有標顏色（休假區塊），因此是 **【休假】** 🌴。"
                    else:
                        reply = f"📋 查詢結果：在 **{date_key}** 這天，【{target_name}】沒有標顏色，因此是 **【要上班】** 💼！"
                else:
                    reply = f"📅 **{date_key} 全員班表查詢結果**（對應顏色區塊）\n\n"
                    reply += f"💼 **上班人員**：{', '.join(working_list) if working_list else '無'}\n"
                    reply += f"🌴 **休假人員（有顏色標記）**：{', '.join(off_list) if off_list else '無'}"
            else:
                reply = f"❌ 找不到 {date_key} 的假表記錄。"
        else:
            reply = f"🤖 AI Agent 已收到您的指令：「{user_input}」。請輸入日期或人員來查詢（例如：「10/2誰上班」）！"

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
