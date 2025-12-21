#!/usr/bin/env python
"""
SQLite 到 MySQL 数据迁移脚本

使用方法：
1. 将SQLite数据库文件放在项目根目录，命名为 db.sqlite3
2. 确保Docker MySQL容器正在运行
3. 运行: python migrate_sqlite_to_mysql.py

注意：此脚本会清空MySQL中的现有数据！
"""

import sqlite3
import mysql.connector
import sys
from datetime import datetime

# SQLite 数据库配置
SQLITE_DB = 'db.sqlite3'

# MySQL 数据库配置（Docker环境）
MYSQL_CONFIG = {
    'host': 'db',
    'port': 3306,  # Docker容器映射到主机33306端口（避免与本地MySQL冲突）
    'user': 'root',
    'password': 'database',
    'database': 'minor_review',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_mysql_connection():
    """连接到MySQL数据库"""
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.Error as e:
        print(f"❌ 无法连接到MySQL: {e}")
        print("\n提示：")
        print("1. 确保Docker容器正在运行: docker-compose ps")
        print("2. 确保MySQL端口已暴露，在docker-compose.yaml的db服务中添加：")
        print("   ports:")
        print("     - \"3306:3306\"")
        print("3. 重启容器: docker-compose restart db")
        sys.exit(1)

def get_sqlite_connection():
    """连接到SQLite数据库"""
    try:
        return sqlite3.connect(SQLITE_DB)
    except sqlite3.Error as e:
        print(f"❌ 无法连接到SQLite: {e}")
        print(f"请确保 {SQLITE_DB} 文件存在")
        sys.exit(1)

def get_table_list(sqlite_conn):
    """获取SQLite中所有用户表"""
    cursor = sqlite_conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]

def get_table_schema(sqlite_conn, table_name):
    """获取表的列信息"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def convert_value(value):
    """转换SQLite值到MySQL兼容格式"""
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    return value

def migrate_table(sqlite_conn, mysql_conn, table_name):
    """迁移单个表的数据"""
    print(f"  迁移表 {table_name}...", end=' ')
    
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    try:
        # 获取所有数据
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print("✓ (空表)")
            return 0
        
        # 获取列名
        columns = [desc[0] for desc in sqlite_cursor.description]
        
        # 清空MySQL表（如果存在）
        mysql_cursor.execute(f"DELETE FROM {table_name}")
        
        # 准备插入语句
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([f"`{col}`" for col in columns])
        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        # 批量插入数据
        converted_rows = []
        for row in rows:
            converted_row = tuple(convert_value(val) for val in row)
            converted_rows.append(converted_row)
        
        mysql_cursor.executemany(insert_sql, converted_rows)
        mysql_conn.commit()
        
        print(f"✓ ({len(rows)} 条记录)")
        return len(rows)
        
    except mysql.connector.Error as e:
        print(f"✗ MySQL错误: {e}")
        mysql_conn.rollback()
        return 0
    except Exception as e:
        print(f"✗ 错误: {e}")
        mysql_conn.rollback()
        return 0

def main():
    """主函数"""
    print("=" * 60)
    print("SQLite 到 MySQL 数据迁移工具")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 确认操作
    response = input("⚠️  此操作将覆盖MySQL中的现有数据，是否继续？(yes/no): ")
    if response.lower() != 'yes':
        print("已取消操作")
        return
    
    print("\n连接数据库...")
    sqlite_conn = get_sqlite_connection()
    mysql_conn = get_mysql_connection()
    print("✓ 数据库连接成功\n")
    
    # 禁用外键检查
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    mysql_conn.commit()
    print("✓ 已禁用外键检查\n")
    
    # 获取表列表
    tables = get_table_list(sqlite_conn)
    print(f"找到 {len(tables)} 个表\n")
    
    # 排除Django系统表（可选）
    skip_tables = []  # 例如: ['django_migrations', 'django_content_type']
    tables_to_migrate = [t for t in tables if t not in skip_tables]
    
    print("开始迁移数据...")
    print("-" * 60)
    
    total_records = 0
    successful_tables = 0
    
    for table in tables_to_migrate:
        count = migrate_table(sqlite_conn, mysql_conn, table)
        if count >= 0:
            successful_tables += 1
            total_records += count
    
    print("-" * 60)
    print(f"\n✓ 迁移完成！")
    print(f"  - 成功迁移表: {successful_tables}/{len(tables_to_migrate)}")
    print(f"  - 总记录数: {total_records}")
    
    # 重新启用外键检查
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    mysql_conn.commit()
    print("\n✓ 已重新启用外键检查")
    
    # 关闭连接
    sqlite_conn.close()
    mysql_conn.close()
    print("✓ 数据库连接已关闭")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        sys.exit(1)
