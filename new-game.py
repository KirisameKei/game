import datetime
import json
import os
import traceback

import discord
import requests
from discord.ext import tasks

import othello
import ox
import syogi

intents = discord.Intents.all()
client3 = discord.Client(intents=intents)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

where_from = os.getenv("where_from")

about_ox = [] #[int, datetime.datetime, discord.Member, discord.Member]
about_othello = []
about_syogi = []

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

        #if not message.channel.id == 691901316133290035: #ミニゲーム
        if not message.channel.id == 597978849476870153: #3組
            return

        if message.content.startswith("/ox"):
            await start_ox(message)
        elif message.content.startswith("/othello"):
            await start_othello(message)
        elif message.content == "/syogi":
            await start_syogi(message)
        elif message.content == "/cancel":
            await cancel(message)

    except:
        unexpected_error()


async def start_ox(message):
    if len(about_ox) == 4: #他にプレイしている人がいたら
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if message.author in about_ox or message.author in about_othello or message.author in about_syogi:
        await message.channel.send("あなたは別のゲームに参加しているか既に参加しているため参加できません")
        return

    if len(about_ox) == 3: #先に募集している人がいたら
        if message.content == "/ox":
            about_ox.append(message.author)
            await message.channel.send("勝負を開始します！")
            await ox.match_ox(client3, message, about_ox)
        else:
            size = about_ox[0]
            await message.channel.send(f"現在{about_ox[2].name}さんが{size}×{size}で募集しています\n参加する場合`/ox`と入力してください")
            return
    else: #募集をかける立場なら
        try:
            size = int(message.content.split()[1])
        except (IndexError, ValueError):
            await message.channel.send("引数は3~9の半角数字です")
            return

        if size < 3 or size > 9:
            await message.channel.send("引数は3~9の半角数字です")
            return

        about_ox.append(size)
        about_ox.append(datetime.datetime.now())
        about_ox.append(message.author)
        await message.channel.send("他の参加者を待っています・・・")


async def start_othello(message):
    if len(about_othello) == 4: #他にプレイしている人がいたら
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if message.author in about_ox or message.author in about_othello or message.author in about_syogi:
        await message.channel.send("あなたは別のゲームに参加しているか既に参加しているため参加できません")
        return

    if len(about_othello) == 3: #先に募集している人がいたら
        if message.content == "/othello":
            about_othello.append(message.author)
            await message.channel.send("勝負を開始します！")
            await othello.match_othello(client3, message, about_othello)
        else:
            size = about_othello[0]
            await message.channel.send(f"現在{about_othello[2].name}さんが{size}×{size}で募集しています\n参加する場合`/othello`と入力してください")
            return
    else: #募集をかける立場なら
        try:
            size = int(message.content.split()[1])
        except (IndexError, ValueError):
            await message.channel.send("引数は4~8の半角数字で偶数です")
            return

        if size < 4 or size > 8:
            await message.channel.send("引数は4~8の半角数字で偶数です")
            return

        if size % 2 == 1:
            await message.channel.send("引数は4~8の半角数字で偶数です")
            return

        about_othello.append(size)
        about_othello.append(datetime.datetime.now())
        about_othello.append(message.author)
        await message.channel.send("他の参加者を待っています・・・")


async def start_syogi(message):
    if len(about_syogi) == 3: #他にプレイしている人がいたら
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if message.author in about_ox or message.author in about_othello or message.author in about_syogi:
        await message.channel.send("あなたは別のゲームに参加しているか既に参加しているため参加できません")
        return

    if len(about_syogi) == 2: #先に募集している人がいたら
        about_syogi.append(message.author)
        await message.channel.send("勝負を開始します！")
        await syogi.match_syogi(client3, message, about_syogi)

    else: #募集をかける立場なら
        about_syogi.append(datetime.datetime.now())
        about_syogi.append(message.author)
        await message.channel.send("他の参加者を待っています・・・")


async def cancel(message):
    if message.author in about_ox:
        if len(about_ox) == 4: #勝負中なら
            await message.channel.send("勝負中は抜けられません")
            return
        else:
            about_ox.clear()
            await message.channel.send("募集をキャンセルしました")

    elif message.author in about_othello:
        if len(about_othello) == 4: #勝負中なら
            await message.channel.send("勝負中は抜けられません")
            return
        else:
            about_othello.clear()
            await message.channel.send("募集をキャンセルしました")

    elif message.author in about_syogi:
        if len(about_othello) == 3: #勝負中なら
            await message.channel.send("勝負中は抜けられません")
            return
        else:
            about_syogi.clear()
            await message.channel.send("募集をキャンセルしました")

    else:
        await message.channel.send("あなたは募集を行っていません")


@client3.event
async def on_ready():
    try:
        ch = client3.get_channel(597978849476870153)
        await ch.send(f"{client3.user.name}がログインしました(from: {where_from})")
    except:
        unexpected_error()


@tasks.loop(seconds=60)
async def loop():
    await client3.wait_until_ready()

    before_30min = datetime.datetime.now() - datetime.timedelta(minutes=3)
    ch = client3.get_channel(691901316133290035) #ミニゲーム
    ch = client3.get_channel(597978849476870153) #3組
    if len(about_ox) == 3:
        if about_ox[1] <= before_30min:
            member = about_ox[2]
            about_ox.clear()
            await ch.send(f"{member.mention}\n30分間参加がなかったので募集は取り消されました")

    if len(about_othello) == 3:
        if about_othello[1] <= before_30min:
            member = about_othello[2]
            about_othello.clear()
            await ch.send(f"{member.mention}\n30分間参加がなかったので募集は取り消されました")

    if len(about_syogi) == 2:
        if about_syogi[0] <= before_30min:
            member = about_syogi[1]
            about_syogi.clear()
            await ch.send(f"{member.mention}\n30分間参加がなかったので募集は取り消されました")

loop.start()


client3.run(os.getenv("discord_bot_token_3"))