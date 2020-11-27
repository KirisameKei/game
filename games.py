import asyncio
import datetime
import json
import os
import random
import traceback

import discord
import requests
from PIL import Image, ImageDraw, ImageFont

intents = discord.Intents.all()
client3 = discord.Client(intents=intents)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

where_from = os.getenv("where_from")

othello_member_list = []
ox_member_list = []

def unexpected_error():
    """
    予期せぬエラーが起きたときの対処
    エラーメッセージ全文と発生時刻を通知"""

    now = datetime.datetime.now().strftime("%H:%M") #今何時？
    error_msg = f"```\n{traceback.format_exc()}```" #エラーメッセージ全文
    error_content = {
        "content": "<@523303776120209408>", #けいにメンション
        "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
        "embeds": [ #エラー内容・発生時間まとめ
            {
                "title": "エラーが発生しました",
                "description": error_msg,
                "color": 0xff0000,
                "footer": {
                    "text": now
                }
            }
        ]
    }
    error_notice_webhook_url = os.getenv("error_notice_webhook")
    requests.post(error_notice_webhook_url, json.dumps(error_content), headers={"Content-Type": "application/json"}) #エラーメッセをウェブフックに投稿


@client3.event
async def on_ready():
    try:
        ch = client3.get_channel(597978849476870153)
        await ch.send(f"{client3.user.name}がログインしました(from: {where_from})")
    except:
        unexpected_error()


@client3.event
async def on_message(message):
    try:
        if message.author.bot:
            return

        if client3.user in message.mentions:
            if not message.author.bot:
                await message.channel.send(where_from)

        if message.guild is None:
            for i in range(5):
                await message.channel.send("DMに来るんじゃねぇ馬鹿野郎！")
            return

        if message.guild.id == 585998962050203672:
            if not message.channel.id == 691901316133290035:
                return

        if message.content == "/othello":
            if len(othello_member_list) == 0:
                othello_member_list.append(message.author.id)
                await message.channel.send("他の参加者を待っています・・・")
            elif len(othello_member_list) == 2:
                await message.channel.send("現在勝負中です。しばらくお待ちください。・・・")
                return
            elif len(othello_member_list) == 1:
                if message.author.id == othello_member_list[0]:
                    await message.channel.send("あなたは既に参加しています")
                    return
                othello_member_list.append(message.author.id)
                await message.channel.send("勝負を開始します!")
                await othello_match(message, client3, othello_member_list)

        elif message.content == "/othello_cancel":
            try:
                if not message.author.id in othello_member_list:
                    await message.channel.send("あなたじゃないです")
                    return
            except IndexError:
                await message.channel.send("誰もプレイしてません")
                return
            if len(othello_member_list) == 2:
                await message.channel.send("プレイ中は離脱できません")
                return
            othello_member_list.clear()
            await message.channel.send("キャンセルしました")

        elif message.content == "/ox_cancel":
            if not message.author.id in ox_member_list:
                await message.channel.send("あなたじゃないです")
                return
            if len(ox_member_list) == 3:
                await message.channel.send("勝負中は抜けられません")
                return
            ox_member_list.clear()
            await message.channel.send("キャンセルしました")

        elif message.content.startswith("/ox"):
            if len(ox_member_list) == 3:
                    await message.channel.send("現在勝負中です。しばらくお待ちください。・・・")
                    return
            elif message.content == "/ox":
                if len(ox_member_list) == 0:
                    await message.channel.send("募集のかけ方が不正です\nヒント: `/ox␣n`(3≦n≦9)")
                    return
                elif len(ox_member_list) == 2:
                    if message.author.id in ox_member_list:
                        await message.channel.send("あなたは既に参加しています\n`/ox_cancel`で募集を終了できます")
                        return
                    ox_member_list.append(message.author.id)
                    await message.channel.send("勝負を開始します!")
                    await ox_match(message, client3, ox_member_list)

            else:
                try:
                    size = int(message.content.split()[1])
                except ValueError:
                    await message.channel.send("3~9の範囲にしてください")
                    return
                except IndexError:
                    await message.channel.send("募集のかけ方が不正です\nヒント: `/ox␣n`(3≦n≦9)")
                    return
                if size <= 2 or size >= 10:
                    await message.channel.send("3~9の範囲にしてください")
                    return

                if len(ox_member_list) == 0:
                    ox_member_list.append(size)
                    ox_member_list.append(message.author.id)
                    await message.channel.send(f"他の参加者を待っています・・・\nサイズ: {size}×{size}")

                elif len(ox_member_list) == 2:
                    size = ox_member_list[0]
                    await message.channel.send(f"現在{size}×{size}での募集が行われています")
                    return

    except:
        unexpected_error()


def create_pic_othello(match):
    black = Image.open("black.png")
    white = Image.open("white.png")
    can = Image.open("can.png")
    null = Image.open("null_othello.png")
    othello = Image.new(mode="RGB", size=(400, 400), color=0xffffff)
    i = 0
    moji = ImageDraw.Draw(othello)
    for line in match[1:9]:
        j = 0
        for cell in line[1:9]:
            if cell == 1:
                othello.paste(black, (i, j))
            elif cell == 2:
                othello.paste(white, (i, j))
            elif cell == 3:
                othello.paste(can, (i, j))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc",size=32)
                moji.text((i+9, j+9), text=f"{int(i/50+1)}{int(j/50+1)}", font=font, fill=0x000000)
            else:
                othello.paste(null, (i, j))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc",size=32)
                moji.text((i+9, j+9), text=f"{int(i/50+1)}{int(j/50+1)}", font=font, fill=0x000000)
            j += 50
        i += 50
    othello.save("othello.png")


async def othello_match(message, client3, othello_member_list):
    match = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 3, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 2, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 2, 3, 0, 0, 0],
        [0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
    index = random.choice([0, 1])
    sente = client3.get_user(othello_member_list[index])
    if index == 0:
        index = 1
    else:
        index = 0
    gote = client3.get_user(othello_member_list[index])
    await message.channel.send(f"先手は{sente.name}さん\n後手は{gote.name}さんです")

    player_list = []
    player_list.append(sente)
    player_list.append(gote)

    def msg_check(m):
        return m.channel == message.channel

    timeout = False
    series_pass = False
    n = 0
    while True:
        index = n%2
        teban_user = player_list[index]
        create_pic_othello(match)
        f = discord.File("./othello.png")
        await message.channel.send(content=f"{teban_user.name}さんの番です", file=f)

        search_three = False
        for line in match[1:9]:
            for cell in line[1:9]:
                if cell == 3:
                    search_three = True
                    break
        if search_three:
            series_pass = False
            while True:
                try:
                    reply = await client3.wait_for("message", check=msg_check, timeout=60)
                except asyncio.TimeoutError:
                    index = (n+1)%2
                    await message.channel.send(f"タイムアウト！{player_list[index]}の勝ち！")
                    timeout = True
                    break
                else:
                    if reply.author.id != teban_user.id:
                        await message.channel.send("あなたではありません")
                    else:
                        try:
                            x = int(reply.content[0:1])
                            y = int(reply.content[1:2])
                        except ValueError:
                            await message.channel.send("画像内にある数字を入力してください")
                        else:
                            if x <= 0 or x >= 9 or y <= 0 or y >= 10:
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
                    reverse = []
                    if index == 0 and check ==2:
                        reverse.append((x+i, y+j))
                        temp = 2
                        while True:
                            if match[x+i*temp][y+j*temp] == 0: #向かった先に何もなかったら
                                break
                            elif match[x+i*temp][y+j*temp] == 2: #向かった先も相手の色がだったら
                                reverse.append((x+i*temp, y+j*temp))
                                temp += 1
                            else: #向かった先に自分の色があったら
                                for r in reverse:
                                    match[r[0]][r[1]] = 1
                                break
                    elif index == 1 and check ==1:
                        reverse.append((x+i, y+j))
                        temp = 2
                        while True:
                            if match[x+i*temp][y+j*temp] == 0: #向かった先に何もなかったら
                                break
                            elif match[x+i*temp][y+j*temp] == 1: #向かった先も相手の色がだったら
                                reverse.append((x+i*temp, y+j*temp))
                                temp += 1
                            else: #向かった先に自分の色があったら
                                for r in reverse:
                                    match[r[0]][r[1]] = 2
                                break

        else:
            if series_pass:
                b = 0
                w = 0
                for line in match[1:9]:
                    for cell in line[1:9]:
                        if cell == 1:
                            b += 1
                        elif cell == 2:
                            w += 1
                msg = (
                    "連続パス！試合終了！\n"
                    f"{sente.name}: {b}\n"
                    f"{gote.name}: {w}"
                )
                await message.channel.send(content=f"{msg}")
                break
            series_pass = True
            await message.channel.send(f"{teban_user.name}さんはパス！")

        #次に置けるところの探索
        x = 1
        for line in match[1:9]: #1列目と10列目は全て0なので確認しない
            y = 1
            for cell in line[1:9]: #1つ目と10つ目は0なので確認しない
                if index == 0 and cell == 2: #今の手番が黒(次が白)の時白の石を見つけたら
                    for i in (-1, 0, 1):
                        for j in (-1, 0, 1):
                            check = match[x+i][y+j] #見つかった石の周り8方向をcheck(自身もチェック対象になるが次のifではじかれる)
                            if check == 1: #自身の周りに相手の石を見つけたら
                                #(x, y) -> 自身
                                #(x+i, y+j) -> 自身の周りの石
                                temp = 2
                                #whileが始まる時、既に進むべき道は決まっているので1方向だけを見ればいい(*temp)
                                while True:
                                    if match[x+i*temp][y+j*temp] == 2: #向かった先が自分の色なら
                                        break
                                    elif match[x+i*temp][y+j*temp] == 1: #向かった先も相手の色がだったら
                                        temp += 1
                                    else: #向かった先に何もなかったら
                                        match[x+i*temp][y+j*temp] = 3
                                        break
                elif index == 1 and cell == 1:
                    for i in (-1, 0, 1):
                        for j in (-1, 0, 1):
                            check = match[x+i][y+j]
                            if check == 2:
                                temp = 2
                                while True:
                                    if match[x+i*temp][y+j*temp] == 1: #向かった先が自分の色なら
                                        break
                                    elif match[x+i*temp][y+j*temp] == 2: #向かった先も相手の色がだったら
                                        temp += 1

                                    else: #向かった先に何もなかったら
                                        match[x+i*temp][y+j*temp] = 3
                                        break
                y += 1
            x += 1

        end = True
        for line in match[1:9]:
            for cell in line[1:9]:
                if cell == 0 or cell == 3:
                    end = False
                    break

        if end:
            create_pic_othello(match)
            f = discord.File("othello.png")
            b = 0
            w = 0
            for line in match[1:9]:
                for cell in line[1:9]:
                    if cell == 1:
                        b += 1
                    elif cell == 2:
                        w += 1
            msg = (
                f"{sente.name}: {b}\n"
                f"{gote.name}: {w}"
            )
            await message.channel.send(content=msg, file=f)
            break

        n += 1

    othello_member_list.clear()


def create_pic_ox(match, size):
    of = Image.open("o.png")
    xf = Image.open("x.png")
    nullf = Image.open("null.png")
    pict = Image.new("RGB", (size*50, size*50))

    moji = ImageDraw.Draw(pict)
    x = 0
    for line in match:
        y = 0
        for cell in line:
            if cell == -1:
                pict.paste(of, (x*50, y*50))
            elif cell == 1:
                pict.paste(xf, (x*50, y*50))
            else:
                pict.paste(nullf, (x*50, y*50))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc",size=32)
                moji.text((x*50+9, y*50+9), text=f"{x+1}{y+1}", font=font, fill=0x000000)
            y += 1
        x += 1

    pict.save("pict.png")


async def ox_match(message, client3, ox_member_list):
    size = ox_member_list[0]
    match = []
    for i in range(size):
        line = []
        for j in range(size):
            line.append(0)
        match.append(line)

    index = random.choice([0, 1])
    sente = client3.get_user(ox_member_list[index+1])
    if index == 0:
        index = 1
    else:
        index = 0
    gote = client3.get_user(ox_member_list[index+1])
    await message.channel.send(f"先手は{sente.name}さん\n後手は{gote.name}さんです")

    player_list = []
    player_list.append(sente)
    player_list.append(gote)

    def check(m):
        return m.channel == message.channel

    flag = False
    for i in range(size*size):
        index = i%2
        teban_user = player_list[index]
        create_pic_ox(match, size)
        f = discord.File("./pict.png")
        await message.channel.send(file=f)
        while True:
            try:
                reply = await client3.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                index = (i+1)%2
                await message.channel.send(f"タイムアウト！{player_list[index]}の勝ち！")
                flag = True
                break
            else:
                if reply.author.id != teban_user.id:
                    await message.channel.send("あなたではありません")
                else:
                    try:
                        x = int(reply.content[0:1]) - 1
                        y = int(reply.content[1:2]) - 1
                    except ValueError:
                        await message.channel.send("画像内の数字を入力してください")
                    else:
                        if teban_user == sente:
                            item = -1
                        else:
                            item = 1
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

        for line in match:
            if sum(line) == size * -1:
                create_pic_ox(match, size)

                f = discord.File("./pict.png")
                await message.channel.send(content=f"{sente.name}の勝ち！縦", file=f)
                flag = True
                break
            elif sum(line) == size:
                create_pic_ox(match, size)
                f = discord.File("./pict.png")
                await message.channel.send(content=f"{gote.name}の勝ち！縦", file=f)
                flag = True
                break

        if not flag:
            for n in range(size):
                s = 0
                for line in match:
                    s += line[n]
                if s == size * -1:
                    create_pic_ox(match, size)
                    f = discord.File("./pict.png")
                    await message.channel.send(content=f"{sente.name}の勝ち！横", file=f)
                    flag = True
                    break
                elif s == size:
                    create_pic_ox(match, size)
                    f = discord.File("./pict.png")
                    await message.channel.send(content=f"{gote.name}の勝ち！横", file=f)
                    flag = True
                    break

        if not flag:
            s1 = 0
            s2 = 0
            for n in range(size):
                s1 += match[n][n]
                if s1 == size * -1:
                    create_pic_ox(match, size)
                    f = discord.File("./pict.png")
                    await message.channel.send(content=f"{sente.name}の勝ち！", file=f)
                    flag = True
                    break
                elif s1 == size:
                    create_pic_ox(match, size)
                    f = discord.File("./pict.png")
                    await message.channel.send(content=f"{gote.name}の勝ち！", file=f)
                    flag = True
                    break

                s2 += match[n][size-1-n]
                if s2 == size * -1:
                    create_pic_ox(match, size)
                    f = discord.File("./pict.png")
                    await message.channel.send(content=f"{sente.name}の勝ち！", file=f)
                    flag = True
                    break
                elif s2 == size:
                    create_pic_ox(match, size)
                    f = discord.File("./pict.png")
                    await message.channel.send(content=f"{gote.name}の勝ち！", file=f)
                    flag = True
                    break

        if flag:
            break
    if not flag:
        create_pic_ox(match, size)
        f = discord.File("./pict.png")
        await message.channel.send(content="引き分け！", file=f)

    ox_member_list.clear()


client3.run(os.getenv("discord_bot_token_3"))