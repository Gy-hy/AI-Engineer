"""数据库会话管理器：自动提交、回滚、关闭。

对应教程：`02 教程/05 Context Manager.md` —— 必做项目（Database Session Manager）。

用标准库 sqlite3 演示（零依赖），但同样的模式适用于任何提供
commit / rollback / close 的数据库驱动（psycopg、pymysql 等）。

提供两种等价实现，用于对比：
- `DatabaseSession`：类方式（显式、可存状态、可复用）
- `database_session`：@contextmanager 生成器方式（简洁）
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator


class DatabaseSession:
    """类实现版本：管理一个数据库连接的事务与生命周期。

    三条保证：
    1. 自动提交 —— with 块正常结束 -> commit
    2. 自动回滚 —— with 块抛异常 -> rollback，异常继续向上传播
    3. 自动关闭 —— 无论提交还是回滚 -> close
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_path)
        return self.conn          # 把连接交给 with 块

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.conn is None:
            return False
        try:
            if exc_type is None:
                self.conn.commit()     # 正常路径：提交
            else:
                self.conn.rollback()   # 异常路径：回滚
        finally:
            self.conn.close()          # 无论如何：关闭连接
        return False                    # 不吞异常，让它继续传播


@contextmanager
def database_session(db_path: str) -> Iterator[sqlite3.Connection]:
    """@contextmanager 版本：与 DatabaseSession 功能等价。"""
    conn = sqlite3.connect(db_path)
    try:
        yield conn          # 把连接交给 with 块
    except Exception:
        conn.rollback()     # 异常：回滚
        raise               # 重新抛出，让调用方感知
    else:
        conn.commit()       # 正常：提交
    finally:
        conn.close()        # 无论如何：关闭
