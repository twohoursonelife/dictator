from db_manager import db_connection as db_conn


def get_user_by_discord_id(discord_id: int):
    with db_conn() as db:
        db.execute(
            f"SELECT email, login_key FROM ticketServer_tickets WHERE discord_id = '{discord_id}'"
        )
        return db.fetchone()


def get_user_by_username(username: str):
    with db_conn() as db:
        db.execute(f"SELECT email FROM ticketServer_tickets WHERE email = '{username}'")
        return db.fetchone()
