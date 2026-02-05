import pytest
import asyncio
from unittest.mock import MagicMock
from dictator.cogs.stats import Stats

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


def test_verify_player_list_valid(stats_cog):
    asyncio.run(stats_cog.verify_player_list("SomeData#"))


def test_verify_player_list_real_data(stats_cog):
    asyncio.run(stats_cog.verify_player_list(SAMPLE_PLAYER_LIST))


def test_parse_player_list(stats_cog):
    server_info, players = asyncio.run(stats_cog.parse_player_list(SAMPLE_PLAYER_LIST))

    assert server_info == ["4/200", "20325", "4"]

    assert len(players) == 4
    assert players[0][0] == "353895"
    assert players[2][7] == "EVE STAR"
    assert players[2][8] == "STAR"


def test_group_families(stats_cog):
    players = [
        ["0", "100", "0", "F", "20", "0", "0", "Eve", "One"],
        ["1", "100", "0", "M", "1", "0", "0", "Son", "One"],
        ["2", "200", "0", "F", "20", "0", "0", "Eve", "Two"],
    ]

    families = asyncio.run(stats_cog.group_families(players))

    assert len(families) == 2
    # Family 100 has 2 members
    assert len(families[0]) == 2
    # Family 200 has 1 member
    assert len(families[1]) == 1


def test_format_family_list(stats_cog):
    # 1. Standard Family
    # player_id, eve_id, parent_id, gender, age, declaredInfertile, isTutorial, name, family_name
    family_standard = [["10", "10", "0", "F", "20", "0", "0", "Eve", "Standard"]]

    # 2. Tutorial
    family_tutorial = [["20", "20", "0", "F", "20", "0", "1", "Eve", "Tutorial"]]

    # 3. Solo Eve (Infertile)
    family_solo = [["30", "30", "0", "F", "20", "1", "0", "Eve", "Solo"]]

    # 4. Unnamed
    family_unnamed = [["40", "40", "0", "F", "20", "0", "0", "Eve", ""]]

    families = [family_standard, family_tutorial, family_solo, family_unnamed]

    result = asyncio.run(stats_cog.format_family_list(families))

    assert "1 in Standard (1 fertile)" in result
    assert "1 playing the tutorial" in result
    assert "1 playing as solo Eves" in result


def test_format_family_list_real_data(stats_cog):
    # Process the sample data through the actual pipeline steps
    _, parsed_players = asyncio.run(stats_cog.parse_player_list(SAMPLE_PLAYER_LIST))
    family_list = asyncio.run(stats_cog.group_families(parsed_players))
    result = asyncio.run(stats_cog.format_family_list(family_list))

    # 353895 is a solo Eve (infertile=1, len=1)
    # 353898 is unnamed family of 1 (not solo eve as infertile=0)
    # 353900 is STAR family
    # 353901 is unnamed family of 1

    assert "1 in Star (1 fertile)" in result
    assert "1 playing as solo Eves" in result
    assert "2 in 2 unnamed families" in result


def test_format_family_list_fertility(stats_cog):
    # Validates correct fertility count
    family_complex = [
        ["50", "50", "-1", "F", "20", "0", "0", "EVE", "WINTERSTEIN"],  # Fertile
        ["54", "50", "50", "F", "2", "1", "0", "NATASHA", "WINTERSTEIN"],  # Infertile
        ["51", "50", "50", "M", "15", "0", "0", "TANYA", "WINTERSTEIN"],  # Male
    ]

    families = [family_complex]

    result = asyncio.run(stats_cog.format_family_list(families))

    assert "3 in Winterstein (1 fertile)" in result
