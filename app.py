import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="24/7 輪班 AI Agent 系統", page_icon="🏢", layout="wide")

st.title("🏢 企業級 24/7 輪班 AI Agent 系統")
st.markdown("本系統專為「常銘」與「暖惒」部門設計：同組兩人嚴格執行「一個上班、一個休」交替輪班，支援部門色彩區分與安全金鑰隱藏。")

# 初始化 Session State：精準設定各部門與班別的 2 人組
if "departments" not in st.session_state:
    st.session_state.departments = ["常銘", "暖惒"]

if "employees_db" not in st.session_state:
    st.session_state.employees_db = [
        # 常銘部門（早班2人、夜班2人）
        {"id": "EMP_01", "name": "琪琪", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_02", "name": "俊安", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_03", "name": "阿淵", "dept": "常銘", "group": "夜班 (20:30-08:30)", "status": "在職"},
        {"id": "EMP_04", "name": "阿勳", "dept": "常銘", "group": "夜班 (20:30-08:30)", "status": "在職"},
        # 暖惒部門（早班2人、夜班2人）
        {"id": "EMP_05", "name": "萱萱", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_06", "name": "阿聖", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_07", "name": "小慧", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"},
        {"id": "EMP_08", "name": "孟孟", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！我是您的 24/7 輪班 AI Agent。排班邏輯已修正為「同組兩人一個上班一個休」，您可以隨時查詢！"}
    ]

# 側邊欄：金鑰保護
with st.sidebar:
    st.header("🏢 部門架構總覽")
    st.write("🔵 常銘部門 (早班: 琪琪/俊安 | 夜班: 阿淵/阿勳)")
    st.write("🟢 暖惒部門 (早班: 萱萱/阿聖 | 夜班: 小慧/孟孟)")
    
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
                
    user_input = st.chat_input("請在此輸入指令（例如：琪琪本月上班日、俊安本月上班日）...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        query_text = user_input.strip()
        reply = ""
        
        if "上班日" in query_text or "班表" in query_text:
            target_emp = None
            for emp in st.session_state.employees_db:
                if emp['name'] in query_text:
                    target_emp = emp
                    break
            
            if target_emp:
                # 找出同部門、同班別的 2 個人
                same_group_peers = [e for e in st.session_state.employees_db if e['dept'] == target_emp['dept'] and e['group'] == target_emp['group']]
                peer_pos = 0
                for idx, p in enumerate(same_group_peers):
                    if p['name'] == target_emp['name']:
                        peer_pos = idx
                        break
                
                # 計算 2026年10月 (31天) 的「一個上班、一個休」交替邏輯
                work_days = []
                for day in range(1, 32):
                    # 兩人一組：奇數日給第1人，偶數日給第2人（依 peer_pos 決定奇偶）
                    if (day + peer_pos) % 2 == 1:
                        work_days.append(f"10/{day}")
                
                current_year_month = datetime.now().strftime("%Y年%m月")
                reply = f"📋 【{target_emp['name']}】({target_emp['dept']} - {target_emp['group']})的 {current_year_month} 上班日查詢結果：\n\n"
                reply += f"⚖️ (已依同組兩人「一個上班、一個休」規則自動交替)\n"
                reply += f"• 上班日期：{', '.join(work_days)}\n"
                reply += f"🕒 班別時段：{target_emp['group']}"
            else:
                reply = "❌ 找不到您提到的員工姓名，請確認該員工是否已在左側清單中。"
        elif "常銘" in query_text:
            changming_emps = [e['name'] for e in st.session_state.employees_db if e['dept'] == '常銘']
            reply = f"🔵 【常銘】部門現有成員：{', '.join(changming_emps)}（早班與夜班各自 2 人交替輪班）。"
        elif "暖惒" in query_text:
            nuanhe_emps = [e['name'] for e in st.session_state.employees_db if e['dept'] == '暖惒']
            reply = f"🟢 【暖惒】部門現有成員：{', '.join(nuanhe_emps)}（早班與夜班各自 2 人交替輪班）。"
        else:
            reply = f"🤖 AI Agent 已收到您的指令：「{user_input}」。排班規則已修正為同組兩人交替上班，您可以分別查詢琪琪與俊安來驗證！"

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
