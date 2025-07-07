import re
from datetime import timezone

import discord
import mysql.connector
from discord import app_commands
from discord.ext import commands

from dictator.constants import (
    ADMIN_ROLE_ID,
    GAME_MOD_ROLE_ID,
    LOG_CHANNEL_ID,
    MOD_ROLE_ID,
)
from dictator.db_manager import db_connection as db_conn
from dictator.exceptions import (
    UsernameAlreadyExistsError,
    UsernameValidationError,
)
from dictator.logger_config import logger
from dictator.utilities import (
    generate_login_key,
    generate_sha1,
    get_user_by_discord_id,
    is_unique_username,
    is_valid_username,
    send_user_account_details,
)


class Admin(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(GAME_MOD_ROLE_ID)
    async def ban(
        self,
        interaction: discord.Interaction,
        discord_user: discord.User,
        reason: str = "The ban hammer has spoken.",
    ) -> None:
        """Bans a user from the game. Input a Discord User like object, such as a username, nickname, ID or formatted mention."""
        await interaction.response.send_message(
            f"Banning {discord_user.name} ({discord_user.id}) for `{reason}`...",
            ephemeral=True,
            delete_after=10,
        )

        log_channel = self.dictator.get_channel(LOG_CHANNEL_ID)

        # Is user already banned?
        with db_conn() as db:
            db.execute(
                "SELECT blocked, email FROM ticketServer_tickets WHERE discord_id = %s",
                (discord_user.id,),
            )
            row = db.fetchone()

        if row is None:
            await interaction.edit_original_response(
                content=f"Could not find an account for Discord ID: `{discord_user.id}`"
            )
            return

        if row[0] == 1:
            logger.info(
                f"{interaction.user} tried to ban {discord_user.name} ({discord_user.id}) but they're already banned."
            )
            await interaction.edit_original_response(
                content=f"{discord_user.name} ({discord_user.id}) is already banned."
            )
            return

        # Ban the user
        with db_conn() as db:
            db.execute(
                "UPDATE ticketServer_tickets SET blocked = 1 WHERE discord_id = %s",
                (discord_user.id,),
            )

        logger.success(
            f"{interaction.user} banned {discord_user.name} ({discord_user.id}) for: {reason}"
        )

        # Notify the user
        try:
            embed = discord.Embed(
                title="You were banned from 2HOL", colour=discord.Colour.red()
            )
            embed.add_field(name="Reason:", value=f"{reason}", inline=True)
            await discord_user.send(embed=embed)

        except Exception as e:
            # Message can fail if the user does not allow messages from anyone
            notify_user = False
            logger.exception(e)

        else:
            notify_user = True

        # Embed log
        embed = discord.Embed(
            title="Banned a user from the game", colour=discord.Colour.red()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.add_field(name="Member:", value=f"{discord_user.name}", inline=True)
        embed.add_field(name="Username:", value=f"{row[1]}", inline=True)
        embed.add_field(name="Reason:", value=f"{reason}", inline=True)
        embed.add_field(
            name="Notification:",
            value="Successful" if notify_user else "Failed",
            inline=True,
        )
        embed.set_footer(
            text=f"Member ID: {discord_user.id}", icon_url=discord_user.avatar
        )
        await log_channel.send(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(GAME_MOD_ROLE_ID)
    async def unban(
        self,
        interaction: discord.Interaction,
        discord_user: discord.User,
        reason: str = "It's your lucky day!",
    ) -> None:
        """Unbans a user from the game. Input a Discord User like object, such as a username, nickname, ID or formatted mention."""
        await interaction.response.send_message(
            f"Unbanning {discord_user.name} ({discord_user.id}) for `{reason}`...",
            ephemeral=True,
            delete_after=10,
        )

        log_channel = self.dictator.get_channel(LOG_CHANNEL_ID)

        # Check that user is banned
        with db_conn() as db:
            db.execute(
                "SELECT blocked, email FROM ticketServer_tickets WHERE discord_id = %s",
                (discord_user.id,),
            )
            row = db.fetchone()

        if row is None:
            await interaction.edit_original_response(
                content=f"Could not find an account for Discord ID: `{discord_user.id}`"
            )
            return

        if row[0] == 0:
            logger.info(
                f"{interaction.user} tried to unban {discord_user.name} ({discord_user.id}) but they're not banned."
            )
            await interaction.edit_original_response(
                content=f"{discord_user.name} ({discord_user.id}) is not already banned."
            )
            return

        # Unban the user
        with db_conn() as db:
            db.execute(
                "UPDATE ticketServer_tickets SET blocked = 0 WHERE discord_id = %s",
                (discord_user.id,),
            )

        logger.success(
            f"{interaction.user} unbanned {discord_user.name} ({discord_user.id}) for: {reason}"
        )

        # Notify the user
        try:
            embed = discord.Embed(
                title="You were unbanned from 2HOL", colour=discord.Colour.green()
            )
            embed.add_field(name="Reason:", value=f"{reason}", inline=True)
            await discord_user.send(embed=embed)

        except Exception as e:
            # Message can fail if the user does not allow messages from anyone
            notify_user = False
            logger.exception(e)

        else:
            notify_user = True

        # Embed log
        embed = discord.Embed(
            title="Unbanned a user from the game", colour=discord.Colour.green()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.add_field(name="Member:", value=f"{discord_user.name}", inline=True)
        embed.add_field(name="Username:", value=f"{row[1]}", inline=True)
        embed.add_field(name="Reason:", value=f"{reason}", inline=True)
        embed.add_field(
            name="Notification:",
            value="Successful" if notify_user else "Failed",
            inline=True,
        )
        embed.set_footer(
            text=f"Member ID: {discord_user.id}", icon_url=discord_user.avatar
        )
        await log_channel.send(embed=embed)

    # TODO: Modernise the user notification.
    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(MOD_ROLE_ID)
    async def regenerate(
        self, interaction: discord.Interaction, user: discord.User
    ) -> None:
        """Regenerates a users key."""
        await interaction.response.send_message(
            f"Regenerating key for {user.mention}.", ephemeral=True, delete_after=15
        )

        log_channel = self.dictator.get_channel(LOG_CHANNEL_ID)

        key = generate_login_key()

        with db_conn() as db:
            db.execute(
                "UPDATE ticketServer_tickets SET login_key = %s WHERE discord_id = %s",
                (key, user.id),
            )

        # Notify the user
        try:
            embed = discord.Embed(
                title="Your key to access 2HOL has been regenerated.",
                colour=discord.Colour.green(),
            )
            await user.send(embed=embed)

        except Exception as e:
            notify_user = False
            logger.exception(e)

        else:
            notify_user = True

        # Embed log
        embed = discord.Embed(
            title="Member key regenerated", colour=discord.Colour.green()
        )
        embed.add_field(name="Member:", value=f"{user.mention}", inline=True)
        embed.add_field(
            name="Moderator:", value=f"{interaction.user.mention}", inline=True
        )
        embed.add_field(
            name="User notification:",
            value="Successful" if notify_user else "Failed",
            inline=True,
        )
        await log_channel.send(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(GAME_MOD_ROLE_ID)
    async def whowas(
        self, interaction: discord.Interaction, character_name: str
    ) -> None:
        """Look up who a player was in the game."""
        await interaction.response.defer()

        # Result limt, due to embed length limitations, the maxium is 8.
        history = 3

        player_id = None

        # Safe characters only
        character_name = re.sub(("[^a-zA-Z0-9 ]"), "", character_name)

        if self.is_int(character_name):
            # character_name is a player life ID, retrieve the associated character name.
            player_id = character_name
            with db_conn() as db:
                """
                A player life ID can be repeated between different servers.
                We have made use of a single server for four years and do not intend to change this in the short term, so are largely unaffected by this.
                To resolve this, we assume we're only interested in the most recent player who lived with this ID.
                This is achieved with 'ORDER BY death_time DESC LIMIT 1'
                """
                db.execute(
                    "SELECT lineageServer_lives.name FROM lineageServer_lives WHERE player_id = %s ORDER BY death_time DESC LIMIT 1",
                    (character_name,),
                )
                character_name = db.fetchone()

            if not character_name:
                embed = discord.Embed(
                    title="No results for that player ID.", colour=0xFFBB35
                )
                await interaction.followup.send(embed=embed)
                return
            else:
                # We really only want the first result of the tuple
                character_name = character_name[0]

        with db_conn() as db:
            db.execute(
                """
                SELECT
                    ticketServer_tickets.discord_id,
                    lineageServer_lives.death_time,
                    lineageServer_users.email,
                    lineageServer_lives.id,
                    ticketServer_tickets.time_played
                FROM lineageServer_lives
                INNER JOIN lineageServer_users ON lineageServer_lives.user_id = lineageServer_users.id
                INNER JOIN ticketServer_tickets ON lineageServer_users.email = ticketServer_tickets.email
                WHERE name = %s
                ORDER BY death_time DESC
                LIMIT %s
                """,
                (character_name, history),
            )
            users = db.fetchall()

        if not users:
            embed = discord.Embed(
                title=f"No results for the character '{character_name}'.",
                description=(
                    f"Found name '{character_name}' from Player ID '{player_id}'"
                    if player_id
                    else ""
                ),
                colour=0xFFBB35,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"Latest {history} results for the name '{character_name}':",
            description=(
                f"Found name '{character_name}' from Player ID '{player_id}'"
                if player_id
                else ""
            ),
            colour=0xFFBB35,
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)

        for u in users:
            found_user = await self.dictator.fetch_user(u[0])
            death_time = u[1].replace(tzinfo=timezone.utc)
            embed.add_field(name="Game username:", value=u[2], inline=True)
            embed.add_field(name="Discord user:", value=found_user, inline=True)
            embed.add_field(
                name="Died:",
                value=f"{discord.utils.format_dt(death_time, 'R')}",
                inline=True,
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(GAME_MOD_ROLE_ID)
    async def whowasext(
        self,
        interaction: discord.Interaction,
        character_name: str,
    ) -> None:
        """Lookup detailed information of a single players life."""
        await interaction.response.defer()

        character_name = re.sub(("[^a-zA-Z0-9 ]"), "", character_name)

        with db_conn() as db:
            db.execute(
                """
                SELECT
                    ticketServer_tickets.discord_id,
                    lineageServer_lives.death_time,
                    lineageServer_users.email,
                    lineageServer_lives.id,
                    ticketServer_tickets.time_played,
                    lineageServer_lives.id,
                    lineageServer_lives.player_id,
                    ticketServer_tickets.blocked,
                    lineageServer_lives.user_id
                FROM lineageServer_lives
                INNER JOIN lineageServer_users ON lineageServer_lives.user_id = lineageServer_users.id
                INNER JOIN ticketServer_tickets ON lineageServer_users.email = ticketServer_tickets.email
                WHERE name = %s
                ORDER BY death_time DESC
                LIMIT 1
                """,
                (character_name,),
            )
            life = db.fetchone()

        if not life:
            embed = discord.Embed(
                title=f"No results for the character '{character_name}'.",
                colour=0xFFBB35,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"Result for the name '{character_name}':",
            colour=0xFFBB35,
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)

        found_user = await self.dictator.fetch_user(life[0])

        death_time = life[1].replace(tzinfo=timezone.utc)
        embed.add_field(name="Game username:", value=life[2], inline=True)
        embed.add_field(name="Discord user:", value=found_user, inline=True)
        embed.add_field(
            name="Died:",
            value=f"{discord.utils.format_dt(death_time, 'R')}",
            inline=True,
        )
        embed.add_field(
            name="Life ID:",
            value=life[5],
            inline=True,
        )
        embed.add_field(
            name="Lineage ID:",
            value=life[8],
            inline=True,
        )
        embed.add_field(
            name="Player ID:",
            value=life[6],
            inline=True,
        )
        embed.add_field(
            name="Blocked:",
            value="Yes :red_circle:" if life[7] else "No :green_circle:",
            inline=True,
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(GAME_MOD_ROLE_ID)
    async def getuser(
        self, interaction: discord.Interaction, game_username: str
    ) -> None:
        """
        Return the Discord ID and or Discord Object
        associated with a game username (2HOL username)
        """
        await interaction.response.defer()

        # Safe characters only
        game_username = re.sub(("[^a-zA-Z0-9 -]"), "", game_username)

        with db_conn() as db:
            db.execute(
                "SELECT ticketServer_tickets.discord_id FROM ticketServer_tickets WHERE email = %s",
                (game_username,),
            )
            result = db.fetchone()

        if not result:
            embed = discord.Embed(
                title=f"No result for the game username '{game_username}'",
                colour=0xFFBB35,
            )
            return await interaction.followup.send(embed=embed)

        id = int(result[0])
        user = await self.dictator.fetch_user(id)

        embed = discord.Embed(
            title=f"Result for the game username '{game_username}'", colour=0xFFBB35
        )

        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.add_field(name="User mention:", value=f"{user.mention}", inline=True)
        embed.add_field(name="Username:", value=f"{user.name}", inline=True)
        embed.add_field(name="User ID:", value=f"{user.id}", inline=True)

        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(ADMIN_ROLE_ID)
    async def update_username(
        self,
        interaction: discord.Interaction,
        discord_user: discord.User,
        new_username: str,
        reason: str,
    ) -> None:
        """
        Update a users game username.

        For restricted administrator use only.
        """
        await interaction.response.defer(ephemeral=True)

        # Get user
        user = get_user_by_discord_id(discord_user.id)

        # TODO create validator function
        if user is None:
            return await interaction.followup.send(
                "User has no account.",
                ephemeral=True,
            )

        old_username = user[0]

        # Validation
        try:
            is_valid_username(new_username)
            is_unique_username(new_username)

        except (UsernameValidationError, UsernameAlreadyExistsError) as e:
            logger.info(
                f"{interaction.user} attempted to update username for {discord_user}: {e}"
            )
            return await interaction.followup.send(
                f"Unable to update username: {str(e)}",
                ephemeral=True,
            )

        new_username_sha1 = generate_sha1(new_username)

        user_tables = [
            "ticketServer_tickets",
            "reviewServer_user_stats",
            "photoServer_users",
            "lifeTokenServer_users",
            "fitnessServer_users",
            "curseServer_users",
        ]

        with db_conn() as db:
            try:
                db.execute("START TRANSACTION")
                db.execute(
                    "UPDATE lineageServer_users SET email = %s, email_sha1 = %s WHERE email = %s",
                    (new_username, new_username_sha1, old_username),
                )
                for table in user_tables:
                    db.execute(
                        f"UPDATE {table} SET email = %s WHERE email = %s",
                        (new_username, old_username),
                    )
                db.execute("COMMIT")

            except mysql.connector.Error as e:
                db.execute("ROLLBACK")
                logger.error(
                    f"{interaction.user} attempted to update username for {discord_user}: {e}"
                )
                return await interaction.followup.send(
                    "Error! Unable to update username.",
                    ephemeral=True,
                )

        await interaction.followup.send("Username updated.", ephemeral=True)

        # Notify
        try:
            embed = discord.Embed(
                title="Your username for 2HOL was changed by an admin.",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="Old username:", value=old_username, inline=True)
            embed.add_field(name="New username:", value=new_username, inline=True)
            embed.add_field(name="Reason:", value=reason, inline=True)
            await discord_user.send(embed=embed)
            await send_user_account_details(self.dictator, discord_user)

        except discord.Forbidden:
            notify_user = False

        else:
            notify_user = True

        # Audit
        log_channel = self.dictator.get_channel(LOG_CHANNEL_ID)

        embed = discord.Embed(
            title="Updated a users username:", colour=discord.Colour.green()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.add_field(name="Member:", value=discord_user.name, inline=True)
        embed.add_field(name="Old username:", value=old_username, inline=True)
        embed.add_field(name="New username:", value=new_username, inline=True)
        embed.add_field(name="Reason:", value=reason, inline=True)
        embed.add_field(
            name="Notification:",
            value="Successful" if notify_user else "Failed",
            inline=True,
        )
        embed.set_footer(
            text=f"Member ID: {discord_user.id}", icon_url=discord_user.avatar
        )

        logger.success(
            f"{interaction.user} updated username for {discord_user}. Old: {old_username}. New: {new_username}."
        )
        await log_channel.send(embed=embed)

    def username_from_player_id(self, player_id: int) -> str:
        """Takes an int as a players life ID and returns the associated username."""
        with db_conn() as db:
            """
            A player life ID can be repeated between different servers.
            We have made use of a single server for four years and do not intend to change this in the short term, so are largely unaffected by this.
            To resolve this, we assume we're only interested in the most recent player who lived with this ID.
            This is achieved with 'ORDER BY death_time DESC LIMIT 1'
            """
            db.execute(
                "SELECT lineageServer_users.email FROM lineageServer_lives INNER JOIN lineageServer_users ON lineageServer_lives.user_id = lineageServer_users.id WHERE player_id = %s ORDER BY death_time DESC LIMIT 1",
                (player_id,),
            )
            username = db.fetchone()

        if not username:
            return
        else:
            # We really only want the first result of the tuple
            username = username[0]

        return username

    def is_int(self, string: str) -> bool:
        """Takes a string and returns a True if it only contains numbers, else False."""
        return bool(re.search("^[0-9]*$", string))


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Admin(dictator))
