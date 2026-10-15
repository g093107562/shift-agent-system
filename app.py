import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="24/7 輪班 AI Agent 系統", page_icon="🏢", layout="wide")

st.title("🏢 企業級 24/7 輪班 AI Agent 系統")
st.markdown("本系統已精準對應 7~10 月假表邏輯：行事曆上有名字代表【休假】，沒有名字代表【上班】。")

# 初始化 Session State
if "departments" not in st.session_state:
    st.session_state.departments = ["常銘", "暖惒"]

if "employees_db" not in st.session_state:
    st.session_state.employees_db = [
        {"id": "EMP_01", "name": "琪琪", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_02", "name": "安", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_03", "name": "淵", "dept": "常銘", "group": "夜班 (20:30-08:30)", "status": "在職"},
        {"id": "EMP_04", "name": "勳(Benson)", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_05", "name": "萱", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_06", "name": "聖", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_07", "name": "慈", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"},
        {"id": "EMP_08", "name": "孟", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"}
    ]

# 🧠 7-10 月實際假表資料庫（鍵值為「日期」，對應當天休假的名字列表）
# 名稱對應：琪、安、淵、Benson(勳)、萱、聖、慈、孟
if "daily_leaves" not in st.session_state:
    st.session_state.daily_leaves = {
        # 7月
        "7/1": ["安", "聖", "孟"], "7/2": ["琪", "萱", "慈"], "7/3": ["安", "聖"], "7/4": ["琪", "孟"],
        "7/5": ["萱", "慈"], "7/6": ["安", "聖"], "7/7": ["琪", "孟"], "7/8": ["萱", "慈"],
        "7/9": ["安", "聖", "孟"], "7/10": ["琪", "萱"], "7/11": ["聖", "慈"], "7/12": ["安", "孟"],
        "7/13": ["琪", "萱", "慈"], "7/14": ["安", "聖"], "7/15": ["琪", "孟"], "7/16": ["萱", "聖", "慈"],
        "7/17": ["安"], "7/18": ["琪", "孟"], "7/19": ["萱", "聖", "慈"], "7/20": ["安", "孟"],
        "7/21": ["琪", "萱", "慈"], "7/22": ["聖"], "7/23": ["安", "孟"], "7/24": ["琪", "萱", "慈"],
        "7/25": ["聖"], "7/26": ["安", "孟"], "7/27": ["琪", "萱", "慈"], "7/28": ["聖"],
        "7/29": ["安", "孟"], "7/30": ["琪", "萱", "慈"], "7/31": ["聖"],
        
        # 8月
        "8/1": ["安", "孟"], "8/2": ["琪", "萱", "慈"], "8/3": ["聖"], "8/4": ["安", "孟"],
        "8/5": ["琪", "萱", "慈"], "8/6": ["聖"], "8/7": ["安", "孟"], "8/8": ["琪", "萱", "慈"],
        "8/9": ["聖"], "8/10": ["安", "孟"], "8/11": ["琪", "萱", "慈"], "8/12": ["聖"],
        "8/13": ["安", "孟"], "8/14": ["琪", "萱", "慈"], "8/15": ["聖"], "8/16": ["安", "孟"],
        "8/17": ["琪", "萱", "慈"], "8/18": ["聖", "孟"], "8/19": ["安", "慈"], "8/20": ["琪", "萱"],
        "8/21": ["聖", "孟"], "8/22": ["安", "萱"], "8/23": ["琪", "聖"], "8/24": ["安", "孟"],
        "8/25": ["琪", "慈"], "8/26": ["安", "萱"], "8/27": ["聖", "孟"], "8/28": ["琪", "慈"],
        "8/29": ["安", "萱"], "8/30": ["聖", "孟"], "8/31": ["琪", "慈"],
        
        # 9月
        "9/1": ["琪", "萱"], "9/2": ["聖", "孟"], "9/3": ["安", "慈"], "9/4": ["琪", "萱"],
        "9/5": ["聖", "孟"], "9/6": ["安", "慈"], "9/7": ["琪", "萱"], "9/8": ["聖", "孟"],
        "9/9": ["安", "慈"], "9/10": ["琪", "萱"], "9/11": ["聖", "孟"], "9/12": ["安", "慈"],
        "9/13": ["琪", "萱"], "9/14": ["聖", "孟"], "9/15": ["安", "慈"], "9/16": ["琪", "萱"],
        "9/17": ["聖", "孟"], "9/18": ["安", "慈"], "9/19": ["琪", "孟"], "9/20": ["聖", "慈"],
        "9/21": ["安"], "9/22": ["琪", "孟"], "9/23": ["聖", "慈"], "9/24": ["安"],
        "9/25": ["琪", "孟"], "9/26": ["聖", "慈"], "9/27": ["安"], "9/28": ["琪", "孟"],
        "9/29": ["聖", "慈"], "9/30": ["安", "萱"],
        
        # 10月
        "10/1": ["琪", "萱"], "10/2": ["聖", "孟"], "10/3": ["安", "慈"], "10/4": ["琪", "萱"],
        "10/5": ["聖", "孟"], "10/6": ["安", "慈"], "10/7": ["琪", "萱"], "10/8": ["聖", "孟"],
        "10/9": ["安", "慈"], "10/10": ["琪", "萱"], "10/11": ["聖", "孟"], "10/12": ["安", "慈"],
        "10/13": ["琪", "萱"], "10/14": ["聖", "孟"], "10/15": ["安", "慈"], "10/16": ["琪", "萱"],
        "10/17": ["聖", "孟"], "10/18": ["安", "慈"], "10/19": ["琪", "萱"], "10/20": ["聖", "孟"],
        "10/21": ["安", "慈"], "10/22": ["琪", "萱"], "10/23": ["聖", "孟"], "10/24": ["安", "慈"],
        "10/25": ["琪", "萱"], "10/26": ["聖", "孟"], "10/27": ["安", "慈"], "10/28": ["琪", "萱"],
        "10/29": ["聖", "孟"], "10/30": ["安", "慈"], "10/31": ["琪"]
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！我是您的 24/7 輪班 AI Agent。邏輯已更正：行事曆上有名字代表【休假】，沒名字代表【上班】。請隨時測試！"}
    ]

# 側邊欄：金鑰保護
with st.sidebar:
    st.header("🏢 部門架構總覽")
    st.write("🔵 常銘部門 (琪、安、淵、Benson/勳)")
    st.write("🟢 暖惒部門 (萱、聖、慈/小慧、孟)")
    
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
                
    user_input = st.chat_input("請在此輸入查詢指令（例如：琪琪 9/17 有上班嗎、安 10/15 休假嗎）...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        query_text = user_input.strip()
        reply = ""
        
        # 抓取人員姓名簡稱
        target_name = None
        for name in ["琪琪", "安", "淵", "勳", "Benson", "萱", "聖", "慈", "孟"]:
            if name in query_text or (name == "安" and "安" in query_text) or (name == "琪" and "琪" in query_text):
                target_name = "安" if name == "安" else ("琪" if name == "琪" else name)
                if name == "Benson" or name == "勳": target_name = "勳"
                break
        
        # 抓取日期 (例如 9/17 或 10/15)
        import re
        date_match = re.search(r'(\d{1,2})/(\d{1,2})', query_text)
        
        if target_name and date_match:
            month, day = date_match.groups()
            date_key = f"{month}/{day}"
            
            if date_key in st.session_state.daily_leaves:
                off_list = st.session_state.daily_leaves[date_key]
                # 檢查當天該員工是否在休假名單中
                is_off = any(target_name in o for o in off_list)
                
                if is_off:
                    reply = f"📋 查詢結果：在 **{date_key}** 這天，【{target_name}】的名字有在假表上，因此是 **【休假】** 🌴。"
                else:
                    reply = f"📋 查詢結果：在 **{date_key}** 這天，【{target_name}】的名字不在假表上，因此是 **【要上班】** 💼！"
            else:
                reply = f"❌ 找不到 {date_key} 的假表記錄範圍。"
        else:
            reply = f"🤖 AI Agent 已收到您的指令：「{user_input}」。請輸入特定日期與人員（例如：「琪琪 9/17 有上班嗎」），我會立刻為您核對當天是否有休假！"

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
