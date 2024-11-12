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
pg.mixer.init()

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
font_big = pg.font.Font(None, 74)
font = pg.font.Font(None, 36)

# スタート画面の表示関数
def start_screen():
    start_background = pg.image.load("fig/start_background.png")  # スタート画面用の背景画像を読み込み
    start_background = pg.transform.scale(start_background, (WIDTH, HEIGHT))  # スケーリング
    screen.blit(start_background, (0, 0))  # 背景を描画

    title_text = font_big.render("Cat Battle Game", True, BLACK)
    start_text = font.render("Press Enter to Start", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
    pg.display.flip()


# キャラクターの基底クラス
class Character:

    def __init__(self, x, y, health, attack_power, img_obj):
        if img_obj:  # 画像が指定されている場合は画像を使う
            self.image = img_obj
        else:  # 画像が指定されていない場合は色で塗る
            self.image = pg.Surface((50, 50))
            self.image.fill((0, 0, 0))     
        self.rect = self.image.get_rect(center = (x, y))
        self.health = health
        self.attack_power = attack_power
        self.moving = True

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# 味方のクラス
class Normal(Character):
    def __init__(self, y,img_obj):
        super().__init__(150, y, health=100, attack_power=10, img_obj=img_obj)

    def move(self):
        if self.moving:
            self.rect.x += 2  # 移動速度


class Strong(Character):
    def __init__(self, y,img_obj):
        super().__init__(150, y, health=200, attack_power=20, img_obj=img_obj)

    def move(self):
        if self.moving:
            self.rect.x += 2


# 防御力が高いキャットクラス
class Health(Character):
    def __init__(self, y,img_obj):
        super().__init__(150, y, health=300, attack_power=5, img_obj=img_obj)

    def move(self):
        if self.moving:
            self.rect.x += 2


# 敵クラスの派生（3種類）
class FastEnemy(Character):
    def __init__(self, y, img_obj):
        super().__init__(WIDTH - 100, y, health=50, attack_power=5, img_obj=img_obj)
        self.image.set_colorkey((255, 255, 255))  # 白い部分を透過

    def move(self):
        self.rect.x -= 7  # 高速移動


class TankEnemy(Character):
    def __init__(self, y, img_obj):
        super().__init__(WIDTH - 100, y, health=200, attack_power=10, img_obj=img_obj)
        self.image.set_colorkey((255, 255, 255))  # 白い部分を透過

    def move(self):
        self.rect.x -= 2  # 遅いが耐久力が高い


class BalancedEnemy(Character):
    def __init__(self, y, img_obj):
        super().__init__(WIDTH - 100, y, health=100, attack_power=8, img_obj=img_obj)
        self.image.set_colorkey((255, 255, 255))  # 白い部分を透過

    def move(self):
        self.rect.x -= 4  # バランス型


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

    ct = 5
    def __init__(self, castle: Castle):
        self.img = pg.image.load("fig/beam.png")  # ビームSurface
        self.rct = self.img.get_rect()  # ビームSurfaceのRectを抽出
        self.rct.centery = castle.rect.centery  # 城の中心縦座標をビームの縦座標
        self.rct.left = castle.rect.right  # 城の右座標をビームの左座標
        self.vx, self.vy = 5, 0
        
        self.hit_targets = []

    def update(self):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct) 


class Money:    #資金クラス
    def __init__(self):
        self.rate = 1   #2フレーム当たりの増加資金
        self.money = 0   #資金
        self.max_money = 500  #資金の上限
        self.level = 1  #現在の資金レベル
        self.max_level = 5  #資金レベルの上限
        self.level_up_cost = self.max_money * 0.8   #資金レベルアップに必要となるコスト

    def update(self):
        self.money += self.rate #一定時間ごとに資金を増加
        #上限を超えない
        if self.money >= self.max_money:
            self.money = self.max_money
    
    def kill_bonus(self, bonus: int):
        self.money += bonus #相手ユニットを倒した際に資金を獲得
        #上限を超えない
        if self.money >= self.max_money:
            self.money = self.max_money

    def change_level(self) -> bool:
        if self.level < self.max_level and self.money >= self.level_up_cost:    #レベルが最大値でないかつ必要資金が集まっている場合
            self.money -= self.level_up_cost    #必要資金を消費
            self.rate += 1  #時間増加資金を追加
            self.max_money += 500   #上限を増加
            self.level += 1 #レベルを増加
            self.level_up_cost = self.max_money * 0.8   #レベルアップに必要なコストを再設定
            return True #正常終了Trueを返却
        else:   #条件を満たさない場合Falseを返却
            return False

        
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


# 終了画面表示用関数
def end_screen(message):
    end_background = pg.image.load("fig/end_background.png")  # 終了画面用の背景画像を読み込み
    end_background = pg.transform.scale(end_background, (WIDTH, HEIGHT))  # スケーリング
    screen.blit(end_background, (0, 0))  # 背景を描画

    end_text = font_big.render(message, True, BLACK)
    screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - end_text.get_height() // 2))
    pg.display.flip()
    pg.time.wait(3000)  # 3秒間表示

#ボタン表示用関数
def draw_button(pos, frame, img1, img2=None):
    """
    ボタンを描画する
    """

    if pos < 1 or WIDTH // frame.get_width() < pos:
        print("cant draw this place now.")
        return -1

    x = WIDTH - ((frame.get_width() + 10) * pos)
    y = HEIGHT - frame.get_height() - 25
    screen.blit(frame, (x, y))
    screen.blit(img1, (x + frame.get_width() / 2 - img1.get_width() / 2, y + 15))
    if img2 is not None:
        screen.blit(img2, (x + frame.get_width() / 2 - img2.get_width() / 2, y + frame.get_height()- img2.get_height() - 10))


# ゲームのメインループ
def main():
    font = pg.font.Font(None, 36)
    clock = pg.time.Clock()

    cat_list = []
    enemy_list = []
    explosions = []
    money = Money() #資金を初期化
    beams = []
    tmr = 0

    sound_bgm = pg.mixer.Sound("sound/battle_music.wav")
    sound_money_failure = pg.mixer.Sound("sound/キャンセル3.mp3")   #資金レベルアップ失敗音
    sound_money_success = pg.mixer.Sound("sound/ゲージ回復2.mp3")   #資金レベルアップ成功音

    sound_bgm.play(-1)

    # 城の設定
    cat_castle = Castle(0, HEIGHT // 2 - 50, 1000, False)  # 味方の城
    enemy_castle = Castle(WIDTH - 180, HEIGHT // 2 - 50, 1000, True)  # 敵の城

    running = True
    tmr = 0

    frame_img = pg.transform.scale(pg.image.load("fig/frame.png"), (150, 100))

    cat_img_data = [["fig/AUNZ4365.JPG", 50],["fig/IMG_E0591.JPG", 100],["fig/IMG_9345.JPG", 200]]
    character_imgs = []
    for i in cat_img_data:
        character_imgs.append(pg.transform.scale(pg.image.load(i[0]).convert_alpha(), (50, 50)))

    enemy_classes = [FastEnemy, TankEnemy, BalancedEnemy]
    enemy_img_data = [["fig/speed.jpg", (125, 65)], ["fig/tank.jpg", (140, 140)], ["fig/balance.jpg", (80, 100)]]
    enemy_imgs = []
    for i in enemy_img_data:
        enemy_imgs.append(pg.transform.scale(pg.image.load(i[0]), i[1]))  # 画像をリサイズ)

    y_position = HEIGHT // 2

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
    
            # キャットを召喚
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1 and money.money >= 50:
                    cat_list.append(Normal(y_position,character_imgs[0]))
                    money.money -= 50
                elif event.key == pg.K_2 and money.money >= 100:
                    cat_list.append(Strong(y_position,character_imgs[1]))
                    money.money -= 100
                elif event.key == pg.K_3 and money.money >= 200:
                    cat_list.append(Health(y_position,character_imgs[2]))
                    money.money -= 200
                
                if event.key == pg.K_q and Beam.ct == 0:
                    beams.append(Beam(cat_castle))
                    Beam.ct = 30

                if event.key == pg.K_w: #wキーで資金レベルを増加
                    res = money.change_level()
                    if not res: #成功時、失敗時の音声を再生
                        sound_money_failure.play(0)
                    else:
                        sound_money_success.play(0)
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    (mouse_x, mouse_y) = event.pos
                    print(WIDTH - ((frame_img.get_width() + 10) * 1), WIDTH - (frame_img.get_width() * (1 - 1) + 10 * 1))
                    print(mouse_x, mouse_y)
                    """
                    x = WIDTH - ((frame.get_width() + 10) * pos)
                    y = HEIGHT - frame.get_height() - 25
                    """
                    if HEIGHT - frame_img.get_height() - 25 <= mouse_y <= HEIGHT - 25:
                        print("in if")
                        if WIDTH - ((frame_img.get_width() + 10) * 1) <= mouse_x <= WIDTH - (frame_img.get_width() * (1 - 1) + 10 * 1) and Beam.ct <= 0:
                            print("in if")
                            beams.append(Beam(cat_castle))
                            Beam.ct = 30
                        elif WIDTH - ((frame_img.get_width() + 10) * 2) <= mouse_x <= WIDTH - (frame_img.get_width() * (2 - 1) + 10 * 2):
                            res = money.change_level()
                            if not res: #成功時、失敗時の音声を再生
                                sound_money_failure.play(0)
                            else:
                                sound_money_success.play(0)
                        elif WIDTH - ((frame_img.get_width() + 10) * 3) <= mouse_x <= WIDTH - (frame_img.get_width() * (3 - 1) + 10 * 3) and money.money >= 50:
                            cat_list.append(Normal(y_position,character_imgs[0]))
                            money.money -= 50
                        elif WIDTH - ((frame_img.get_width() + 10) * 4) <= mouse_x <= WIDTH - (frame_img.get_width() * (4 - 1) + 10 * 4) and money.money >= 100:
                            cat_list.append(Strong(y_position,character_imgs[1]))
                            money.money -= 100
                        elif WIDTH - ((frame_img.get_width() + 10) * 5) <= mouse_x <= WIDTH - (frame_img.get_width() * (5 - 1) + 10 * 5) and money.money >= 200:
                            cat_list.append(Health(y_position,character_imgs[2]))
                            money.money -= 200


        # 敵の出現
        if (tmr + 1) % 60 == 0:  # 1秒ごとに敵を生成
            enemy_number = random.randint(0, 2)
            enemy_list.append(enemy_classes[enemy_number](HEIGHT // 2, enemy_imgs[enemy_number]))

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
                if cat.rect.colliderect(enemy.rect):  # 衝突判定
                    cat.moving = False  # 移動を止める
                    enemy.moving = False
                    if battle(cat, enemy):
                        enemy_list.remove(enemy) # バトル後に敵を削除
                        money.kill_bonus(20)  # 勝ったらお金が増える
                        cat.moving = True  # 敵を倒したら再び前に進む
                        Beam.ct -= 5
                        if Beam.ct <= 0:
                            Beam.ct = 0
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
                        money.kill_bonus(20)  # お金を増やす
                        Beam.ct -= 5
                        if Beam.ct <= 0:
                            Beam.ct = 0

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

        beam_text = font.render("Beam", True, RED)
        if Beam.ct <= 0:
            beam_ct_text_origin = "Ready!!"
        else:
            beam_ct_text_origin = f"CT: {Beam.ct}s"
        beam_ct_text = font.render(beam_ct_text_origin, True, RED)
        draw_button(1, frame_img, beam_text, beam_ct_text)

        if money.level < money.max_level:
            level_text = cost_text = font.render(f"Money Lv. {money.level}", True, BLACK)
            cost_text = font.render(f"{money.level_up_cost:.0f}", True, BLACK)
        else:
            level_text = cost_text = font.render("Money", True, BLACK)
            cost_text = font.render("Lv. MAX!!", True, BLACK)
        draw_button(2, frame_img, level_text, cost_text)

        for (i, character) in enumerate(cat_img_data):
            cost_text = font.render(f"{character[1]}", True, BLACK)
            draw_button(i + 3, frame_img, character_imgs[i], cost_text)

        for cat in cat_list:
            cat.draw(screen)
        for enemy in enemy_list:
            enemy.draw(screen)

        if tmr % 1 == 0:    #2フレームごとに資金を増加
            money.update()

        #資金レベルを描画
        if money.level < money.max_level:
            button_text = f"push 'W': Money Lv up (cost={money.level_up_cost:.0f})"
        else:
            button_text = f"push 'W': Money Lv up (Lv. MAX)"
        screen.blit(font.render(button_text, True, BLACK), (10, 10))

        # 資金を表示
        money_text = font.render(f"Money: {money.money:.0f}/{money.max_money} (Lv.{money.level})", True, BLACK)
        screen.blit(money_text, (10, 40))

        # HPを表示
        castle_hp_text = font.render(f"My Castle HP: {cat_castle.health}", True, BLACK)
        screen.blit(castle_hp_text, (10, 70))
        enemy_castle_hp_text = font.render(f"Enemy Castle HP: {enemy_castle.health:4}", True, BLACK)
        enemy_castle_health_pg = enemy_castle_hp_text.get_width()
        screen.blit(enemy_castle_hp_text, (WIDTH - enemy_castle_health_pg, 70))

        #ビームクールタイムを表示
        beam_ct_txt = font.render(f"beam CT: {Beam.ct}", True, RED)
        beam_pg = beam_ct_txt.get_width() / 2
        screen.blit(beam_ct_txt, (WIDTH / 2 - beam_pg, 70))

        for i, cat in enumerate(cat_list):
            hp_text = font.render(f"Caractor {i + 1} HP: {cat.health}", True, BLACK)
            screen.blit(hp_text, (10, 100 + i * 30))

        for i, enemy in enumerate(enemy_list):
            hp_text = font.render(f"Enemy {i + 1} HP: {enemy.health}", True, BLACK)
            screen.blit(hp_text, (WIDTH - 200, 100 + i * 30))

        for beam in beams:
            if not check_bound(beam.rct)[0]:
                beams.remove(beam)
            else:
                beam.update()
        if tmr % 60 == 0 and Beam.ct > 0:
            Beam.ct -= 1

        # 爆発エフェクトの更新と描画
        for explosion in explosions[:]:  # スライスでコピーして削除
            explosion.update()
            explosion.draw(screen)
            if explosion.lifetime <= 0:
                explosions.remove(explosion)  # ライフタイムが0になったら削除

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

# スタート画面を表示
    start_screen()
    # スタート画面のループ
    while not game_active:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    game_active = True  # Enterキーでゲーム開始

    # メインゲームの開始
    main()
    pg.quit()


