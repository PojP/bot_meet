import sqlite3
from typing import Union

conn = sqlite3.connect("users.db")
cur = conn.cursor()

def init_database():
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
   userid INT PRIMARY KEY,
   age INT,
   interest TEXT,
   gender TEXT);
    """)
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS search(
   userid INT PRIMARY KEY,
   interest TEXT);
    """)
    conn.commit()
    cur.execute(f"DELETE FROM search;")
    conn.commit()
def update(id : str, data_to_append : str, data : str):
    cur.execute(f"UPDATE users SET {data} = '{data_to_append}' WHERE userid={id};")
    conn.commit()
def add_user(data : tuple[str,int,str,str]):
    cur.execute("INSERT INTO users VALUES(?, ?, ?, ?);", data)
    conn.commit()
def check_user(id : str):
    cur.execute(f"SELECT * FROM users WHERE userid={id}")
    #print(cur.fetchone())
    if cur.fetchone()==None:
        return False
    return True
def get_user(id : str):
    cur.execute(f"SELECT * FROM users WHERE userid={id}")
    return cur.fetchone()



def get_users(interest : str):
    cur.execute(f"SELECT userid FROM search WHERE interest='{interest}'")
    return cur.fetchmany()
def check_user_search(id : str):
    cur.execute(f"SELECT * FROM search WHERE userid={id}")
    #print(cur.fetchone())
    if cur.fetchone()==None:
        return False
    return True
def add_user_to_search(data : tuple[int,str]):
    cur.execute("INSERT INTO search VALUES(?, ?);", data)
    conn.commit()
def del_user_from_search(id: int):
    cur.execute(f"DELETE FROM search WHERE userid='{id}';")
    conn.commit()