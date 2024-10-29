import pygame as pg
import os
import random
import math
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

# 初期設定
pg.init()

# 画面サイズ
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("にゃんこ大戦争風ゲーム")

# カラー定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255,0,0)

# キャラクターの基底クラス
class Character:
    def __init__(self, x, y, health, attack_power, image_path=None, image_color=None):
        if image_path:  # 画像が指定されている場合は画像を使う
            self.image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.image, (50, 50))
        else:  # 画像が指定されていない場合は色で塗る
            self.image = pg.Surface((50, 50))
            self.image.fill(image_color)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = health
        self.attack_power = attack_power
        self.moving = True


    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 味方のクラス
class Normal(Character):
    def __init__(self, y):
        super().__init__(150, y, health=100, attack_power=10, image_path="fig/AUNZ4365.JPG")

    def move(self):
        if self.moving:
            self.rect.x += 2  # 移動速度

class Strong(Character):
    def __init__(self, y):
        super().__init__(150, y, health=200, attack_power=20, image_path="fig/IMG_E0591.JPG")

    def move(self):
        if self.moving:
            self.rect.x += 2

# 防御力が高いキャットクラス
class Health(Character):
    def __init__(self, y):
        super().__init__(150, y, health=300, attack_power=5, image_path="fig/IMG_9345.JPG")

    def move(self):
        if self.moving:
            self.rect.x += 2

# 敵のクラス
class Enemy(Character):
    def __init__(self, y):
        super().__init__(WIDTH - 100, y, health=100, attack_power=5, image_color=(204, 204, 255))

    def move(self):
        self.rect.x -= 5  # 移動速度

# 城のクラス
class Castle:
    def __init__(self, x, y, health):
        self.image = pg.Surface((100, 100))
        self.image.fill((150, 75, 0))  # 茶色の城
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = health

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Beam:
    def __init__(self, castle: Castle):
        self.img = pg.image.load("fig/beam.png")  # ビームSurface
        self.rct = self.img.get_rect()  # ビームSurfaceのRectを抽出
        self.rct.centery = castle.rect.centery  # 城の中心縦座標をビームの縦座標
        self.rct.left = castle.rect.right  # 城の右座標をビームの左座標
        self.vx, self.vy = 5, 0

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

# バトル関数
def battle(cat, enemy):
    while cat.health > 0 and enemy.health > 0:
        enemy.health -= cat.attack_power
        if enemy.health > 0:
            cat.health -= enemy.attack_power
    return cat.health > 0  # Trueならキャットが勝った

# ゲームのメインループ
def main():
    clock = pg.time.Clock()
    cat_list = []
    enemy_list = []
    money = 1000  # 最初のお金
    spawn_timer = 0
    beams = []
    selected_cat_type = Normal
    cat_castle = Castle(50, HEIGHT // 2 - 50, health=1000)  # 味方の城
    enemy_castle = Castle(WIDTH - 150, HEIGHT // 2 - 50, health=1000)  # 敵の城

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            # キャットを召喚
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    selected_cat_type = Normal
                    y_position = HEIGHT // 2
                    cat_list.append(selected_cat_type(y_position))
                    money -= 10
                elif event.key == pg.K_2:
                    selected_cat_type = Strong
                    y_position = HEIGHT // 2
                    cat_list.append(selected_cat_type(y_position))
                    money -= 50
                elif event.key == pg.K_3:
                    selected_cat_type = Health
                    y_position = HEIGHT // 2
                    cat_list.append(selected_cat_type(y_position))
                    money -= 100
                #if event.key == pg.K_SPACE and money >= 100:
                    #y_position = HEIGHT // 2
                    #cat_list.append(selected_cat_type(y_position))
                    #money -= 100
                if event.key == pg.K_q:
                    beams.append(Beam(cat_castle))

        # 敵の出現
        spawn_timer += 1
        if spawn_timer >= 60:
            enemy_list.append(Enemy(HEIGHT // 2))  # 中央のy座標に設定
            spawn_timer = 0

        # 移動とバトル処理
        for cat in cat_list:
            cat.move()

        for enemy in enemy_list:
            enemy.move()
            if enemy.rect.x < 0:
                enemy_list.remove(enemy)

            # バトル発生
            for cat in cat_list:
                if cat.rect.colliderect(enemy.rect):
                    cat.moving = False
                    enemy_list.remove(enemy)
                    if battle(cat, enemy):
                        money += 50
                        cat.moving = True
                    else:
                        cat_list.remove(cat)

        # 敵が自城を攻撃する処理
        for enemy in enemy_list:
            if enemy.rect.colliderect(cat_castle.rect):
                cat_castle.health -= enemy.attack_power
                enemy_list.remove(enemy)

        # 城の攻撃処理
        for cat in cat_list:
            if cat.rect.colliderect(enemy_castle.rect):
                enemy_castle.health -= cat.attack_power
                cat_list.remove(cat)

        # 描画
        screen.fill(WHITE)
        cat_castle.draw(screen)
        enemy_castle.draw(screen)

        for cat in cat_list:
            cat.draw(screen)
        for enemy in enemy_list:
            enemy.draw(screen)

        # 資源を表示
        font = pg.font.Font(None, 36)
        money_text = font.render(f"Money: {money}", True, BLACK)
        screen.blit(money_text, (10, 10))
        selected_text = font.render(f"Selected: {selected_cat_type.__name__}", True, RED)
        screen.blit(selected_text, (400, 10))

        # HPを表示
        castle_hp_text = font.render(f"My Castle HP: {cat_castle.health}", True, BLACK)
        screen.blit(castle_hp_text, (10, 40))
        enemy_castle_hp_text = font.render(f"Enemy Castle HP: {enemy_castle.health}", True, BLACK)
        screen.blit(enemy_castle_hp_text, (10, 70))

        for i, cat in enumerate(cat_list):
            hp_text = font.render(f"Caractor {i + 1} HP: {cat.health}", True, BLACK)
            screen.blit(hp_text, (10, 100 + i * 30))

        for i, enemy in enumerate(enemy_list):
            hp_text = font.render(f"Enemy {i + 1} HP: {enemy.health}", True, BLACK)
            screen.blit(hp_text, (WIDTH - 150, 100 + i * 30))

        for beam in beams:
            if not check_bound(beam.rct)[0]:
                beams.remove(beam)
            else:
                beam.update(screen)

        # ゲーム終了条件
        if cat_castle.health <= 0 or enemy_castle.health <= 0:
            running = False  # ゲーム終了

        pg.display.flip()
        clock.tick(60)

    pg.quit()

if __name__ == "__main__":
    main()

