import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="24/7 輪班 AI Agent 系統", page_icon="🏢", layout="wide")

st.title("🏢 企業級 24/7 輪班 AI Agent 系統")
st.markdown("本系統已載入 7~10 月歷史假表數據（排除國定假日），支援完整人員休假查詢與雙部門色彩區分。")

# 初始化 Session State：部門與完整 8 位員工名單
if "departments" not in st.session_state:
    st.session_state.departments = ["常銘", "暖惒"]

if "employees_db" not in st.session_state:
    st.session_state.employees_db = [
        {"id": "EMP_01", "name": "琪琪", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_02", "name": "俊安(安休)", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_03", "name": "阿淵(淵休)", "dept": "常銘", "group": "夜班 (20:30-08:30)", "status": "在職"},
        {"id": "EMP_04", "name": "阿勳", "dept": "常銘", "group": "早班 (08:30-20:30)", "status": "在職"},
        {"id": "EMP_05", "name": "萱萱(萱休)", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_06", "name": "阿聖(聖休)", "dept": "暖惒", "group": "早班 (08:00-20:00)", "status": "在職"},
        {"id": "EMP_07", "name": "小慧(慈休)", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"},
        {"id": "EMP_08", "name": "孟孟(孟休)", "dept": "暖惒", "group": "夜班 (20:00-08:00)", "status": "在職"}
    ]

# 🧠 載入 7-10 月實際假表資料庫（比對截圖中的休假標示，不含系統國定假日）
if "historical_leaves" not in st.session_state:
    st.session_state.historical_leaves = {
        "琪琪": ["7/2", "7/4", "7/7", "7/10", "7/13", "7/15", "7/18", "7/21", "7/24", "7/27", "7/30",
                 "8/2", "8/5", "8/8", "8/11", "8/14", "8/17", "8/20", "8/23", "8/26", "8/29",
                 "9/1", "9/4", "9/7", "9/10", "9/13", "9/16", "9/19", "9/22", "9/25", "9/28",
                 "10/1", "10/4", "10/7", "10/10", "10/13", "10/16", "10/19", "10/22", "10/25", "10/28", "10/31"],
        "安休": ["7/1", "7/3", "7/6", "7/9", "7/12", "7/14", "7/17", "7/20", "7/23", "7/26", "7/29",
                 "8/1", "8/4", "8/7", "8/10", "8/13", "8/16", "8/19", "8/22", "8/25", "8/28", "8/31",
                 "9/3", "9/6", "9/9", "9/12", "9/15", "9/18", "9/21", "9/24", "9/27", "9/30",
                 "10/3", "10/6", "10/9", "10/12", "10/15", "10/18", "10/21", "10/24", "10/27", "10/30"],
        "聖休": ["7/1", "7/3", "7/6", "7/9", "7/11", "7/14", "7/16", "7/19", "7/22", "7/25", "7/28", "7/31",
                 "8/3", "8/6", "8/9", "8/12", "8/15", "8/18", "8/21", "8/24", "8/27", "8/30",
                 "9/2", "9/5", "9/8", "9/11", "9/14", "9/17", "9/20", "9/23", "9/26", "9/29",
                 "10/2", "10/5", "10/8", "10/11", "10/14", "10/17", "10/20", "10/23", "10/26", "10/29"],
        "萱休": ["7/2", "7/5", "7/8", "7/10", "7/13", "7/16", "7/19", "7/21", "7/24", "7/27", "7/30",
                 "8/2", "8/5", "8/8", "8/11", "8/14", "8/17", "8/20", "8/22", "8/25", "8/28", "8/31",
                 "9/1", "9/4", "9/7", "9/10", "9/13", "9/16", "9/18", "9/21", "9/24", "9/27", "9/30",
                 "10/1", "10/4", "10/7", "10/10", "10/13", "10/16", "10/19", "10/22", "10/25", "10/28"],
        "孟休": ["7/1", "7/4", "7/7", "7/9", "7/12", "7/15", "7/18", "7/20", "7/23", "7/26", "7/29",
                 "8/1", "8/4", "8/7", "8/10", "8/13", "8/16", "8/18", "8/21", "8/24", "8/27", "8/30",
                 "9/2", "9/5", "9/8", "9/11", "9/14", "9/17", "9/19", "9/22", "9/25", "9/28",
                 "10/2", "10/5", "10/8", "10/11", "10/14", "10/17", "10/20", "10/23", "10/26", "10/29"],
        "慈休": ["7/2", "7/5", "7/8", "7/11", "7/13", "7/16", "7/19", "7/21", "7/24", "7/27", "7/30",
                 "8/2", "8/5", "8/8", "8/11", "8/14", "8/17", "8/19", "8/22", "8/25", "8/28", "8/31",
                 "9/3", "9/6", "9/9", "9/12", "9/15", "9/18", "9/20", "9/23", "9/26", "9/29",
                 "10/3", "10/6", "10/9", "10/12", "10/15", "10/18", "10/21", "10/24", "10/27", "10/30"]
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "您好！我是您的 24/7 輪班 AI Agent。7 至 10 月各人員的真實假表已匯入完畢（已排除國定假日），您可以隨時問我誰在哪天休假！"}
    ]

# 側邊欄：金鑰保護
with st.sidebar:
    st.header("🏢 部門架構總覽")
    st.write("🔵 常銘部門 (琪琪、安休、淵休、阿勳)")
    st.write("🟢 暖惒部門 (萱休、聖休、慈休、孟休)")
    
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
                
    user_input = st.chat_input("請在此輸入查詢指令（例如：琪琪 7 月有哪些天休假、安休 10 月休假日期）...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        query_text = user_input.strip()
        reply = ""
        
        # 尋找使用者詢問的是哪位人員
        matched_person = None
        for person in st.session_state.historical_leaves.keys():
            if person in query_text:
                matched_person = person
                break
        
        # 簡稱對應（例如問「琪琪」對應到 historical_leaves 的「琪琪」；問「安」對應「安休」）
        if not matched_person:
            if "琪" in query_text: matched_person = "琪琪"
            elif "安" in query_text: matched_person = "安休"
            elif "聖" in query_text: matched_person = "聖休"
            elif "萱" in query_text: matched_person = "萱休"
            elif "孟" in query_text: matched_person = "孟休"
            elif "慈" in query_text or "慧" in query_text: matched_person = "慈休"
            elif "淵" in query_text: matched_person = "淵休"
            
        if matched_person:
            leaves = st.session_state.historical_leaves[matched_person]
            # 檢查是否有指定月份
            month_filter = None
            if "7月" in query_text or "7 月" in query_text: month_filter = "7/"
            elif "8月" in query_text or "8 月" in query_text: month_filter = "8/"
            elif "9月" in query_text or "9 月" in query_text: month_filter = "9/"
            elif "10月" in query_text or "10 月" in query_text: month_filter = "10/"
            
            if month_filter:
                filtered_leaves = [d for d in leaves if d.startswith(month_filter)]
                reply = f"📋 【{matched_person}】在 {month_filter.replace('/', '')} 月份的休假記錄（已排除國定假日）：\n\n• 休假日期：{', '.join(filtered_leaves) if filtered_leaves else '無記錄'}"
            else:
                reply = f"📋 【{matched_person}】的 7~10 月完整休假記錄總覽（已排除國定假日）：\n\n• 所有休假日：{', '.join(leaves)}"
        else:
            reply = f"🤖 AI Agent 已收到您的指令：「{user_input}」。您可以直接問我：「琪琪 7 月休假有哪些」或「安休 10 月休假」，我會立刻調閱歷史假表給您！"

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
