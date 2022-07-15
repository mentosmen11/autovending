import discord, uuid, sqlite3, os, asyncio, requests, random, traceback, licensing, setting, traceback
from discord_webhook import DiscordWebhook, DiscordEmbed
from discord_components import DiscordComponents, Button, ButtonStyle, Select, Interaction, SelectOption
import funcs as fc
from funcs import embed

client = discord.Client()
DiscordComponents(client)

@client.event
async def on_message(msg):
    if msg.author.id == setting.adminid:
        if msg.content.startswith("!생성 "):
            gen_amount = msg.content.split(" ")[1]
            if gen_amount.isdigit() and (10 >= int(gen_amount) > 0):
                generated_keys = []
                con, cur = fc.start_db()
                for n in range(int(gen_amount)):
                    key = str(uuid.uuid4()).upper() + "/VEND"
                    cur.execute("INSERT INTO keys VALUES(?, ?);", (key, 30))
                    con.commit()
                    generated_keys.append(key)
                con.close()
                generated_keys_string = "\n".join(generated_keys)
                await msg.channel.send(embed=embed("success", "코드 생성됨" , generated_keys_string))
            else:
                await msg.channel.send(embed=embed("error", "생성 실패" , "코드 갯수가 잘못되었습니다."))

    if msg.guild != None and (msg.author.id == msg.guild.owner_id or msg.author.id == setting.adminid):
        if msg.content.startswith("!라이센스 "):
            if (fc.is_guild_valid(msg.guild.id)[0]):
                await msg.channel.send(embed=embed("error", "오류", "이미 등록된 서버입니다. 연장은 패널에서 부탁드립니다."))
                return
            key = msg.content.split(" ")[1]
            con, cur = fc.start_db()
            cur.execute("SELECT * FROM keys WHERE key == ?;", (key,))
            key_info = cur.fetchone()
            if key_info == None:
                con.close()
                await msg.channel.send(embed=embed("error", "오류", "존재하지 않는 코드입니다."))
                return
            else:
                cur.execute("DELETE FROM keys WHERE key == ?;", (key,))
                con.commit()
                con.close()
                pw = str(uuid.uuid4())
                await msg.channel.send(embed=embed("success", "성공", f"패널 접속 : {setting.panel}\n아이디 : {str(msg.guild.id)}\n비밀번호 : {pw}"))
            
            con, cur = fc.start_db(msg.guild.id)
            cur.execute("CREATE TABLE configs (expiringdate TEXT, panelpw TEXT, msgid INTEGER, cultureid TEXT, culturepw TEXT, adminlog TEXT, buylog TEXT);")
            con.commit()
            cur.execute("CREATE TABLE products (id TEXT, name TEXT, price INTEGER, stocks TEXT);")
            con.commit()
            cur.execute("CREATE TABLE users (id INTEGER, balance INTEGER);")
            con.commit()
            cur.execute("INSERT INTO configs VALUES(?, ?, ?, ?, ?, ?, ?);", (licensing.make_new_expiringdate(int(key_info[1])), pw, 0, "", "", "", ""))
            con.commit()
            con.close()

        if msg.content == "!버튼":
            try:
                await msg.delete()
            except:
                pass
            button_msg = await msg.channel.send(embed=discord.Embed(color=0x00ff00, title="메뉴 선택하기", description="원하시는 버튼을 클릭해주세요."), components=[[Button(label="제품", id="list", style=ButtonStyle.green), Button(label="충전", id="charge", style=ButtonStyle.green), Button(label="정보", id="info", style=ButtonStyle.green), Button(label="구매", id="buy", style=ButtonStyle.green)]])
            con, cur = fc.start_db(msg.guild.id)
            cur.execute("UPDATE configs SET msgid = ?;", (button_msg.id,))
            con.commit()
            con.close()

@client.event
async def on_button_click(interaction: Interaction):
    if fc.is_guild_valid(interaction.message.guild.id)[0] and fc.is_guild_valid(interaction.message.guild.id)[1]:
        con, cur = fc.start_db(interaction.message.guild.id)
        cur.execute("SELECT * FROM configs;")
        msg_id = cur.fetchone()[2]
        con.close()
        if interaction.message.id == msg_id:
            con, cur = fc.start_db(interaction.message.guild.id)
            cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
            user_info = cur.fetchone()
            if user_info == None:
                cur.execute("INSERT INTO users VALUES(?, ?);", (interaction.user.id, 0))
                con.commit()
                con.close()
            else:
                con.close()
            
            if interaction.component.custom_id == "list":
                con, cur = fc.start_db(interaction.message.guild.id)
                cur.execute("SELECT * FROM products;")
                products = cur.fetchall()
                con.close()

                br = "\n"
                products_embed = embed("success", "제품", "")

                for product in products:
                    products_embed.add_field(inline=False, name=product[1], value=f"{str(product[2])}원  {br}재고 {str(len(product[3].split(br))) if product[3] != '' else '0'}개")

                await interaction.respond(embed=products_embed)

            if interaction.component.custom_id == "charge":
                con, cur = fc.start_db(interaction.message.guild.id)
                cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                user_info = cur.fetchone()
                con.close()
                if user_info == None:
                    await interaction.respond(embed=embed("error", "오류", "가입되어 있지 않습니다."))
                    return

                try:
                    try_msg = await interaction.user.send(embed=embed("success", "문화상품권 충전", "문화상품권 핀번호를 -를 포함해서 입력해주세요.\n문화상품권 충전 수수료: 0%"))
                except:
                    await interaction.respond(type=6)
                    return

                await interaction.respond(embed=embed("success", "전송 성공", "DM을 확인해 주세요."))

                try:
                    ms_msg = await client.wait_for("message", timeout=60, check=lambda m : isinstance(m.channel, discord.channel.DMChannel) and (m.author.id == interaction.user.id or m.author.id == client.user.id))
                except asyncio.TimeoutError:
                    try:
                        await try_msg.delete()
                    except:
                        return
                    return

                try:
                    await try_msg.delete()
                except:
                    pass

                if ms_msg.author.id == client.user.id:
                    return

                con, cur = fc.start_db(interaction.message.guild.id)
                cur.execute("SELECT * FROM configs;")
                configs = cur.fetchone()
                con.close()

                json_data = {"id" : configs[3], "pw" : configs[4], "pin" : ms_msg.content}
                try:
                    ms_result = requests.post("http://127.0.0.1:5000/api", json=json_data)
                    if ms_result.status_code != 200:
                        raise TypeError
                    ms_result = ms_result.json()
                except:
                    try:
                        await interaction.user.send(embed=embed("error", "오류", "알 수 없는 오류가 발생했습니다."))
                        return
                    except:
                        return

                if ms_result["result"] == False or ms_result["amount"] == 0:
                    try:
                        await interaction.user.send(embed=embed("error", "오류", f"문화상품권 자동충전에 실패했습니다.\n사유 : {ms_result['reason']}"))
                    except:
                        pass
                    try:
                        webhook = DiscordWebhook(username=client.user.name, avatar_url=str(client.user.avatar_url), url=configs[5])
                        eb = DiscordEmbed(title='문화상품권 충전 내역', color=0xff0000)
                        eb.add_embed_field(name='디스코드 태그', value=str(ms_msg.author), inline=False)
                        eb.add_embed_field(name='핀 번호', value=str(ms_msg.content), inline=False)
                        eb.add_embed_field(name='실패 사유', value=str(ms_result["reason"]), inline=False)
                        webhook.add_embed(eb)
                        webhook.execute()
                    except Exception as e:
                        print(e)
                        pass
                    return
                elif ms_result["result"] == True:
                    try:
                        await interaction.user.send(embed=embed("success", "성공", f"성공적으로 충전이 완료되었습니다.\n충전 금액 : {str(ms_result['amount'])}"))
                    except:
                        pass

                    con, cur = fc.start_db(interaction.message.guild.id)
                    cur.execute("UPDATE users SET balance = balance + ? WHERE id == ?;", (ms_result['amount'], interaction.user.id))
                    con.commit()
                    con.close()
                    try:
                        webhook = DiscordWebhook(username=client.user.name, avatar_url=str(client.user.avatar_url), url=configs[5])
                        eb = DiscordEmbed(title='문화상품권 충전 내역', color=0x00ff00)
                        eb.add_embed_field(name='디스코드 태그', value=str(ms_msg.author), inline=False)
                        eb.add_embed_field(name='핀 번호', value=str(ms_msg.content), inline=False)
                        eb.add_embed_field(name='충전 금액', value=str(ms_result["amount"]) + "원", inline=False)
                        webhook.add_embed(eb)
                        webhook.execute()
                    except:
                        pass

            if interaction.component.custom_id == "info":
                con, cur = fc.start_db(interaction.message.guild.id)
                cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                user_info = cur.fetchone()
                con.close()
                if user_info == None:
                    await interaction.respond(embed=embed("error", "오류", "가입되어 있지 않습니다."))
                    return
                else:
                    await interaction.respond(embed=embed("success", "정보", f"잔액: {user_info[1]}원\n등급: 일반"))

            if interaction.component.custom_id == "buy":
                con, cur = fc.start_db(interaction.message.guild.id)
                cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                user_info = cur.fetchone()
                cur.execute("SELECT * FROM products;")
                products = cur.fetchall()
                con.close()
                if user_info == None:
                    await interaction.respond(embed=embed("error", "오류", "가입되어 있지 않습니다."))
                    return

                options = []
                br = "\n"

                for product in products:
                    options.append(SelectOption(value=str(product[0]), label=product[1], description=f"{str(product[2])}원, 재고 {str(len(product[3].split(br))) if product[3] != '' else '0'}개"))

                try:
                    buy_choose_msg = await interaction.user.send(content=f"<@{str(interaction.user.id)}>", components=[Select(placeholder="구매하실 제품을 선택해주세요", options=options)])
                    await interaction.respond(content="DM을 확인 해 주세요..")
                except Exception as e:
                    traceback.print_exc()

                try:
                    inter = await client.wait_for("select_option", check = lambda i: i.message.id == buy_choose_msg.id and i.user.id == interaction.user.id , timeout=60)
                except asyncio.TimeoutError:
                    try:
                        await buy_choose_msg.delete()
                    except:
                        pass
                    return

                try:
                    await buy_choose_msg.delete()
                except:
                    pass
                
                selected_product_id = inter.values[0]
                con, cur = fc.start_db(interaction.message.guild.id)
                cur.execute("SELECT * FROM users WHERE id == ?;", (inter.user.id,))
                user_info = cur.fetchone()
                cur.execute("SELECT * FROM products WHERE id == ?;", (selected_product_id,))
                product_info = cur.fetchone()

                if product_info == None:
                    con.close()
                    try:
                        await inter.user.send(embed=embed("error", "오류", "알 수 없는 오류가 발생했습니다."))
                    except:
                        pass
                    return

                if product_info[2] > user_info[1]:
                    con.close()
                    try:
                        await inter.user.send(embed=embed("error", "오류", "잔액이 부족합니다."))
                    except:
                        pass
                    return

                if (len(product_info[3].split("\n")) if product_info[3] != "" else 0) == 0:
                    con.close()
                    try:
                        await inter.user.send(embed=embed("error", "오류", "재고가 부족합니다."))
                    except:
                        pass
                    return

                try:
                    await buy_choose_msg.delete()
                except:
                    pass


                con, cur = fc.start_db(interaction.message.guild.id)
                cur.execute("SELECT * FROM users WHERE id == ?;", (inter.user.id,))
                user_info = cur.fetchone()
                cur.execute("SELECT * FROM products WHERE id == ?;", (selected_product_id,))
                product_info = cur.fetchone()

                if product_info[2] > user_info[1]:
                    try:
                        await buy_choose_msg.delete()
                    except:
                        pass
                    con.close()
                    try:
                        await inter.user.send(embed=embed("error", "오류", "잔액이 부족합니다."))
                    except:
                        pass
                    return

                if (len(product_info[3].split("\n")) if product_info[3] != "" else 0)  < 1:
                    try:
                        await buy_choose_msg.delete()
                    except:
                        pass
                    con.close()
                    try:
                        await inter.user.send(embed=embed("error", "오류", "재고가 부족합니다."))
                    except:
                        pass
                    return


                cur.execute("UPDATE users SET balance = balance - ? WHERE id == ?;", (product_info[2], inter.user.id))
                con.commit()
                cur_stock = product_info[3].split("\n")
                stock_sold = random.choice(cur_stock)
                cur_stock.remove(stock_sold)
                cur.execute("UPDATE products SET stocks = ? WHERE id == ?;", ("\n".join(cur_stock), selected_product_id))
                con.commit()
                con.close()

                try:
                    await inter.user.send(embed=embed("success", "구매해주셔서 감사합니다!", f"제품 가격: {str(product_info[2])}원\n구매 후 잔액: {str(user_info[1] - product_info[2])}원"))
                    await inter.user.send(stock_sold)
                except:
                    pass

                con, cur = fc.start_db(interaction.message.guild.id)
                cur.execute("SELECT * FROM configs;")
                guild_info = cur.fetchone()

                try:
                    webhook = DiscordWebhook(username=client.user.name, avatar_url=str(client.user.avatar_url), url=guild_info[6])
                    eb = DiscordEmbed(color=0x00ff00, description=f"`익명` 구매자 님 {product_info[1]} 제품 구매 진심으로 감사합니다.")
                    webhook.add_embed(eb)
                    webhook.execute()
                except:
                    pass

                try:
                    webhook = DiscordWebhook(username=client.user.name, avatar_url=str(client.user.avatar_url), url=guild_info[5])
                    eb = DiscordEmbed(title='제품 구매 내역', color=0x00ff00)
                    eb.add_embed_field(name='디스코드 태그', value=str(inter.user), inline=False)
                    eb.add_embed_field(name='제품 이름', value=str(product_info[1]), inline=False)
                    eb.add_embed_field(name='구매 금액', value=str(product_info[2]) + "원", inline=False)
                    eb.add_embed_field(name='구매한 코드', value=str(stock_sold) , inline=False)
                    webhook.add_embed(eb)
                    webhook.execute()
                except:
                    pass
    else:
        await interaction.respond(type=6)

client.run(setting.token)