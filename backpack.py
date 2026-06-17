# 背包

import pygame

class BackpackSystem:
    def __init__(self):
        # 將原本在 main.py 的背包變數搬過來
        self.is_open = False
        self.current_tab = 0
        self.tabs = ["狀態", "術法",  "離開"]

    def toggle(self):
        """切換背包開關"""
        self.is_open = not self.is_open

    def handle_input(self, event):
        """專門處理背包開啟時的左右切換按鍵"""
        if self.is_open and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.current_tab = (self.current_tab + 1) % len(self.tabs)
            elif event.key == pygame.K_LEFT:
                self.current_tab = (self.current_tab - 1) % len(self.tabs)

    def draw(self, screen, game_state):
        """負責畫出背包畫面"""
        # 建立一個跟 main.py 一樣絕對安全的細明體，用來畫背包文字
        font = pygame.font.SysFont("simsun", 12)
        game_width, game_height = 480, 270

        if not self.is_open:
            return

        # 1. 畫出背包主面板背景
        menu_width = 360
        menu_height = 200
        menu_x = (game_width - menu_width) // 2
        menu_y = (game_height - menu_height) // 2
        
        pygame.draw.rect(screen, (30, 30, 35), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (255, 255, 255), (menu_x, menu_y, menu_width, menu_height), 1)
        
        # 2. 畫出多分頁標籤
        tab_width = menu_width // len(self.tabs)
        for i, tab_name in enumerate(self.tabs):
            tab_x = menu_x + (i * tab_width)
            color = (255, 255, 0) if i == self.current_tab else (150, 150, 150)
            tab_surface = font.render(tab_name, False, color)
            screen.blit(tab_surface, (tab_x + (tab_width - tab_surface.get_width()) // 2, menu_y + 5))
        
        # 3. 分隔線
        pygame.draw.line(screen, (100, 100, 100), (menu_x, menu_y + 25), (menu_x + menu_width, menu_y + 25), 1)
        
        # 4. 顯示全域資訊（從傳進來的 game_state 讀取）
        #karma_text = f"善惡值 (Karma): {game_state.karma}"
        #karma_surface = font.render(karma_text, False, (200, 200, 200))
        #screen.blit(karma_surface, (menu_x + 15, menu_y + 35))
        

        if self.current_tab == 0:
            
            # 📌 善惡值單獨繪製在物品欄的下方
            karma_text = f"善惡值: {game_state.karma}"
            karma_surf = font.render(karma_text, True, (255, 255, 255))
            screen.blit(karma_surf, (100, 80))

             # 2.. 好感度 (favorability) - 稍微偏橘紅色的字體，代表警戒
            favorability_text = f"好感度: {game_state.favorability}"
            favorability_surf = font.render(favorability_text, True, (231, 136, 221))
            screen.blit(favorability_surf, (280, 80))

            # 3. 精神污染度 (Corruption) - 稍微偏紫紅色的字體，增加氛圍感
            corruption_text = f"精神污染度: {game_state.corruption}"
            corruption_surf = font.render(corruption_text, True, (240, 128, 128))
            screen.blit(corruption_surf, (100, 120))
            
            # 4. 警戒值 (Suspicion) - 稍微偏橘紅色的字體，代表警戒
            suspicion_text = f"警戒值: {game_state.suspicion}"
            suspicion_surf = font.render(suspicion_text, True, (255, 140, 0))
            screen.blit(suspicion_surf, (280, 120))

            


        # 1 代表「術法」分頁  
        if self.current_tab == 1:
            heal_level = game_state.get_magic_level("heal")
            attack_level = game_state.get_magic_level("attack")
            thief_level = game_state.get_magic_level("thief")

            heal_surf = font.render(f"治療魔法 等級: {heal_level}", True, (255, 255, 255))
            attack_surf = font.render(f"攻擊魔法 等級: {attack_level}", True, (255, 255, 255))
            thief_surf = font.render(f"盜賊魔法 等級: {thief_level}", True, (255, 255, 255))

            screen.blit(heal_surf, (80, 80))
            screen.blit(attack_surf, (240, 80))
            screen.blit(thief_surf, (80, 100))

        # 4 代表「離開」分頁   
        if self.current_tab == 2:  # 4 代表「離開」分頁
            confirm_surface = font.render("👉 按下 [ Enter ] 鍵確定離開遊戲", False, (255, 255, 255))

            screen.blit(confirm_surface, (menu_x + 15, menu_y + 110))

        # 提示字
        hint_surface = font.render("按 ← / → 切換分頁 | 按 E 關閉", False, (100, 100, 100))
        screen.blit(hint_surface, (menu_x + 15, menu_y + menu_height - 20))