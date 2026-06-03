import pygame
import random

class MagicTrainingSystem:
    def __init__(self):
        self.is_active = False          # 是否開啟選單或小遊戲
        self.state = "MENU"             # "MENU" (選擇魔法) 或 "GAME" (打字小遊戲)
        self.has_triggered_zone = False  # 防重複觸發鎖
        
        # 選單相關
        self.options = ["治療", "攻擊", "盜賊"]
        self.selected_idx = 0
        
        # 打字小遊戲相關
        self.target_word = ""           # 當前畫面上要打的單字/字母
        self.player_typed = ""          # 玩家目前打進去的字母
        self.wrong_count = 0            # 錯誤次數
        self.success_needed = 3         # 成功打對幾次算完成練習
        self.success_count = 0          # 目前成功幾次
        
        # 字庫
        self.word_pool = ["heal", "cure", "light", "fire", "burn", "blast", "lock", "hide", "steal"]

    def start_training(self):
        """ 觸發進入選單 """
        if self.has_triggered_zone: # 如果鎖住了，就不重複觸發
            return
        self.is_active = True
        self.state = "MENU"
        self.selected_idx = 0
        self.has_triggered_zone = True # 觸發後立刻鎖上

    def start_typing_game(self):
        """ 進入打字小遊戲狀態 """
        self.state = "GAME"
        self.wrong_count = 0
        self.success_count = 0
        self.player_typed = ""
        self.generate_new_word()

    def generate_new_word(self):
        """ 隨機抽一個單字 """
        self.target_word = random.choice(self.word_pool)
        self.player_typed = ""

    def handle_keydown(self, event, player, engine=None):
        """ 
        處理按鍵事件
        engine: 傳入主引擎實體 self，以便在此讀取皮歐里與時間管理器的狀態
        """
        if not self.is_active:
            return

        # ---- 狀態 A：選擇魔法選單 ----
        if self.state == "MENU":
            
            if event.key == pygame.K_ESCAPE: # 按下 ESC 退出選單
                self.is_active = False
                return
            elif event.key == pygame.K_UP or event.key == pygame.K_LEFT:
                self.selected_idx = (self.selected_idx - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
                self.selected_idx = (self.selected_idx + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if player.energy >= 10:
                    player.energy -= 10 
                    
                    chosen_magic = self.options[self.selected_idx]
                    
                    # 📌 檢查皮歐里是否在地下室，且玩家不聽話選了非治療魔法
                    if engine and hasattr(engine, 'pioli') and hasattr(engine, 'time_manager'):
                        # 只要皮歐里目前的場景跟玩家一樣都在地下室，他就看得到你
                        if engine.pioli.current_scene == "basement":
                            if chosen_magic != "治療":
                                engine.time_manager.favorability -= 5
                                print(f"【系統】皮歐里在你身後盯著你... 他不喜歡你練這個。好感度降至: {engine.time_manager.favorability}")
                    
                    self.start_typing_game()
                else:
                    # 體力不足，不觸發遊戲，直接關閉
                    self.is_active = False

        # ---- 狀態 B：打字小遊戲狀態 ----
        elif self.state == "GAME":
            # 拿到玩家按下的英文字母鍵 (a-z)
            char = event.unicode.lower()
            if char.isalpha() and len(char) == 1:
                # 檢查玩家打的字母是否符合單字的下一個位置
                expected_index = len(self.player_typed)
                if char == self.target_word[expected_index]:
                    self.player_typed += char
                    
                    # 如果整個單字打完了
                    if self.player_typed == self.target_word:
                        self.success_count += 1
                        if self.success_count >= self.success_needed:
                            # 📌 雙倍經驗判定
                            is_double_time = False
                            if engine and hasattr(engine, 'time_manager'):
                                current_m = engine.time_manager.current_minutes
                                # 條件：在 09:00 ~ 11:30 (540~690分鐘) 且 皮歐里確實人在地下室陪你
                                if 540 <= current_m < 690 and engine.pioli.current_scene == "basement":
                                    is_double_time = True
                            
                            exp_gain = 20 if is_double_time else 10
                            if is_double_time:
                                print(f"【特訓成功】皮歐里在旁指導！獲得雙倍經驗值：+{exp_gain}")
                            else:
                                print(f"【練習成功】獨自練習結束。獲得經驗值：+{exp_gain}")
                            
                            # 增加對應魔法經驗值
                            chosen_magic = self.options[self.selected_idx]
                            if chosen_magic == "治療":
                                player.magic_exp_heal += exp_gain
                            elif chosen_magic == "攻擊":
                                player.magic_exp_attack += exp_gain
                            elif chosen_magic == "盜賊":
                                player.magic_exp_thief += exp_gain
                                
                            self.is_active = False # 結束小遊戲
                        else:
                            self.generate_new_word() # 繼續下一個字
                else:
                    # 打錯了
                    self.wrong_count += 1
                    if self.wrong_count >= 3:
                        # ❌ 錯誤滿三次，練習失敗
                        self.is_active = False

    def draw(self, screen, font):
        if not self.is_active:
            return

        # ---- 繪製 A：選擇魔法選單 UI ----
        if self.state == "MENU":
            # 繪製一個精緻的黃色提示框
            menu_rect = pygame.Rect(40, 80, 400, 80)
            pygame.draw.rect(screen, (30, 30, 35), menu_rect)
            pygame.draw.rect(screen, (255, 215, 0), menu_rect, 2) # 金色邊框
            
            title_surf = font.render("【開始練習：請選擇魔法】 [Enter]確認 / [Esc]離開 (消耗 10 體力)", True, (255, 255, 255))
            screen.blit(title_surf, (50, 90))
            
            # 渲染三個選項
            start_x = 70
            for i, option in enumerate(self.options):
                if i == self.selected_idx:
                    opt_text = f"▶ [{option}]"
                    color = (255, 215, 0) # 黃色亮點
                else:
                    opt_text = f"  {option} "
                    color = (150, 150, 150)
                    
                opt_surf = font.render(opt_text, True, color)
                screen.blit(opt_surf, (start_x, 125))
                start_x += 120

        # ---- 繪製 B：打字小遊戲 UI (背景變暗) ----
        elif self.state == "GAME":
            # 1. 背景變暗：覆蓋一層黑色的半透明 Surface
            dark_overlay = pygame.Surface((480, 270), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 180)) # 黑色，Alpha 180
            screen.blit(dark_overlay, (0, 0))
            
            # 2. 顯示小遊戲 UI 主框
            game_rect = pygame.Rect(80, 60, 320, 140)
            pygame.draw.rect(screen, (20, 20, 25), game_rect)
            pygame.draw.rect(screen, (0, 255, 255), game_rect, 1) # 青色邊框
            
            # 3. 顯示目前正在練習的魔法標題
            title_text = f"正在練習：{self.options[self.selected_idx]}魔法"
            title_surf = font.render(title_text, True, (0, 255, 255))
            screen.blit(title_surf, (100, 70))
            
            # 4. 渲染打字提示與進度
            progress_text = f"進度: {self.success_count}/{self.success_needed}  |  錯誤: {self.wrong_count}/3"
            progress_surf = font.render(progress_text, True, (200, 200, 200))
            screen.blit(progress_surf, (100, 100))
            
            # 5. 渲染目標單字 建立專門給打字遊戲使用的大字體 (大小設為 22，非常清晰)
            big_game_font = pygame.font.SysFont("microsoftjhenghei", 22)
            
            word_y = 130  # 稍微往上提一點點微調座標
            
            # 使用大字體渲染已打對的部分
            correct_part = self.player_typed
            correct_surf = big_game_font.render(correct_part, True, (0, 255, 255))
            
            # 計算置中起點，讓單字能隨長度置中
            total_word_width = big_game_font.size(self.target_word)[0]
            start_x = (480 - total_word_width) // 2
            
            screen.blit(correct_surf, (start_x, word_y))
            
            # 使用大字體渲染未打的部分
            remaining_part = self.target_word[len(self.player_typed):]
            remaining_surf = big_game_font.render(remaining_part, True, (255, 255, 255))
            screen.blit(remaining_surf, (start_x + correct_surf.get_width(), word_y))
            
            # 畫一條打字橫線
            pygame.draw.line(screen, (100, 100, 100), (150, 165), (330, 165), 1)