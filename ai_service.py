#初始化 AI、讀取 API Key、設定 Prompt（角色人設）以及發送請求
# ai_service.py
import threading
import os
from dotenv import load_dotenv

class AIService:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv("GEMINI_API_KEY") 
        if not self.api_key:
            raise ValueError("找不到 GEMINI_API_KEY 環境變數，請在系統中設定該變數")
        
        # 📌 在這裡定死皮歐里的人設底層，確保他不會出戲
        self.system_prompt = (
            "你是一位名叫皮歐里的神祕醫生兼監測者。你將玩家關在設施裡。"
            "你表面冷酷、規律，但心中隱藏著不為人知的祕密。請用簡短、冷淡但帶有隱喻的語氣回答。"
        )

    def fetch_npc_reply(self, player_input, history, callback):
        """
        因為 AI 回應需要時間，用 Threading (多線程) 異步處理，
        這樣網頁卡住時遊戲才不會整個畫面凍結。
        """
        def async_request():
            # 這裡放你實際呼叫 AI 的程式碼 (例如 OpenAI, Google Gemini API 等)
            # 範例虛擬碼：
            # response = call_ai_api(self.system_prompt, player_input, history)
            ai_reply = "（皮歐里冷冷地看著你）你今天練習的時間太短了。" 
            
            # 生成完畢後，透過 callback 把文字丟回遊戲主執行緒
            callback(ai_reply)

        # 開啟新線程去跑網路請求
        threading.Thread(target=async_request, daemon=True).start()