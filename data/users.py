import data.db_connect as con

# USER METHODS
def get_users():
    con.connect_db()
    users = con.fetch_all(con.USERS_COLLECTION)
    
    return users