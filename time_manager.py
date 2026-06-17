# 時間與作息系統
import pygame

class TimeManager:
    def __init__(self):
        self.day = 1
        # 📌 一開始進去的第一天直接從早上 08:00 開始 (8 * 60 = 480)
        self.current_minutes = 480  
        self.MINUTES_PER_REAL_SECOND = 1
        self.timer_accumulator = 0
        
        # 皮歐里專屬狀態與權限
        # 📌 關鍵修改：初始狀態設為空字串，確保遊戲第一幀更新 08:00 時，
        # 會因為不等於 "MEDICAL_ROOM_MORNING" 而立刻觸發 plan_pioli_route() 讓 NPC 出現！
        self.priori_schedule_state = ""
        


    def update(self, dt, pioli=None, room=None, corridor=None, office=None, basement=None, is_fading=False):
        # 1. 推進時間 (如果正在黑屏/過渡動畫，就跳過時間推進，防止時間暴衝)
        if not is_fading:
            self.timer_accumulator += dt
            if self.timer_accumulator >= 1000:
                self.timer_accumulator -= 1000
                self.current_minutes += self.MINUTES_PER_REAL_SECOND

            
        # 2. 檢查日程狀態切換
        old_state = self.priori_schedule_state
        self.update_priori_schedule()
        
        # 3. 核心：如果狀態變了，為皮歐里規劃移動路徑（星露谷式）
        if self.priori_schedule_state != old_state and pioli and room:
            self.plan_pioli_route(pioli, room, corridor, office, basement)
            
        # 4. 讓走路中的皮歐里繼續前進
        if pioli and pioli.state == "WALKING":
            # 根據皮歐里目前所在場景，傳對應地圖給他
            current_map = {
                "room": room,
                "office": office,
                "basement": basement
            }.get(pioli.current_scene)
            
            pioli.move_to_target_nodes(dt, tilemap=current_map)
            self.check_scene_transition(pioli, room, corridor, office, basement)

    def update_priori_schedule(self):
        """ 根據精準時間表 """
        m = self.current_minutes
        
        if 450 <= m < 480:     # 07:30 ~ 08:00 (保留給後續天數循環使用)
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
        """ 節點路徑規劃器：根據目的地，把沿途的走廊轉角像素座標塞給皮歐里 """
        rx, ry = room.offset_x, room.offset_y
        ox, oy = office.offset_x, office.offset_y
        bx, by = basement.offset_x, basement.offset_y
        
        if "KITCHEN" in self.priori_schedule_state:
            pioli.target_scene = "room"
            pioli.path_nodes = [(rx + 240, ry + 80)]
            
        elif "MEDICAL_ROOM" in self.priori_schedule_state:
            pioli.target_scene = "room"
            if pioli.current_scene == "office":
                pioli.path_nodes = [(office.offset_x + 16, office.offset_y + 144)]
            elif pioli.current_scene == "basement":
                pioli.path_nodes = [(basement.offset_x + 48, basement.offset_y + 48)]
            else:
                # 從門口 (rx+240, ry+0) 進來，往下走到床旁邊
                pioli.path_nodes = [
                    (rx + 240, ry + 16),   # 門口進入點（上方）
                    (rx + 64,  ry + 80),   # 往左走到床旁邊的 x 軸
                    (rx + 64,  ry + 112),  # 往下走到與圖中相同高度
                ]
                     
        elif "BASEMENT" in self.priori_schedule_state:
            pioli.target_scene = "basement"
            pioli.path_nodes = [(rx + 120, ry + 180), (bx + 272, by + 120)]
            
        elif "OFFICE" in self.priori_schedule_state:
            pioli.target_scene = "office"
            pioli.path_nodes = [(ox + 112, oy + 64)]
            
        elif "HUNTING" in self.priori_schedule_state:
            pioli.target_scene = "outside"
            pioli.current_scene = "outside" 
            pioli.path_nodes = [] 
            pioli.state = "IDLE"
            
        pioli.state = "WALKING"

    def check_scene_transition(self, pioli, room, corridor, office, basement):
        """ 皮歐里只有在走到特定地圖邊緣（傳送點）時，才會切換場景，絕對不瞬移！ """
        if not pioli.path_nodes and pioli.current_scene != pioli.target_scene:
            if pioli.current_scene == "room":
                if pioli.target_scene == "office":
                    pioli.current_scene = "office"
                    pioli.x = office.offset_x + 16 
                    pioli.y = office.offset_y + 160
                    pioli.path_nodes = [(office.offset_x + 112, office.offset_y + 64)]
                    
                elif pioli.target_scene == "basement":
                    pioli.current_scene = "basement"
                    pioli.x = basement.offset_x + 48
                    pioli.y = basement.offset_y + 48
                    pioli.path_nodes = [(basement.offset_x + 272, basement.offset_y + 120)]

            elif pioli.current_scene in ["office", "basement"] and pioli.target_scene == "room":
                pioli.current_scene = "room"
                pioli.x = room.offset_x + 240
                pioli.y = room.offset_y + 16
                pioli.path_nodes = [
                    (room.offset_x + 240, room.offset_y + 32),  # 先往下走一點，脫離門口
                    (room.offset_x + 120,  room.offset_y + 80)  # 往左走到床附近的x軸
                ]

            elif pioli.target_scene == "outside":
                pioli.current_scene = "outside"
                pioli.x = 0
                pioli.y = 0

    def get_time_string(self):
        hours = self.current_minutes // 60
        minutes = self.current_minutes % 60
        return f"Day {self.day} - {str(hours).zfill(2)}:{str(minutes).zfill(2)}"
    
    def set_to_six_am(self, engine=None):
        """
        強制將時間重置為早上的 08:00 (8 * 60 = 480 分鐘)
        並清空毫秒累積器、更新皮歐里的作息狀態，同時將體力補滿
        """
        self.current_minutes = 480
        self.timer_accumulator = 0
        self.update_priori_schedule()
        
        # 📌 配合 main.py 的實體結構與變數名稱安全洗滿體力值 (energy)
        if engine and hasattr(engine, 'game_state'):
            if hasattr(engine.game_state, 'energy'):
                engine.game_state.energy = engine.game_state.max_energy