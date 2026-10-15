import streamlit as st

def query_employee(employee_name, action_type):
    if not employee_name:
        return "請輸入員工姓名"
    
    if "張小美" in employee_name:
        if action_type == "查詢所屬組別與狀態":
            return "【張小美】\n- 所屬部門：A 部門\n- 組別：EARLY 組 (早班)\n- 目前狀態：在職中 (ACTIVE)\n- 循環規則：做二休二（大月輪休）"
        elif action_type == "查詢本月加班與變形三班制":
            return "【張小美 的工時與加班統計】\n- 目前模式：減員變形三班制（因編制剩 1 人）\n- 月休天數：8 天\n- 12 小時強制加班天數：16 天\n- 正常 8 小時天數：7 天"
        else:
            return "【通知發送成功】LINE & Email 雙軌發送：明天您有早班，請提前準備！"
    else:
        return f"【{employee_name}】\n- 所屬部門：B 部門\n- 組別：NIGHT 組 (夜班)\n- 目前狀態：在職中 (ACTIVE)"

st.title("企業級 24/7 做二休二輪班 AI Agent 系統")
st.write("這是一套專為 24/7 輪班環境設計的智慧排班與管理系統模擬介面。")

emp_input = st.text_input("輸入員工姓名", value="張小美")
action_dropdown = st.selectbox(
    "選擇系統操作項目",
    ["查詢所屬組別與狀態", "查詢本月加班與變形三班制", "模擬觸發 LINE/Email 提醒"]
)

if st.button("執行 AI 智慧查詢與操作", type="primary"):
    result = query_employee(emp_input, action_dropdown)
    st.subheader("系統模擬輸出畫面")
    st.text(result)
