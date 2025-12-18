"""
数据库优化脚本
直接连接数据库，执行索引创建和其他优化

这是一个独立的脚本，不依赖后端配置，直接使用指定的数据库连接信息。

使用方法:
1. 确保已安装 pymysql: pip install pymysql
2. 修改下面的数据库连接配置（如果需要）
3. 运行: python optimize_database.py
"""
import sys
import os
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================
# 数据库连接配置（直接在这里配置，不依赖后端）
# ============================================
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'database': 'srm',
    'charset': 'utf8mb4'
}

# ============================================
# 尝试导入数据库连接库
# ============================================
try:
    import pymysql
    USE_PYMYSQL = True
    USE_SQLALCHEMY = False
except ImportError:
    try:
        from sqlalchemy import create_engine, text
        USE_SQLALCHEMY = True
        USE_PYMYSQL = False
    except ImportError:
        print("[错误] 需要安装 pymysql 或 sqlalchemy")
        print("请运行: pip install pymysql")
        sys.exit(1)


def check_index_exists_pymysql(cursor, table_name, index_name):
    """检查索引是否存在"""
    try:
        cursor.execute(f"SHOW INDEXES FROM {table_name} WHERE Key_name = %s", (index_name,))
        return cursor.fetchone() is not None
    except:
        return False


def execute_sql_file_pymysql(connection, sql_file_path):
    """使用 pymysql 执行 SQL 文件"""
    print(f"\n正在执行: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割 SQL 语句（按分号和换行）
    statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        # 跳过注释和空行
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        
        current_statement += line + ' '
        
        # 如果行以分号结尾，说明是一个完整的 SQL 语句
        if line.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""
    
    # 执行所有 SQL 语句
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    cursor = connection.cursor()
    try:
        for statement in statements:
            if not statement:
                continue
            
            # 提取表名和索引名（用于检查）
            table_name = None
            index_name = None
            
            if 'CREATE INDEX' in statement.upper():
                # 解析: CREATE INDEX idx_name ON table_name(...)
                parts = statement.upper().split()
                try:
                    idx_pos = parts.index('INDEX')
                    index_name = parts[idx_pos + 1].split('(')[0] if idx_pos + 1 < len(parts) else None
                    on_pos = parts.index('ON')
                    table_name = parts[on_pos + 1].split('(')[0] if on_pos + 1 < len(parts) else None
                except:
                    pass
                
                # 检查索引是否已存在
                if table_name and index_name and check_index_exists_pymysql(cursor, table_name, index_name):
                    print(f"  [跳过] 索引已存在: {index_name}")
                    skipped_count += 1
                    continue
            
            try:
                cursor.execute(statement)
                connection.commit()
                success_count += 1
                # 提取索引名称用于显示
                if 'CREATE INDEX' in statement.upper() and index_name:
                    print(f"  [OK] 创建索引: {index_name}")
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                # 如果索引已存在，忽略错误
                if 'Duplicate key name' in error_msg or 'already exists' in error_msg.lower() or 'Duplicate' in error_msg or '1061' in error_msg:
                    print(f"  [跳过] 索引已存在: {index_name if index_name else '未知'}")
                    skipped_count += 1
                    success_count += 1
                    error_count -= 1
                else:
                    print(f"  [错误] 执行失败: {error_msg}")
                    print(f"     SQL: {statement[:100]}...")
    finally:
        cursor.close()
    
    print(f"\n执行完成: 成功 {success_count} 条, 跳过 {skipped_count} 条, 失败 {error_count} 条")
    return success_count, error_count


def execute_sql_file_sqlalchemy(connection, sql_file_path):
    """使用 sqlalchemy 执行 SQL 文件"""
    print(f"\n正在执行: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割 SQL 语句（按分号和换行）
    statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        # 跳过注释和空行
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        
        current_statement += line + ' '
        
        # 如果行以分号结尾，说明是一个完整的 SQL 语句
        if line.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""
    
    # 执行所有 SQL 语句
    success_count = 0
    error_count = 0
    
    for statement in statements:
        if not statement:
            continue
        
        try:
            connection.execute(text(statement))
            connection.commit()
            success_count += 1
            # 提取索引名称用于显示
            if 'CREATE INDEX' in statement.upper():
                index_name = statement.split('idx_')[1].split()[0] if 'idx_' in statement else '未知'
                print(f"  [OK] 创建索引: {index_name}")
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            # 如果索引已存在，忽略错误
            if 'Duplicate key name' in error_msg or 'already exists' in error_msg.lower() or 'Duplicate' in error_msg:
                print(f"  [警告] 索引已存在，跳过")
                success_count += 1
                error_count -= 1
            else:
                print(f"  [错误] 执行失败: {error_msg}")
                print(f"     SQL: {statement[:100]}...")
    
    print(f"\n执行完成: 成功 {success_count} 条, 失败 {error_count} 条")
    return success_count, error_count


def check_indexes_pymysql(connection):
    """使用 pymysql 检查现有索引"""
    print("\n正在检查现有索引...")
    
    tables = [
        'suppliers', 'projects', 'quotations', 'users',
        'project_items', 'quotation_items', 'project_milestones',
        'upload_files', 'supplier_project_history'
    ]
    
    cursor = connection.cursor()
    try:
        for table in tables:
            try:
                cursor.execute(f"SHOW INDEXES FROM {table}")
                indexes = cursor.fetchall()
                if indexes:
                    index_names = set([idx[2] for idx in indexes])  # index_name 在第3列（索引从0开始）
                    print(f"  {table}: {len(index_names)} 个索引")
            except Exception as e:
                print(f"  {table}: 表不存在或无法查询 - {e}")
    finally:
        cursor.close()


def check_indexes_sqlalchemy(connection):
    """使用 sqlalchemy 检查现有索引"""
    print("\n正在检查现有索引...")
    
    tables = [
        'suppliers', 'projects', 'quotations', 'users',
        'project_items', 'quotation_items', 'project_milestones',
        'upload_files', 'supplier_project_history'
    ]
    
    for table in tables:
        try:
            result = connection.execute(text(f"SHOW INDEXES FROM {table}"))
            indexes = result.fetchall()
            if indexes:
                index_names = set([idx[2] for idx in indexes])  # index_name 在第3列（索引从0开始）
                print(f"  {table}: {len(index_names)} 个索引")
        except Exception as e:
            print(f"  {table}: 表不存在或无法查询 - {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("数据库优化脚本")
    print("=" * 60)
    print(f"数据库: {DB_CONFIG['database']}")
    print(f"主机: {DB_CONFIG['host']}")
    print("=" * 60)
    
    try:
        # 连接数据库
        print("\n正在连接数据库...")
        
        if USE_PYMYSQL:
            connection = pymysql.connect(**DB_CONFIG)
            print("[OK] 数据库连接成功 (使用 pymysql)")
            check_indexes = check_indexes_pymysql
            execute_sql_file = execute_sql_file_pymysql
        else:
            DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
            engine = create_engine(DATABASE_URL, echo=False)
            connection = engine.connect()
            print("[OK] 数据库连接成功 (使用 sqlalchemy)")
            check_indexes = check_indexes_sqlalchemy
            execute_sql_file = execute_sql_file_sqlalchemy
        
        # 检查现有索引
        check_indexes(connection)
        
        # 执行索引创建脚本
        sql_file = Path(__file__).parent / "migrations" / "add_indexes.sql"
        if sql_file.exists():
            success_count, error_count = execute_sql_file(connection, sql_file)
            
            # 再次检查索引
            print("\n" + "=" * 60)
            print("优化后的索引情况:")
            print("=" * 60)
            check_indexes(connection)
            
            print("\n" + "=" * 60)
            if error_count == 0:
                print("[OK] 数据库优化完成！")
            else:
                print(f"[警告] 数据库优化完成，但有 {error_count} 个错误")
            print("=" * 60)
        else:
            print(f"[错误] SQL 文件不存在: {sql_file}")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n[错误] 数据库操作失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n提示: 如果提示模块未找到，请运行: pip install pymysql")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()
        if 'engine' in locals():
            engine.dispose()
        print("\n数据库连接已关闭")


if __name__ == "__main__":
    main()

