"""演示 DatabaseSession 的自动提交、自动回滚、自动关闭。

运行方式：
    python3 demo.py
"""

from __future__ import annotations

import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from session_manager import DatabaseSession, database_session


def run_sql(db_path: str, sql: str, params=()):
    """用独立连接执行 SQL，自动 commit + close（用于建表与验证查询）。"""
    with closing(sqlite3.connect(db_path)) as conn, conn:
        return conn.execute(sql, params).fetchall()


def main() -> None:
    tmp = Path(tempfile.mkdtemp())
    db = str(tmp / "app.db")
    run_sql(db, "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

    print("=" * 60)
    print("1. 自动提交：with 块正常结束 -> commit 生效")
    with DatabaseSession(db) as conn:
        conn.execute("INSERT INTO users(name) VALUES (?)", ("alice",))
    print("   提交后查询到：", run_sql(db, "SELECT name FROM users"))

    print("=" * 60)
    print("2. 自动回滚：with 块抛异常 -> rollback，异常向上传播")
    try:
        with DatabaseSession(db) as conn:
            conn.execute("INSERT INTO users(name) VALUES (?)", ("bob",))
            raise RuntimeError("模拟业务出错")
    except RuntimeError as e:
        print("   捕获到传播的异常：", e)
    print("   回滚后查询到：", run_sql(db, "SELECT name FROM users"))

    print("=" * 60)
    print("3. 自动关闭：with 块结束后连接已 close")
    with DatabaseSession(db) as conn:
        pass
    try:
        conn.execute("SELECT 1")   # 连接已关闭，应报错
    except sqlite3.ProgrammingError as e:
        print("   连接已关闭，报错符合预期：", e)

    print("=" * 60)
    print("4. @contextmanager 版本同样满足三条要求")
    with database_session(db) as conn:
        conn.execute("INSERT INTO users(name) VALUES (?)", ("carol",))
    print("   提交后查询到：", run_sql(db, "SELECT name FROM users"))


if __name__ == "__main__":
    main()
