import discord
import asyncio
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core import Config, checks
import random
#Coded by PaPí#0001

class Rainbow_Six_Siege(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.data = Config.get_conf(self, identifier=62078023501206325104, force_registration=True)
        default_guild = {
            "maps": [],
            "lobbies": {},
            "channel": None
        }
        default_member = {
            "registered": False,
            "points": 0
        }
        self.data.register_guild(**default_guild)
        self.data.register_member(**default_member)

    @commands.group()
    async def rssset(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @rssset.command(name="channel")
    async def _setchannel(self, ctx, channel: discord.TextChannel):
        """Set a channel"""
        if not await self.role_check(ctx.author, ctx.guild):
            await ctx.send("You can't use this command.")
            return
        await self.data.guild(ctx.guild).channel.set(channel.id)
        await ctx.send(f"Successfully set the channel to {channel.mention}.")

    @rssset.command(name="add")
    async def addmap(self, ctx, *, name: str):
        """Add a map to the list."""
        if not await self.role_check(ctx.author, ctx.guild):
            await ctx.send("You can't use this command.")
            return

        maps_list = await self.data.guild(ctx.guild).maps()
        if name.lower() in maps_list:
            await ctx.send("That map already exists in the list.")
        elif name.lower() not in maps_list:
            maps_list.append(name.lower())
            await self.data.guild(ctx.guild).maps.set(maps_list)
            await ctx.send("Successfully added the map to the list.")

    @rssset.command(name="remove")
    async def removemap(self, ctx, *, name: str):
        """Remove a map from the list."""
        if not await self.role_check(ctx.author, ctx.guild):
            await ctx.send("You can't use this command.")
            return
        maps_list = await self.data.guild(ctx.guild).maps()
        if name.lower() in maps_list:
            maps_list.remove(name.lower())
            await self.data.guild(ctx.guild).maps.set(maps_list)
            await ctx.send(f"**{name}** was removed from the list.")
        elif name.lower() not in maps_list:
            await ctx.send(f"**{name}** is not in the list.")

    @rssset.command(name="allmaps")
    async def _allmaps(self, ctx):
        maps_list = await self.data.guild(ctx.guild).maps()
        if maps_list:
            await ctx.send(f"**Total Maps - {len(maps_list)}**\n\n{', '.join(maps_list)}")
        else:
            await ctx.send("There are no existing maps.")

    @rssset.command(name="win")
    async def _win(self, ctx, user: discord.Member, points: int):
        """Assign points to a user."""
        if not await self.role_check(ctx.author, ctx.guild):
            await ctx.send("You can't use this command.")
            return
        if await self.data.member(user).registered() == True:
            points = await self.data.member(user).points() + points
            if points > 0:
                await self.data.member(user).points.set(points)
                await ctx.send(f"Successfully set the points to {points}.")
            else:
                await ctx.send("The points you are trying to set cannot be less than 0, please try again.")
        elif await self.data.member(user).registered() == False:
            await ctx.send("This user is not registered")

    @rssset.command(name="lose")
    async def _lose(self, ctx, user: discord.Member, points: int):
        """Remove points to a user."""
        if not await self.role_check(ctx.author, ctx.guild):
            await ctx.send("You can't use this command.")
            return
        if await self.data.member(user).registered() == True:
            points = await self.data.member(user).points() - points
            if points > 0:
                await self.data.member(user).points.set(points)
                await ctx.send(f"Successfully set the points too {points}.")
            else:
                await ctx.send("The point can't be less than 0.")
        elif await self.data.member(user).registered() == False:
            await ctx.send("This user is not registered")

    @rssset.command(name="game")
    async def _game(self, ctx, channel: discord.TextChannel, team: str, points_to_add: int, points_to_deduct: int):
        """Award game points to users."""
        lobbies = await self.data.guild(ctx.guild).lobbies()
        channel_id = str(ctx.channel.id)
        if not await self.role_check(ctx.author, ctx.guild):
            await ctx.send("You can't use this command.")
            return

        if str(ctx.channel.id) not in lobbies:
            await ctx.send("There is no lobby created in that channel.")
            return

        if team.lower() not in ["team1", "team2"]:
            await ctx.send("Invalid team name, it should be one of these `team1 or team2`.")
        elif team.lower() == "team1":
            # add points to team one
            captain_one = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "captains")
            players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_one", "players")
            for user in players:
                user = ctx.guild.get_member(user)
                if user and await self.data.member(user).registered():
                    points_to_add = await self.data.member(user).points() + points_to_add
                    await self.data.member(user).points.set(points_to_add)
            #add points to the team captain
            captain = ctx.guild.get_member(int(captain_one))
            if captain:
                points_to_add = await self.data.member(captain).points() + points_to_add
                await self.data.member(captain).points.set(points_to_add)
            await ctx.send("Successfully added points to the players in team one and reset the data.")

            #remove points from team two
            captain_two = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "captains")
            players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_two", "players")
            for user in players:
                user = ctx.guild.get_member(user)
                if user and await self.data.member(user).registered():
                    points_to_deduct = await self.data.member(user).points() - points_to_deduct
                    await self.data.member(user).points.set(points_to_deduct)
            #remove points from team captain
            captain = ctx.guild.get_member(int(captain_two))
            if captain:
                points_to_deduct = await self.data.member(captain).points() - points_to_deduct
                await self.data.member(captain).points.set(points_to_deduct)
            await self.data.guild(ctx.guild).lobbies.clear_raw(str(ctx.channel.id))
        elif team.lower() == "team2":
            #add points to the team two
            captain_two = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "captains")
            players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_two", "players")
            for user in players:
                user = ctx.guild.get_member(user)
                if user and await self.data.member(user).registered():
                    points_to_add = await self.data.member(user).points() + points_to_add
                    await self.data.member(user).points.set(points_to_add)
            #add points the team captain
            captain = ctx.guild.get_member(int(captain_two))
            if captain:
                points_to_add = await self.data.member(captain).points() + points_to_add
                await self.data.member(captain).points.set(points_to_add)
            await ctx.send("Successfully added points to the players in team two and reset the data!")

            #remove points from the team one
            captain_one = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "captains")
            players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_one", "players")
            for user in players:
                user = ctx.guild.get_member(user)
                if user and await self.data.member(user).registered():
                    points_to_deduct = await self.data.member(user).points() - points_to_deduct
                    await self.data.member(user).points.set(points_to_deduct)
            #remove points from the team one captain
            captain = ctx.guild.get_member(int(captain_one))
            if captain:
                points_to_deduct = await self.data.member(captain).points() - points_to_deduct
                await self.data.member(captain).points.set(points_to_deduct)
            await self.data.guild(ctx.guild).lobbies.clear_raw(str(ctx.channel.id))

    @commands.command(aliases=["lb"])
    async def _leadeboard(self, ctx, page_no: int=None):
        """Leaderboard for the points."""
        server = ctx.guild
        server_data = await self.data.all_members(server)
        msg = ""
        if page_no is None:
            page_no = 1

        if page_no <= 0:
            await ctx.send("Invalid page number.")
            return
        index_number = page_no*10
        if index_number > 10:
            if len(server_data) < index_number:
                await ctx.send(f"There is no data in page number {page_no}.")
                return
        try:
            rank = sorted(server_data, key=lambda x: server_data[x]["points"], reverse=True)[:index_number]
        except Exception as e:
            await ctx.send(f"An error occured, ```{e}```.")
            return

        if not rank:
            await ctx.send("Invalid page number.")
            return

        if page_no == 1:
            i = 0
        elif page_no > 1:
            i = (page_no - 1)*10

        for x in rank:
            i+=1
            points = server_data[x]["points"]
            user = ctx.guild.get_member(x)
            if user:
                msg+= f'{i} - `{user.name}` - {points}\n'
            else:
                msg+= f'{i} - `User Not Found` - {points}\n'
        embed=discord.Embed(description=msg, colour=ctx.author.colour)
        embed.set_author(name="Points Leaderboard", icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def register(self, ctx):
        """Register yourself."""
        if await self.data.member(ctx.author).registered() == True:
            await ctx.send("You are already registered!")
        elif await self.data.member(ctx.author).registered() == False:
            await self.data.member(ctx.author).registered.set(True)
            await ctx.send(f"Thank you for registering {ctx.author.mention} : [0] - {ctx.author.name}")

    @commands.command()
    async def createlobby(self, ctx):
        """Create a lobby"""
        lobbies = await self.data.guild(ctx.guild).lobbies()
        if str(ctx.channel.id) in lobbies:
            await ctx.send("There is already a lobby created in this channel.")
            return

        e=discord.Embed(description="1️⃣ General Team Name\n2️⃣ Custom team name")
        e.set_footer(text="React below with a specific emoji to set the team names.")
        msg = await ctx.send(embed=e)
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        def reactioncheck(reaction, user):
            if user != self.bot.user:
                if user == ctx.author:
                    if reaction.message.channel == ctx.channel:
                        if reaction.message.id == msg.id:
                            if reaction.emoji == "1️⃣" or reaction.emoji == "2️⃣":
                                return True
        try:
            response, author = await self.bot.wait_for("reaction_add", check=reactioncheck, timeout=60)
        except asyncio.TimeoutError:
            await self._remove_reactions(msg)
            return
        else:
            if response.emoji == "1️⃣":
                await self._remove_reactions(msg)
                team_name_type = "general"
            elif response.emoji == "2️⃣":
                await self._remove_reactions(msg)
                team_name_type = "custom_name"

        msg = await ctx.send("How many people would it take for a match to be begin? (Even number)")
        def confirmation_msg(m):
            return m.channel == ctx.channel and ctx.author == m.author
        try:
            answer = await self.bot.wait_for("message", timeout=60, check=confirmation_msg)
        except asyncio.TimeoutError:
            await ctx.send('Timed out, try again!')
            return

        if answer:
            try:
                if isinstance(int(answer.content), int):
                    minimum_members = int(answer.content)
                    if minimum_members%2 == 0:
                        minimum_members = int(answer.content)
                    else:
                        await ctx.send("The number you provided wasn't even.")
                        return
                else:
                    await ctx.send("Invalid amount of people provided.")
                    return
            except:
                await ctx.send("Invalid amount of people provided.")
                return
        else:
            await ctx.send("Invalid amount of people provided.")
            return

        channel_id = ctx.channel.id

        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "team_one", value={"team_name": None, "players": [], "captains": None, "max_players": minimum_members/2})
        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "team_two", value={"team_name": None, "players": [], "captains": None, "max_players": minimum_members/2})
        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "players", value={"list_of_players": [], "type": team_name_type})
        await ctx.send(f"Lobby created with {minimum_members} members limit.")

    @commands.command(aliases=["j"])
    async def _join(self, ctx):
        channel_id = str(ctx.channel.id)
        if await self.data.member(ctx.author).registered() == False:
            await ctx.send(f"You should register your self first by using ``{ctx.prefix}register` command.")
        elif await self.data.member(ctx.author).registered() == True:
            if channel_id not in await self.data.guild(ctx.guild).lobbies():
                await ctx.send("There is no queue in this channel!")
                return
            elif channel_id in await self.data.guild(ctx.guild).lobbies():
                teamOne = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_one", "max_players")
                teamTwo = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_two", "max_players")
                max_players = int(teamOne + teamTwo)
                current_players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "players", "list_of_players")
                if len(current_players) < max_players:
                    current_players.append(ctx.author.id)
                    await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "players", "list_of_players", value=current_players)
                    await ctx.send(f"You were added to the queue! {len(current_players)}/{max_players}")

                if len(current_players) == max_players:
                    team_one_leader = random.choice(current_players)
                    current_players.remove(team_one_leader)
                    team_two_leader = random.choice(current_players)
                    current_players.remove(team_two_leader)
                    channel_id  = ctx.channel.id
                    await ctx.send(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"players", "type"))
                    await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"players", "list_of_players", value=current_players)
                    if await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"players", "type") == "general":
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "team_name", value="team_1")
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "captains", value=team_one_leader)
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "team_name", value="team_2")
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "captains", value=team_two_leader)
                    if await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"players", "type") == "custom_name":
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "team_name", value=str(ctx.guild.get_member(int(team_one_leader))))
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "captains", value=team_one_leader)
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "team_name", value=str(ctx.guild.get_member(int(team_two_leader))))
                        await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "captains", value=team_two_leader)
                    await ctx.send(f"Team One leader {ctx.guild.get_member(int(team_one_leader))}\n\n Team Two Leader {ctx.guild.get_member(int(team_two_leader))}\n\n Leaders can now choose their team mates by using `{ctx.prefix}pick` command.")
                    return

    @commands.command(aliases=["l"])
    async def _leave(self, ctx):
        """Leave a queue."""
        channel_id = str(ctx.channel.id)
        if channel_id not in await self.data.guild(ctx.guild).lobbies():
            await ctx.send("There is no queue in this channel!")
            return
        elif channel_id in await self.data.guild(ctx.guild).lobbies():
            current_players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "players", "list_of_players")
            teamOne = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_one", "max_players")
            teamTwo = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id, "team_two", "max_players")
            max_players = int(teamOne + teamTwo)
            if ctx.author.id in current_players:
                current_players.remove(ctx.author.id)
                await self.data.guild(ctx.guild).lobbies.set_raw(channel_id, "players", "list_of_players", value=current_players)
                await ctx.send(f"You were removed from the queue! {len(current_players)}/{max_players}")
            elif ctx.author.id not in current_players:
                await ctx.send("You are not in the lobby!")

    @commands.command(aliases=["p"])
    async def _pick(self, ctx, user: discord.Member):
        """Pick a member for your team."""
        channel_id = str(ctx.channel.id)
        if channel_id not in await self.data.guild(ctx.guild).lobbies():
            await ctx.send("There is no queue in this channel!")
            return
        elif channel_id in await self.data.guild(ctx.guild).lobbies():
            captain_one = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "captains")
            captain_two = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "captains")
            if captain_one and int(captain_one) == ctx.author.id:
                max_players = int(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "max_players"))
                players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "players")
                if len(players) == max_players - 1:
                    await ctx.send(f"Your team can't have any more players, max limit reached. - **{len(players)}/{max_players-1}**")
                else:
                    players.append(user.id)
                    await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_one", "players", value=players)
                    await ctx.send(f"Added {user.name} to the team.")
            elif captain_two and int(captain_two) == ctx.author.id:
                max_players = int(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "max_players"))
                players = await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "players")
                if len(players) == max_players - 1:
                    await ctx.send(f"Your team can't have any more players, max limit reached. - **{len(players)}/{max_players-1}**")
                else:
                    players.append(user.id)
                    await self.data.guild(ctx.guild).lobbies.set_raw(channel_id,"team_two", "players", value=players)
                    await ctx.send(f"Added {user.name} to the team.")

        if (await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "max_players") + await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "max_players")) - 2 == (len(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "players")) + len(await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "players"))):
            maps = await self.data.guild(ctx.guild).maps()
            if maps:
                map = random.choice(maps)
            else:
                map = "No maps are been set!"
            members_team_one = []
            members_team_two = []
            for member in await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "players"):
                user = ctx.guild.get_member(int(member))
                if user:
                    members_team_one.append(str(user.name))

            for member in await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "players"):
                user = ctx.guild.get_member(int(member))
                if user:
                    members_team_two.append(str(user.name))
            text_msg = f'Map: {map}\nTeam1: {await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "team_name")}\nMembers: {", ".join(members_team_one)}\n\nTeam2: {await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "team_name")}\nMembers: {", ".join(members_team_two)}\n\n\n"React with ▶ for a different map else react with ✅'
            channel_to_send = ctx.guild.get_channel(self.data.guild(ctx.guild).channel())
            if channel_to_send:
                msg = await channel_to_send.send(text_msg)
            else:
                msg = await ctx.send(text_msg)
            msg_id = msg.id
            await msg.add_reaction("▶")
            await msg.add_reaction("✅")
            def reactioncheck(reaction, user):
                if user != self.bot.user:
                    if user == ctx.author:
                        if reaction.message.channel == ctx.channel:
                            if reaction.message.id == msg_id:
                                if reaction.emoji == "▶" or reaction.emoji == "✅":
                                    return True
            x = True
            while x:
                try:
                    reaction, author = await self.bot.wait_for("reaction_add", timeout=120, check=reactioncheck)
                    if reaction.emoji == "▶":
                        map = random.choice(maps)
                        text_msg = f'Map: {map}\nTeam1: {await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_one", "team_name")}\nMembers: {", ".join(members_team_one)}\n\nTeam2: {await self.data.guild(ctx.guild).lobbies.get_raw(channel_id,"team_two", "team_name")}\nMembers: {", ".join(members_team_two)}\n\n\n"React with ▶ for a different map else react with ✅'
                        try:
                            msg = await ctx.channel.fetch_message(msg_id)
                        except:
                            msg = await channel_to_send.fetch_message(msg_id)
                        await msg.edit(content=text_msg)
                    elif reaction.emoji == "✅":
                        await ctx.send("Teams successfully created!")
                        x = False
                except asyncio.TimeoutError:
                    try:
                        await msg.remove_reaction("▶")
                        await msg.remove_reaction("✅")
                    except:
                        pass
                    x = False


    async def role_check(self, user, guild):
        roles_list = []
        for x in [620317742637252620, 620317607395983416, 620317690715832332, 577099737975488532]:
            role = guild.get_role(x)
            if role:
                roles_list.append(role.name)

        for i in range(len(user.roles)):
            if user.roles[i].name in roles_list:
                return True
        return False

    async def _remove_reactions(self, msg):
        try:
            await msg.clear_reactions()
        except:
            return
