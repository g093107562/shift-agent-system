import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.message_template import ConfirmTemplate, TemplateSendMessage
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent

app = Flask(__name__)

# 請填入您的 LINE Bot 憑證（若暫時測試，可先填入字串）
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

def save_leaves(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
    
    # 範例指令：查詢 10/5 誰休假
    if "誰休假" in text or "/" in text:
        data = load_leaves()
        # 簡易解析如 "10/5"
        for k, v in data.items():
            if text in k:
                off_list = ", ".join(v) if v else "無"
                reply = f"📅 記錄日期 {k}\n🌴 休假人員：{off_list}"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
                return
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"找不到 {text} 的休假記錄。"))
    else:
        reply = "🤖 歡迎使用 24/7 排假機器人！\n您可以直接輸入日期（例如：10/5）查詢當日休假名單。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(port=5000)
