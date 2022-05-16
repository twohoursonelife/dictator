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
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                # Message was deleted by an earlier function
                pass
            await ctx.send(f'{ctx.author.mention} Invalid input. See {await self.dictator.get_prefix(ctx)}help', delete_after=10)

        # Surely this could be better :sweatsmile:
        elif isinstance(error, commands.CommandInvokeError):
            try:
                # In other errors, the message is sometimes found in error.original.msg
                errmsg = error.original.text

            except:
                await self.default_error(ctx, error)

            else:
                if 'Cannot send messages to this user' in errmsg:
                    await ctx.message.delete()
                    await ctx.send(f'{ctx.author.mention} You must allow me to message you, check your Discord settings.', delete_after=20)

                else:
                    await self.default_error(ctx, error)

        else:
            await self.default_error(ctx, error)

    async def default_error(self, ctx, error):
        await ctx.send(f'{ctx.author.mention}, Uh oh... an error has occurred. We\'ll be right on it!')
        print(f'\n\nCOMMAND ERROR:\nAuthor: {ctx.author}\nChannel: {ctx.channel}\nCommand: {ctx.message.content}\n{error}\n\n')


def setup(dictator):
    dictator.add_cog(Error_Handling(dictator))
