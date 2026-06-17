import pygame
import sys

class MainMenuScreen:
    def __init__(self, width=480, height=270):
        # 配合 480x270 低解析度，縮小並重新配置按鈕範圍
        self.start_btn_rect = pygame.Rect(width // 2 - 50, 140, 100, 25)
        self.help_btn_rect = pygame.Rect(width // 2 - 50, 175, 100, 25)
        self.quit_btn_rect = pygame.Rect(width // 2 - 50, 210, 100, 25)
        self.back_btn_rect = pygame.Rect(20, 230, 50, 20)
        
        # 子狀態："MAIN" 代表主選單，"HELP" 代表看說明
        self.sub_state = "MAIN"

        self.background_image = None
        self.background_image = pygame.image.load("E:\Posterior record\picture/login.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (width, height))

        self.title_font = pygame.font.SysFont("simsun", 36)
    def handle_event(self, event):
        """專門處理登入與說明頁面的點擊事件，返回 'PLAYING' 代表要開始遊戲了"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.sub_state == "MAIN":
                if self.start_btn_rect.collidepoint(mouse_pos):
                    return "PLAYING"  # 通知 main.py 切換到遊戲地圖
                elif self.help_btn_rect.collidepoint(mouse_pos):
                    self.sub_state = "HELP"
                elif self.quit_btn_rect.collidepoint(mouse_pos): 
                    import pygame as pg
                    import sys
                    pg.quit()
                    sys.exit()
 
            elif self.sub_state == "HELP":
                if self.back_btn_rect.collidepoint(mouse_pos):
                    self.sub_state = "MAIN"
        return None

    def draw(self, screen, font):
        """根據目前的子狀態繪製畫面"""
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((15, 15, 20))
        
        if self.sub_state == "MAIN":
            # 1. 繪製遊戲標題 【後驗記錄】
            title_text = self.title_font.render("後驗記錄", True, (230, 230, 250))
            screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 70))
            
            # 2. 繪製 開始遊戲 按鈕
            pygame.draw.rect(screen, (40, 45, 60), self.start_btn_rect, border_radius=3)
            pygame.draw.rect(screen, (100, 100, 120), self.start_btn_rect, 1, border_radius=3)
            start_text = font.render("開始遊戲", True, (255, 255, 255))
            screen.blit(start_text, (screen.get_width() // 2 - start_text.get_width() // 2, 145))
            
            # 3. 繪製 遊戲說明 按鈕
            pygame.draw.rect(screen, (40, 45, 60), self.help_btn_rect, border_radius=3)
            pygame.draw.rect(screen, (100, 100, 120), self.help_btn_rect, 1, border_radius=3)
            help_text = font.render("遊戲說明", True, (255, 255, 255))
            screen.blit(help_text, (screen.get_width() // 2 - help_text.get_width() // 2, 180))

            # 4. 繪製 退出遊戲 按鈕
            pygame.draw.rect(screen, (60, 35, 35), self.quit_btn_rect, border_radius=3)
            pygame.draw.rect(screen, (120, 80, 80), self.quit_btn_rect, 1, border_radius=3)
            quit_text = font.render("退出遊戲", True, (255, 255, 255))
            screen.blit(quit_text, (screen.get_width() // 2 - quit_text.get_width() // 2, 215))
            
        elif self.sub_state == "HELP":
            intro_lines = [
                "【遊戲說明】",
                "WASD：移動角色",
                "E：開啟 / 關閉背包",
                "F：與場景物件互動（開門、睡覺等）",
                "Q：與皮歐里對話",
                "Enter：對話框中送出文字",
                "Esc：關閉對話框 / 背包"
            ]
            for i, line in enumerate(intro_lines):
                text_surf = font.render(line, True, (200, 200, 200))
                screen.blit(text_surf, (30, 50 + i * 25))
                
            # 返回按鈕
            pygame.draw.rect(screen, (60, 60, 60), self.back_btn_rect, border_radius=3)
            back_text = font.render("返回", True, (255, 255, 255))
            screen.blit(back_text, (self.back_btn_rect.x + (self.back_btn_rect.width // 2) - back_text.get_width() // 2, self.back_btn_rect.y + 4))


class EndingScreen:
    def __init__(self):
        self.title = ""
        self.content = ""

    def set_ending(self, title, content):
        """由對話系統觸發結局時，把文案塞進來"""
        self.title = title
        self.content = content

    def handle_event(self, event):
        """結局頁面按下 ESC 關閉遊戲"""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    def wrap_text(self, text, font, max_width):
        """將過長的單行文字依照字體寬度自動換行，回傳斷好行的清單"""
        wrapped_lines = []
        for paragraph in text.split('\n'):
            current_line = ""
            for char in paragraph:
                test_line = current_line + char
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = char
            wrapped_lines.append(current_line)
        return wrapped_lines

    def draw(self, screen, font):
        """繪製全黑沉浸式的結局文字"""
        screen.fill((0, 0, 0)) # 結局全黑背景
        
        # 1. 繪製結局標題（紅色特顯）
        title_text = font.render(self.title, True, (220, 50, 50))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 40))
        
        # 2. 繪製結局詳細文案（支援換行處理）
        lines = self.content.split('\n')
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, (220, 220, 220))
            screen.blit(text_surf, (40, 90 + i * 20))
            
        # 3. 提示關閉
        tip_text = font.render("[ 按下 ESC 鍵結束遊戲 ]", True, (100, 100, 100))
        screen.blit(tip_text, (screen.get_width() // 2 - tip_text.get_width() // 2, 230))