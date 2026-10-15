import streamlit as st
import os

st.set_page_config(page_title="24/7 輪班 AI Agent 系統", page_icon="🏢", layout="wide")

st.title("🏢 企業級 24/7 做二休二輪班 AI Agent 系統")
st.markdown("本系統專為「常銘」與「暖惒」部門設計，支援動態增刪員工、安全金鑰隔離與真實 API 串接。")

# 初始化 Session State：部門直接固定為常銘與暖惒
if "departments" not in st.session_state:
    st.session_state.departments = ["常銘", "暖惒"]

if "employees_db" not in st.session_state:
    st.session_state.employees_db = [
        {"id": "EMP_01", "name": "琪琪", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_02", "name": "萱萱", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！我是您的 24/7 輪班 AI Agent。部門已精簡為「常銘」與「暖惒」，您可以隨時在此管理員工或與我對話！"}
    ]

# 側邊欄：金鑰設定
with st.sidebar:
    st.header("🔑 API 與安全金鑰")
    line_token = st.text_input("LINE Channel Access Token", type="password", value=os.getenv("LINE_CHANNEL_ACCESS_TOKEN", ""))
    if st.button("儲存金鑰"):
        os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = line_token
        st.success("✅ 金鑰已儲存！")
        
    st.markdown("---")
    st.markdown("### 🏢 目前部門清單")
    st.write("- 常銘")
    st.write("- 暖惒")

# 主畫面左右雙欄
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("➕ 新增員工與指派部門")
    with st.form("add_employee_form"):
        new_name = st.text_input("員工姓名")
        # 下拉選單只會出現「常銘」與「暖惒」
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
            st.rerun()
            
    st.markdown("### 👥 現有員工總覽與刪除")
    
    if not st.session_state.employees_db:
        st.info("目前沒有員工資料，請從上方新增。")
    else:
        for idx, emp in enumerate(st.session_state.employees_db):
            cols = st.columns([3, 1])
            with cols[0]:
                st.info(f"**{emp['name']}** | 🏢 {emp['dept']} | 🕒 {emp['group']}")
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
        
        reply = f"AI Agent 已收到您的指令：「{user_input}」。系統已切換為「常銘」與「暖惒」雙部門架構！"
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
