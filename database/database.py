import sqlite3


async def db_connect():
    table_creation = ("CREATE TABLE IF NOT EXISTS user_requests(user_id TEXT PRIMARY KEY NOT NULL, name TEXT, "
                      "lang_level TEXT,age INT, learn_target TEXT, telephone INT, time_prior TEXT)")
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(table_creation)


async def save_user_request(sql_data: [int, dict[str, str | int | bool]]):
    records: list = []
    insert_query = (f'INSERT INTO user_requests(user_id, name, lang_level, age, learn_target, telephone, time_prior) '
                    f'VALUES (?, ?, ?, ?, ?, ?, ?)')

    for key1 in sql_data:
        user_id = key1
        records.append(user_id)
        for key2 in sql_data[user_id]:
            records.append(sql_data[user_id][key2])

    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        cursor.execute(insert_query, tuple(records))


def get_user_request(user_id):
    get_query = (f'SELECT DISTINCT * FROM user_requests WHERE user_id = {user_id}')
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
        user = cursor.execute(get_query).fetchone()
    if user is not None:
        return user
    else:
        return None


