import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from dictator.cogs.stats import Player, Stats

# Protocol:
# SN
# current_players/max_players
# challenge_string
# required_version_number
# #num_players
# p_id,eve_id,parent_id,gender,age,delcaredInfertile,isTutorial,name,familyName
# ...
# #
SAMPLE_PLAYER_LIST = (
    "SN\n"
    "4/200\n"
    "43E85D77D3368BE84C5F482AAB6F0A8F90CAC46A1632171\n"
    "20325\n"
    "#4\n"
    "353895,353895,-1,F,84.7,1,0,,\n"
    "353898,353898,-1,F,67.8,0,0,,\n"
    "353900,353900,-1,F,65.2,0,0,EVE STAR,STAR\n"
    "353901,353901,-1,F,24.5,0,0,,\n"
    "#"
)


@pytest.fixture
def stats_cog():
    bot = MagicMock()
    return Stats(bot)


def test_player_list_response(stats_cog):
    response = stats_cog.parse_player_list(SAMPLE_PLAYER_LIST)

    assert response.required_version == "20325"
    assert response.player_count == len(response.players) == 4
    assert response.players[0] == Player(
        353895, 353895, -1, "F", 84.7, True, False, "", ""
    )
    assert response.players[2].family_name == "STAR"


def test_empty_server(stats_cog):
    raw = SAMPLE_PLAYER_LIST.split("#")[0] + "#0\n#"
    stats_cog.player_list_request = AsyncMock(
        return_value=stats_cog.parse_player_list(raw)
    )

    server_version, player_count, families = asyncio.run(stats_cog.get_server_stats())

    assert player_count == 0
    assert server_version == "20325"
    assert families.startswith("0 active\n")


def test_stats_message_active_families_excludes_tutorial(stats_cog):
    player_list = SAMPLE_PLAYER_LIST.replace(
        "353901,353901,-1,F,24.5,0,0,,",
        "353901,353901,-1,F,24.5,0,1,,",
    )
    stats_cog.player_list_request = AsyncMock(
        return_value=stats_cog.parse_player_list(player_list)
    )
    stats_cog.STATS_MESSAGE = AsyncMock()

    asyncio.run(stats_cog.update_stats())

    embed = stats_cog.STATS_MESSAGE.edit.call_args.kwargs["embed"]
    assert embed.fields[0].value == "4"
    assert "Server v20325" in embed.fields[2].value
    assert embed.fields[1].value.startswith("2 active\n")
    assert "1 playing the tutorial" in embed.fields[1].value


def test_format_families(stats_cog):
    players = [
        Player(40, 40, -1, "F", 20, False, False, "Eve", ""),
        Player(10, 10, -1, "F", 103.9, False, False, "Eve", "Standard"),
        Player(20, 20, -1, "F", 20, False, True, "Eve", "Tutorial"),
        Player(30, 30, -1, "F", 20, True, False, "Eve", "Solo"),
        Player(11, 10, 10, "F", 104, False, False, "Child", "Standard"),
        Player(12, 10, 10, "M", 20, False, False, "Son", "Standard"),
        Player(13, 10, 10, "F", 20, True, False, "Child", "Standard"),
    ]

    family_message = stats_cog.format_families(players)
    assert "2 active\n" in family_message
    assert "4 in Standard (1 fertile)\n" in family_message
    assert "1 in *Unnamed* (1 fertile)\n" in family_message
    assert "1 playing as solo Eve\n" in family_message
    assert "1 playing the tutorial\n" in family_message
