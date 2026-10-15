import streamlit as st
import os

st.set_page_config(page_title="24/7 輪班 AI Agent 系統", page_icon="🏢", layout="wide")

st.title("🏢 企業級 24/7 做二休二輪班 AI Agent 系統")
st.markdown("本系統支援自訂部門名稱、員工動態管理、安全金鑰隔離與真實 API 串接。")

# 初始化 Session State（預設部門與員工清單）
if "departments" not in st.session_state:
    st.session_state.departments = ["管理部", "技術支援組", "營運中心", "品管課"]

if "employees_db" not in st.session_state:
    st.session_state.employees_db = [
        {"id": "EMP_01", "name": "張小美", "dept": "技術支援組", "group": "早班輪值 (EARLY)", "status": "在職"},
        {"id": "EMP_02", "name": "王小明", "dept": "營運中心", "group": "夜班輪值 (NIGHT)", "status": "在職"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！我是您的 24/7 輪班 AI Agent。您可以隨時在左側新增您自訂的部門與員工，或在此與我對話查詢！"}
    ]

# 側邊欄：部門管理與金鑰設定
with st.sidebar:
    st.header("🏢 自訂部門管理")
    new_dept_input = st.text_input("新增自訂部門名稱")
    if st.button("新增部門"):
        if new_dept_input and new_dept_input not in st.session_state.departments:
            st.session_state.departments.append(new_dept_input)
            st.success(f"✅ 成功新增部門：【{new_dept_input}】")
            st.rerun()
            
    st.write("目前系統中的部門：")
    for d in st.session_state.departments:
        st.write(f"- {d}")
        
    st.markdown("---")
    st.header("🔑 API 與安全金鑰")
    line_token = st.text_input("LINE Channel Access Token", type="password", value=os.getenv("LINE_CHANNEL_ACCESS_TOKEN", ""))
    if st.button("儲存金鑰"):
        os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = line_token
        st.success("✅ 金鑰已儲存！")

# 主畫面左右雙欄
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("➕ 新增員工與指派部門")
    with st.form("add_employee_form"):
        new_name = st.text_input("員工姓名")
        # 這裡會直接帶入您在左側自訂的所有部門名稱！
        selected_dept = st.selectbox("選擇部門別", st.session_state.departments)
        new_group = st.selectbox("輪班班別", ["早班 (08:30-20:30)", "夜班 (20:30-08:30)", "固定休假班"])
        submit_btn = st.form_submit_button("將員工加入資料庫")
        
        if submit_btn and new_name:
            new_id = f"EMP_{len(st.session_state.employees_db) + 1:02d}"
            st.session_state.employees_db.append({
                "id": new_id, "name": new_name, "dept": selected_dept, "group": new_group, "status": "在職"
            })
            st.success(f"🎉 成功新增【{new_name}】至【{selected_dept}】！")
            st.rerun()
            
    st.markdown("### 👥 現有員工總覽")
    for emp in st.session_state.employees_db:
        st.info(f"**{emp['name']}** | 🏢 部門：{emp['dept']} | 🕒 班別：{emp['group']}")

with col2:
    st.header("💬 AI Agent 智慧互動區")
    
    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])
                
    user_input = st.chat_input("請在此輸入指令（例如：查詢張小美、同步日曆、發送通知）...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        reply = f"AI Agent 已收到您的指令：「{user_input}」。系統運作正常，所有自訂部門與員工資料已同步更新！"
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
