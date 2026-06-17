# 數值變動字幕提示系統
import pygame

class NotificationSystem:
    def __init__(self):
        self.queue = []           # 等待顯示的訊息佇列
        self.current_message = "" # 目前正在顯示的訊息
        self.is_active = False    # 是否有訊息正在顯示

    def push(self, message):
        """ 將一條新訊息加入佇列尾端 """
        self.queue.append(message)
        if not self.is_active:
            self._show_next()

    def _show_next(self):
        """ 從佇列頭部取出下一條訊息顯示 """
        if self.queue:
            self.current_message = self.queue.pop(0)
            self.is_active = True
        else:
            self.current_message = ""
            self.is_active = False

    def handle_keydown(self, event):
        """ 按下任意鍵時，消除目前訊息並顯示佇列裡的下一條 """
        if self.is_active and event.type == pygame.KEYDOWN:
            self._show_next()
            return True  # 告知 main.py 這個按鍵已被吃掉
        return False

    def draw(self, screen, font):
        if not self.is_active:
            return

        box_width = 360
        box_height = 24
        box_x = (480 - box_width) // 2
        box_y = 240    # 畫面下方中央，避開地圖主視覺與互動提示文字

        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (20, 20, 22), box_rect)
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 1)

        # 訊息文字
        text_surf = font.render(self.current_message, True, (255, 255, 255))
        screen.blit(text_surf, (box_rect.x + 10, box_rect.y + (box_height - text_surf.get_height()) // 2))

