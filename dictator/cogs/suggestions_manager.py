import discord
import pandas as pd
from discord.ext import commands

from constants import SUGGESTION_CHANNEL_ID


class SuggestionsManager(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        if thread.parent_id != SUGGESTION_CHANNEL_ID:
            return

        tag = self._get_forum_tag(thread.parent, "status: discussion")
        await thread.add_tags(tag)

    @commands.Cog.listener()
    async def on_thread_update(self, before, after):
        """Modify the tags and lock the thread when certain tags added"""
        discussion_tag_unchanged = (
            "status: discussion" in before.applied_tags
            and "status: discussion" in after.applied_tags
        )

        # Ignore if 
        # no change in tags
        # discussion tag is unchanged
        # 
        if before.applied_tags == after.applied_tags and not discussion_tag_unchanged:
            print("No eligible change in tags")  # TODO: Remove this
            return
        
        eligible_tags = ["status: dev ready", "status: unlikely", "status: needs art"]
        
        if "status: dev ready" in after.applied_tags and "status: dev ready" not in before.applied_tags:
            self._remove_thread_tag(after, "status: discussion")
            await after.lock()
            
        if "status: unlikely" in after.applied_tags and "status: unlikely" not in before.applied_tags:
            self._remove_thread_tag(after, "status: discussion")
            await after.lock()
            
        if "status: needs art" in after.applied_tags and "status: needs art" not in before.applied_tags:
            # Remove the discussion tag
            self._remove_thread_tag(after, "status: discussion")
            await after.lock()

        print(set(before.applied_tags) ^ set(after.applied_tags))

    def _get_forum_tag(self, channel: discord.TextChannel, tag_name: str):
        try:
            return discord.utils.get(channel.available_tags, name=tag_name)
        except AttributeError:
            print(f"Tag {tag_name} not found on channel with id: {channel.id}")
            return
        
    def _remove_thread_tag(self, thread: discord.Thread, tag_name: str):
        tag = self._get_forum_tag(thread.parent, tag_name)
        
        if not tag:
            return
        
        return thread.remove_tags(tag)


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(SuggestionsManager(dictator))
