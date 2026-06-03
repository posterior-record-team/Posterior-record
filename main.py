# 遊戲核心引擎

import pygame
import sys

from time_manager import TimeManager  #時間
from game_state import GameState     #數值條
from backpack import BackpackSystem  #背包 
from entities import Player , NPC  # 角色模組
from entities import Bed, Table    # 物件模組
from map import RoomMap, CorridorMap ,OfficeMap, BasementMap #地圖
from dialogue_system import DialogueSystem #對話狀態、打字處理、UI 繪製和劇本走向
from magic_training import MagicTrainingSystem #魔法


class GameEngine:
    def __init__(self):
        # 1. 初始化 Pygame
        pygame.init()
        
        # 2. 設定遊戲的「原始美術解析度」（星露谷/Undertale 風格的主流低解析度）
        self.GAME_WIDTH = 480
        self.GAME_HEIGHT = 270
        
        # 3. 建立視窗：設定為「獨佔全螢幕」並開啟「自動等比例縮放」
        self.screen = pygame.display.set_mode(
            (self.GAME_WIDTH, self.GAME_HEIGHT), 
            pygame.FULLSCREEN | pygame.SCALED
        )

        # 初始化字體（使用微軟正黑體，大小設為 12 像素，適合低解析度畫面）
        self.font = pygame.font.SysFont("simsun", 12)

        self.game_state = GameState()
        self.bar_font = pygame.font.SysFont("microsoftjhenghei", 10) # 條狀圖專用小字
        
        # 4. 設定視窗標題與時鐘
        pygame.display.set_caption("後驗紀錄：404 監測點")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # 5. 實體化時間管理器
        self.time_manager = TimeManager()

        # 6. 背包引入
        self.backpack = BackpackSystem()
        
        # 定義不同地同場景函式名
        self.room_map = RoomMap()           # 醫療室
        self.corridor_map = CorridorMap()   # 走廊
        self.office_map = OfficeMap()       # 辦公室
        self.basement_map = BasementMap()   # 地下室

        # 打开地图
        self.tilemap = self.room_map
        # 預設起點
        self.current_scene = "room"

        # ====== 實體物件狀態 =======
        # 取得醫療室（room_map）的偏移量，讓物件精準對齊置中的房間
        rx = self.room_map.offset_x if hasattr(self.room_map, 'offset_x') else 0
        ry = self.room_map.offset_y if hasattr(self.room_map, 'offset_y') else 0

        # 【床】：放在醫療室左下角 (直放，往上微調 Y 座標防卡牆)
        self.bed = Bed(rx + 32, ry + 100) 
        
        # 【桌子】：放在醫療室中間偏下
        self.table = Table(rx + 120, ry + 130)
        
        # 將桌子的 Rect 塞進 room_map 的牆壁/障礙物清單，讓它在玩家诞生前就具備「碰撞體積」
        if hasattr(self.room_map, 'walls'):
            self.room_map.walls.append(self.table.get_rect())
        if hasattr(self.room_map, 'wall_rects'):
            self.room_map.wall_rects.append(self.table.get_rect())
        if hasattr(self.room_map, 'obstacles'):
            self.room_map.obstacles.append(self.table.get_rect())
        if hasattr(self.room_map, 'colliders'):
            self.room_map.colliders.append(self.table.get_rect())

        # 2. 控制睡眠與午夜強制黑畫面的計時器
        self.is_fading = False        # 是否處於黑畫面狀態
        self.fade_timer = 0.0         # 黑畫面計時器（秒）

        # 內部初始化角色位置（在牆壁清單完整後才建立玩家）
        self.player = Player(self.tilemap.offset_x + 32, self.tilemap.offset_y + 112)
        self.pioli = NPC(self.office_map.offset_x + (7 * 16), self.office_map.offset_y + (4 * 16))
        self.pioli.current_scene = "office"  # 記錄皮歐里目前所在的空間
        
        # 錄當前可互動的目標：None, "to_corridor", "to_room", "to_office", "to_basement", "use_bed"
        self.current_interact_target = None
        
        # 對話系統相關狀態
        self.dialogue_system = DialogueSystem()
        self.can_talk_with_npc = False  # 玩家是否靠近到可以對話的距離

        # 魔法系統相關狀態
        self.magic_training_system = MagicTrainingSystem()

        # 遊戲運行狀態標記
        self.running = True

    def run(self):
        # 遊戲主循環 (Game Loop)
        while self.running:
            # 取得這一幀與上一幀之間過去了多少毫秒 (Delta Time)
            # tick(60) 除了限制 60 幀，還會回傳毫秒數
            dt = self.clock.tick(self.FPS)

            self.handle_events()
            self.update(dt) # 將時間差傳入更新邏輯
            self.draw()
            
            
        # 退出遊戲
        pygame.quit()
        sys.exit()

    def handle_events(self):
        #  事件監聽（按鍵、滑鼠、視窗關閉等）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # =================================================================
            # 狀況 A：鍵盤事件優先導向小遊戲
            # =================================================================
            # 優先攔截：如果魔法小遊戲/選單處於開啟狀態
            if self.magic_training_system.is_active:
                if event.type == pygame.KEYDOWN:
                    # 將事件丟給小遊戲處理
                    self.magic_training_system.handle_keydown(event, self.game_state, engine=self)
                continue # 攔截成功，不執行常規的走路或對話按鍵

            # =================================================================
            # 狀況 B：正在與皮歐里進行 AI 對話中（文字輸入打字模式）
            # =================================================================
            # 📌 整合點：只要對話框是開啟狀態 (is_active)，就將所有打字與選字事件餵給它
            elif self.dialogue_system.is_active:
                # 1. 處理特殊功能鍵（如 Enter 送出、Esc 關閉、Backspace 刪除）
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        # 呼叫對話系統的刪除字元功能
                        self.dialogue_system.handle_backspace()
                    else:
                        # 傳遞其他按鍵（如 Enter / Esc）
                        self.dialogue_system.handle_keydown(event, game_state=self)
                    
                # 2. 📌 修正事件 770：將未確認的注音/組字，精準傳給對話系統的 composition_text
                elif event.type == 770:
                    if hasattr(event, 'text'):
                        self.dialogue_system.composition_text = event.text
                    
                # 3. 📌 修正 TEXTINPUT：文字完成選字（或輸入英文）時，安全塞入緩衝
                elif event.type == pygame.TEXTINPUT: 
                    if hasattr(event, 'text'):
                        # 呼叫安全寫入函式，交給對話系統處理（同時會自動阻斷重複輸入）
                        self.dialogue_system.handle_text_input(event.text)
                        
                        # 當正式文字成立時，清空黃色預覽字緩衝
                        self.dialogue_system.composition_text = ""
            # =================================================================
            # 狀況 C：一般探索模式（移動、背包、地圖傳送、觸發對話）
            # =================================================================
            else:
                if event.type == pygame.KEYDOWN:
                    
                    # --- 1. 背包開啟狀態下的專屬按鍵判定 ---
                    if self.backpack.is_open:
                        # 按 ESC 或 E 鍵可以關閉背包
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_e:
                            self.backpack.toggle()
                            
                        # 如果目前切換到最後一個分頁「離開」(索引值為 4)，按下 Enter 鍵安全退出
                        elif self.backpack.current_tab == 4 and event.key == pygame.K_RETURN:
                            self.running = False
                            
                    # --- 2. 背包關閉（平常走路探索）狀態下的按鍵判定 ---
                    else:
                        # 平常未開背包時，按 ESC 或 E 鍵可以打開背包
                        if event.key == pygame.K_e or event.key == pygame.K_ESCAPE:
                            self.backpack.toggle()

                        # 【Q鍵觸發】靠近皮歐里時開啟 AI 對話
                        elif event.key == pygame.K_q and self.can_talk_with_npc:
                            # 📌 修正：不再讀取死台詞，直接啟動全新的 Gemini AI 對話模式！
                            self.dialogue_system.start_ai_dialogue(npc_name="皮歐里")
                            
                            # 📌 保持你的輸入法安全彈出視窗設定（微軟/Mac 选字框精準定位）
                            ime_rect = pygame.Rect(20, 225, 440, 25)
                            pygame.key.set_text_input_rect(ime_rect)
                            pygame.key.start_text_input() # 強制啟動系統中文輸入法

                        # 【F鍵互動與傳送】當玩家按下 F 鍵且有可互動目標時
                        elif event.key == pygame.K_f and self.current_interact_target is not None:
                            # 在床上按 F 睡覺
                            if self.current_interact_target == "use_bed":
                                self.is_fading = True
                                self.player.x = self.bed.x + 8
                                self.player.y = self.bed.y + 8
                                self.current_scene = "room"
                                self.tilemap = self.room_map
                                
                            # 從小房間出門到長廊
                            elif self.current_interact_target == "to_corridor":
                                self.current_scene = "corridor"
                                self.tilemap = self.corridor_map
                                self.player.x = self.corridor_map.spawn_x
                                self.player.y = self.corridor_map.spawn_y

                            # 從長廊回頭進小房間  
                            elif self.current_interact_target == "to_room":
                                self.current_scene = "room"
                                self.tilemap = self.room_map
                                self.player.x = self.room_map.door_rect.x
                                self.player.y = self.room_map.door_rect.y + 18

                            # 從長廊進入辦公室   
                            elif self.current_interact_target == "to_office":
                                if not self.time_manager.has_office_permission:
                                    # 📌 修正：這裡也可以直接呼叫 start_normal_dialogue 來播系統警告，不用透過舊的 dead-code
                                    self.dialogue_system.start_normal_dialogue(["系統：房門被鎖上了。沒有皮歐里的許可，不能進入他的辦公室。"])
                                    self.current_interact_target = None
                                else:
                                    self.current_scene = "office"
                                    self.tilemap = self.office_map
                                    self.player.x = self.office_map.door_rect.x + 16
                                    self.player.y = self.office_map.door_rect.y - 16

                            # 從辦公室回長廊   
                            elif self.current_interact_target == "to_corridor_from_office":
                                self.current_scene = "corridor"
                                self.tilemap = self.corridor_map
                                self.player.x = self.corridor_map.office_door_rect.x
                                self.player.y = self.corridor_map.office_door_rect.y + 18

                            # 從長廊下樓到地下一樓   
                            elif self.current_interact_target == "to_basement":                                
                                self.current_scene = "basement"
                                self.tilemap = self.basement_map
                                self.player.x = self.basement_map.offset_x + (6 * 16)
                                self.player.y = self.basement_map.offset_y + (3 * 16)

                            # 從地下室上樓回長廊    
                            elif self.current_interact_target == "to_corridor_from_basement":
                                self.current_scene = "corridor"
                                self.tilemap = self.corridor_map
                                self.player.x = self.corridor_map.stairs_rect.x + 50
                                self.player.y = self.corridor_map.stairs_rect.y + 16
                
                # 📌 只有當不在對話中時，背包才去處理它的輸入事件，避免它干擾打字
                self.backpack.handle_input(event)

    def update(self, dt):
        # --- 狀況 0：處理睡覺/昏倒的黑畫面 5 秒鐘 ---
        if self.is_fading:
            self.fade_timer += dt / 1000.0  # pygame的dt是毫秒，要除以1000變秒
            if self.fade_timer >= 3.0:
                self.is_fading = False
                self.fade_timer = 0.0

                # 📌 修正點：直接呼叫專用重置函式，精準切換到 06:00
                if hasattr(self.time_manager, 'set_to_six_am'):
                    self.time_manager.set_to_six_am()
                
                # 如果你的時間系統有天數（Day），可以在這裡讓天數加 1
                if hasattr(self.time_manager, 'day'):
                    self.time_manager.day += 1

                # 📌 修正核心：醒來時，把玩家位置往右、往下移開床的範圍（移到空地上），防止原地無限重複觸發睡覺！
                self.player.x = self.bed.x + 32
                self.player.y = self.bed.y + 16

            return # 🚀 重中之重：黑畫面期間，到這裡就 return 結束！絕對不讓下方的午夜判定去重置計時器。
        
        # 當背包打開、或是正在跟皮歐里對話時，全部不更新移動與地圖判定
        if self.backpack.is_open or self.dialogue_system.is_talking:
            return # 直接結束這輪更新，凍結玩家與時間

        # --- 以下是正常的探索、移動與感應更新邏輯 ---
        self.time_manager.update(
            dt, 
            pioli=self.pioli, 
            room=self.room_map, 
            corridor=self.corridor_map, # 如果你有傳走廊地圖的話
            office=self.office_map, 
            basement=self.basement_map
        )
        
        # 📌 新增：午夜 12 點（24:00 或 00:00）強制昏倒黑屏判定
        # 這裡會檢查時間是否來到 24 點（或根據你系統判定午夜的數值修改）
        if hasattr(self.time_manager, 'current_minutes') and self.time_manager.current_minutes >= 1440:
            self.is_fading = True
            self.fade_timer = 0.0     
            # 強制將場景切換回醫療室
            self.current_scene = "room"
            self.tilemap = self.room_map   
            # 強制將玩家移回床上（置中對齊直放的床）
            self.player.x = self.bed.x + 8
            self.player.y = self.bed.y + 16
            return

        # 📌 終極修正：如果是醫療室，直接將桌子的碰撞箱貼在玩家身上，完全避開函式參數數量問題
        if self.current_scene == "room" and hasattr(self, 'table'):
            self.player.current_obstacles = [self.table.get_rect()]
        else:
            self.player.current_obstacles = None  # 其他地圖清空障礙物

        # 🚀 這樣呼叫就維持原本的參數數量，絕對不會再報 TypeError 說數量不對！
        self.player.handle_movement(dt, self.tilemap)

        
        # 每次更新前先重置互動目標
        self.current_interact_target = None
        
        # 建立玩家碰撞框時，維持純粹的物理坐標，確保與地圖各門的 Rect 同步
        player_rect = pygame.Rect(int(self.player.x), int(self.player.y), self.player.width, self.player.height)

        # --- 1. 玩家在初始小房間 ---
        if self.current_scene == "room":
            # 📌 這裡純粹只做「偵測是否顯示 [F] 睡覺提示」，絕對不主動觸發黑屏！
            if player_rect.colliderect(self.bed.get_rect()):
                self.current_interact_target = "use_bed"
            else:
                trigger = self.room_map.door_rect.copy()
                trigger.height += 3  

                if player_rect.colliderect(trigger):
                    self.current_interact_target = "to_corridor"

        # --- 2. 玩家在長廊 ---
        elif self.current_scene == "corridor":
            # 偵測回醫療室的門
            trigger_room = self.corridor_map.room_door_rect.copy()
            trigger_room.height -= 17
            
            # 偵測去辦公室的門
            trigger_office = self.corridor_map.office_door_rect.copy()
            trigger_office.height += 6
            
            # 將 inflate_ip 改為 inflate，防止 Y 軸偵測在遊戲迴圈中被無限放大而跑掉
            trigger_stairs = self.corridor_map.stairs_rect.inflate(8, 8)
            
            if player_rect.colliderect(trigger_room):
                self.current_interact_target = "to_room"
            elif player_rect.colliderect(trigger_office):
                self.current_interact_target = "to_office"
            elif player_rect.colliderect(trigger_stairs):
                self.current_interact_target = "to_basement"
                
        # --- 3. 玩家在皮歐里辦公室 ---
        elif self.current_scene == "office":
            trigger = self.office_map.door_rect.copy()
            trigger.height -= 3  # 修正：精簡寫法，向上微調出門感應區
            if player_rect.colliderect(trigger):
                self.current_interact_target = "to_corridor_from_office"
                
        # --- 4. 玩家在地下一樓 ---
        # --- 4. 玩家在地下一樓 ---
        elif self.current_scene == "basement":
            # 將 inflate_ip 改為 inflate，確保地下室的傳送判定格不會位移
            trigger = self.basement_map.door_rect.inflate(8, 8)
            if player_rect.colliderect(trigger):
                self.current_interact_target = "to_corridor_from_basement" 
            
            # 📌 改用像素座標 (x, y) 來判定是否踩在中央 3x3 的格子區域內
            if 216 <= self.player.x <= 264 and 111 <= self.player.y <= 159:
                if not self.magic_training_system.is_active:
                    self.magic_training_system.start_training()
            else:
                # 📌 核心修正：當玩家的腳完全離開這塊區域時，解鎖！
                # 這樣下次重新走進來時，才能再次觸發選單
                self.magic_training_system.has_triggered_zone = False

        # 動態 NPC 對話感應區：只有當玩家與皮歐里在同一個場景時才計算
        if self.current_scene == self.pioli.current_scene and not self.dialogue_system.is_talking:
            pioli_rect = pygame.Rect(int(self.pioli.x), int(self.pioli.y), self.pioli.width, self.pioli.height)
            talk_trigger = pioli_rect.inflate(32, 32) # 周圍 16 像素感應區
            
            if player_rect.colliderect(talk_trigger):
                self.can_talk_with_npc = True
            else:
                self.can_talk_with_npc = False
        else:
            self.can_talk_with_npc = False
                        
    def draw(self):
        #  畫面繪製
        # 預設底色塗黑
        self.screen.fill((0, 0, 0))

        # =================================================================
        # LAYER 1：世界實體與地圖層（最底層）
        # =================================================================
        # 1. 自動繪製當前地圖
        self.tilemap.draw(self.screen)
        
        # 2. 如果玩家在醫療室，畫出床和桌子（確保他們被畫在地圖上方、玩家與 UI 下方）
        if self.current_scene == "room":
            self.bed.draw(self.screen)
            self.table.draw(self.screen)

        # 3. 如果玩家跟皮歐里在同一個場景，就呼叫 NPC 的 draw 將他畫出來
        if self.current_scene == self.pioli.current_scene:
            self.pioli.draw(self.screen)

         # 4. 如果在地下一樓，渲染中央 3x3 區域為半透明土黃色
        if self.current_scene == "basement":
            # 建立一個 48x48 大小的半透明畫布 (208 - 160 = 48)
            magic_zone_surf = pygame.Surface((48, 48), pygame.SRCALPHA)
            # 填入半透明土黃色 (紅色180, 綠色135, 藍色50, 透明度100)
            magic_zone_surf.fill((180, 135, 50, 100))

            # 渲染到世界像素座標 (160, 160) 的位置
            self.screen.blit(magic_zone_surf, (216, 111))
            # (選做) 給它一個土黃色邊框，讓邊界更明顯
            pygame.draw.rect(self.screen, (200, 150, 60), (216, 111, 48, 48), 1)   

        # 繪製玩家自己
        self.player.draw(self.screen)


        # 📌 渲染魔法選單或打字小遊戲
        self.magic_training_system.draw(self.screen, self.bar_font)
        # =================================================================
        # LAYER 2：常駐遊戲 UI 與世界提示層（中層）
        # =================================================================
        # 1. 根據當前可互動的目標，動態渲染特定的互動提示文字 (當背包打開時隱藏，防止穿透)
        if self.current_interact_target is not None and not self.backpack.is_open:
            # 預設提示字
            prompt_str = "[F] 開門"
            
            if self.current_interact_target == "to_corridor":
                prompt_str = "[F] 進入走廊"
            elif self.current_interact_target == "to_room":
                prompt_str = "[F] 進入醫療室"
            elif self.current_interact_target == "to_office":
                prompt_str = "[F] 進入辦公室"
            elif self.current_interact_target == "to_corridor_from_office":
                prompt_str = "[F] 進入走廊"
            elif self.current_interact_target == "to_basement":
                prompt_str = "[F] 下樓 (B1)"
            elif self.current_interact_target == "to_corridor_from_basement":
                prompt_str = "[F] 上樓 (1F)"
            elif self.current_interact_target == "use_bed":
                prompt_str = "[F] 睡覺"
                
            prompt_surface = self.font.render(prompt_str, True, (255, 255, 0))
            # 固定渲染在畫面的中下方，精緻又不擋視線（睡覺提示統一使用此處）
            self.screen.blit(prompt_surface, ((480 - prompt_surface.get_width()) // 2, 230))

        # 2. 靠近皮歐里且沒在對話、沒開背包時提示 [Q]
        if self.can_talk_with_npc and not self.dialogue_system.is_talking and not self.backpack.is_open:
            prompt_surface = self.font.render("[Q] 與皮歐里對話", True, (255, 255, 0))
            self.screen.blit(prompt_surface, ((480 - prompt_surface.get_width()) // 2, 210))

        # 3. 右上角時間 UI ( "Day 1 - 08:00")
        time_text = self.time_manager.get_time_string()
        time_surface = self.font.render(time_text, False, (255, 255, 255)) 
        self.screen.blit(time_surface, (self.GAME_WIDTH - time_surface.get_width() - 10, 10))
        """
        # 4. 左上角皮歐里狀態除錯文字
        schedule_tag = self.time_manager.priori_schedule_state
        status_text = self.time_manager.get_priori_status_text()
        debug_text = f"【排程標籤】: {schedule_tag} | {status_text}"
        debug_surface = self.font.render(debug_text, False, (0, 255, 255)) 
        self.screen.blit(debug_surface, (10, 10))
         """
        
        # 5. 右下角直立式血量與體力條 (HP / Energy Bar)
        margin_x = 10  # 距離右邊界的邊距
        margin_y = 0   # 距離下邊界的邊距
        bar_width = 12 # 條狀圖的寬度
        bar_height = 60 # 條狀圖的總高度
        
        energy_x = self.GAME_WIDTH - bar_width - margin_x
        energy_y = self.GAME_HEIGHT - bar_height - margin_y
        hp_x = energy_x - bar_width - 10
        hp_y = self.GAME_HEIGHT - bar_height - margin_y
        
        # 畫生命條 (綠色)
        current_hp_height = int(bar_height * (self.game_state.health / self.game_state.max_health))
        pygame.draw.rect(self.screen, (50, 50, 50), (hp_x, hp_y, bar_width, bar_height)) 
        pygame.draw.rect(self.screen, (67, 223, 77), (hp_x, hp_y + (bar_height - current_hp_height), bar_width, current_hp_height)) 
        
        # 畫體力條 (黃色)
        current_energy_height = int(bar_height * (self.game_state.energy / self.game_state.max_energy))
        pygame.draw.rect(self.screen, (50, 50, 50), (energy_x, energy_y, bar_width, bar_height)) 
        pygame.draw.rect(self.screen, (255, 200, 0), (energy_x, energy_y + (bar_height - current_energy_height), bar_width, current_energy_height)) 
        
        # 條狀圖上方 H 和 E 小字標籤
        hp_text = self.bar_font.render("H", False, (255, 255, 255))
        energy_text = self.bar_font.render("E", False, (255, 255, 255))
        self.screen.blit(hp_text, (hp_x + 2, hp_y - 12))
        self.screen.blit(energy_text, (energy_x + 2, energy_y - 12))

        # 6. 渲染對話框（確保對話框在普通 UI 上方，但依然在背包下方）
        self.dialogue_system.draw(self.screen, self.font)


        # =================================================================
        # LAYER 3：最高優先級 UI 層（最頂層）
        # =================================================================
        # 只有當背包打開時，才呼叫繪製，這會直接覆蓋掉下方所有的實體、地圖、對話框與提示字
        if self.backpack.is_open:
            self.backpack.draw(self.screen, self.game_state)


        # =================================================================
        # LAYER 4：螢幕特效層（全黑遮罩）
        # =================================================================
        # 當睡覺或午夜斷片昏倒時，強制用滿版黑畫面覆蓋整個螢幕 5 秒鐘
        if self.is_fading:
            fade_surface = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
            fade_surface.fill((0, 0, 0)) 
            self.screen.blit(fade_surface, (0, 0))
            
            # 在全黑畫面正中央顯示熟睡文字提示
            sleep_font = self.font.render("Zzz...", True, (255, 255, 255))
            self.screen.blit(sleep_font, ((self.GAME_WIDTH - sleep_font.get_width()) // 2, self.GAME_HEIGHT // 2 - 10))


        # 最終刷洗並同步顯示到視窗上
        pygame.display.flip()

# 程式進入點
if __name__ == "__main__":
    game = GameEngine()
    game.run()