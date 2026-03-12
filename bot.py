import asyncio
import discord
import os
import re
import aiohttp
import json
from discord.ext import commands
from dotenv import load_dotenv
import sys
 

load_dotenv()
TOKEN = os.getenv('TOKEN')  
TEST_TOKEN = os.getenv('TEST_TOKEN')  

intents = discord.Intents.default()
intents.message_content = True
if len(sys.argv) == 2 and sys.argv[1] == 'test':
    bot = commands.Bot(command_prefix='.', intents=intents)
else:
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
                if category == "CTF Archive":
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
                f"🏆 Rank **{entry['rank_text']}**\n"
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
    embed.add_field(name="⭐ Score", value=f"{score} / 16655", inline=False)
    embed.add_field(name="✅ Solves", value=f"{solves} / 233", inline=False)
    embed.set_thumbnail(url="https://cryptohack.org/static/img/logo_4.png")

    await loading_msg.edit(content="", embed=embed)

@bot.command(aliases=['rm'])
async def rootme(ctx, username: str):
    url = f"https://www.root-me.org/{username}?inc=score&lang=en"
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    # }
    
    loading_msg = await ctx.send(f"🔍 Bé **{username}** giỏi qué 🫃")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await loading_msg.edit(content=f"❌ Không tìm thấy bé **{username}**")
                    return
                
                html_content = await response.text()
    except Exception as e:
        await loading_msg.edit(content=f"❌ Lỗi khi kết nối: {e}")
        return

    # with open("sample_response.txt", 'wb') as f:
    #     f.write(html_content.encode())
    lines = html_content.split('\n')
    score = "N/A"
    solved = "N/A"
    total = "N/A"
    in_cracking = False

    for line in lines:
        # Find the specific Cracking header, excluding the sidebar menu (which has class="smenu")
        if ">Cracking</a>" in line and "smenu" not in line:
            # print(line)
            in_cracking = True
            continue
        
        if in_cracking:
            # Parse Score: <b>1920</b>&nbsp;Points<br/>
            if "Points" in line and "<b>" in line:
                # print(line)
                match = re.search(r'<b>(\d+)</b>', line)
                if match:
                    score = match.group(1)
                    # print(score)

            # Parse Solves: <b>57</b>&nbsp;/&nbsp;70
            elif "/" in line and "<b>" in line:
                # print(line)
                try:
                    match = re.search(r'<b>(\d+)</b>&nbsp;/&nbsp;(\d+)', line)
                    if match:
                        solved = match.group(1)
                        total = match.group(2)
                        # print(f'{solved}/{total}')
                        break # We found both parts, stop parsing
                except:
                    pass

    if score != "N/A":
        embed = discord.Embed(title=f"{username}", url=url, color=0xff4b4b)
        embed.add_field(name="⭐ Score", value=f"{score}", inline=False)
        embed.add_field(name="✅ Solves", value=f"{solved} / {total}", inline=False)
        embed.set_thumbnail(url="https://www.root-me.org/squelettes/img/rblackGrand32.png")
        
        await loading_msg.edit(content="", embed=embed)
    else:
         await loading_msg.edit(content=f"❌ Không tìm thấy thông tin Cracking cho bé **{username}**")

@bot.command(aliases=['pc'])
async def pico(ctx, username: str):
    async def fetch_participant(session, user_id):
        url = f"https://play.picoctf.org/api/participants/{user_id}/"
        async with session.get(url) as response:
            if response.status != 200:
                return None
            return await response.json(content_type=None)

    async def fetch_category_stats(session, user_id):
        url = f"https://play.picoctf.org/api/participants/{user_id}/category_stats/"
        async with session.get(url) as response:
            if response.status != 200:
                return None
            return await response.json(content_type=None)

    def extract_name(entry, fallback):
        if isinstance(entry, dict):
            value = entry.get("username")
            if value:
                return str(value)
        return str(fallback)

    def extract_score(entry):
        if not isinstance(entry, dict):
            return "N/A"
        score = entry.get("individual_score")
        return str(score) if score is not None else "N/A"

    def score_sort_key(score_text):
        try:
            return (1, float(str(score_text).replace(",", "")))
        except (ValueError, TypeError):
            return (0, -1)

    def is_user_id(value):
        return re.fullmatch(r"\d+", value) is not None

    def load_user_map(map_path):
        if not os.path.exists(map_path):
            return {}
        try:
            with open(map_path, "r", encoding="utf-8") as map_file:
                data = json.load(map_file)
            if isinstance(data, dict):
                return {str(k).strip().lower(): str(v).strip() for k, v in data.items() if str(k).strip() and str(v).strip()}
        except Exception:
            return {}
        return {}

    def save_user_map(map_path, username_to_id):
        with open(map_path, "w", encoding="utf-8") as map_file:
            json.dump(username_to_id, map_file, ensure_ascii=False, indent=2)

    def format_category_status(stats_payload):
        if not isinstance(stats_payload, dict):
            return "N/A"
        categories = stats_payload.get("categories")
        if not isinstance(categories, dict) or not categories:
            return "N/A"

        lines = []
        for category_name in sorted(categories.keys()):
            category_data = categories.get(category_name)
            if not isinstance(category_data, dict):
                continue
            solved = category_data.get("solved", 0)
            total = category_data.get("total", 0)
            points_earned = category_data.get("points_earned", 0)
            points_available = category_data.get("points_available", 0)
            lines.append(
                f"• {category_name}: {solved}/{total} ({points_earned}/{points_available} pts)"
            )

        return "\n".join(lines) if lines else "N/A"

    loading_msg = await ctx.send(f"Bé **{username}** giỏi qué :pregnant_man:")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    }
    timeout = aiohttp.ClientTimeout(total=20)
    user_map_path = os.path.join(os.path.dirname(__file__), "pico_user_map.json")

    if username.strip().lower() == "whip":
        list_path = os.path.join(os.path.dirname(__file__), "list_pico.txt")
        with open(list_path, "r", encoding="utf-8") as list_file:
            raw_list = list_file.read().strip()

        user_ids = [item.strip() for item in raw_list.replace("\n", ",").split(",") if item.strip()]
        entries = []
        username_to_id = {}

        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            for user_id in user_ids:
                data = await fetch_participant(session, user_id)
                if not data:
                    entries.append({"name": user_id, "score": "N/A"})
                    continue
                resolved_name = extract_name(data, user_id)
                username_to_id[resolved_name.strip().lower()] = str(user_id).strip()
                entries.append({
                    "name": resolved_name,
                    "score": extract_score(data),
                })

        save_user_map(user_map_path, username_to_id)

        entries.sort(key=lambda item: score_sort_key(item["score"]), reverse=True)

        embed = discord.Embed(title="whip", url="https://play.picoctf.org/events/79/scoreboards", color=0xF7D247)
        for i, item in enumerate(entries):
            field_name = f"**{i+1}.{item['name']}**"
            field_value = (
                f"⭐ Score **{item['score']}**\n"
            )
            embed.add_field(name=field_name, value=field_value, inline=True)

        await loading_msg.edit(content="", embed=embed)
        return

    raw_input = username.strip()
    user_id = raw_input
    if not is_user_id(raw_input):
        username_to_id = load_user_map(user_map_path)
        user_id = username_to_id.get(raw_input.lower())
        if not user_id:
            await loading_msg.edit(content=f"❌ Không tìm thấy username **{username}**. Hãy chạy `!pico whip` để cập nhật danh sách.")
            return

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        data, category_stats = await asyncio.gather(
            fetch_participant(session, user_id),
            fetch_category_stats(session, user_id),
        )

    if not data:
        await loading_msg.edit(content=f"❌ Không tìm thấy bé **{username}**")
        return

    entry = {
        "name": extract_name(data, username),
        "score": extract_score(data),
    }
    category_status_text = format_category_status(category_stats)

    embed = discord.Embed(title=f"{entry['name']}", url=f"https://play.picoctf.org/participants/{user_id}/", color=0xF7D247)
    embed.add_field(name="⭐ Score", value=f"{entry['score']}", inline=False)
    embed.add_field(name="📚 Category Status", value=category_status_text, inline=False)
    embed.set_thumbnail(url="https://play.picoctf.org/static/media/picoctf-logo.7f40395d.svg")
    await loading_msg.edit(content="", embed=embed)

# @bot.command(aliases=['pc'])
# @commands.cooldown(1, 10, commands.BucketType.user)
# async def pico(ctx, username: str):
#     login_username = os.getenv("PICO_USERNAME")
#     login_password = os.getenv("PICO_PASSWORD")
#     pico_cf_clearance = os.getenv("PICO_CF_CLEARANCE", "").strip()
#     pico_csrftoken = os.getenv("PICO_CSRFTOKEN", "").strip()

#     if not login_username or not login_password:
#         await ctx.send("❌ Thiếu `PICO_USERNAME` hoặc `PICO_PASSWORD` trong .env")
#         return

#     loading_msg = await ctx.send(f"🔍 Đang tìm picoCTF cho bé **{username}**")

#     is_whip_mode = username.strip().lower() == "whip"

#     def extract_name(item):
#         return (
#             item.get("name")
#             or item.get("username")
#             or item.get("display_name")
#             or "N/A"
#         )

#     def extract_score(item):
#         for key in ("score", "points", "total_score"):
#             if key in item and item.get(key) is not None:
#                 return str(item.get(key))
#         return "N/A"

#     def score_sort_key(score_text):
#         try:
#             return (1, float(str(score_text).replace(",", "")))
#         except (ValueError, TypeError):
#             return (0, -1)

#     target_users = {}
#     if is_whip_mode:
#         list_path = os.path.join(os.path.dirname(__file__), "list_pico.txt")
#         with open(list_path, "r", encoding="utf-8") as list_file:
#             raw_list = list_file.read().strip()

#         usernames = [item.strip() for item in raw_list.replace("\n", ",").split(",") if item.strip()]
#         for name in usernames[:10]:
#             target_users[name.lower()] = name
#     else:
#         target_users[username.strip().lower()] = username.strip()

#     base_headers = {
#         "accept": "application/json, text/plain, */*",
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
#     }

#     login_url = "https://play.picoctf.org/api/_allauth/browser/v1/auth/login"
#     csrf_bootstrap_url = "https://play.picoctf.org/api/_allauth/browser/v1/auth/session"
#     scores_url = "https://play.picoctf.org/api/scoreboards/7006/scores/"

#     timeout = aiohttp.ClientTimeout(total=20)
#     async with aiohttp.ClientSession(headers=base_headers, timeout=timeout) as session:
#         if pico_cf_clearance:
#             session.cookie_jar.update_cookies({"cf_clearance": pico_cf_clearance}, response_url="https://play.picoctf.org")
#         if pico_csrftoken:
#             session.cookie_jar.update_cookies({"csrftoken": pico_csrftoken}, response_url="https://play.picoctf.org")

#         # Seed baseline cookies first.
#         async with session.get("https://play.picoctf.org/"):
#             pass

#         # picoCTF sets csrftoken on this endpoint even when it returns 401.
#         bootstrap_headers = {
#             "referer": "https://play.picoctf.org/events/79/scoreboards",
#             "accept": "application/json, text/plain, */*",
#             "x-csrftoken": "",
#         }
#         async with session.get(csrf_bootstrap_url, headers=bootstrap_headers):
#             pass

#         cookies = session.cookie_jar.filter_cookies("https://play.picoctf.org")
#         csrf_cookie = cookies.get("csrftoken")

#         if not csrf_cookie or not csrf_cookie.value:
#             await loading_msg.edit(content="❌ Không lấy được csrftoken từ picoCTF session endpoint")
#             print("[pico] missing csrftoken after GET /api/_allauth/browser/v1/auth/session")
#             return

#         login_headers = {
#             "content-type": "application/json",
#             "accept": "application/json, text/plain, */*",
#             "origin": "https://play.picoctf.org",
#             "referer": "https://play.picoctf.org/login",
#             "x-csrftoken": csrf_cookie.value,
#         }

#         login_payload = {
#             "username": login_username,
#             "password": login_password,
#         }

#         async with session.post(login_url, json=login_payload, headers=login_headers) as login_response:
#             if login_response.status >= 400:
#                 login_text = await login_response.text()
#                 await loading_msg.edit(content=f"❌ Đăng nhập picoCTF thất bại (HTTP {login_response.status})")
#                 print(f"[pico] login failed: HTTP {login_response.status}")
#                 print("[pico] hint: set PICO_CF_CLEARANCE and PICO_CSRFTOKEN in .env from a logged-in browser session if Cloudflare/CSRF blocks aiohttp")
#                 print(login_text)
#                 return

#         matched_entries = {}
#         pages_scraped = 0

#         for page in range(1, 66):
#             params = {"page": page, "page_size": 50}
#             async with session.get(scores_url, params=params) as response:
#                 if response.status != 200:
#                     print(f"[pico] page {page} failed: HTTP {response.status}")
#                     continue

#                 page_json = await response.json(content_type=None)
#                 pages_scraped += 1

#                 results = page_json.get("results", [])
#                 if not isinstance(results, list):
#                     continue

#                 for item in results:
#                     if not isinstance(item, dict):
#                         continue

#                     candidate = str(extract_name(item)).strip().lower()
#                     if candidate in target_users and candidate not in matched_entries:
#                         matched_entries[candidate] = {
#                             "name": extract_name(item),
#                             "score": extract_score(item),
#                             "page": page,
#                         }

#                         # In normal mode, stop as soon as we find the username.
#                         if not is_whip_mode:
#                             break

#                 if not is_whip_mode and matched_entries:
#                     break

#         print(f"[pico] pages scraped: {pages_scraped}")
#         print(f"[pico] matches found: {len(matched_entries)}")

#     if is_whip_mode:
#         embed = discord.Embed(title="whip", url="https://play.picoctf.org/events/79/scoreboards", color=0xF7D247)
#         display_entries = []
#         for raw_name in target_users.values():
#             entry = matched_entries.get(raw_name.lower())
#             score = entry["score"] if entry else "N/A"
#             display_name = entry["name"] if entry else raw_name
#             display_entries.append({"name": display_name, "score": score})

#         display_entries.sort(key=lambda item: score_sort_key(item["score"]), reverse=True)

#         for item in display_entries:
#             embed.add_field(name=f"{item['name']}", value=f"⭐ Score: **{item['score']}**", inline=False)
#         await loading_msg.edit(content="", embed=embed)
#         return

#     key = username.strip().lower()
#     entry = matched_entries.get(key)
#     if not entry:
#         await loading_msg.edit(content=f"❌ Không tìm thấy bé **{username}**")
#         return

#     embed = discord.Embed(title=f"{entry['name']}", url="https://play.picoctf.org/events/79/scoreboards", color=0xF7D247)
#     embed.add_field(name="⭐ Score", value=f"{entry['score']}", inline=False)
#     embed.set_thumbnail(url="https://play.picoctf.org/static/media/picoctf-logo.7f40395d.svg")
#     await loading_msg.edit(content="", embed=embed)



if len(sys.argv) == 2 and sys.argv[1] == 'test':
    bot.run(TEST_TOKEN)
else:
    bot.run(TOKEN)
