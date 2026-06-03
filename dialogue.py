#這個沒有用到

import pygame

class DialogueSystem:
    def __init__(self):
        self.is_talking = False          # 是否正在對話中
        self.chat_input_text = ""         # 玩家正在輸入的文字（已確認）
        self.composition_text = ""      # 📌 保留：玩家正在打、尚未選字的黃色注音/組字
        self.npc_response_text = ""       # NPC 回應的文字
        
    def start_dialogue(self, npc_scene):
        self.is_talking = True
        self.chat_input_text = ""
        self.composition_text = ""       # 初始化清空
        pygame.key.start_text_input()     # 開啟打字環境
        


    def end_dialogue(self):
        self.is_talking = False
        self.chat_input_text = ""
        self.composition_text = ""       # 離開時清空
        pygame.key.stop_text_input()

    def handle_backspace(self):
        """ 處理退格鍵 """
        self.chat_input_text = self.chat_input_text[:-1]

    def handle_text_input(self, text):
        """ 處理最終確認的字元 """
        self.chat_input_text += text

    def handle_submit(self, npc_scene):
        if self.chat_input_text.strip() == "":
            return
            
        self.chat_input_text = ""  # 送出後清空
        self.composition_text = "" # 確保清空

    def draw(self, screen, font):
        if not self.is_talking:
            return
            
        # A. 繪製底部對話主框 (深灰色半透明)
        dialog_rect = pygame.Rect(10, 160, 460, 100)
        dialog_bg = pygame.Surface((460, 100), pygame.SRCALPHA)
        dialog_bg.fill((20, 20, 25, 230))
        screen.blit(dialog_bg, (10, 160))
        pygame.draw.rect(screen, (100, 100, 120), dialog_rect, 1)
        
        # B. 渲染 NPC 說的話
        npc_surface = font.render(self.npc_response_text, True, (240, 240, 240))
        screen.blit(npc_surface, (20, 170))
        
        # C. 繪製輸入框
        input_rect = pygame.Rect(20, 225, 440, 25)
        pygame.draw.rect(screen, (5, 5, 5), input_rect)
        pygame.draw.rect(screen, (0, 255, 255), input_rect, 1)
        
        # D. 分段渲染輸入框文字
        # 1. 渲染已確認的文字 (青色)
        confirmed_text = f"> {self.chat_input_text}"
        confirmed_surface = font.render(confirmed_text, True, (0, 255, 255))
        screen.blit(confirmed_surface, (25, 230))
        
        # 2. 計算黃色字要接著渲染的 X 軸起點
        current_x = 25 + confirmed_surface.get_width()
        
        # 3. 📌 渲染正在打的注音/組字 (亮黃色 + 黃色底線)
        if self.composition_text:
            comp_surface = font.render(self.composition_text, True, (255, 215, 0)) 
            screen.blit(comp_surface, (current_x, 230))
            
            # 畫一條簡單的底線，提示玩家此字尚未按 Enter 確認
            comp_width = comp_surface.get_width()
            pygame.draw.line(screen, (255, 215, 0), (current_x, 248), (current_x + comp_width, 248), 1)
        
        # E. 右下角小提示 
        hint_surface = font.render("[Enter]送出 [Esc]離開", True, (120, 120, 120))
        screen.blit(hint_surface, (340, 205))