import asyncio
import random

import discord
from PIL import Image, ImageDraw, ImageFont

def create_pic_quoridor(match, index, player_list):
    """
    画像を生成する関数
    後手の時は180°回転する"""

    background = Image.new("RGB", size=(500, 600), color=0x0065cb)
    ban = Image.new("RGB", size=(450, 450))
    null = Image.open("./quoridor/null.png")
    can = Image.open("./quoridor/can.png")
    red = Image.open("./quoridor/red.png")
    blue = Image.open("./quoridor/blue.png")
    square_red_yoko = Image.open("./quoridor/square_red_yoko.png")
    square_red_tate = Image.open("./quoridor/square_red_tate.png")
    square_red_midium = Image.open("./quoridor/square_red_midium.png")
    square_blue_yoko = Image.open("./quoridor/square_blue_yoko.png")
    square_blue_tate = Image.open("./quoridor/square_blue_tate.png")
    square_blue_midium = Image.open("./quoridor/square_blue_midium.png")
    y = 0

    for i in range(17):
        if i % 2 == 0:
            x = 0
            for j in range(17):
                if j % 2 == 0:
                    cell = match[i][j]
                    if cell == 0:
                        ban.paste(null, (x, y))
                    elif cell == 3:
                        ban.paste(can, (x, y))
                    elif cell == 1:
                        ban.paste(red, (x, y))
                    elif cell == 2:
                        ban.paste(blue, (x, y))
                    x += 50
            y += 50

    for i in range(17):
        for j in range(17):
            cell = match[i][j]
            if i % 2 == 1 and j % 2 == 1: #iもjも奇数(マスの間とマスの間の交点なら)
                if cell == 1:
                    ban.paste(square_red_midium, ((j-1)*25+45, (i-1)*25+45))
                elif cell == 2:
                    ban.paste(square_blue_midium, ((j-1)*25+45, (i-1)*25+45))
            elif i % 2 == 1 and j % 2 == 0: #iは奇数、jは偶数
                if cell == 1:
                    ban.paste(square_red_yoko, (j*25+5, (i-1)*25+45))
                elif cell == 2:
                    ban.paste(square_blue_yoko, (j*25+5, (i-1)*25+45))
            elif i % 2 == 0 and j % 2 == 1: #iは偶数、jは奇数
                if cell == 1:
                    ban.paste(square_red_tate, ((j-1)*25+45, i*25+5))
                elif cell == 2:
                    ban.paste(square_blue_tate, ((j-1)*25+45, i*25+5))

    if index == 1:
        ban = ban.rotate(180)

    background.paste(ban, (50, 100))

    moji = ImageDraw.Draw(background)
    font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
    upper_alfabet_tuple = ("A", "B", "C", "D", "E", "F", "G", "H")
    lower_alfabet_tuple = ("a", "b", "c", "d", "e", "f", "g", "h")
    sente_ita = match[17]
    gote_ita = match[18]
    sente = player_list[0]
    gote = player_list[1]
    if index == 0:
        for y in range(9):
            moji.text((y*50+67, 50), text=f"{y+1}", font=font, fill=0x000000) #実際は横軸を描くが都合がいいのでyを使う
            moji.text((8, y*50+109), text=f"{y+1}", font=font, fill=0x000000)
            if y < 8: #盤面横の英語を描く(大文字)
                moji.text((y*50+92, 66), text=lower_alfabet_tuple[y], font=font, fill=0x000000) #実際は横軸を描くが都合がいいのでyを使う
                moji.text((24, y*50+134), text=upper_alfabet_tuple[y], font=font, fill=0x000000)
            for x in range(9): #盤面内の数字を描く
                moji.text((x*50+59, y*50+109), text=f"{x+1}{y+1}", font=font, fill=0x000000)

        moji.text((50, 558), text=f"{sente.display_name}", font=font, fill=0x000000)
        moji.text((150, 8), text=f"{gote.display_name}", font=font, fill=0x000000)
        moji.rectangle((410, 555, 490, 595), fill=0x0000ff)
        moji.rectangle((60, 5, 140, 45), fill=0xff0000)
        moji.text((433, 558), text=f"{sente_ita}", font=font, fill=0xffffff)
        moji.text((83, 8), f"{gote_ita}", font=font, fill=0xffffff)

    else:
        for y in range(9):
            moji.text(((8-y)*50+67, 50), text=f"{y+1}", font=font, fill=0x000000) #実際は横軸を描くが都合がいいのでyを使う
            moji.text((8, (8-y)*50+109), text=f"{y+1}", font=font, fill=0x000000)
            if y < 8: #盤面横の英語を描く(大文字)
                moji.text(((8-y)*50+42, 66), text=lower_alfabet_tuple[y], font=font, fill=0x000000) #実際は横軸を描くが都合がいいのでyを使う
                moji.text((24, (8-y)*50+84), text=upper_alfabet_tuple[y], font=font, fill=0x000000)
            for x in range(9): #盤面内の数字を描く
                moji.text((x*50+59, y*50+109), text=f"{9-x}{9-y}", font=font, fill=0x000000)
        moji.text((50, 558), text=gote.display_name, font=font, fill=0x000000)
        moji.text((150, 8), text=sente.display_name, font=font, fill=0x000000)
        moji.rectangle((410, 555, 490, 595), fill=0xff0000)
        moji.rectangle((60, 5, 140, 45), fill=0x0000ff)
        moji.text((433, 558), text=f"{gote_ita}", font=font, fill=0xffffff)
        moji.text((83, 8), f"{sente_ita}", font=font, fill=0xffffff)

    background.save("quoridor.png")


async def match_quoridor(client3, message, about_quoridor):
    match = [
        [0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 3, 0, 0, 0, 0, 0, 0],
        10, #先手の壁の保有数
        10 #後手の壁の保有数
    ]

    index = random.choice([1, 2])
    sente = about_quoridor[index]
    if index == 1:
        index = 2
    else:
        index = 1
    gote = about_quoridor[index]
    await message.channel.send(f"先手は{sente.name}さん\n後手は{gote.name}さんです")

    player_list = []
    player_list.append(sente)
    player_list.append(gote)

    def msg_check(m):
        return m.channel == message.channel and not m.author.bot

    n = 0
    timeout = False
    while True:
        index = n % 2
        teban_member = player_list[index]
        create_pic_quoridor(match, index, player_list)
        f = discord.File("./quoridor.png")
        await message.channel.send(content=f"{teban_member.name}さんの番です", file=f)

        while True:
            try:
                reply = await client3.wait_for("message", check=msg_check, timeout=50)
            except asyncio.TimeoutError:
                await message.channel.send("残り10秒")
                try:
                    reply = await client3.wait_for("message", check=msg_check, timeout=10)
                except asyncio.TimeoutError:
                    index = (n+1)%2
                    await message.channel.send(f"タイムアウト！{player_list[index]}の勝ち！")
                    timeout = True
                    break

            cannot_go_next = False
            if reply.author.id != teban_member.id:
                cannot_go_next = True

            if not cannot_go_next: 
                user_operate = list(reply.content)
                if user_operate[0] in ("A", "B", "C", "D", "E", "F", "G", "H"):
                    row = (("A", "B", "C", "D", "E", "F", "G", "H").index(user_operate[0]) * 2) + 1
                    try:
                        col_1 = int(user_operate[1])
                        col_2 = int(user_operate[2])
                    except (ValueError, IndexError):
                        await message.channel.send("画面内にある数字かD23のような英語+連続した数字2文字が使用できます")
                        cannot_go_next = True
                    else:
                        if col_1 < 1 or col_1 > 9 or col_2 < 1 or col_2 > 9:
                            await message.channel.send("画面内にある数字かD23のような英語+連続した数字2文字が使用できます")
                            cannot_go_next = True
                        else:
                            if abs(col_1 - col_2) != 1:
                                await message.channel.send("壁の設置は隣接した2マスに限ります")
                                cannot_go_next = True
                            else:
                                col_1 = (min(col_1, col_2) - 1) * 2 
                                col_midium = col_1 + 1
                                col_2 = col_1 + 2
                                operate = "put_row"

                elif user_operate[0] in ("a", "b", "c", "d", "e", "f", "g", "h"):
                    col = (("a", "b", "c", "d", "e", "f", "g", "h").index(user_operate[0]) * 2) + 1
                    try:
                        row_1 = int(user_operate[1])
                        row_2 = int(user_operate[2])
                    except (ValueError, IndexError):
                        await message.channel.send("画面内にある数字かD23のような英語+連続した数字2文字が使用できます")
                        cannot_go_next = True
                    else:
                        if row_1 < 1 or row_1 > 9 or row_2 < 1 or row_2 > 9:
                            await message.channel.send("画面内にある数字かD23のような英語+連続した数字2文字が使用できます")
                            cannot_go_next = True
                        else:
                            if abs(row_1 - row_2) != 1:
                                await message.channel.send("壁の設置は隣接した2マスに限ります")
                                cannot_go_next = True
                            else:
                                row_1 = (min(row_1, row_2) - 1) * 2
                                row_midium = row_1 + 1
                                row_2 = row_1 + 2
                                operate = "put_col"

                else:
                    try:
                        move_x = int(user_operate[0])
                        move_y = int(user_operate[1])
                    except (ValueError, IndexError):
                        await message.channel.send("画面内にある数字かD23のような英語+連続した数字2文字が使用できます")
                        cannot_go_next = True
                    else:
                        if move_x < 1 or move_x > 9 or move_y < 1 or move_y > 9:
                            await message.channel.send("画面内にある数字かD23のような英語+連続した数字2文字が使用できます")
                            cannot_go_next = True
                        else:
                            if match[(move_y-1)*2][(move_x-1)*2] != 3:
                                await message.channel.send("そこには動けません")
                                cannot_go_next = True
                            else:
                                operate = "move"

            if not cannot_go_next:
                if "put" in operate:
                    wall_count = match[index+17]
                    if wall_count == 0:
                        await message.channel.send("壁の保有数が足りません")
                        cannot_go_next = True

            if not cannot_go_next:
                if operate == "put_row":
                    if any((match[row][col_1] != 0, match[row][col_midium] != 0, match[row][col_2] != 0)):
                        await message.channel.send("そこには置けません")
                        cannot_go_next = True

                elif operate == "put_col":
                    if any((match[row_1][col] != 0, match[row_midium][col] != 0, match[row_2][col] != 0)):
                        await message.channel.send("そこには置けません")
                        cannot_go_next = True

            if not cannot_go_next:
                #いずれゴール不可能な壁の設置を弾くようにする
                pass

            if not cannot_go_next:
                break

        if timeout:
            break

        if operate == "put_row":
            for i in range(3):
                match[row][col_1+i] = index + 1
            match[index+17] -= 1
        elif operate == "put_col":
            for i in range(3):
                match[row_1+i][col] = index + 1
            match[index+17] -= 1

        for i in range(9):
            for j in range(9):
                if operate == "move":
                    if match[i*2][j*2] == index + 1 or match[i*2][j*2] == 3:
                        match[i*2][j*2] = 0
                    elif match[i*2][j*2] == 2 - index: #相手の駒なら
                        aite_y = i * 2
                        aite_x = j * 2
                else:
                    if match[i*2][j*2] == 3:
                        match[i*2][j*2] = 0
                    elif match[i*2][j*2] == 2 - index: #相手の駒なら
                        aite_y = i * 2
                        aite_x = j * 2

        if operate == "move":
            match[(move_y-1)*2][(move_x-1)*2] = index + 1
            if (move_y - 1) * 2 == index * 16: #相手の最下段に到達したら
                create_pic_quoridor(match, index, player_list)
                f = discord.File("./quoridor.png")
                await message.channel.send(content=f"{player_list[index].name}の勝ち！", file=f)
                break

        if aite_y >= 2:
            if match[aite_y-1][aite_x] == 0: #上方向に壁が無ければ
                if match[aite_y-2][aite_x] == 0: #上のマスが空いていれば
                    match[aite_y-2][aite_x] = 3
                elif match[aite_y-2][aite_x] == index + 1: #上のマスが自分の駒なら
                    if aite_y >= 4:
                        if match[aite_y-3][aite_x] == 0: #自分の駒の上方向に壁が無ければ
                            match[aite_y-4][aite_x] = 3
                        else:
                            if aite_x - 2 >= 0:
                                if match[aite_y-2][aite_x-1] == 0:
                                    match[aite_y-2][aite_x-2] = 3
                            if aite_x + 2 <= 16:
                                if match[aite_y-2][aite_x+1] == 0:
                                    match[aite_y-2][aite_x+2] = 3

        if aite_y <= 14:
            if match[aite_y+1][aite_x] == 0: #下方向に壁が無ければ
                if match[aite_y+2][aite_x] == 0: #下のマスが空いていれば
                    match[aite_y+2][aite_x] = 3
                elif match[aite_y+2][aite_x] == index + 1: #下のマスが自分の駒なら
                    if aite_y <= 12:
                        if match[aite_y+3][aite_x] == 0: #相手の駒の下方向に壁が無ければ
                            match[aite_y+4][aite_x] = 3
                        else:
                            if aite_x - 2 >= 0:
                                if match[aite_y+2][aite_x-1] == 0:
                                    match[aite_y+2][aite_x-2] = 3
                            if aite_x + 2 <= 16:
                                if match[aite_y+2][aite_x+1] == 0:
                                    match[aite_y+2][aite_x+2] = 3

        if aite_x >= 2:
            if match[aite_y][aite_x-1] == 0: #左方向に壁が無ければ
                if match[aite_y][aite_x-2] == 0: #左のマスが空いていれば
                    match[aite_y][aite_x-2] = 3
                elif match[aite_y][aite_x-2] == index + 1: #左のマスが自分の駒なら
                    if aite_x >= 4:
                        if match[aite_y][aite_x-3] == 0: #自分の駒の左方向に壁が無ければ
                            match[aite_y][aite_x-4] = 3
                        else:
                            if aite_y - 2 >= 0:
                                if match[aite_y-1][aite_x-2] == 0:
                                    match[aite_y-2][aite_x-2] = 3
                            if aite_y + 2 <= 16:
                                if match[aite_y+1][aite_x-2] == 0:
                                    match[aite_y+2][aite_x-2] = 3

        if aite_x <= 14:
            if match[aite_y][aite_x+1] == 0: #右方向に壁が無ければ
                if match[aite_y][aite_x+2] == 0: #右のマスが空いていれば
                    match[aite_y][aite_x+2] = 3
                elif match[aite_y][aite_x+2] == index + 1: #右のマスが自分の駒なら
                    if aite_x >= 4:
                        if match[aite_y][aite_x+3] == 0: #自分の駒の右方向に壁が無ければ
                            match[aite_y][aite_x+4] = 3
                        else:
                            if aite_y - 2 >= 0:
                                if match[aite_y-1][aite_x+2] == 0:
                                    match[aite_y-2][aite_x+2] = 3
                            if aite_y + 2 <= 16:
                                if match[aite_y+1][aite_x+2] == 0:
                                    match[aite_y+2][aite_x+2] = 3

        n += 1

    about_quoridor.clear()