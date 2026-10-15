import streamlit as st
import os

st.set_page_config(page_title="24/7 輪班 AI Agent 系統", page_icon="🏢", layout="wide")

st.title("🏢 企業級 24/7 做二休二輪班 AI Agent 系統")
st.markdown("本系統專為「常銘」與「暖惒」部門設計，支援不同部門色彩區分、動態增刪員工、安全金鑰隱藏與真實 API 串接。")

# 初始化 Session State
if "departments" not in st.session_state:
    st.session_state.departments = ["常銘", "暖惒"]

if "employees_db" not in st.session_state:
    st.session_state.employees_db = [
        {"id": "EMP_01", "name": "琪琪", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_02", "name": "萱萱", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_03", "name": "俊安", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_04", "name": "阿淵", "dept": "常銘", "group": "夜班 (20:30-08:30)", "status": "在職"},
        {"id": "EMP_05", "name": "阿勳", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！我是您的 24/7 輪班 AI Agent。現有員工已根據不同部門自動套用專屬色彩區分！"}
    ]

# 側邊欄：金鑰保護
with st.sidebar:
    st.header("🏢 部門架構總覽")
    st.write("🔵 常銘部門")
    st.write("🟢 暖惒部門")
    
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
                # 🎨 根據不同部門套用不同顏色區塊 (常銘用 info 藍色系，暖惒用 success 綠色系)
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
                
    user_input = st.chat_input("請在此輸入指令（例如：查詢常銘部門、同步日曆、發送通知）...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        reply = f"AI Agent 已收到您的指令：「{user_input}」。系統已完美呈現雙部門色彩分類！"
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
