# 角色與物件模組tilemap

import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 32
        self.speed = 50

        self.facing = "down"  # "up", "down", "left", "right"
        self.images = {}      # 之後填入: {"up": Surface, "down": Surface, "left": Surface, "right": Surface}
        self._load_images()

    def _load_images(self):
        """ 圖片載入位置，圖檔準備好後取消註解並填入正確路徑 """
        try:
            # 📌 先讀取原始圖片
            raw_up = pygame.image.load("picture/player_up.png").convert_alpha()
            raw_down = pygame.image.load("picture/player_down.png").convert_alpha()
            raw_left = pygame.image.load("picture/player_left.png").convert_alpha()
            raw_right = pygame.image.load("picture/player_right.png").convert_alpha()

        # 📌 縮放成角色格子大小（16x32），存入 images 字典
            self.images["up"] = pygame.transform.scale(raw_up, (self.width, self.height))
            self.images["down"] = pygame.transform.scale(raw_down, (self.width, self.height))
            self.images["left"] = pygame.transform.scale(raw_left, (self.width, self.height))
            self.images["right"] = pygame.transform.scale(raw_right, (self.width, self.height))
        except Exception as e:    
            print(f"【圖片載入失敗】{e}")
       

    def get_rect(self, next_x, next_y):
        """根據傳入的位置，回傳該位置的 Pygame Rect 物件（用於碰撞計算）"""
        return pygame.Rect(int(next_x), int(next_y), self.width, self.height)

    def check_collision(self, rect, tilemap, extra_obstacles=None):
        """
        檢查傳入的矩形是否與牆壁或障礙物相交。
        優先檢查外部傳入的 extra_obstacles，
        其次檢查掛在 self 上的 current_obstacles，
        最後才跑地圖網格。
        """
        # 1. 檢查外部傳入的障礙物（呼叫時直接帶入）
        if extra_obstacles:
            for obstacle_rect in extra_obstacles:
                if obstacle_rect and rect.colliderect(obstacle_rect):
                    return True

        # 2. 檢查動態掛載在 self 上的障礙物（main.py 在每幀更新時塞入）
        if hasattr(self, 'current_obstacles') and self.current_obstacles:
            for obstacle_rect in self.current_obstacles:
                if obstacle_rect and rect.colliderect(obstacle_rect):
                    return True

        # 3. 地圖網格牆壁檢查
        for row_idx, row in enumerate(tilemap.grid):
            for col_idx, tile in enumerate(row):
                if tile in [1, 2, 3, 4, 5]:
                    wall_x = col_idx * tilemap.tile_size + tilemap.offset_x
                    wall_y = row_idx * tilemap.tile_size + tilemap.offset_y
                    wall_rect = pygame.Rect(wall_x, wall_y, tilemap.tile_size, tilemap.tile_size)
                    if rect.colliderect(wall_rect):
                        return True
        return False

    def handle_movement(self, dt, tilemap):
        """偵測移動，並加上雙軸分離的碰撞偵測（維持原本的 3 個參數，不改動結構）"""
        keys = pygame.key.get_pressed()
        move_amount = self.speed * (dt / 1000.0)
        
        dx = 0
        dy = 0
        
        if keys[pygame.K_a]: 
            dx -= move_amount
            self.facing = "left"
        if keys[pygame.K_d]: 
            dx += move_amount
            self.facing = "right"
        if keys[pygame.K_w]: 
            dy -= move_amount
            self.facing = "up"
        if keys[pygame.K_s]: 
            dy += move_amount
            self.facing = "down"

        # --- X 軸移動與碰撞偵測 ---
        new_x = self.x + dx
        player_rect_x = self.get_rect(new_x, self.y)
        if not self.check_collision(player_rect_x, tilemap):
            self.x = new_x 
            
        # --- Y 軸移動與碰撞偵測 ---
        new_y = self.y + dy
        player_rect_y = self.get_rect(self.x, new_y)
        if not self.check_collision(player_rect_y, tilemap):
            self.y = new_y
    def draw(self, screen):
        # 📌 如果該方向有圖片就用圖片，否則用色塊頂著
        img = self.images.get(self.facing)
        if img:
            screen.blit(img, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(screen, (0, 255, 200), (int(self.x), int(self.y), self.width, self.height))



class NPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16   
        self.height = 32  
        self.color = (215, 195, 157)  
        self.speed = 40               
        

        self.current_scene = "office" # 初始場景
        self.state = "IDLE"           # "IDLE" (站立) 或 "WALKING" (走路中)
        self.path_nodes = []          # 接下來要走的節點列表 [(x1, y1), (x2, y2)...]
        self.target_scene = None      # 最終目的地的場景

        self.facing = "down"
        self.images = {}
        self._load_images()

    def _load_images(self):
        """ 圖片載入位置 """
        try:
            raw_up = pygame.image.load("picture/pioli_up.png").convert_alpha()
            raw_down = pygame.image.load("picture/pioli_down.png").convert_alpha()
            raw_left = pygame.image.load("picture/pioli_left.png").convert_alpha()
            raw_right = pygame.image.load("picture/pioli_right.png").convert_alpha()

            # 📌 縮放成角色格子大小（16x32）
            self.images["up"] = pygame.transform.scale(raw_up, (self.width, self.height))
            self.images["down"] = pygame.transform.scale(raw_down, (self.width, self.height))
            self.images["left"] = pygame.transform.scale(raw_left, (self.width, self.height))
            self.images["right"] = pygame.transform.scale(raw_right, (self.width, self.height))
        except Exception as e:
            print(f"【圖片載入失敗】{e}")
       

    def move_to_target_nodes(self, dt, tilemap=None):
        """ 讓皮歐里順暢地往節點走去，不瞬移 """
        if not self.path_nodes:
            self.state = "IDLE"
            return

        target_x, target_y = self.path_nodes[0]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx**2 + dy**2) ** 0.5

        step = self.speed * (dt / 1000.0)

        # 📌 根據移動向量判斷面向（取較大的軸向）
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"

        if distance <= step:
            self.x = target_x
            self.y = target_y
            self.path_nodes.pop(0)
        else:
            self.x += (dx / distance) * step
            self.y += (dy / distance) * step
            self.state = "WALKING"

    def draw(self, screen):
        # 📌 如果有對應方向圖片就用圖片
        img = self.images.get(self.facing)
        if img:
            screen.blit(img, (int(self.x), int(self.y)))
            return

        # 否則維持原本的色塊手繪外觀
        x, y = int(self.x), int(self.y)
        w, h = self.width, self.height

        pygame.draw.rect(screen, self.color, (x, y + 2, w, 10))
        pygame.draw.rect(screen, (255, 220, 0), (x, y, w, 3))
        pygame.draw.rect(screen, (255, 220, 0), (x, y, 2, 8))
        pygame.draw.rect(screen, (255, 220, 0), (x + w - 2, y, 2, 8))
        pygame.draw.rect(screen, (70, 130, 220), (x + 4, y + 5, 2, 2))
        pygame.draw.rect(screen, (70, 130, 220), (x + 10, y + 5, 2, 2))
        pygame.draw.rect(screen, (255, 220, 0), (x + 3, y + 9, 10, 2))
        pygame.draw.rect(screen, (60, 160, 60), (x, y + 12, w, 12))
        pygame.draw.rect(screen, (30, 30, 30), (x, y + 24, w, 8))
        


class Bed:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48
        self.height = 64
        self.color = (100, 149, 237)  # 矢車菊藍（代表床的顏色）

    def draw(self, screen):
        # 畫出床的範圍
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.width, self.height))
        # 畫個小枕頭區分頭尾
        pygame.draw.rect(screen, (240, 240, 240), (int(self.x) + 4, int(self.y) + 4, 24, 10))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)


class Table:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48
        self.height = 32
        self.color = (139, 69, 19)  # 馬鞍棕色（木頭桌）

    def draw(self, screen):
        # 畫出桌子
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.width, self.height))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)