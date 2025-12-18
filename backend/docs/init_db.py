"""
数据库初始化脚本
创建数据库表并初始化默认数据
"""
import sys
from sqlalchemy import create_engine, text
from app.db.database import Base, SessionLocal
from app.models import User, Role, Permission
from app.core.config import settings
from app.core.security import get_password_hash


def create_database():
    """创建数据库"""
    print("正在创建数据库...")
    
    # 连接MySQL服务器（不指定数据库）
    engine_url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}"
    engine = create_engine(engine_url)
    
    try:
        with engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(
                text(f"SHOW DATABASES LIKE '{settings.DB_NAME}'")
            )
            if not result.fetchone():
                # 创建数据库
                conn.execute(
                    text(f"CREATE DATABASE {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
                )
                conn.commit()
                print(f"数据库 {settings.DB_NAME} 创建成功！")
            else:
                print(f"数据库 {settings.DB_NAME} 已存在")
    except Exception as e:
        print(f"创建数据库失败: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


def create_tables():
    """创建数据表"""
    print("正在创建数据表...")
    
    from app.db.database import engine
    
    try:
        Base.metadata.create_all(bind=engine)
        print("数据表创建成功！")
    except Exception as e:
        print(f"创建数据表失败: {e}")
        sys.exit(1)


def init_data():
    """初始化基础数据"""
    print("正在初始化基础数据...")
    
    db = SessionLocal()
    
    try:
        # 检查是否已经初始化
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("数据已初始化，跳过...")
            return
        
        # 创建默认权限
        permissions = [
            # 用户权限
            Permission(name="用户查看", code="user:view", resource="user", action="view", description="查看用户信息"),
            Permission(name="用户创建", code="user:create", resource="user", action="create", description="创建用户"),
            Permission(name="用户编辑", code="user:edit", resource="user", action="edit", description="编辑用户信息"),
            Permission(name="用户删除", code="user:delete", resource="user", action="delete", description="删除用户"),
            # 角色权限
            Permission(name="角色查看", code="role:view", resource="role", action="view", description="查看角色信息"),
            Permission(name="角色管理", code="role:manage", resource="role", action="manage", description="管理角色"),
            # 供应商权限
            Permission(name="供应商查看", code="supplier:view", resource="supplier", action="view", description="查看供应商信息"),
            Permission(name="供应商审核", code="supplier:audit", resource="supplier", action="audit", description="审核供应商资质"),
            # 项目权限
            Permission(name="项目查看", code="project:view", resource="project", action="view", description="查看项目"),
            Permission(name="项目创建", code="project:create", resource="project", action="create", description="创建项目"),
            Permission(name="项目编辑", code="project:edit", resource="project", action="edit", description="编辑项目"),
            Permission(name="项目删除", code="project:delete", resource="project", action="delete", description="删除项目"),
            Permission(name="项目发布", code="project:publish", resource="project", action="publish", description="发布项目"),
            # 报价权限
            Permission(name="报价查看", code="quotation:view", resource="quotation", action="view", description="查看报价"),
            Permission(name="报价创建", code="quotation:create", resource="quotation", action="create", description="创建报价"),
            Permission(name="报价编辑", code="quotation:edit", resource="quotation", action="edit", description="编辑报价"),
            Permission(name="报价评审", code="quotation:evaluate", resource="quotation", action="evaluate", description="评审报价"),
        ]
        
        db.add_all(permissions)
        db.flush()
        
        # 项目相关权限
        project_permissions = [p for p in permissions if p.resource == "project"]
        quotation_view_permissions = [p for p in permissions if p.code in ["quotation:view", "quotation:evaluate"]]
        
        # 供应商相关权限
        supplier_permissions = [p for p in permissions if p.code in ["project:view", "quotation:view", "quotation:create", "quotation:edit"]]
        
        # 创建默认角色
        admin_role = Role(
            name="超级管理员",
            code="admin",
            description="系统超级管理员，拥有所有权限",
            permissions=permissions
        )
        
        project_manager_role = Role(
            name="项目经理",
            code="project_manager",
            description="分公司项目负责人，可管理招标项目和查看报价",
            permissions=project_permissions + quotation_view_permissions
        )
        
        supplier_role = Role(
            name="供应商",
            code="supplier",
            description="供应商角色，可查看项目并进行报价",
            permissions=supplier_permissions
        )
        
        user_role = Role(
            name="普通用户",
            code="user",
            description="普通用户角色"
        )
        
        db.add(admin_role)
        db.add(project_manager_role)
        db.add(supplier_role)
        db.add(user_role)
        db.flush()
        
        # 创建默认管理员
        admin_user = User(
            username=settings.DEFAULT_ADMIN_USERNAME,
            email="admin@example.com",
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True,
            roles=[admin_role]
        )
        
        db.add(admin_user)
        db.flush()
        
        # 创建默认公司（分公司）
        from app.models.company import Company
        
        companies_data = [
            Company(
                company_code="HQ",
                company_name="集团总部",
                company_type="总部",
                contact_person="总经理",
                contact_phone="010-88888888",
                province="北京市",
                city="北京市",
                address="朝阳区建国路88号",
                sort_order=1
            ),
            Company(
                company_code="BJ01",
                company_name="北京分公司",
                company_type="分公司",
                contact_person="北京负责人",
                contact_phone="010-66666666",
                province="北京市",
                city="北京市",
                address="海淀区中关村大街1号",
                sort_order=2
            ),
            Company(
                company_code="SH01",
                company_name="上海分公司",
                company_type="分公司",
                contact_person="上海负责人",
                contact_phone="021-88888888",
                province="上海市",
                city="上海市",
                address="浦东新区陆家嘴环路1000号",
                sort_order=3
            ),
        ]
        
        db.add_all(companies_data)
        db.flush()
        
        # 创建默认品牌
        from app.models.brand import Brand
        
        brands_data = [
            Brand(
                brand_code="LENOVO",
                brand_name="联想",
                brand_name_en="Lenovo",
                category="电子产品",
                origin_country="中国",
                manufacturer="联想集团",
                is_recommended=True,
                sort_order=1
            ),
            Brand(
                brand_code="HUAWEI",
                brand_name="华为",
                brand_name_en="HUAWEI",
                category="电子产品",
                origin_country="中国",
                manufacturer="华为技术有限公司",
                is_recommended=True,
                sort_order=2
            ),
            Brand(
                brand_code="HA螺",
                brand_name="海螺水泥",
                category="建筑材料",
                origin_country="中国",
                manufacturer="安徽海螺水泥股份有限公司",
                sort_order=3
            ),
        ]
        
        db.add_all(brands_data)
        db.commit()
        
        print("基础数据初始化成功！")
        print(f"默认管理员账号: {settings.DEFAULT_ADMIN_USERNAME}")
        
        # 安全提示：不直接输出密码
        if not settings.DEFAULT_ADMIN_PASSWORD or settings.DEFAULT_ADMIN_PASSWORD == "admin123":
            print("⚠️  警告：使用默认密码 'admin123'")
            print("⚠️  生产环境部署前必须修改密码！")
            print("⚠️  请在 .env 文件中设置：DEFAULT_ADMIN_PASSWORD=你的强密码")
        else:
            print("✅ 管理员密码已从环境变量读取（不显示）")
        
        print("已创建 {0} 个默认公司".format(len(companies_data)))
        print("已创建 {0} 个默认品牌".format(len(brands_data)))
        print("请尽快修改默认密码！")
        
    except Exception as e:
        print(f"初始化数据失败: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 50)
    print("SRM 数据库初始化工具")
    print("=" * 50)
    
    # 1. 创建数据库
    create_database()
    
    # 2. 创建数据表
    create_tables()
    
    # 3. 初始化数据
    init_data()
    
    print("=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()

