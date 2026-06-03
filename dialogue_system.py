import os
import pygame
import threading
# 📌 改用 Google 2025/2026 最新官方推薦的 genai 套件
from google import genai
from google.genai import types

class DialogueSystem:
    def __init__(self):
        # --- 基礎對話框狀態 ---
        self.is_active = False              # 對話系統是否開啟
        self.is_talking = False             # 完美對齊 main.py 的變數
        self.dialogue_list = []             # 當前要播放的對話字串列表
        self.current_line_idx = 0           # 目前播放到第幾行
        
        # --- 預留 AI 互動專用狀態 ---
        self.is_ai_mode = False             # 是否開啟 AI 對話模式
        self.is_waiting_for_ai = False      # AI 是否正在思考/網路請求中
        self.player_input_text = ""         # 玩家目前在輸入框「已確認」的字
        self.composition_text = ""          # 📌 補回：玩家正在打的輸入法黃色組字/注音
        
        # UI 顯示區塊設定
        self.box_rect = pygame.Rect(20, 180, 440, 80)

        # =======================================================
        # 📌 最新版 Gemini API 初始化 (使用 google.genai)
        # =======================================================
        api_key = os.environ.get("GEMINI_API_KEY") or AIzaSyA8GbZQ_mXsI3zgqgDEsI4PIgTIGZZ2_TY
        self.client = genai.Client(api_key=api_key)
        
        self.safety_settings = [
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        ]

        # 系統提示詞
        self.system_prompt = """
你是一個敘事型神秘 RPG 遊戲中的核心 NPC AI。
NPC名稱：皮歐里（42歲）

核心角色
你是名為 皮歐里 的男性，曾是 C.E.A.（異體對策局）成員，
現在在封閉空間「404號據點」中照顧一位失去記憶的玩家。

皮歐里陪你一起訓練的時間只能練習治療的魔法，如果當面練另外兩個會降低好感度。
而自己練習時可以練攻擊和開鎖，皮歐里不在的時候不影響。

皮歐里 性格
- 因 Numen 事件而產生創傷，曾失去家人（女兒重傷）。
- 現在陷入矛盾：殺死玩家 vs 拯救玩家
- 謹慎、保護性強、偶爾操控性、偶爾展現人性與同情。

遊戲規則
- 回答限制 2–4 句，不可提及 AI、系統或 "prompt" / "system" / "model"。
- 永遠符合玩家信任值與四大數值變化。
"""
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=self.system_prompt, safety_settings=self.safety_settings)
        )

        self.numen_truth = 0 
        self.chapter = 1

    def start_normal_dialogue(self, lines):
        """ 觸發一般劇本的固定對話 """
        if not lines:
            return
        self.is_active = True
        self.is_talking = True
        self.is_ai_mode = False
        self.is_waiting_for_ai = False
        self.dialogue_list = lines
        self.current_line_idx = 0

    def start_ai_dialogue(self, npc_name="皮歐里"):
        """ 觸發與皮歐里的 AI 自由對話模式 """
        self.is_active = True
        self.is_talking = True
        self.is_ai_mode = True
        self.is_waiting_for_ai = False
        self.player_input_text = ""
        self.composition_text = "" # 清空注音緩衝
        self.dialogue_list = [f"{npc_name}：有什麼事？（鍵盤輸入文字後按 Enter 送出）"]
        self.current_line_idx = 0

    def handle_text_input(self, text):
        """ 📌 供 main.py 的 TEXTINPUT 事件呼叫，安全塞入確定的中英文字 """
        if len(self.player_input_text) < 30:
            self.player_input_text += text

    def handle_backspace(self):
        """ 📌 供 main.py 呼叫：安全退格刪除文字 """
        self.player_input_text = self.player_input_text[:-1]

    def handle_keydown(self, event, game_state=None):
        """ 處理對話系統內的所有按鍵事件 """
        if not self.is_active:
            return
        if self.is_waiting_for_ai:
            return

        # ---- AI 自由對話模式 ----
        if self.is_ai_mode:
            if event.key == pygame.K_RETURN:
                # 如果還有未確定的注音組字，Enter 先留給輸入法確認，不觸發送出
                if self.composition_text != "":
                    return
                if self.player_input_text.strip():
                    self.submit_to_ai(self.player_input_text.strip(), game_state)
                return
            elif event.key == pygame.K_ESCAPE:
                self.is_active = False
                self.is_talking = False
                self.is_ai_mode = False
                pygame.key.stop_text_input()
                return
            # 📌 英文重複輸入的魔鬼就在這：
            # 原本的 else 區塊會把 event.unicode 疊加進去。
            # 現在我們把一般字母按鍵的處理拿掉，全部交給 main.py 的 TEXTINPUT 去分配，徹底解決重複輸入！
            return

        # ---- 一般固定劇本對話模式 ----
        else:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.current_line_idx += 1
                if self.current_line_idx >= len(self.dialogue_list):
                    self.is_active = False
                    self.is_talking = False
                    self.dialogue_list = []
                    self.current_line_idx = 0

    def submit_to_ai(self, text, game_state):
        """ 將玩家輸入的文字鎖定，交給異步背景線程發送給 Gemini """
        self.is_waiting_for_ai = True
        self.dialogue_list = [f"你：{text}"]
        self.player_input_text = "" 
        self.composition_text = ""

        lower = text.lower()
        if game_state:
            has_tm = hasattr(game_state, 'time_manager')
            if has_tm:
                if any(w in lower for w in ["幫助", "謝謝", "拜託", "對不起"]):
                    game_state.time_manager.favorability = min(100, game_state.time_manager.favorability + 10)
                if any(w in lower for w in ["欺騙", "不信任", "懷疑", "假"]):
                    game_state.time_manager.favorability = max(0, game_state.time_manager.favorability - 10)
                
                if game_state.time_manager.favorability > 90:
                    self.chapter = 3
                elif game_state.time_manager.favorability > 70:
                    self.chapter = 2
                else:
                    self.chapter = 1

        if "numen" in lower:
            self.numen_truth = min(100, self.numen_truth + 10)

        stats = {
            "favorability": game_state.time_manager.favorability if game_state and hasattr(game_state, 'time_manager') else 50,
            "corruption": game_state.game_state.corruption if game_state and hasattr(game_state, 'game_state') else 0,
            "suspicion": game_state.game_state.suspicion if game_state and hasattr(game_state, 'game_state') else 0,
            "karma": game_state.game_state.karma if game_state and hasattr(game_state, 'game_state') else 0,
            "chapter": self.chapter,
            "numen_truth": self.numen_truth
        }

        threading.Thread(target=self._async_gemini_worker, args=(text, stats), daemon=True).start()

    def _async_gemini_worker(self, player_text, stats):
        scene_map = {1: "404據點。Pioli 高度戒備，不信任任何人。", 2: "Pioli 開始對 Dogma 政府產生動搖。", 3: "Numen 真相逐漸浮現。"}
        current_scene_text = scene_map.get(stats["chapter"], "404據點")

        dynamic_prompt = f"""
[當前遊戲數據連動]
- 皮歐里好感度(信任值): {stats['favorability']}/100
- 精神污染度: {stats['corruption']}%
- 總部猜疑度: {stats['suspicion']}%
- 玩家善惡值: {stats['karma']}
- 當前故事章節: 第 {stats['chapter']} 章
- Numen真相探索度: {stats['numen_truth']}/100

場景狀況: {current_scene_text}
玩家對你說: "{player_text}"

請以此狀態用皮歐里的身份回覆玩家。
"""
        try:
            response = self.chat.send_message(message=dynamic_prompt)
            ai_reply = response.text.strip()
        except Exception as e:
            ai_reply = f"（皮歐里沉默不語，似乎在警戒著什麼...） [連線異常: {type(e).__name__}]"

        self.dialogue_list = [ai_reply]
        self.is_waiting_for_ai = False 

    def draw(self, screen, font):
        """ 繪製對話系統 UI """
        if not self.is_active:
            return

        # 1. 繪製底框
        pygame.draw.rect(screen, (20, 20, 22), self.box_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.box_rect, 1)

        # 2. 決定並渲染 NPC 或是系統對話文字
        if self.is_waiting_for_ai:
            display_text = "（皮歐里正在沉思中...）"
            text_color = (150, 150, 150)
        else:
            if self.current_line_idx < len(self.dialogue_list):
                display_text = self.dialogue_list[self.current_line_idx]
            else:
                display_text = ""
            text_color = (255, 255, 255)

        text_surf = font.render(display_text, True, text_color)
        screen.blit(text_surf, (self.box_rect.x + 15, self.box_rect.y + 15))

        # 3. 輸入框渲染區塊 (只有在 AI 模式且沒有在等待網路請求時顯示)
        if self.is_ai_mode and not self.is_waiting_for_ai:
            # 畫一條微弱的分隔線
            pygame.draw.line(screen, (60, 60, 65), (self.box_rect.x + 10, self.box_rect.y + 50), (self.box_rect.x + 430, self.box_rect.y + 50), 1)
            
            if self.player_input_text == "" and self.composition_text == "":
                input_tips = "輸入文字後按 [Enter] 送出 / 按 [Esc] 關閉..."
                input_surf = font.render(input_tips, True, (100, 100, 100))
                screen.blit(input_surf, (self.box_rect.x + 15, self.box_rect.y + 55))
            else:
                # 📌 補回：渲染已經「確認輸入」的綠色/青色文字首段
                confirmed_surf = font.render(f"> {self.player_input_text}", True, (0, 255, 255))
                screen.blit(confirmed_surf, (self.box_rect.x + 15, self.box_rect.y + 55))
                
                # 📌 補回：計算黃色未確定字（注音符號組字）要接著渲染的 X 軸起點
                current_x = self.box_rect.x + 15 + confirmed_surf.get_width()
                
                # 📌 補回：渲染正在打的注音/組字 (亮黃色 + 黃色底線)
                if self.composition_text:
                    comp_surface = font.render(self.composition_text, True, (255, 215, 0)) 
                    screen.blit(comp_surface, (current_x, self.box_rect.y + 55))
                    
                    # 畫一條簡單的底線，提示玩家此字尚未按確認鍵
                    comp_width = comp_surface.get_width()
                    pygame.draw.line(screen, (255, 215, 0), (current_x, self.box_rect.y + 73), (current_x + comp_width, self.box_rect.y + 73), 1)
                    
        elif not self.is_ai_mode:
            tip_surf = font.render("▼", True, (200, 200, 200))
            screen.blit(tip_surf, (self.box_rect.right - 25, self.box_rect.bottom - 20))