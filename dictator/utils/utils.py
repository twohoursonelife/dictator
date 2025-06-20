from db_manager import db_connection as db_conn


# Search whether a user exists, return username and key if they do
def search_user(user_id: int):
    with db_conn() as db:
        db.execute(
            f"SELECT email, login_key FROM ticketServer_tickets WHERE discord_id = '{user_id}'"
        )

        return db.fetchone()
