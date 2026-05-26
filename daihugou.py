import pygame as pg
import random
import sys
import os

pg.init()
WIDTH, HEIGHT = 900, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("大富豪（複数枚＋階段＋CPU対応 完全版）")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
clock = pg.time.Clock()

font = pg.font.SysFont("meiryo", 24)

# -------------------------
# カードの準備
# -------------------------
suits = ["♠", "♥", "♦", "♣"]
ranks = list(range(3, 16))  # 3〜A
rank_name = {11:"J", 12:"Q", 13:"K", 14:"A",15:"2"}#数字と記号を合わせる

def card_to_text(card):
    """
    引数：カードのlist
    何を出したかの文章生成
    """
    s, r = card
    return f"{s}{r if r <= 10 else rank_name[r]}"#文字と数字で分けて考えてtxt表示

def create_deck():
    """
    デッキの作成（トランプ52枚）
    """
    deck = [(s, r) for s in suits for r in ranks]#数字とスートを組み合わせる
    random.shuffle(deck)#作ったdeckのシャッフル
    return deck

def is_straight(cards):
    """
    階段判定（スート無視・連番）
    引数：プレイヤーが選んだカードのlist
    Trueで階段判定、Falseで階段ではない判定
    """
    if len(cards) < 2:#選んだカードが２枚未満だとそもそも階段ではないからFalse
        return False
    ranks_ = sorted(c[1] for c in cards)#listカードからint型数字を取り出す
    for i in range(len(ranks_) - 1):#取り出した数字から+1してあっている数字ではなかったらFalse
        if ranks_[i] + 1 != ranks_[i+1]:#[5,4,6]-->soted[4,5,6]-->判定
            return False
    return True

def find_straights(hand):
    """
    # CPU用：手札から階段候補を探す（長さ2以上の連番）
    引数：手札
    """
    straights = []
    # ランクだけで見ればいいので、スートは無視してソート
    hand_sorted = sorted(hand, key=lambda c: c[1])#lambdaで簡単な関数表記＋カードlistの数字を取り出す
    temp = [hand_sorted[0]]#階段になるものを探してtempにlistで追加する
    for i in range(1, len(hand_sorted)):#CPUの手札にある連番を見つける
        if hand_sorted[i][1] == hand_sorted[i-1][1] + 1:#CPUhandの中の連番なりそうなものを探している
            temp.append(hand_sorted[i])#tempに追加
        else:
            if len(temp) >= 2:
                straights.append(temp.copy())#strairhtsのlistを変更しないようにそのコピーを渡す
            temp = [hand_sorted[i]]
    if len(temp) >= 2:
        straights.append(temp.copy())#strairhtsのlistを変更しないようにそのコピーを渡す
    return straights

def cpu_play(hand, field):
    """
    # CPUの行動（複数枚＋階段対応）
    # 引数：手札とその場
    """
    if len(hand) == 0:
        return None

    # ランクごとにまとめる（同ランク複数枚用）
    groups = {}
    for c in hand:
        groups.setdefault(c[1], []).append(c)

    straights = find_straights(hand)

    if field is None:
        # -------------------------
        # 場が流れている（自由に出せる）
        # -------------------------
        
        # 1. 最弱の階段
        if straights:
            play = min(straights, key=lambda s: s[-1][1])#手札の複数の階段で最小のものを選ぶ
            for c in play:
                hand.remove(c)
            return play

        # 2. 最弱の複数枚（同ランク）
        multi = [g for g in groups.values() if len(g) >= 2]
        if multi:
            play = min(multi, key=lambda g: g[0][1])#手札の複数のカードで最小のものを選ぶ
            for c in play:
                hand.remove(c)
            return play

        # 3. 最弱の1枚
        card = min(hand, key=lambda c: c[1])#手札の最小のカードを出す
        hand.remove(card)
        return card

    if isinstance(field, list):
        # -------------------------
        # 場がリスト（複数枚 or 階段）
        # -------------------------

        # 場が階段かどうか
        if is_straight(field):
            need = len(field)#場のカードの枚数
            field_ranks = sorted(c[1] for c in field)#場の数字を並び替える
            max_f = field_ranks[-1]#場の数字の最大を取る
            start_needed = max_f + 1#始まりはそのカードの＋１から始める
            # 「場の最大の次の数字から始まる同じ長さの階段」
            candidates = []
            for s in straights:
                if len(s) != need:#文字数の確認
                    continue
                ranks_s = sorted(c[1] for c in s)
                if ranks_s[0] == start_needed:#最大数の候補の取得
                    candidates.append(s)
            if candidates:
                play = min(candidates, key=lambda s: s[-1][1])
                for c in play:
                    hand.remove(c)
                return play
            return None
        else:
            # 同ランク複数枚として比較
            need = len(field)
            base_rank = field[0][1]
            candidates = []
            for r, g in groups.items():
                if len(g) == need and r > base_rank:
                    candidates.append(g)
            if candidates:
                play = min(candidates, key=lambda g: g[0][1])
                for c in play:
                    hand.remove(c)
                return play
            return None

    # -------------------------
    # 場が1枚出し（CPUは必ず1枚だけ出す・階段は出さない）
    # -------------------------
    base_rank = field[1]
    valid = [c for c in hand if c[1] > base_rank]
    if valid:
        card = min(valid, key=lambda c: c[1])
        hand.remove(card)
        return card

    return None

def draw_card(x, y, card):
    """
    # -------------------------
    # カード描画
    # -------------------------
    """
    s, r = card
    rect = pg.Rect(x, y, 60, 90)

    pg.draw.rect(screen, (255, 255, 255), rect)
    pg.draw.rect(screen, (0, 0, 0), rect, 3)

    color = (0, 0, 0) if s in ["♠", "♣"] else (200, 0, 0)
    rank_text = str(r) if r <= 10 else rank_name[r]

    text1 = font.render(f"{s}{rank_text}", True, color)
    screen.blit(text1, (x + 3, y + 2))

    text2 = font.render(f"{s}{rank_text}", True, color)
    tw, th = text2.get_size()
    screen.blit(text2, (x + 60 - tw - 3, y + 90 - th - 2))

    return rect

def draw_player_hand(hand, selected_cards):
    """
    # -------------------------
    # プレイヤー手札（選択対応）
    # -------------------------
    """
    rects = []
    for i, card in enumerate(hand):
        row = i // 10
        col = i % 10
        x = 50 + col * 70
        y = 400 + row * 100

        if card in selected_cards:
            y -= 20

        rect = draw_card(x, y, card)
        rects.append((rect, card))
    return rects

def draw_pass_button():
    """
    # -------------------------
    # ボタン
    # -------------------------
    """
    rect = pg.Rect(700, 450, 150, 60)
    pg.draw.rect(screen, (200, 50, 50), rect)
    pg.draw.rect(screen, (255, 255, 255), rect, 3)
    screen.blit(font.render("PASS", True, (255, 255, 255)), (740, 470))
    return rect

def draw_play_button():
    rect = pg.Rect(700, 380, 150, 60)
    pg.draw.rect(screen, (50, 150, 50), rect)
    pg.draw.rect(screen, (255, 255, 255), rect, 3)
    screen.blit(font.render("出す", True, (255, 255, 255)), (740, 400))
    return rect

rank_name_list = ["あなた", "CPU1", "CPU2", "CPU3"]
def show_result_screen(finished):
    """
    # -------------------------
    # リザルト画面
    # -------------------------
    """
    running = True

    if finished[0] == 0:
        result_text = "YOU WIN!"
        result_color = (255, 215, 0)
    else:
        result_text = "YOU LOSE..."
        result_color = (255, 80, 80)

    while running:
        screen.fill((20, 20, 20))

        title = font.render("GAME RESULT", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        result = font.render(result_text, True, result_color)
        screen.blit(result, (WIDTH//2 - result.get_width()//2, 140))

        y = 220
        for i, p in enumerate(finished):
            text = font.render(f"{i+1}位：{rank_name_list[p]}", True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 50

        ok_rect = pg.Rect(WIDTH//2 - 75, 500, 150, 50)
        pg.draw.rect(screen, (80, 80, 200), ok_rect)
        pg.draw.rect(screen, (255, 255, 255), ok_rect, 3)
        screen.blit(font.render("OK", True, (255, 255, 255)), (WIDTH//2 - 20, 515))

        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if ok_rect.collidepoint(event.pos):
                    running = False

# -------------------------
# メインゲーム
# -------------------------
def play_game():
    deck = create_deck()

    hands = [
        deck[0:13],
        deck[13:26],
        deck[26:39],
        deck[39:52],
    ]

    for h in hands:
        h.sort(key=lambda c: c[1])

    field = None
    message = ""
    finished = []
    selected_cards = []

    turn = 0
    last_player = 0
    pass_count = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if turn == 0 and event.type == pg.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # 出すボタン
                play_rect = draw_play_button()
                if play_rect.collidepoint(mx, my):

                    if len(selected_cards) == 0:
                        message = "カードを選択してください"
                        continue

                    ranks_sel = [c[1] for c in selected_cards]
                    same_rank = (len(set(ranks_sel)) == 1)
                    straight = is_straight(selected_cards)

                    # 場が1枚のときは階段禁止
                    if isinstance(field, tuple) and straight:
                        message = "場が1枚のときは階段は出せません"
                        continue

                    # 同ランクでも階段でもない → エラー
                    if len(selected_cards) >= 2 and (not same_rank and not straight):
                        message = "同じ数字か階段だけ出せます"
                        continue

                    # 場が複数枚 or 階段
                    if isinstance(field, list):
                        if is_straight(field):
                            # 場が階段 → 階段同士で比較
                            if not straight:
                                message = "場は階段です"
                                continue
                            if len(field) != len(selected_cards):
                                message = "枚数が違います"
                                continue
                            field_ranks = sorted(c[1] for c in field)
                            max_f = field_ranks[-1]
                            sel_ranks = sorted(c[1] for c in selected_cards)
                            # 「場の最大の次の数字から始まる」かどうか
                            if sel_ranks[0] != max_f + 1:
                                message = "その階段は出せません"
                                continue
                        else:
                            # 場が同ランク複数枚
                            if not same_rank:
                                message = "場は同じ数字の複数枚です"
                                continue
                            if len(field) != len(selected_cards):
                                message = "枚数が違います"
                                continue
                            if selected_cards[0][1] <= field[0][1]:
                                message = "弱いです"
                                continue

                    # 場が1枚
                    if isinstance(field, tuple):
                        if len(selected_cards) != 1:
                            message = "複数枚出しはできません（場が1枚）"
                            continue
                        if selected_cards[0][1] <= field[1]:
                            message = "弱いです"
                            continue

                    # 出す処理
                    for c in selected_cards:
                        hands[0].remove(c)

                    if len(selected_cards) == 1:
                        field = selected_cards[0]
                    else:
                        field = selected_cards.copy()

                    selected_cards.clear()
                    last_player = 0
                    pass_count = 0
                    message = "カードを出した"
                    turn = 1
                    continue

                # PASS
                pass_rect = draw_pass_button()
                if pass_rect.collidepoint(mx, my):
                    message = "あなたはパスした"
                    pass_count += 1
                    selected_cards.clear()
                    turn = 1
                    continue

                # カード選択
                rects = draw_player_hand(hands[0], selected_cards)
                for rect, card in rects:
                    if rect.collidepoint(mx, my):
                        if card in selected_cards:
                            selected_cards.remove(card)
                        else:
                            selected_cards.append(card)
                        break

        # CPUターン
        if turn != 0:

            if len(hands[turn]) == 0:
                turn = (turn + 1) % 4
                continue

            pg.time.wait(300)

            card = cpu_play(hands[turn], field)
            if card:
                field = card

                if isinstance(card, list):
                    text = " ".join(card_to_text(c) for c in card)
                    message = f"CPU{turn} は {text} を出した"
                else:
                    message = f"CPU{turn} は {card_to_text(card)} を出した"

                last_player = turn
                pass_count = 0
            else:
                message = f"CPU{turn} はパスした"
                pass_count += 1

            turn = (turn + 1) % 4

        # 場流し
        if pass_count >= 3:
            field = None
            message = "場が流れた！"
            turn = last_player
            pass_count = 0

        # 上がり判定
        for i in range(4):
            if len(hands[i]) == 0 and i not in finished:
                finished.append(i)

        # 3人上がったら終了
        if len(finished) == 3:
            for i in range(4):
                if i not in finished:
                    finished.append(i)
                    break
            show_result_screen(finished)
            break

        # 描画
        screen.fill((0, 120, 0))

        # 場の描画
        if field:
            if isinstance(field, list):
                x = WIDTH//2 - (len(field)*35)
                for c in field:
                    draw_card(x, HEIGHT//2 - 45, c)
                    x += 70
            else:
                draw_card(WIDTH//2 - 30, HEIGHT//2 - 45, field)

        draw_player_hand(hands[0], selected_cards)

        screen.blit(font.render(f"CPU1：{len(hands[1])}枚", True, (255, 255, 255)), (WIDTH//2 - 80, 30))
        screen.blit(font.render(f"CPU2：{len(hands[2])}枚", True, (255, 255, 255)), (50, 150))
        screen.blit(font.render(f"CPU3：{len(hands[3])}枚", True, (255, 255, 255)), (WIDTH - 180, 150))

        draw_pass_button()
        draw_play_button()

        msg = font.render(message, True, (255, 255, 255))
        screen.blit(msg, (50, 300))

        pg.display.update()
        clock.tick(60)

# -------------------------
# 実行
# -------------------------
play_game()
