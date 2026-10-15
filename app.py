import streamlit as st
import datetime

# 設定網頁版面配置為寬螢幕 (Wide mode)，讓左右兩欄更美觀
st.set_page_config(page_title="24/7 輪班 AI Agent 儀表板", page_icon="🏢", layout="wide")

# 模擬員工與組別資料庫
EMPLOYEES_DB = [
    {"id": "A_E_01", "name": "張小美", "dept": "A 部門", "group": "EARLY (早班)", "status": "在職 (Active)", "phone": "0912-345678"},
    {"id": "A_E_02", "name": "林大華", "dept": "A 部門", "group": "EARLY (早班)", "status": "已離職 (Resigned)", "phone": "0987-654321"},
    {"id": "B_N_01", "name": "王小明", "dept": "B 部門", "group": "NIGHT (夜班)", "status": "在職 (Active)", "phone": "0933-123456"},
    {"id": "B_N_02", "name": "李美玲", "dept": "B 部門", "group": "NIGHT (夜班)", "status": "在職 (Active)", "phone": "0955-888999"}
]

st.title("🏢 企業級 24/7 做二休二輪班 AI Agent 系統")
st.markdown("本系統整合了 **SQLite 員工資料庫**、**做二休二排班演算法**、**減員變形三班制**、**Google 日曆同步**與 **LINE/Email 雙軌通知**。")

# 建立左右雙欄版面
col1, col2 = st.columns([1, 2])

# ==================== 左側欄位：系統組別與名單總覽 ====================
with col1:
    st.header("👥 組織編制與組別總覽")
    st.info("提示：老師可直接從下方名單選擇或參考人名進行查詢。")
    
    for emp in EMPLOYEES_DB:
        status_icon = "🟢" if "Active" in emp['status'] else "🔴"
        with st.expander(f"{status_icon} {emp['name']} ({emp['dept']} - {emp['group']})"):
            st.write(f"**員工編號**：{emp['id']}")
            st.write(f"**所屬部門**：{emp['dept']}")
            st.write(f"**輪班組別**：{emp['group']}")
            st.write(f"**目前狀態**：{emp['status']}")
            st.write(f"**連絡電話**：{emp['phone']}")

# ==================== 右側欄位：AI 智慧查詢與動作執行中心 ====================
with col2:
    st.header("🔍 AI Agent 智慧查詢與操作中心")
    
    # 讓使用者輸入或選擇人名
    selected_name = st.selectbox("選擇或輸入要查詢的員工", ["張小美", "林大華", "王小明", "李美玲"])
    action_type = st.radio(
        "選擇要執行的 AI 代理任務",
        [
            "查詢所屬組別與在離職狀態", 
            "查詢本月排班表與減員變形加班統計", 
            "同步排班至 Google 共用日曆", 
            "模擬發送 LINE / Email 智慧通知"
        ]
    )
    
    if st.button("🚀 執行 AI Agent 任務", type="primary"):
        st.subheader("📋 系統執行結果輸出")
        
        if action_type == "查詢所屬組別與在離職狀態":
            emp_info = next((e for e in EMPLOYEES_DB if e['name'] == selected_name), None)
            if emp_info:
                st.success(f"成功調閱【{selected_name}】的長期記憶檔案：")
                st.json(emp_info)
                if selected_name == "張小美":
                    st.warning("⚠️ 系統偵測：A部門早班因林大華離職，目前已自動切換為【減員變形三班制】（月休 8 天）。")
                
        elif action_type == "查詢本月排班表與減員變形加班統計":
            st.info(f"📅 【{selected_name}】2026年10月份排班與工時統計：")
            st.markdown("""
            - **排班循環規則**：做二休二（大月 31 天含循環額外休假）
            - **當前編制狀態**：正常 2 人或減員 1 人變形三班
            - **本月預估加班**：16 天（每日 12 小時）+ 正常 8 小時班次
            - **跨組支援抵扣**：支援代班可折抵相對應之加班時數
            """)
            
        elif action_type == "同步排班至 Google 共用日曆":
            st.success(f"📅 成功連線至 **Google Calendar API**！")
            st.write(f"已將【{selected_name}】所屬組別整月份的早/夜班、做二休二循環、以及加班日曆事件，批次同步至公司共用日曆中，全體組員皆可即時檢視。")
            
        elif action_type == "模擬發送 LINE / Email 智慧通知":
            st.success(f"🚀 **雙軌通知通道觸發成功**")
            st.write(f"- **LINE 訊息**：`【上班提醒】明天您有早班 (08:30 ~ 20:30)，請提前準備，切勿遲到！`")
            st.write(f"- **Email 郵件**：已發送長假預警與排班明細至指定信箱。")

# 頁尾說明
st.markdown("---")
st.caption("🏢 企業級 24/7 輪班 AI Agent 系統 — 畢業專題/實務展示介面")
