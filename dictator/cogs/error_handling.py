import discord
from discord.ext import commands


class Error_Handling(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.MissingPermissions):
            await ctx.message.delete()
            await ctx.send('{ctx.author.mention}, Insufficient permissions', delete_after=10)

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.send(f'{ctx.author.mention}, Missing argument. See {await self.dictator.get_prefix(ctx)}help', delete_after=10)

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(f'{ctx.author.mention}, you can\'t use this command in a private message. Head to the bot channel.')

        elif isinstance(error, commands.MissingRole) or isinstance(error, commands.MissingAnyRole):
            await ctx.message.delete()
            await ctx.send(f'{ctx.author.mention}, You don\'t have the required role.', delete_after=10)

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.delete()
            await ctx.send('{ctx.author.mention} You must wait a minute to use this command again.', delete_after=10)

        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.message.delete()
            await ctx.send(f'{ctx.author.mention} You can only run this command once at a time.', delete_after=10)

        elif isinstance(error, commands.UserInputError):
            await ctx.message.delete()
            await ctx.send(f'{ctx.author.mention} Invalid input. See {await self.dictator.get_prefix(ctx)}help', delete_after=10)

        else:
            if isinstance(ctx.channel, discord.TextChannel):
                await ctx.send(f'{ctx.author.mention}, Uh oh... {ctx.guild.owner.mention} broke something again. Stand by.\nMake sure you\'re not blocking the bot from messaging you!')
                print(f'\n\nCOMMAND ERROR:\nAuthor: {ctx.author}\nChannel: {ctx.channel}\nCommand: {ctx.message.content}\n{error}\n\n')

            else:
                await ctx.send(f'{ctx.author.mention}, Uh oh... Colin broke something again. Contact Colin#9391 or admin@twohoursonelife.com for assistance.')
                print(f'\n\nCOMMAND ERROR:\nAuthor: {ctx.author}\nChannel: {ctx.channel}\nCommand: {ctx.message.content}\n{error}\n\n')


def setup(dictator):
    dictator.add_cog(Error_Handling(dictator))