"""
数据库迁移脚本：为suppliers表添加tax_number, bank_name, bank_account字段
"""
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'database': 'srm',
    'charset': 'utf8mb4'
}

def add_supplier_fields():
    """添加供应商表的缺失字段"""
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 检查字段是否存在，如果不存在则添加
        cursor.execute("SHOW COLUMNS FROM suppliers LIKE 'tax_number'")
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE suppliers 
                ADD COLUMN tax_number VARCHAR(50) NULL COMMENT '公司税号' AFTER company_name
            """)
            print("✓ 已添加 tax_number 字段")
        else:
            print("- tax_number 字段已存在")
        
        cursor.execute("SHOW COLUMNS FROM suppliers LIKE 'bank_name'")
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE suppliers 
                ADD COLUMN bank_name VARCHAR(200) NULL COMMENT '开户行' AFTER business_scope
            """)
            print("✓ 已添加 bank_name 字段")
        else:
            print("- bank_name 字段已存在")
        
        cursor.execute("SHOW COLUMNS FROM suppliers LIKE 'bank_account'")
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE suppliers 
                ADD COLUMN bank_account VARCHAR(50) NULL COMMENT '银行账号' AFTER bank_name
            """)
            print("✓ 已添加 bank_account 字段")
        else:
            print("- bank_account 字段已存在")
        
        # 更新现有字段注释
        cursor.execute("""
            ALTER TABLE suppliers 
            MODIFY COLUMN company_address VARCHAR(500) NULL COMMENT '注册地址'
        """)
        
        cursor.execute("""
            ALTER TABLE suppliers 
            MODIFY COLUMN business_scope TEXT NULL COMMENT '主营产品'
        """)
        
        connection.commit()
        print("\n✓ 数据库迁移完成！")
        
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    print("开始执行数据库迁移...")
    add_supplier_fields()
