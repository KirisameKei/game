import asyncio
import random

import discord
from PIL import Image, ImageDraw, ImageFont


def create_pic_othello(match, size):
    black = Image.open("./othello/black.png")
    white = Image.open("./othello/white.png")
    can = Image.open("./othello/can.png")
    null = Image.open("./othello/null.png")
    othello = Image.new(mode="RGB", size=(size*50, size*50), color=0xffffff)
    i = 0
    moji = ImageDraw.Draw(othello)
    for line in match[1:size+1]:
        j = 0
        for cell in line[1:size+1]:
            if cell == 1:
                othello.paste(black, (i, j))
            elif cell == 2:
                othello.paste(white, (i, j))
            elif cell == 3:
                othello.paste(can, (i, j))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
                moji.text((i+9, j+9), text=f"{int(i/50+1)}{int(j/50+1)}", font=font, fill=0x000000)
            else:
                othello.paste(null, (i, j))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
                moji.text((i+9, j+9), text=f"{int(i/50+1)}{int(j/50+1)}", font=font, fill=0x000000)
            j += 50
        i += 50
    othello.save("othello.png")


async def match_othello(client3, message, about_othello):
    #match = [
    #    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0],
    #    [0, 0, 0, 3, 2, 1, 0, 0, 0, 0],
    #    [0, 0, 0, 0, 1, 2, 3, 0, 0, 0],
    #    [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
    #    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #]

    size = about_othello[0]
    match = []
    for i in range(size+2):
        line = []
        for j in range(size+2):
            line.append(0)
        match.append(line)

    match[int(size/2)][int(size/2)] = 2
    match[int(size/2+1)][int(size/2+1)] = 2
    match[int(size/2+1)][int(size/2)] = 1
    match[int(size/2)][int(size/2+1)] = 1
    match[int(size/2-1)][int(size/2)] = 3
    match[int(size/2)][int(size/2-1)] = 3
    match[int(size/2+1)][int(size/2+2)] = 3
    match[int(size/2+2)][int(size/2+1)] = 3

    temp = random.choice([0, 1])
    player_list = []
    player_list.append(about_othello[2+temp])
    if temp == 0:
        temp = 1
    else:
        temp = 0
    player_list.append(about_othello[2+temp])
    await message.channel.send(f"先手は{player_list[0].name}さん、後手は{player_list[1].name}さんです")

    def msg_check(m):
        return m.channel == message.channel and not m.author.bot

    timeout = False
    #series_pass = False
    for n in range(size**2):
        index = n % 2
        teban_member = player_list[index]
        create_pic_othello(match, size)
        f = discord.File("./othello.png")
        await message.channel.send(f"{teban_member.name}さんの番です", file=f)

        is_exist_can_put_place = False
        for line in match[1:size+1]:
            for cell in line[1:size+1]:
                if cell == 3:
                    is_exist_can_put_place = True
                    break

        if is_exist_can_put_place: #置ける場所があるなら
            series_pass = False

            while True:
                try:
                    reply = await client3.wait_for("message", check=msg_check, timeout=50)
                except asyncio.TimeoutError:
                    await message.channel.send("残り10秒・・・")
                    try:
                        reply = await client3.wait_for("message", check=msg_check, timeout=10)
                    except asyncio.TimeoutError:
                        next_index = (n+1)%2
                        await message.channel.send(f"タイムアウト！{player_list[next_index]}の勝ち！")
                        timeout = True
                        break

                if reply.author != teban_member:
                    pass
                else:
                    try:
                        x = int(reply.content[0:1])
                        y = int(reply.content[1:2])
                    except ValueError:
                        await message.channel.send("画像内の数字を入力してください")
                    else:
                        if x <= 0 or x > size or y <= 0 or y > size:
                            await message.channel.send("画像内にある数字を入力してください")
                        else:
                            place = match[x][y]
                            if not place == 3:
                                await message.channel.send("そこは置けません")
                            else:
                                break

            if timeout:
                break

            match[x][y] = index + 1 #石を置く

            #置けるところを表示していたが、ここで消す
            for line in match:
                temp = 0
                for cell in line:
                    if cell == 3:
                        line[temp] = 0
                    temp += 1

            #反転の判定
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    check = match[x+i][y+j]
                    reverse_list = []
                    if check == 2 - index:
                        reverse_list.append((x+i, y+j))
                        temp = 2
                        while True:
                            if match[x+i*temp][y+j*temp] == 0: #向かった先に何もなかったら
                                break
                            elif match[x+i*temp][y+j*temp] == 2 - index: #向かった先も相手の色がだったら
                                reverse_list.append((x+i*temp, y+j*temp))
                                temp += 1
                            else: #向かった先に自分の色があったら
                                for r in reverse_list:
                                    match[r[0]][r[1]] = index + 1 #自分の色にする
                                break

        else: #パスの時の動作
            if series_pass:
                b = 0
                w = 0
                for line in match[1:size+1]:
                    for cell in line[1:size+1]:
                        if cell == 1:
                            b += 1
                        elif cell == 2:
                            w += 1
                msg = (
                    "連続パス！試合終了！\n"
                    f"{player_list[0].name}: {b}\n"
                    f"{player_list[1].name}: {w}"
                )
                await message.channel.send(f"{msg}")
                break
            series_pass = True
            await message.channel.send(f"{teban_member.name}さんはパス！")

        #次に置けるところの探索
        x = 1
        for line in match[1:size+1]:
            y = 1
            for cell in line[1:size+1]:
                if cell == 2- index: #今の手番の相手の石を見つけたら
                    for i in (-1, 0, 1):
                        for j in (-1, 0, 1):
                            check = match[x+i][y+j] #見つかった石の周り8方向をcheck(自身もチェック対象になるが次のifではじかれる)
                            if check == index + 1: #自身の周りに相手の石を見つけたら
                                #(x, y) -> 自身
                                #(x+i, y+j) -> 自身の周りの石
                                temp = 2
                                #whileが始まる時、既に進むべき道は決まっているので1方向だけを見ればいい(*temp)
                                while True:
                                    if match[x+i*temp][y+j*temp] == 2 - index: #向かった先が自分の色なら
                                        break
                                    elif match[x+i*temp][y+j*temp] == index + 1: #向かった先も相手の色がだったら
                                        temp += 1
                                    else: #向かった先に何もなかったら
                                        match[x+i*temp][y+j*temp] = 3
                                        break
                y += 1
            x += 1

        finish = True
        for line in match[1:size+1]:
            for cell in line[1:size+1]:
                if cell == 0 or cell == 3:
                    finish = False
                    break

        if finish:
            create_pic_othello(match, size)
            f = discord.File("othello.png")
            b = 0
            w = 0
            for line in match[1:size+1]:
                for cell in line[1:size+1]:
                    if cell == 1:
                        b += 1
                    elif cell == 2:
                        w += 1
            msg = (
                f"{player_list[0].name}: {b}\n"
                f"{player_list[1].name}: {w}"
            )
            await message.channel.send(msg, file=f)
            break

#0 -> 2, 1 -> 1 = 2 - index
#0 -> 1, 1 -> 2 = index + 1

    about_othello.clear()