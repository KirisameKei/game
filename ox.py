import asyncio
import random

import discord
from PIL import Image, ImageDraw, ImageFont

def create_pic_ox(match, size):
    of = Image.open("./ox/o.png")
    xf = Image.open("./ox/x.png")
    nullf = Image.open("./ox/null.png")
    pict = Image.new("RGB", (size*50, size*50))

    moji = ImageDraw.Draw(pict)
    x = 0
    for line in match:
        y = 0
        for cell in line:
            if cell == 1:
                pict.paste(of, (x*50, y*50))
            elif cell == -1:
                pict.paste(xf, (x*50, y*50))
            else:
                pict.paste(nullf, (x*50, y*50))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
                moji.text((x*50+9, y*50+9), text=f"{x+1}{y+1}", font=font, fill=0x000000)
            y += 1
        x += 1

    pict.save("ox.png")


async def match_ox(client3, message, about_ox):
    size = about_ox[0]
    match = []
    for i in range(size):
        line = []
        for j in range(size):
            line.append(0)
        match.append(line)

    temp = random.choice([0, 1])
    player_list = []
    player_list.append(about_ox[2+temp])
    if temp == 0:
        temp = 1
    else:
        temp = 0
    player_list.append(about_ox[2+temp])
    await message.channel.send(f"先手は{player_list[0].name}さん、後手は{player_list[1].name}さんです")

    def check(m):
        return m.channel == message.channel and not m.author.bot

    finish = False
    for i in range(size**2):
        index = i % 2
        teban_member = player_list[index]
        create_pic_ox(match, size)
        f = discord.File("./ox.png")
        await message.channel.send(f"{teban_member.name}さんの番です", file=f)
        while True:
            try:
                reply = await client3.wait_for("message", check=check, timeout=50)
            except asyncio.TimeoutError:
                await message.channel.send("残り10秒・・・")
                try:
                    reply = await client3.wait_for("message", check=check, timeout=10)
                except asyncio.TimeoutError:
                    next_index = (i+1)%2
                    await message.channel.send(f"タイムアウト！{player_list[next_index]}の勝ち！")
                    finish = True
                    break

            if reply.author != teban_member:
                pass
            else:
                try:
                    x = int(reply.content[0:1]) - 1
                    y = int(reply.content[1:2]) - 1
                except ValueError:
                    await message.channel.send("画像内の数字を入力してください")
                else:
                    item = index * -2 + 1
                    try:
                        num = match[x][y]
                    except IndexError:
                        await message.channel.send("画像内の数字を入力してください")
                    else:
                        if num != 0:
                            await message.channel.send("そこは埋まっています")
                        else:
                            match[x][y] = item
                            break

        if not finish:
            create_pic_ox(match, size)
            f = discord.File("./ox.png")

            #横の判定
            for line in match:
                if sum(line) == size:
                    await message.channel.send(f"{player_list[0].name}の勝ち！", file=f)
                    finish = True
                    break
                elif sum(line) == size * -1:
                    await message.channel.send(f"{player_list[1].name}の勝ち！", file=f)
                    finish = True
                    break

        if not finish:
            for n in range(size):
                s = 0
                for line in match:
                    s += line[n]
                if s == size:
                    await message.channel.send(f"{player_list[0].name}の勝ち！", file=f)
                    finish = True
                    break
                elif s == size * -1:
                    await message.channel.send(f"{player_list[1].name}の勝ち！", file=f)
                    finish = True
                    break

        if not finish:
            s1 = 0
            s2 = 0
            for n in range(size):
                s1 += match[n][n]
                if s1 == size:
                    await message.channel.send(f"{player_list[0].name}の勝ち！", file=f)
                    finish = True
                    break
                elif s1 == size * -1:
                    await message.channel.send(f"{player_list[1].name}の勝ち！", file=f)
                    finish = True
                    break

                s2 += match[n][size-1-n]
                if s2 == size:
                    await message.channel.send(f"{player_list[0].name}の勝ち！", file=f)
                    finish = True
                    break
                elif s2 == size * -1:
                    await message.channel.send(f"{player_list[1].name}の勝ち！", file=f)
                    finish = True
                    break

        if finish:
            break #タイムアウト

    if not finish:
        await message.channel.send("引き分け！", file=f)

    about_ox.clear()