20251105 09.00
1、已完成大部分功能

20251105 09.30
1、替换各个组件中重复定义的函数  formatDate、formatAmount 等函数
2、使用新组件重构现有页面 使用 ActionButtons、FormDialog 等组件
3、新增项目分类
4、完善个人资料
5、修复已知问题

20251106 10.00
1、完成代码统一优化；

20251106 13.00
1、开始增加项目节点流程管理
2、增加项目评审功能；

20251107 9.00
1、用户名密码错误提示修复；1
2、增加角色权限分配菜单管理功能；1
3、增加权限管理菜单；1
4、项目类别菜单无法点开报错；1
5、修复图片、手机号显示的问题；1
6、修复排除管理员信息在供应商列表；

20251107 10.00
1、分析后端框架，优化后端管理；
修复默认管理员密码硬编码问题（极高优先级）
提取文件权限检查代码到统一模块（高优先级）
实现统一异常处理机制（高优先级）
2、修复数据库索引优化，日志系统，文件路径安全验证；
3、统一查询工具模块，优化大数据量查询的问题；
4、报价详情页缺少中标操作；

20251107 12.00
1、修复创建项目失败的错误；1
2、创建操作日志模型和数据库表
创建操作日志服务
在关键操作处添加日志记录
创建操作日志查询接口
3、修复创建项目的验证提示错误；1
4、更新所有表单页面的验证方式统一化；1
5、项目详情页中的附件图片类型预览不显示；1
6、新增权限报错的故障修复；1

20251107 13.00
1、修复登录过期的问题；1
2、重新规划仪表盘显示；1
3、项目详情页增加参与项目的按钮跳转到需求报价；1

20251107 14.00
1、通过审核的供应商无法参与报价修复；
2、增加供应商参与报价之后可取消、重新报价的功能；
3、修复基于用户活动的自动退出机制：30分钟无操作后退出，而不是基于 token 过期时间。

20251107 15.00
1、增加报价明细的品牌和型号的功能
以上比较稳定


20251107 16.00 优化版
1、清理前后端测试和无效代码；1
2、检查前后端硬编码，尤其是URL，给出系统部署方案；
前端硬编码修复，创建统一API配置工具
新建 frontend/src/utils/api.js
后端硬编码修复
CORS配置优化
修改 backend/app/core/config.py：
修改 backend/main.py：简化CORS配置，直接使用 settings.CORS_ORIGINS

已修复发现的错误：1
重新报价提交失败；公司资料更新报错；修复了 vite.config.js 的代理配置；
去掉项目列表完成度的百分比显示；登录用户后端 token 过期时间修复；
报价中的单价计算问题修复完成；

3、检查后端有没有CDN使用
仅在使用 Swagger UI（/api/v1/docs）和 ReDoc（/api/v1/redoc）时加载；
FastAPI 框架内置的 API 文档使用了 CDN，应用代码未使用 CDN；
4、检查前端有没有CDN使用
5、管理员后台增加清空缓存按钮的功能；

20251108 09.00 优化版
1、用户角色权限分配菜单样式修改；
2、用户列表增加搜索功能；
3、修复硬编码，前后端都采取环境变量配置，开发环境可随意更换前端端口

20251109 20.00
1、修复3个权限菜单显示不正常的问题，还没有彻底修复权限硬编码

20251112 14.00
1、修复列宽及按钮样式；

20251112 15.00
1、移除仪表盘甘特图；

20251114 14.00
1、仪表盘数据权限修复，各自角色只能查看自己的数据信息；
2、修复项目经理只可以查看自己发布项目的供应商信息；





1panel配置说明：
第一步：后端：修改.env数据库地址172.18.0.4密码jQmxdXTJ3dAz28Hr
目录下执行python启动命令：
python -m venv venv && pip install --upgrade pip && source venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8001
第二步：前端：.env 配置如下
# Vite 开发服务器端口
VITE_DEV_PORT=3000  （也就是要启动的前端端口）
# 后端API地址，用于代理
VITE_PROXY_TARGET=http://172.18.0.3:8001（对接后端端口容器内网IP）
第三步：重启node环境

超管密码：
13800138000 
admin123



jQmxdXTJ3dAz28Hr

cd d:/trae/srm
venv\Scripts\activate.bat
uvicorn main:app --reload --host 0.0.0.0 --port 8001

/opt/1panel/apps/openresty/openresty/www/sites/SRM/app
python -m venv venv && pip install --upgrade pip && source venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8001



http://www.google.cn/chrome/browser/desktop/index.html?standalone=1&platform=win64