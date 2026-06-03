# 角色與物件模組tilemap

import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 32
        self.speed = 50

    def get_rect(self, next_x, next_y):
        """根據傳入的位置，回傳該位置的 Pygame Rect 物件（用於碰撞計算）"""
        return pygame.Rect(int(next_x), int(next_y), self.width, self.height)

    def check_collision(self, rect, tilemap, extra_obstacles=None):
        """
        檢查傳入的矩形是否與地圖上的牆壁，或是額外的實體障礙物相交
        extra_obstacles: 傳入一個 Rect 清單，例如 [self.table.get_rect()]
        """
        # 1. 檢查額外實體障礙物（例如桌子）
        if extra_obstacles:
            for obstacle_rect in extra_obstacles:
                if obstacle_rect and rect.colliderect(obstacle_rect):
                    return True

        # 2. 原本的地圖網格牆壁檢查
        for row_idx, row in enumerate(tilemap.grid):
            for col_idx, tile in enumerate(row):
                if tile in [1, 2, 3, 4, 5]: # 如果是牆壁
                    # 計算該牆壁在螢幕上的實際 Rect
                    wall_x = col_idx * tilemap.tile_size + tilemap.offset_x
                    wall_y = row_idx * tilemap.tile_size + tilemap.offset_y
                    wall_rect = pygame.Rect(wall_x, wall_y, tilemap.tile_size, tilemap.tile_size)
                    
                    # 只要相交就代表撞牆
                    if rect.colliderect(wall_rect):
                        return True
        return False

    def check_collision(self, rect, tilemap):
        """檢查傳入的矩形是否與地圖上的牆壁（1）相交，並一併檢查動態附加的障礙物"""
        
        # 📌 終極防呆：直接檢查 self 身上有沒有被塞入額外障礙物清單
        if hasattr(self, 'current_obstacles') and self.current_obstacles:
            for obstacle_rect in self.current_obstacles:
                if obstacle_rect and rect.colliderect(obstacle_rect):
                    return True

        # 原本的地圖網格牆壁檢查
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
        
        if keys[pygame.K_a]: dx -= move_amount
        if keys[pygame.K_d]: dx += move_amount
        if keys[pygame.K_w]: dy -= move_amount
        if keys[pygame.K_s]: dy += move_amount

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
        # 角色暫代：改用亮青色長方形，在木地板上比較顯眼
        pygame.draw.rect(screen, (0, 255, 200), (int(self.x), int(self.y), self.width, self.height))



class NPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16   
        self.height = 32  
        self.color = (215, 195, 157)  # 黃色皮歐里
        self.speed = 40               # 📌 皮歐里的走路速度（可自行調整）
        
        # 📌 新增：星露谷式移動需要的變數
        self.current_scene = "office" # 初始場景
        self.state = "IDLE"           # "IDLE" (站立) 或 "WALKING" (走路中)
        self.path_nodes = []          # 接下來要走的節點列表 [(x1, y1), (x2, y2)...]
        self.target_scene = None      # 最終目的地的場景

    def move_to_target_nodes(self, dt):
        """ 📌 讓皮歐里順暢地往節點走去，不瞬移 """
        if not self.path_nodes:
            self.state = "IDLE"
            return

        target_x, target_y = self.path_nodes[0]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx**2 + dy**2) ** 0.5

        # 計算這一幀能走的距離
        step = self.speed * (dt / 1000.0)

        if distance <= step:
            # 已經非常接近節點了，直接精準踩上，並移除該節點
            self.x = target_x
            self.y = target_y
            self.path_nodes.pop(0)
        else:
            # 向量移動
            self.x += (dx / distance) * step
            self.y += (dy / distance) * step
            self.state = "WALKING"

    def draw(self, screen):
        # 原本的繪製程式碼不變
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (int(self.x) + 3, int(self.y) + 4, 2, 2))
        pygame.draw.rect(screen, (0, 0, 0), (int(self.x) + 11, int(self.y) + 4, 2, 2))

class Bed:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
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