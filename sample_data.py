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
background_image = pg.image.load("fig/pg_bg.jpg")
background_image = pg.transform.scale(background_image, (WIDTH, HEIGHT))  # 画面サイズに合わせてリサイズ

# カラー定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# キャラクターの基底クラス
class Character:
    def __init__(self, x, y, health, attack_power, image_path: str, size=(70, 70)):
        self.image = pg.image.load(image_path)  # 画像を読み込む
        self.image = pg.transform.scale(self.image, size)  # 画像をリサイズ
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = health
        self.attack_power = attack_power

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 味方のクラス
class Cat(Character):
    def __init__(self, y):
        super().__init__(150, y, health=100, attack_power=10, image_path="fig/2.png")
        self.moving = True  # 移動中かどうかを管理

    def move(self):
        if self.moving:
            self.rect.x += 2  # 移動速度


# 敵クラスの派生（3種類）
class FastEnemy(Character):
    def __init__(self, y):
        super().__init__(WIDTH - 100, y, health=50, attack_power=5, image_path="fig/speed.jpg", size=(125, 65))
        self.image.set_colorkey((255, 255, 255))  # 白い部分を透過

    def move(self):
        self.rect.x -= 7  # 高速移動

class TankEnemy(Character):
    def __init__(self, y):
        super().__init__(WIDTH - 100, y, health=200, attack_power=10, image_path="fig/tank.jpg", size=(140, 140))
        self.image.set_colorkey((255, 255, 255))  # 白い部分を透過

    def move(self):
        self.rect.x -= 2  # 遅いが耐久力が高い

class BalancedEnemy(Character):
    def __init__(self, y):
        super().__init__(WIDTH - 100, y, health=100, attack_power=8, image_path="fig/balance.jpg", size=(80, 100))
        self.image.set_colorkey((255, 255, 255))  # 白い部分を透過

    def move(self):
        self.rect.x -= 4  # バランス型

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
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self,castle:Castle):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load("fig/beam.png")  # ビームSurface
        self.rct = self.img.get_rect()  # ビームSurfaceのRectを抽出
        self.rct.centery = castle.rect.centery  # こうかとんの中心縦座標をビームの縦座標
        self.rct.left = castle.rect.right  # こうかとんの右座標をビームの左座標
        self.vx, self.vy = 5, 0
        self.hit_targets = []

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """

        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)  


class Explosion:
    def __init__(self, x, y):
        self.image = pg.image.load("fig/explosion.gif")  # 爆発エフェクトの画像を読み込み
        self.image = pg.transform.scale(self.image, (100, 100))  # サイズを調整（必要に応じて）
        self.rect = self.image.get_rect(center=(x, y))  # 爆発エフェクトの位置を設定
        self.lifetime = 30  # 表示フレーム数

    def update(self):
        self.lifetime -= 1  # フレーム数を減らす

    def draw(self, surface):
        surface.blit(self.image, self.rect)  # エフェクトを描画


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
    explosions = []
    money = 1000  # 最初のお金
    spawn_timer = 0
    beams = []
    # 城の設定
    cat_castle = Castle(50, HEIGHT // 2 - 50, health=1000)  # 味方の城
    enemy_castle = Castle(WIDTH - 150, HEIGHT // 2 - 50, health=1000)  # 敵の城

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            # キャットを召喚
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and money >= 100:  # スペースキーで召喚
                    y_position = HEIGHT // 2  # 中央のy座標に設定
                    cat_list.append(Cat(y_position))
                    money -= 100  
                if event.key == pg.K_q:
                    beams.append(Beam(cat_castle))

        # 敵の出現
        spawn_timer += 1
        if spawn_timer >= 60:  # 1秒ごとに敵を生成
            enemy_type = random.choice([FastEnemy, TankEnemy, BalancedEnemy])
            enemy_list.append(enemy_type(HEIGHT // 2))
            spawn_timer = 0

        # 移動とバトル処理
        for cat in cat_list:
            cat.move()

        for enemy in enemy_list:
            enemy.move()
            if enemy.rect.x < 0:  # 画面外に出たら削除
                enemy_list.remove(enemy)

            # バトル発生
            for cat in cat_list:
                if cat.rect.colliderect(enemy.rect):  # 衝突判定
                    cat.moving = False  # 移動を止める
                    enemy.moving = False
                    if battle(cat, enemy):
                        enemy_list.remove(enemy) # バトル後に敵を削除
                        money += 50  # 勝ったらお金が増える
                        cat.moving = True  # 敵を倒したら再び前に進む
                        break
                    else:
                        cat_list.remove(cat)  # 負けたらキャットを削除
                        enemy.moving = True #見方を倒したら再び前に進む

            #ビームの攻撃
            for beam in beams:
                for enemy in enemy_list:
                    if beam.rct.colliderect(enemy.rect) and enemy not in beam.hit_targets:  # ビームが敵に当たった かつ　まだこの敵にビームが当たっていないならば
                        enemy.health -= 50  # 体力を50減らす
                        beam.hit_targets.append(enemy) #この敵にビームが当たったことを記録

                        # 爆発エフェクトを生成
                        explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))

                        if enemy.health <= 0:  # 敵の体力が0以下になったら
                            enemy_list.remove(enemy)  # 敵を削除
                            money += 50  # お金を増やす



        # 敵が自城を攻撃する処理
        for enemy in enemy_list:
            if enemy.rect.colliderect(cat_castle.rect):  # 敵が自城に当たった場合
                cat_castle.health -= enemy.attack_power  # 城にダメージ
                enemy_list.remove(enemy)  # 攻撃後に敵を削除

        # 城の攻撃処理
        for cat in cat_list:
            if cat.rect.colliderect(enemy_castle.rect):
                enemy_castle.health -= cat.attack_power  # 敵の城にダメージ
                cat_list.remove(cat)  # 城に攻撃した味方を削除

        # 描画
        screen.blit(background_image, (0, 0))  # 背景を描画
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

        # HPを表示
        castle_hp_text = font.render(f"Cat Castle HP: {cat_castle.health}", True, BLACK)
        screen.blit(castle_hp_text, (10, 40))
        enemy_castle_hp_text = font.render(f"Enemy Castle HP: {enemy_castle.health}", True, BLACK)
        screen.blit(enemy_castle_hp_text, (10, 70))

        for i, cat in enumerate(cat_list):
            hp_text = font.render(f"Cat {i + 1} HP: {cat.health}", True, BLACK)
            screen.blit(hp_text, (10, 100 + i * 30))

        for i, enemy in enumerate(enemy_list):
            hp_text = font.render(f"Enemy {i + 1} HP: {enemy.health}", True, BLACK)
            screen.blit(hp_text, (WIDTH - 200, 100 + i * 30))

        for beam in beams:
            if not check_bound(beam.rct)[0]:
                beams.remove(beam)
            else:
                beam.update(screen)

        # 爆発エフェクトの更新と描画
        for explosion in explosions[:]:  # スライスでコピーして削除
            explosion.update()
            explosion.draw(screen)
            if explosion.lifetime <= 0:
                explosions.remove(explosion)  # ライフタイムが0になったら削除


        # ゲーム終了条件
        if cat_castle.health <= 0 or enemy_castle.health <= 0:
            running = False  # ゲーム終了

        pg.display.flip()
        clock.tick(60)

    pg.quit()

if __name__ == "__main__":
    main()
