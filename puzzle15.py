import asyncio
import datetime
import random

import discord
from PIL import Image, ImageDraw, ImageFont

def create_pic_puzzle15(match):
    pict = Image.new("RGB", (200, 200))
    koma = Image.open("./puzzle15/koma.png")
    null = Image.open("./puzzle15/null.png")
    moji = ImageDraw.Draw(pict)
    i = 0
    for line in match:
        j = 0
        for cell in line:
            if cell == 0:
                pict.paste(null, (i*50, j*50))
            else:
                pict.paste(koma, (i*50, j*50))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
                if cell >= 10:
                    moji.text((i*50+9, j*50+9), text=f"{cell}", font=font, fill=0x000000)
                else:
                    moji.text((i*50+25, j*50+9), text=f"{cell}", font=font, fill=0x000000)
            j += 1
        i += 1

    pict.save("./puzzle15.png")

async def play_puzzle15(client3, message, about_puzzle15):
    figure = random.sample(list(range(16)), k=16)
    match = []
    complete = [
        [1, 5, 9, 13],
        [2, 6, 10, 14],
        [3, 7, 11, 15],
        [4, 8, 12, 0]
    ]

    check_list = []
    check_complete_list = [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 0]
    #match =      [3, 2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]
    change_counter = 0
    while True:
        #生成
        counter = 0
        for i in range(4):
            line = []
            for j in range(4):
                line.append(figure[counter])
                counter += 1
            match.append(line)

        #チェック用のリストにぶち込む
        for line in match:
            for cell in line:
                check_list.append(cell)

        print(check_list)

        for i in range(16):
            if check_list[i] == check_complete_list[i]:
                pass
            else:
                wrong_number = check_list[i]
                collect_number = check_complete_list[i]
                index = check_list.index(collect_number)
                check_list[i] = collect_number
                check_list[index] = wrong_number
                change_counter += 1
                check_list = check_list

        if change_counter % 2 == 0:
            break

    timeout = False
    counter = 0
    start_time = datetime.datetime.now()
    while True:
        create_pic_puzzle15(match)
        f = discord.File("./puzzle15.png")
        await message.channel.send(file=f)
        def check(m):
            return m.channel == message.channel and m.author == message.author
        while True:
            try:
                reply = await client3.wait_for("message", check=check, timeout=50)
            except asyncio.TimeoutError:
                await message.channel.send("残り10秒・・・")
                try:
                    reply = await client3.wait_for("message", check=check, timeout=10)
                except asyncio.TimeoutError:
                    await message.channel.send("タイムアウト")
                    timeout = True
                    break

            no = False

            try:
                move = int(reply.content)
            except ValueError:
                await message.channel.send("1~15の数字を入力してください")
                no = True

            if not no:
                if move < 1 or 15 < move:
                    await message.channel.send("1~15の数字を入力してください")
                    no = True

            if not no:
                x = 0
                for line in match:
                    y = 0
                    for cell in line:
                        if cell == move:
                            move_x = x
                            move_y = y
                        elif cell == 0:
                            zero_x = x
                            zero_y = y
                        y += 1
                    x += 1

            if not no:
                if move_x == zero_x:
                    move_count = abs(move_y - zero_y)
                    if zero_y < move_y:
                        for i in range(move_count):
                            match[move_x][zero_y+i] = match[move_x][zero_y+i+1]
                        match[move_x][move_y] = 0
                    elif zero_y > move_y:
                        for i in range(move_count):
                            match[move_x][zero_y-i] = match[move_x][zero_y-i-1]
                        match[move_x][move_y] = 0
                elif move_y == zero_y:
                    move_count = abs(move_x - zero_x)
                    if zero_x < move_x:
                        for i in range(move_count):
                            match[zero_x+i][move_y] = match[zero_x+i+1][move_y]
                        match[move_x][move_y] = 0
                    elif zero_x > move_x:
                        for i in range(move_count):
                            match[zero_x-i][move_y] = match[zero_x-i-1][move_y]
                        match[move_x][move_y] = 0
                else:
                    await message.channel.send("そこは動かせません")
                    no = True

            if not no:
                break

        if timeout:
            break

        counter += 1

        if match == complete:
            goal_time = datetime.datetime.now()
            during_time = goal_time - start_time
            create_pic_puzzle15(match)
            f = discord.File("./puzzle15.png")
            await message.channel.send(f"完成！\n手数: {counter}\n時間:{during_time.seconds}秒", file=f)
            break

    about_puzzle15.clear()