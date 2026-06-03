# 資料庫與數值追蹤


class GameState:
    def __init__(self):
        # 1. 玩家生理數值 
        
        # 📌 1. 生命值相關 (對應畫面上的 H 條)
        self.health = 100          # 當前生命值 (剛剛報錯就是因為 main.py 找不到這個變數)
        self.max_health = 100      # 最大生命值上限
        
        # 📌 2. 體力值相關 (對應畫面上的 E 條)
        self.energy = 100          # 當前體力值
        self.max_energy = 100      # 最大體力值上限
        # 魔法經驗值
        self.magic_exp_heal = 0       # 治療經驗
        self.magic_exp_attack = 0     # 攻擊經驗
        self.magic_exp_thief = 0      # 盜賊(開鎖)經驗
        
        self.current_tab = 0          # 背包目前分頁：0=道具, 1=術法, 2=檔案
        
        # 2. 皮歐里的關係數值 (先占位)
        self.priori_trust = 20  # 信任值（決定對話語氣與結局走向）
        
        # 3. 背包與其他系統占位（之後會對接到背包系統）
        self.inventory = []     # 物品欄
        
        self.karma = 0          # 善惡值
        self.corruption = 0      # 精神污染度 (0 ~ 100)
        self.suspicion = 0       # 警戒值 (0 ~ 100)
        self.favorability=0     #好感度
 