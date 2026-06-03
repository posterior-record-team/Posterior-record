import pygame

""" 玩家初始的醫療室小房間 (19x12 置中) """
class RoomMap:
    def __init__(self):
        self.tile_size = 16
        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        self.offset_x = (480 - (19 * self.tile_size)) // 2
        self.offset_y = (270 - (12 * self.tile_size)) // 2
        
        door_real_x = 15 * self.tile_size + self.offset_x
        door_real_y = 0 * self.tile_size + self.offset_y
        #判定玩家是否靠近門
        self.door_rect = pygame.Rect(door_real_x, door_real_y, self.tile_size * 2, self.tile_size)

    def draw(self, screen):
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                x = col_idx * self.tile_size + self.offset_x
                y = row_idx * self.tile_size + self.offset_y
                if tile == 1:
                    pygame.draw.rect(screen, (70, 60, 50), (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(screen, (40, 30, 20), (x, y, self.tile_size, self.tile_size), 1)
                elif tile == 2:
                    pygame.draw.rect(screen, (160, 80, 40), (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(screen, (255, 200, 150), (x, y, self.tile_size, self.tile_size), 1)
                elif tile == 0:
                    pygame.draw.rect(screen, (130, 100, 70), (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(screen, (110, 85, 60), (x, y, self.tile_size, self.tile_size), 1)

""" 走廊地圖 (30x12 格) """
class CorridorMap:

    def __init__(self):
        self.tile_size = 16
        # 全螢幕不需偏移量
        self.offset_x = 0
        self.offset_y = 0
        
        # 1=外牆空氣牆, 0=走廊地板
        # 3=皮歐里辦公室(右上), 4=醫療室回頭門(右下)
        # 5=外界大門(最右側中央)
        # 6=通往B1樓梯(左上), 7=廚房(左下)
        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],# Row 0
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1],# Row 1 (辦公室門)
            [1,1,6,6,6,6,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],# Row 2 (樓梯起點)
            [1,1,6,6,6,6,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],# Row 3
            [1,1,6,6,6,6,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],# Row 4
            [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5],# Row 5
            [1,1,7,7,7,7,7,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5],# Row 6
            [1,1,7,7,7,7,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5],# Row 7
            [1,1,7,7,7,7,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],# Row 8
            [1,1,7,7,7,7,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],# Row 9
            [1,1,7,7,7,7,7,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,4,1,1,1],# Row 10 (醫療室門)
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] # Row 11
        ]
        
        # 走廊和地下室如果都是 30x12 格，直接用同一套置中公式：
        self.offset_x = (480 - (len(self.grid[0]) * self.tile_size)) // 2  # 算出來是 0 (左右填滿)
        self.offset_y = (270 - (len(self.grid) * self.tile_size)) // 2  # 算出來是 39 (上下置中)
        
        # 玩家從房間傳送過來時，預設生成的右下角位置 (對齊 4=醫療室門前)
        self.spawn_x = 26 * self.tile_size + self.offset_x
        self.spawn_y = 8 * self.tile_size + self.offset_y

        # 走廊各出入口感應區（加上 offset 確保跟置中後的地圖重合）
        self.office_door_rect = pygame.Rect(25 * self.tile_size + self.offset_x, 1 * self.tile_size + self.offset_y, 32, 16)   # 右上 3 (在Row 1)
        self.room_door_rect = pygame.Rect(25 * self.tile_size + self.offset_x, 10 * self.tile_size + self.offset_y, 32, 16)  # 右下 4 (在Row 10)
        self.stairs_rect = pygame.Rect(2 * self.tile_size + self.offset_x, 2 * self.tile_size + self.offset_y, 80, 48)       # 左上 6 (從Row 2開始)
    def draw(self, screen):
        # 建立臨時字體用來標註門的名字
        font = pygame.font.SysFont("simsun", 10)
        
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                x = col_idx * self.tile_size + self.offset_x
                y = row_idx * self.tile_size + self.offset_y
                
                if tile == 1: # 走廊外牆（鋼筋混凝土灰色）
                    pygame.draw.rect(screen, (50, 55, 60), (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(screen, (30, 35, 40), (x, y, self.tile_size, self.tile_size), 1)
                elif tile == 0: # 走廊地板（冷色調磁磚）
                    pygame.draw.rect(screen, (100, 110, 115), (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(screen, (90, 100, 105), (x, y, self.tile_size, self.tile_size), 1)
                elif tile == 3: # 皮歐里辦公室（紫色門）
                    pygame.draw.rect(screen, (100, 60, 120), (x, y, self.tile_size, self.tile_size))
                elif tile == 4: # 醫療室（亮木門）
                    pygame.draw.rect(screen, (160, 80, 40), (x, y, self.tile_size, self.tile_size))
                elif tile == 5: # 外界大門（鐵捲門色）
                    pygame.draw.rect(screen, (140, 140, 140), (x, y, self.tile_size, self.tile_size))
                elif tile == 6: # 樓梯（深藍色）
                    pygame.draw.rect(screen, (30, 50, 80), (x, y, self.tile_size, self.tile_size))
                elif tile == 7: # 廚房（暗紅色門）
                    pygame.draw.rect(screen, (120, 40, 40), (x, y, self.tile_size, self.tile_size))

""" 皮歐里辦公室 (15x10 置中) """
class OfficeMap:

    def __init__(self):
        self.tile_size = 16
        # 1=牆, 0=地板, 3=回長廊的門
        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,3,3,1,1]
        ]
        self.offset_x = (480 - (15 * self.tile_size)) // 2
        self.offset_y = (270 - (10 * self.tile_size)) // 2
        
        # 辦公室門的感應區 (右下角 3 的位置)
        self.door_rect = pygame.Rect(11 * self.tile_size + self.offset_x, 8 * self.tile_size + self.offset_y, 32, 16)

    def draw(self, screen):
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                x = col_idx * self.tile_size + self.offset_x
                y = row_idx * self.tile_size + self.offset_y
                if tile == 1:
                    pygame.draw.rect(screen, (60, 50, 70), (x, y, self.tile_size, self.tile_size))
                elif tile == 3: # 門
                    pygame.draw.rect(screen, (100, 60, 120), (x, y, self.tile_size, self.tile_size))
                elif tile == 0:
                    pygame.draw.rect(screen, (110, 100, 120), (x, y, self.tile_size, self.tile_size))

""" 地下一樓空間(30x12 格) """
class BasementMap:
    
    def __init__(self):
        self.tile_size = 16
        # 1=牆, 0=地板, 6=回長廊的樓梯(設在左上角 [1][1] 和 [1][2])
        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,1,6,6,6,6,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,6,6,6,6,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,6,6,6,6,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
            [1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        
        # 補上讓 entities.py 認得的置中坐標
        self.offset_x = (480 - (len(self.grid[0]) * self.tile_size)) // 2  # 剛好為 0 填滿寬度
        self.offset_y = (270 - (len(self.grid) * self.tile_size)) // 2  # 負責上下置中

        # 地下室樓梯的感應區 (左上角 6 的位置)
        self.door_rect = pygame.Rect(2 * self.tile_size + self.offset_x, 4 * self.tile_size + self.offset_y, 80, 48) 

    def draw(self, screen):
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                x = col_idx * self.tile_size + self.offset_x
                y = row_idx * self.tile_size + self.offset_y
                if tile == 1:
                    pygame.draw.rect(screen, (40, 45, 50), (x, y, self.tile_size, self.tile_size))
                elif tile == 6: # 樓梯
                    pygame.draw.rect(screen, (30, 50, 80), (x, y, self.tile_size, self.tile_size))
                elif tile == 0:
                    pygame.draw.rect(screen, (70, 75, 80), (x, y, self.tile_size, self.tile_size))        