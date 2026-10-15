import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 請替換為您從 LINE Developers 取得的真實憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "您的_Channel_Access_Token")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "您的_Channel_Secret")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

DB_FILE = "leave_database.json"

def load_leaves():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_string=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    data = load_leaves()
    
    # 支援輸入日期查詢（例如 10/5 或 10月5日）
    found = False
    for k, v in data.items():
        if text in k:
            off_list = ", ".join(v) if v else "無"
            reply = f"📅 查詢日期：{k}\n🌴 休假人員：{off_list}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            found = True
            break
            
    if not found:
        reply = f"🤖 24/7 排班機器人運行中！\n您可以直接輸入日期（例如：10/5）來查詢當日休假名單，資料與網頁即時同步。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(port=5000)
