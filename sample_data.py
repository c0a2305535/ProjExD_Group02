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

# 背景画像の読み込み
background = pg.image.load("fig/background.png")  # 背景画像を読み込み
background = pg.transform.scale(background, (WIDTH, HEIGHT))  # スケーリング
# カラー定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255,0,0)

# フォント設定
font = pg.font.Font(None, 74)
small_font = pg.font.Font(None, 36)

# スタート画面の表示関数
def start_screen():
    start_background = pg.image.load("fig/start_background.png")  # スタート画面用の背景画像を読み込み
    start_background = pg.transform.scale(start_background, (WIDTH, HEIGHT))  # スケーリング
    screen.blit(start_background, (0, 0))  # 背景を描画

    title_text = font.render("Cat Battle Game", True, BLACK)
    start_text = small_font.render("Press Enter to Start", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
    pg.display.flip()

# キャラクターの基底クラス
class Character:
    #def __init__(self, x, y, health, attack_power, image_color):
        #self.image = pg.Surface((50, 50))  # 正方形のキャラクター
        #self.image.fill(image_color)  # 指定された色
        #self.rect = self.image.get_rect(center=(x, y))
    def __init__(self, x, y, health, attack_power, image_path=None, image_color=None):
        if image_path:  # 画像が指定されている場合は画像を使う
            self.image = image_path
        else:  # 画像が指定されていない場合は色で塗る
            self.image = pg.Surface((50, 50))
            self.image.fill(image_color)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health
        self.attack_power = attack_power
        self.moving = True


    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 味方のクラス
class Normal(Character):
    def __init__(self, y,gazou):
        super().__init__(90, y, health=100, attack_power=10, image_color=(255, 204, 204))
        self.moving = True  # 移動中かどうかを管理
        super().__init__(150, y, health=100, attack_power=10, image_path=gazou)

    def move(self):
        if self.moving:
            self.rect.x += 2  # 移動速度

class Strong(Character):
    def __init__(self, y,gazou):
        super().__init__(150, y, health=200, attack_power=20, image_path=gazou)

    def move(self):
        if self.moving:
            self.rect.x += 2

# 防御力が高いキャットクラス
class Health(Character):
    def __init__(self, y,gazou):
        super().__init__(150, y, health=300, attack_power=5, image_path=gazou)

    def move(self):
        if self.moving:
            self.rect.x += 2

# 敵のクラス
class Enemy(Character):
    def __init__(self, y):
        super().__init__(WIDTH - 90, y, health=100, attack_power=5, image_color=(204, 204, 255))

    def move(self):
        self.rect.x -= 5  # 移動速度

# 城のクラス
class Castle:
    def __init__(self, x, y, health, is_enemy):
        if is_enemy :
            self.image = pg.image.load("fig/Eiffel_tower.png")
        else:
            self.image = pg.image.load("fig/landmark_sapporo_terebitou.png")
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = health

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    ct = 100
    def __init__(self, castle: Castle):
        self.img = pg.image.load("fig/beam.png")  # ビームSurface
        self.rct = self.img.get_rect()  # ビームSurfaceのRectを抽出
        self.rct.centery = castle.rect.centery  # 城の中心縦座標をビームの縦座標
        self.rct.left = castle.rect.right  # 城の右座標をビームの左座標
        self.vx, self.vy = 5, 0
        

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct) 

    


        screen.blit(self.img, self.rct)

# バトル関数
def battle(cat, enemy):
    while cat.health > 0 and enemy.health > 0:
        enemy.health -= cat.attack_power
        if enemy.health > 0:
            cat.health -= enemy.attack_power
    return cat.health > 0  # Trueならキャットが勝った

# 終了画面表示用関数
def end_screen(message):
    end_background = pg.image.load("fig/end_background.png")  # 終了画面用の背景画像を読み込み
    end_background = pg.transform.scale(end_background, (WIDTH, HEIGHT))  # スケーリング
    screen.blit(end_background, (0, 0))  # 背景を描画

    end_text = font.render(message, True, BLACK)
    screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - end_text.get_height() // 2))
    pg.display.flip()
    pg.time.wait(3000)  # 3秒間表示


# ゲームのメインループ
def main():
    pg.init()  # Pygameの初期化
    pg.mixer.init()  # ミキサーの初期化
    pg.mixer.music.load("fig/battle_music.wav")  # 音楽ファイルの読み込み
    pg.mixer.music.play(-1)  # 音楽をループ再生
    clock = pg.time.Clock()
    cat_list = []
    enemy_list = []
    money = 1000  # 最初のお金
    spawn_timer = 0
    beams = []
    y_position = HEIGHT // 2
    # 城の設定
    cat_castle = Castle(0, HEIGHT // 2 - 50, 1000, False)  # 味方の城
    enemy_castle = Castle(WIDTH - 180, HEIGHT // 2 - 50, 1000, True)  # 敵の城
    selected_cat_type = Normal
    #cat_castle = Castle(50, HEIGHT // 2 - 50, health=1000)  # 味方の城
    #enemy_castle = Castle(WIDTH - 150, HEIGHT // 2 - 50, health=1000)  # 敵の城

    running = True
    tmr = 0
    imag_name = ["fig/AUNZ4365.JPG","fig/IMG_E0591.JPG","fig/IMG_9345.JPG"]
    caractor_imgs = []
    for i in imag_name:
        caractor_imgs.append(pg.transform.scale(pg.image.load(i).convert_alpha(), (50, 50)))
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
    
            # キャットを召喚
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    cat_list.append(Normal(y_position,caractor_imgs[0]))
                    money -= 10
                elif event.key == pg.K_2:
                    cat_list.append(Strong(y_position,caractor_imgs[1]))
                    money -= 50
                elif event.key == pg.K_3:
                    cat_list.append(Health(y_position,caractor_imgs[2]))
                    money -= 100
                
                if event.key == pg.K_q and Beam.ct == 0:
                    beams.append(Beam(cat_castle))
                    Beam.ct = 100

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
                break

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
        screen.blit(background, (0, 0))  # 背景を描画
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
        if tmr % 60 == 0 and Beam.ct > 0:
            Beam.ct -= 1
        

        # ゲーム終了条件
        if cat_castle.health <= 0:
            end_screen("Lose..")
            running = False  # ゲーム終了
        elif enemy_castle.health <= 0:
            end_screen("Win!!")
            running = False #ゲーム終了

        pg.display.flip()
        clock.tick(60)
        tmr += 1

    pg.quit()

if __name__ == "__main__":
    game_active = False  # ゲームが開始されているかどうか

    # スタート画面のループ
    while not game_active:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    game_active = True  # Enterキーでゲーム開始
        # スタート画面を表示
        start_screen()

    # メインゲームの開始
    main()
    pg.quit()


