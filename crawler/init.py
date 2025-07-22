# -*-coding:utf-8 -*-
import pymysql
import subprocess
import time
from contextlib import contextmanager
from config.conf import MYSQL_CONFIG, TABLES


@contextmanager
def get_db_connection():
    conn = pymysql.connect(**MYSQL_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def check_and_create_tables():
    """检查并创建数据库表"""
    print(f"[+] Check the database connection and initialize the database table...")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for table_name, create_table_sql in TABLES.items():
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                result = cursor.fetchone()
                if not result:
                    print(f"[>] Database table {table_name} does not exist and is being created...")
                    cursor.execute(create_table_sql)
                else:
                    print(f"[>] Database table {table_name} has been created...")
        conn.commit()


def start_mitmproxy():
    """启动 mitmproxy"""
    print("[+] Starting mitmproxy...")
    process = subprocess.Popen(
        ['mitmproxy', '--listen-host', '127.0.0.1', '--listen-port', '8082'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)  # 等待 mitmproxy 启动
    return process


def init():
    check_and_create_tables()
    start_mitmproxy()

if __name__ == '__main__':
    check_and_create_tables()
    mitmproxy_process = start_mitmproxy()
    try:
        # 这里可以放置其他初始化代码
        pass
    finally:
        print("[+] Shutting down mitmproxy...")
        mitmproxy_process.terminate()
