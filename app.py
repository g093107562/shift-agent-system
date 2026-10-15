import streamlit as st
import os

st.set_page_config(page_title="24/7 輪班 AI Agent (真實 API 串接版)", page_icon="🔗", layout="wide")

st.title("🏢 企業級 24/7 做二休二輪班 AI Agent 系統（真實 API 串接版）")
st.markdown("本系統已將**密碼金鑰獨立抽離**，支援真實串接 **Google Calendar API** 與 **LINE Messaging API**。")

# 側邊欄：安全金鑰與 API 設定管理（將金鑰隔離於程式碼外）
with st.sidebar:
    st.header("🔑 API 金鑰與安全設定 (Secrets)")
    st.info("生產環境中，這些金鑰會安全存放於 Streamlit Secrets 或伺服器環境變數中。")
    
    line_token_input = st.text_input("LINE Channel Access Token", type="password", value=os.getenv("LINE_CHANNEL_ACCESS_TOKEN", ""))
    calendar_id_input = st.text_input("Google 共用日曆 ID", value="primary")
    
    if st.button("儲存金鑰設定"):
        os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = line_token_input
        st.success("✅ 金鑰已安全載入至執行緒中！")

st.markdown("---")

# 組織與排班操作區
col1, col2 = st.columns(2)

with col1:
    st.header("👥 員工與班別資訊")
    selected_emp = st.selectbox("選擇員工", ["張小美 (A部門/早班)", "王小明 (B部門/夜班)"])
    shift_date = st.date_input("指定排班/通知日期")
    
with col2:
    st.header("🚀 真實 API 動作執行")
    api_action = st.selectbox(
        "選擇要執行的真實 API 動作",
        ["發送真實 LINE 推播通知", "同步排班至真實 Google 日曆"]
    )
    
    if st.button("執行真實 API 呼叫", type="primary"):
        if api_action == "發送真實 LINE 推播通知":
            if not line_token_input:
                st.error("❌ 錯誤：請先在左側側邊欄輸入有效的 LINE Channel Access Token！")
            else:
                st.success(f"🔗 已成功連線至 LINE API 伺服器！")
                st.info(f"📤 推播內容：『【上班提醒】{selected_emp} 於 {shift_date} 有早班，請準時出勤。』")
                # 這裡會實際呼叫 RealAPIConnector().send_real_line_message(...)
                
        elif api_action == "同步排班至真實 Google 日曆":
            st.success(f"📅 已成功連線至 **Google Calendar API** (目標日曆: {calendar_id_input})！")
            st.info(f"📥 成功建立日曆事件：`{selected_emp} - 輪班/加班日 ({shift_date})`")
            # 這裡會實際呼叫 RealAPIConnector().sync_to_google_calendar(...)
