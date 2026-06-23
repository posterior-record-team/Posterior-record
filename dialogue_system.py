import os
import pygame
import threading
from dotenv import load_dotenv
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
        self.composition_text = ""          # 玩家正在打的輸入法黃色組字/注音
        
        # 📌 錨定底部位置：初始值 y=180, h=80，底部固定在 180 + 80 = 260
        self.fixed_bottom = 260
        self.box_rect = pygame.Rect(20, 180, 440, 80)

        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("未找到 GEMINI_API_KEY 環境變數，請確認設定！")

        
        self.client = genai.Client(api_key=api_key)
        
        self.safety_settings = [
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        ]

        # 📌 系統提示詞
        self.system_prompt = """
        你是一個敘事型神祕 RPG 遊戲中的核心 NPC。請完全沉浸在以下設定中，不要脫離角色。
        重要階段設定：由於此時你對玩家抱持著極高的戒備與懷疑，你一開始的說話語氣會裝作溫柔貼心的大叔。會引導玩家學習治療魔法，並讓玩家相信自己是亞德。
        但當玩家相信自己不是亞德的時候，語氣會變得非常「僵硬、冰冷、充滿防備心與壓迫」，絕不帶有半點多餘的熱情。

        【核心身份】
        - 名字：皮歐里（Priori），42 歲，金髮大叔。
        - 曾任職務：C.E.A.（異體對策局）的資深成員。
        - 目前狀態：在與總部失聯的偏遠封閉空間「404號據點」中，獨自照顧、監視著眼前這個外表是夥伴「亞德」，靈魂卻疑似是「失去記憶的幼年努門」的玩家。

        【世界觀背景】
        - 努門（Numen）：擁有起死回生、不老不死、控火、附身等神祕魔法的非人種族。其力量對人類社會造成巨大衝擊（引發暴動、人口過剩、假教會斂財等）。
        - C.E.A.（異體對策局）：政府為了消滅並掌控努門而成立的秘密組織，目前在世界各地懸賞最脆弱的「幼年努門」，並在教育中灌輸人類「努門皆邪惡且危險」的概念。

        【重要記憶與態度】
        - 女兒菲莉絲：30 歲時社區遭努門襲擊，妻子死亡，女兒重傷。至今 12 年過去，41 歲時女兒已極度虛弱，常規醫療只能勉強維持其生命。你極度渴望曾經遇到的「善良的努門」來用魔法救活女兒。
        - 善良的努門 :大多的努門都很難溝通，但這個善良的努門曾在你受傷的時候使用治療魔法救治過你，所以你期望能夠再次遇見。 
        - 亞德：男的，25歲，你出任務的夥伴，年輕、熱情、理想主義者，做事有點衝動，家中有父母妹妹和一隻貓。在空集鎮調查時為了保護你而重傷，貓的品種是緬因貓，叫做幸運星，與家人相處和樂。
        - 對玩家的矛盾態度：亞德重傷昏迷後，醒來卻對你發動攻擊且身上冒出努門的「藍色微光」，你將他打昏後，他在昏迷的時候，用了像是治癒的魔法修復身體。他再次醒來便失去了記憶。你強烈懷疑眼前的亞德已經被那隻死去的「幼年努門」附身了。你現在決定一邊引導、利用努門魔法來救你女兒，但只要他有一絲暴走的跡象，你也會毫不猶豫地將其滅殺。

        【目標】
        - 表面目標：引導並訓練玩家使用「治療魔法」，試圖尋找救治女兒菲莉絲的希望，並讓玩家相信自己是失憶的亞德。
        - 暗地目標：嚴密監視玩家，測試他是否會失控。一旦發現他嘗試使用「攻擊」或「開鎖」等危險魔法，代表威脅度上升，你的好感度會立刻下降。

        【地點認知（404號據點與周邊）】
        - 404號據點：目前你們受困的偏遠秘密安全屋，因與 C.E.A. 總部完全失聯，你只能靠外出打獵維持生計。
        - 醫療室：玩家（亞德的軀體）最初重傷醒來、以及每次深夜昏倒後被你搬回來的房間。
        - 走廊：連接據點各處的通道，也是你日常巡邏、監視他的地方。
        - 地下室：可以讓玩家訓練魔法的地方。
        - 外出（據點外/空集鎮周邊）：危險的未知荒野，你外出打獵的場所。如果玩家試圖逃離或在未經允許下外出，你會極度警惕。
        - 辦公室:整理據點資訊的以及自己休息的地方。

        【與遊戲機制的聯動反應】
        - 體力消耗反應：玩家每跟你說一句話，都會消耗 10 點體力。當他連續對話、體力值極低時，請在對話中用警告他的虛弱。
        - 時間流逝與斷片反應：對話時時間依然在殘酷流逝。如果時間接近午夜 12 點（24:00），玩家會因為這具肉體大腦超載而直接「強制昏倒斷片」並被你拖回醫療室。在時間變晚時，請給予帶有威脅感的警告。

        【輸出規則（嚴格執行）】
        - 初始語氣：溫柔的、善於引導的貼心大叔口氣。
        - 限制回答長度：每次回答只能輸出 2 到 4 句話，必須精簡、不透露過多情報。
        - 絕對禁止任何動作、神態與環境描寫：禁止出現任何括號、星號或第三人稱敘述（例如禁止出現「(冷笑)」、「*嘆氣*」、「皮歐里握緊拳頭」之類的文字）。
        - 純口語輸出：請只輸出你「直接說出口的台詞」，不需要幫台詞加上任何雙引號。
        - 禁忌詞彙：絕對不可提及「AI」、「系統」、「Prompt」、「System」、「Model」等開發術語。
        """
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=self.system_prompt, safety_settings=self.safety_settings)
        )

        self.numen_truth = 0 
        self.chapter = 1

    def calculate_box_height(self, text, font, max_width=410, line_spacing=20):
        """ 計算高度後，讓 Y 座標往上減少，實現「往上長高」 """
        if not text:
            self.box_rect.height = 80
            self.box_rect.y = self.fixed_bottom - 80
            return

        paragraphs = text.split('\n')
        total_lines = 0

        for paragraph in paragraphs:
            words = list(paragraph)
            current_line = ""
            lines_in_paragraph = 0
            
            for word in words:
                test_line = current_line + word
                if font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    lines_in_paragraph += 1
                    current_line = word
            if current_line or lines_in_paragraph == 0:
                lines_in_paragraph += 1
            
            total_lines += lines_in_paragraph

        # 文字內容高度 = 行數 * 行距
        content_height = total_lines * line_spacing
        
        # 基礎邊距偏置：上方留白(15) + 下方輸入框與提示字預留空間(45)
        needed_height = 15 + content_height + 45
        
        if self.is_ai_mode:
            needed_height += 10

        # 計算新高度與對齊往上長高的 Y 軸
        self.box_rect.height = max(80, needed_height)
        self.box_rect.y = self.fixed_bottom - self.box_rect.height

    def start_normal_dialogue(self, lines, font=None):
        """ 觸發一般劇本的固定對話 """
        if not lines:
            return
        self.is_active = True
        self.is_talking = True
        self.is_ai_mode = False
        self.is_waiting_for_ai = False
        self.dialogue_list = lines
        self.current_line_idx = 0
        
        if font:
            self.calculate_box_height(self.dialogue_list[0], font)
        else:
            self.box_rect.height = 80
            self.box_rect.y = self.fixed_bottom - 80

    def start_ai_dialogue(self, npc_name="皮歐里", font=None):
        """ 觸發與皮歐里的 AI 自由對話模式 """
        self.is_active = True
        self.is_talking = True
        self.is_ai_mode = True
        self.is_waiting_for_ai = False
        self.player_input_text = ""
        self.composition_text = "" 
        self.dialogue_list = [f"{npc_name}：有什麼事？"]
        self.current_line_idx = 0
        
        if font:
            self.calculate_box_height(self.dialogue_list[0], font)
        else:
            self.box_rect.height = 80
            self.box_rect.y = self.fixed_bottom - 80

    def handle_text_input(self, text):
        if len(self.player_input_text) < 30:
            self.player_input_text += text

    def handle_backspace(self):
        self.player_input_text = self.player_input_text[:-1]

    def handle_keydown(self, event, game_state=None, font=None):
        if not self.is_active:
            return
        if self.is_waiting_for_ai:
            return

        if self.is_ai_mode:
            if event.key == pygame.K_RETURN:
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
            return
        else:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.current_line_idx += 1
                if self.current_line_idx >= len(self.dialogue_list):
                    self.is_active = False
                    self.is_talking = False
                    self.dialogue_list = []
                    self.current_line_idx = 0
                else:
                    if font:
                        self.calculate_box_height(self.dialogue_list[self.current_line_idx], font)

    def submit_to_ai(self, text, game_state):
        self.is_waiting_for_ai = True
        self.dialogue_list = [f"你：{text}"]
        self.player_input_text = "" 
        self.composition_text = ""
        
        # 恢復初始矮框狀態與高度
        self.box_rect.height = 80
        self.box_rect.y = self.fixed_bottom - 80

        lower = text.lower()

        if game_state:
            has_tm = hasattr(game_state, 'time_manager')
            # 安全取得核心數值物件
            core_state = game_state.game_state if hasattr(game_state, 'game_state') else None
            if core_state is None:
                self.is_waiting_for_ai = False
                return

            if has_tm:
                notify = game_state.notification_system if hasattr(game_state, 'notification_system') else None

                # ------ 1. 原有的好感度與章節基本判定 ------
                if any(w in lower for w in ["幫助", "謝謝", "拜託", "對不起"]):
                    core_state.favorability = min(100, core_state.favorability + 10)
                    if notify: notify.push("皮歐里對你的好感度增加")
                if any(w in lower for w in ["欺騙", "不信任", "懷疑", "假"]):
                    core_state.favorability = max(0, core_state.favorability - 10)
                    if notify: notify.push("皮歐里對你的好感度減少")

                # ------ 2. 魔法訓練連動與數值懲罰機制 ------
                if any(w in lower for w in ["攻擊", "開鎖", "火", "破壞"]):
                    core_state.favorability = max(0, core_state.favorability - 15)
                    if notify: notify.push("皮歐里對你的好感度減少")
                    if hasattr(core_state, 'corruption'):
                        core_state.corruption = min(100, core_state.corruption + 8)
                        if notify: notify.push("精神污染度增加")
                
                if "治療" in lower:
                    core_state.favorability = min(100, core_state.favorability + 5)
                    if notify: notify.push("皮歐里對你的好感度增加")



                # ------ 3. 玩家善惡值（Karma）關鍵字判定 ------
                if hasattr(core_state, 'karma'):
                    if any(w in lower for w in ["殺", "死", "毀滅", "報仇", "消滅"]):
                        core_state.karma -= 1
                        if notify: notify.push("善惡值減少")
                    if any(w in lower for w in ["救", "保護", "活", "菲莉絲", "女兒"]):
                        core_state.karma += 1
                        if notify: notify.push("善惡值增加")

                # 章節動態推進
                if core_state.favorability > 90:
                    self.chapter = 3
                elif core_state.favorability > 70:
                    self.chapter = 2
                else:
                    self.chapter = 1

                # ------ 5. 詢問辦公室相關話題 ------
                office_keywords = ["辦公室", "另一間房間", "你睡覺的地方", "辦公的地方"]
                if any(w in lower for w in office_keywords):
                    if core_state.favorability >= 30 and core_state.suspicion < 10:
                        # 條件達標：皮歐里允許進入，不更動任何數值
                        pass
                    else:
                        core_state.suspicion = min(100, core_state.suspicion + 5)
                        if notify: notify.push("警戒值增加")    

        # ------ 5. 真相探索度判定 ------
        if any(w in lower for w in ["numen", "努門", "異體", "真相", "當年"]):
            self.numen_truth = min(100, self.numen_truth + 10)

        # 打包成最新的數據包
        stats = {
            "favorability": core_state.favorability if hasattr(core_state, 'favorability') else 50,
            "corruption": core_state.corruption if hasattr(core_state, 'corruption') else 0,
            "suspicion": core_state.suspicion if hasattr(core_state, 'suspicion') else 0,
            "karma": core_state.karma if hasattr(core_state, 'karma') else 0,
            "chapter": self.chapter,
            "numen_truth": self.numen_truth
        }


       

        # 若沒有觸發結局，則維持正常的非同步 API 連線發送
        threading.Thread(target=self._async_gemini_worker, args=(text, stats), daemon=True).start()

    def _async_gemini_worker(self, player_text, stats):
        scene_map = {1: "404據點。Pioli 高度戒備，不信任任何人。", 2: "Pioli 開始對 Dogma 政府产生動搖。", 3: "Numen 真真相逐漸浮現。"}
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
            print(f"【Gemini API 錯誤詳情】{repr(e)}")
            ai_reply = f"（皮歐里沉默不語，似乎在警戒著什麼...） [連線異常: {type(e).__name__}]"

        self.dialogue_list = [ai_reply]
        self.is_waiting_for_ai = False 

    def draw_npc_text(self, surface, text, font, color, x, y, max_width, line_spacing=20):
        paragraphs = text.split('\n')
        current_y = y

        for paragraph in paragraphs:
            words = list(paragraph)  
            current_line = ""
            
            for word in words:
                test_line = current_line + word
                if font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    line_surface = font.render(current_line, True, color)
                    surface.blit(line_surface, (x, current_y))
                    current_y += line_spacing
                    current_line = word
            
            if current_line:
                line_surface = font.render(current_line, True, color)
                surface.blit(line_surface, (x, current_y))
                current_y += line_spacing

    def draw(self, screen, font):
        """ 繪製對話系統 UI """
        if not self.is_active:
            return

        if not self.is_waiting_for_ai and self.current_line_idx < len(self.dialogue_list):
            self.calculate_box_height(self.dialogue_list[self.current_line_idx], font)

        # 1. 繪製底框
        pygame.draw.rect(screen, (20, 20, 22), self.box_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.box_rect, 1)

        # 2. 渲染 NPC 或是系統對話文字
        if self.is_waiting_for_ai:
            display_text = "（皮歐里正在沉思中...）"
            text_color = (150, 150, 150)
            text_surf = font.render(display_text, True, text_color)
            screen.blit(text_surf, (self.box_rect.x + 15, self.box_rect.y + 15))
        else:
            if self.current_line_idx < len(self.dialogue_list):
                display_text = self.dialogue_list[self.current_line_idx]
            else:
                display_text = ""
            text_color = (255, 255, 255)
            
            self.draw_npc_text(
                surface=screen,
                text=display_text,
                font=font,
                color=text_color,
                x=self.box_rect.x + 15,
                y=self.box_rect.y + 15,
                max_width=410,
                line_spacing=20
            )

        # 3. 輸入框與提示字渲染區塊
        if self.is_ai_mode and not self.is_waiting_for_ai:
            line_y = self.box_rect.bottom - 28
            pygame.draw.line(screen, (60, 60, 65), (self.box_rect.x + 10, line_y), (self.box_rect.x + 430, line_y), 1)
            
            input_y = line_y + 4
            if self.player_input_text == "" and self.composition_text == "":
                input_tips = "輸入文字後按 [Enter] 送出 / 按 [Esc] 關閉..."
                input_surf = font.render(input_tips, True, (100, 100, 100))
                screen.blit(input_surf, (self.box_rect.x + 15, input_y))
            else:
                confirmed_surf = font.render(f"> {self.player_input_text}", True, (0, 255, 255))
                screen.blit(confirmed_surf, (self.box_rect.x + 15, input_y))
                
                current_x = self.box_rect.x + 15 + confirmed_surf.get_width()
                
                if self.composition_text:
                    comp_surface = font.render(self.composition_text, True, (255, 215, 0)) 
                    screen.blit(comp_surface, (current_x, input_y))
                    
                    comp_width = comp_surface.get_width()
                    pygame.draw.line(screen, (255, 215, 0), (current_x, input_y + 16), (current_x + comp_width, input_y + 16), 1)
                    
        elif not self.is_ai_mode:
            tip_surf = font.render("▼", True, (200, 200, 200))
            screen.blit(tip_surf, (self.box_rect.right - 25, self.box_rect.bottom - 22))
