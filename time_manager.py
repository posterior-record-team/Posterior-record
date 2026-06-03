# 時間與作息系統
import pygame

class TimeManager:
    def __init__(self):
        self.day = 1
        self.current_minutes = 450  # 📌 從早上 07:30 開始 (7 * 60 + 30 = 450)
        self.MINUTES_PER_REAL_SECOND = 1
        self.timer_accumulator = 0
        
        # 皮歐里專屬狀態與權限
        self.priori_schedule_state = "KITCHEN_BREAKFAST"
        self.has_office_permission = False  # 📌 玩家是否有辦公室許可
        self.has_outside_permission = False # 📌 玩家是否有出門許可
        self.favorability = 50              # 📌 皮歐里對玩家的好感度 (初始50)

    def update(self, dt, pioli=None, room=None, corridor=None, office=None, basement=None):
        # 1. 推進時間
        self.timer_accumulator += dt
        if self.timer_accumulator >= 1000:
            self.timer_accumulator -= 1000
            self.current_minutes += self.MINUTES_PER_REAL_SECOND
            
        if self.current_minutes >= 1440:
            self.current_minutes = 0
            self.day += 1
            
        # 2. 檢查日程狀態切換
        old_state = self.priori_schedule_state
        self.update_priori_schedule()
        
        # 3. 📌 核心：如果狀態變了，為皮歐里規劃移動路徑（星露谷式）
        if self.priori_schedule_state != old_state and pioli and room:
            self.plan_pioli_route(pioli, room, corridor, office, basement)
            
        # 4. 讓走路中的皮歐里繼續前進
        if pioli and pioli.state == "WALKING":
            pioli.move_to_target_nodes(dt)
            # 檢查是否走到了地圖邊緣需要切換場景（傳送門點）
            self.check_scene_transition(pioli, room, corridor, office, basement)

    def update_priori_schedule(self):
        """ 根據阿蟹設定的精準時間表 """
        m = self.current_minutes
        
        if 450 <= m < 480:     # 07:30 ~ 08:00
            self.priori_schedule_state = "KITCHEN_BREAKFAST"
        elif 480 <= m < 540:   # 08:00 ~ 09:00
            self.priori_schedule_state = "MEDICAL_ROOM_MORNING"
        elif 540 <= m < 690:   # 09:00 ~ 11:30
            self.priori_schedule_state = "BASEMENT_TRAINING"
        elif 690 <= m < 720:   # 11:30 ~ 12:00
            self.priori_schedule_state = "KITCHEN_LUNCH"
        elif 720 <= m < 780:   # 12:00 ~ 13:00
            self.priori_schedule_state = "MEDICAL_ROOM_NOON"
        elif 780 <= m < 840:   # 13:00 ~ 14:00
            self.priori_schedule_state = "OFFICE_WORK"
        elif 840 <= m < 1020:  # 14:00 ~ 17:00
            self.priori_schedule_state = "HUNTING_OUTSIDE"
        elif 1020 <= m < 1080: # 17:00 ~ 18:00
            self.priori_schedule_state = "KITCHEN_DINNER"
        elif 1080 <= m < 1110: # 18:00 ~ 18:30
            self.priori_schedule_state = "MEDICAL_ROOM_DINNER"
        elif 1110 <= m < 1200: # 18:30 ~ 20:00
            self.priori_schedule_state = "MEDICAL_ROOM_NIGHT"
        else:                  # 20:00 ~ 07:30 (隔天)
            self.priori_schedule_state = "OFFICE_NIGHT"

    def plan_pioli_route(self, pioli, room, corridor, office, basement):
        """ 📌 節點路徑規劃器：根據目的地，把沿途的走廊轉角像素座標塞給皮歐里 """
        rx, ry = room.offset_x, room.offset_y
        ox, oy = office.offset_x, office.offset_y
        bx, by = basement.offset_x, basement.offset_y
        
        # 這裡示範設定目的地（實際地圖像素請根據你實際的位置調整）
        if "KITCHEN" in self.priori_schedule_state:
            # 廚房假設在醫療室右側
            pioli.target_scene = "room"
            pioli.path_nodes = [(rx + 240, ry + 80)]
            
        elif "MEDICAL_ROOM" in self.priori_schedule_state:
            pioli.target_scene = "room"
            pioli.path_nodes = [(rx + 56, ry + 106)]
            
        elif "BASEMENT" in self.priori_schedule_state:
            # 要去地下室，皮歐里必須先走到醫療室門口 -> 走廊 -> 地下室樓梯
            pioli.target_scene = "basement"
            pioli.path_nodes = [(rx + 120, ry + 180), (bx + 272, by + 120)]
            
        elif "OFFICE" in self.priori_schedule_state:
            pioli.target_scene = "office"
            pioli.path_nodes = [(ox + 112, oy + 64)]
            
        elif "HUNTING" in self.priori_schedule_state:
            pioli.target_scene = "outside"
            pioli.path_nodes = [(0, 0)] # 直接出門
            
        pioli.state = "WALKING"

    def check_scene_transition(self, pioli, room, corridor, office, basement):
        """
        📌 修正：皮歐里只有在走到特定地圖邊緣（傳送點）時，才會切換場景，絕對不瞬移！
        """
        if not pioli.path_nodes and pioli.current_scene != pioli.target_scene:
            # 當前區域的節點走完了，但還沒到最終目的地，代表他走到了邊緣傳送點
            
            # 1. 如果他在醫療室，準備去辦公室/地下室，走到門口後切換
            if pioli.current_scene == "room":
                if pioli.target_scene == "office":
                    pioli.current_scene = "office"
                    # 設定他出現在辦公室門口的像素座標（請根據你 office 的門口位置微調）
                    pioli.x = office.offset_x + 16 
                    pioli.y = office.offset_y + 160
                    # 補上在辦公室內走向座位的後續路徑
                    pioli.path_nodes = [(office.offset_x + 112, office.offset_y + 64)]
                    
                elif pioli.target_scene == "basement":
                    pioli.current_scene = "basement"
                    # 設定他出現在地下室樓梯口的像素座標
                    pioli.x = basement.offset_x + 48
                    pioli.y = basement.offset_y + 48
                    # 補上在地下室走到特訓位置的路徑
                    pioli.path_nodes = [(basement.offset_x + 272, basement.offset_y + 120)]

            # 2. 如果他在辦公室/地下室，時間到了要回醫療室
            elif pioli.current_scene in ["office", "basement"] and pioli.target_scene == "room":
                pioli.current_scene = "room"
                # 出現在醫療室門口
                pioli.x = room.offset_x + 120
                pioli.y = room.offset_y + 180
                # 補上走向病床的路徑
                pioli.path_nodes = [(room.offset_x + 56, room.offset_y + 106)]

            # 3. 如果是要出門狩獵
            elif pioli.target_scene == "outside":
                pioli.current_scene = "outside"
                pioli.x = 0
                pioli.y = 0

    def get_time_string(self):
        hours = self.current_minutes // 60
        minutes = self.current_minutes % 60
        return f"Day {self.day} - {str(hours).zfill(2)}:{str(minutes).zfill(2)}"
    
    def set_to_six_am(self):
        """
        📌 補回重置功能：強制將時間重置為早上的 08:00 (8 * 60 = 480 分鐘)
        並清空毫秒累積器、更新皮歐里的作息狀態
        """
        self.current_minutes = 480
        self.timer_accumulator = 0
        # 同步更新皮歐里當前的作息狀態標籤
        self.update_priori_schedule()