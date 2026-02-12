import asyncio
import discord
import os
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv
 

load_dotenv()
TOKEN = os.getenv('TOKEN')  

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.command(aliases=['cryptohack', 'stats'])
async def ch(ctx, username: str = "h4n13"):
    async def fetch_user(session, name):
        url = f"https://cryptohack.org/api/user/{name}/"
        async with session.get(url) as response:
            if response.status != 200:
                return None
            return await response.json()

    def format_solves(payload):
        solved_challenges = payload.get("solved_challenges")
        if isinstance(solved_challenges, list): 
            count = 0
            for item in solved_challenges:
                category = ""
                if isinstance(item, dict):
                    category = str(item.get("category", ""))
                if category.strip().lower() == "ctf archived":
                    continue
                count += 1
            return str(count)
        solves = payload.get("solves")
        if isinstance(solves, dict):
            solved = solves.get("solved") or solves.get("total") or solves.get("count")
            total = solves.get("total") or solves.get("max") or solves.get("available")
            if solved is not None and total is not None:
                return f"{solved} / {total}"
            return str(solved) if solved else "N/A"
        return "N/A"

    def parse_rank(value):
        text = str(value).strip()
        return int(text) if text.isdigit() else 999999

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    if username.lower() == "whip":
        list_path = os.path.join(os.path.dirname(__file__), "list.txt")
        with open(list_path, "r", encoding="utf-8") as list_file:
            raw_list = list_file.read().strip()

        usernames = [item.strip() for item in raw_list.replace('\n', ',').split(",") if item.strip()]

       

        loading_msg = await ctx.send("🔍 Các bé giỏi qué 🫃")
        entries = []

        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            for name in usernames[:10]:
                data = await fetch_user(session, name)
                await asyncio.sleep(0.5)
                if not data:
                    entries.append({
                        "name": name,
                        "url": f"https://cryptohack.org/user/{name}/",
                        "rank_value": 999999,
                        "rank_text": "N/A",
                        "score_text": "N/A",
                        "solves_text": "N/A",
                    })
                    continue

                score = data.get('score', 'N/A')
                rank = data.get('rank', 'N/A')
                solves = format_solves(data)
                display_name = data.get('username', name)
                rank_value = parse_rank(rank)

                entries.append({
                    "name": display_name,
                    "url": f"https://cryptohack.org/user/{name}/",
                    "rank_value": rank_value,
                    "rank_text": f"#{rank}",
                    "score_text": f"{score}",
                    "solves_text": f"{solves}",
                })

        entries.sort(key=lambda item: item["rank_value"])

        embed = discord.Embed(color=0xadd8e6)

        for i,entry in enumerate(entries):
            field_name = f"**{i+1}.{entry['name']}**"
            field_value = (
                f"👤 Profile: **[{entry['name']}]({entry['url']})**\n"
                f"🏆 Rank {entry['rank_text']}\n"
                f"⭐ Score **{entry['score_text']} / 16655**\n"
                f"✅ Solves **{entry['solves_text']} / 233**\n\n\n\n"
            )
            embed.add_field(name=field_name, value=field_value, inline=True)
            
    
        await loading_msg.edit(content="", embed=embed)
        return

    url = f"https://cryptohack.org/api/user/{username}/"
    loading_msg = await ctx.send(f"🔍 Bé **{username}** giỏi qué 🫃")

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        data = (await asyncio.gather(fetch_user(session, username), return_exceptions=True))[0]

        if isinstance(data, Exception):
            data = None

    if not data:
        await loading_msg.edit(content=f"❌ Không tìm thấy bé **{username}**")
        return

    embed = discord.Embed(
        title=f"{data.get('username', username)}",
        url=f"https://cryptohack.org/user/{username}/",
        color=0x00ff00
    )
    
    score = data.get('score', 'N/A')
    rank = data.get('rank', 'N/A')
    solves = format_solves(data)

    embed.add_field(name="🏆 Rank", value=f"#{rank}", inline=False)
    embed.add_field(name="⭐ Score", value=f"{score}", inline=False)
    embed.add_field(name="✅ Solves", value=f"{solves}", inline=False)
    embed.set_thumbnail(url="https://cryptohack.org/static/img/logo_4.png")

    await loading_msg.edit(content="", embed=embed)

bot.run(TOKEN)