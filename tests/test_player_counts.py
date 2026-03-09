import asyncio
import socket
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from dictator.cogs.player_counts import PlayerCounts


class TestPlayerCounts:
    def test_record_player_count(self):
        mock_bot = MagicMock()
        mock_bot.loop.run_in_executor = AsyncMock(return_value=42)
        cog = PlayerCounts(mock_bot)

        # Mock datetime.now to return a specific time with non-zero seconds/microseconds
        fixed_now = datetime(2026, 3, 9, 15, 0, 7, 123456, tzinfo=timezone.utc)
        expected_time = datetime(2026, 3, 9, 15, 0, 0, 0, tzinfo=timezone.utc)

        with (
            patch("dictator.cogs.player_counts.datetime") as mock_datetime,
            patch("dictator.cogs.player_counts.db_connection") as mock_db_conn,
        ):
            mock_datetime.now.return_value = fixed_now
            mock_cursor = MagicMock()
            mock_db_conn.return_value.__enter__.return_value = mock_cursor

            asyncio.run(cog.record_player_count())

            # Verify the timestamp was forced to the minute (seconds and micros zeroed)
            mock_cursor.execute.assert_called_once_with(
                "INSERT INTO player_counts (timestamp, player_count) VALUES (%s, %s)",
                (expected_time, 42),
            )

    def test_get_player_count_success(self):
        cog = PlayerCounts(MagicMock())
        with patch("socket.socket") as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock_instance
            mock_fd = MagicMock()
            mock_sock_instance.makefile.return_value = mock_fd
            # Readline needs to return SN on first call, and player count string on second call
            mock_fd.readline.side_effect = ["SN\n", "42/100\n"]

            assert cog.get_player_count() == 42

    def test_get_player_count_timeout(self):
        cog = PlayerCounts(MagicMock())
        with patch("socket.socket") as mock_socket:
            mock_socket.return_value.__enter__.return_value.connect.side_effect = (
                socket.timeout
            )

            assert cog.get_player_count() is None

    def test_get_player_count_malformed(self):
        cog = PlayerCounts(MagicMock())
        with patch("socket.socket") as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock_instance
            mock_fd = MagicMock()
            mock_sock_instance.makefile.return_value = mock_fd
            # SN present, but count string is malformed
            mock_fd.readline.side_effect = ["SN\n", "bad_data\n"]

            assert cog.get_player_count() is None

    def test_get_player_count_no_sn(self):
        cog = PlayerCounts(MagicMock())
        with patch("socket.socket") as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock_instance
            mock_fd = MagicMock()
            mock_sock_instance.makefile.return_value = mock_fd
            # missing SN
            mock_fd.readline.side_effect = ["other data\n", "42/100\n"]

            assert cog.get_player_count() is None
