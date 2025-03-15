import sqlite3


def check_database(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"发现 {len(tables)} 张表")

    #添加过滤，仅查看用户表数量
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    ''')
    tables = cursor.fetchall()
    print(f"用户表数量: {len(tables)}")  # 输出 11
    # 关闭连接
    conn.close()


if __name__ == "__main__":
    check_database(r"D:\Code\python\MOOC_Recommender\db.sqlite3")