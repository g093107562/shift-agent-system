import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 🔴 請將下面引號內的字串替換成您從 LINE Developers 後台「重新發行」並複製的全新 Token
LINE_CHANNEL_ACCESS_TOKEN = "JkDCud7Ffr/IjklUeV5LrKSgnJf1mavRORc3/oYGMrzxFLHS1MwUwISbO6sCyeuL8AogRt8Dq3qOhBsI6C4hoVCEU4FTVmZCsQVXuUKrutVrFisyT7BILKzU6KlfloOm9Vh6Zh7D8hO8ZUYvE7JgwgdB04t89/1O/w1cDnyilFU="
# 🔴 請填入您的 Channel Secret
LINE_CHANNEL_SECRET = "1c9396bd71bd481688f1325f41170ad8"

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

@app.route("/callback", methods=['POST', 'GET'])
def callback():
    if request.method == 'GET':
        return 'LINE Bot Webhook is running!', 200
        
    signature = request.headers.get('X-Line-Signature', '')
    
    try:
        body = request.get_data(as_text=True)
    except TypeError:
        body = request.data.decode('utf-8')
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print(f"Error: {e}")
        
    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        text = event.message.text.strip()
        data = load_leaves()
        
        found = False
        reply = ""
        for k, v in data.items():
            if text in k:
                off_list = ", ".join(v) if v else "無"
                reply = f"📅 查詢日期：{k}\n🌴 休假人員：{off_list}"
                found = True
                break
                
        if not found:
            reply = f"🤖 24/7 排班機器人運行中！\n收到您的訊息：{text}\n您可以直接輸入日期（例如：10/5）來查詢當日休假名單與網頁同步。"
            
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    except Exception as e:
        print(f"Reply Error: {e}")

if __name__ == "__main__":
    app.run(port=5000)
