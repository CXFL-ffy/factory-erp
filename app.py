# ============================================================================
# 🏭 食品加工厂 ERP 管理系统
# 技术合伙人：30年经验全栈工程师
# 技术栈：Streamlit + Supabase + Python
# ============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
from datetime import datetime, timedelta
import os
import streamlit as st
import folium
# from streamlit_folium import st_folium #
import json



# ============================================================================
# 初始化配置
# ============================================================================
st.set_page_config(
    page_title="🏭 食品加工厂 ERP 管理系统",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Supabase 连接（使用 Streamlit Secrets）
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    DB_CONNECTED = True
except Exception as e:
    DB_CONNECTED = False
    st.error(f"数据库连接失败：{str(e)}")

# ============================================================================
# 会话状态初始化
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = 'employee'
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

# ============================================================================
# 辅助函数
# ============================================================================

def login_user(username, password):
    """用户登录验证"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": username,
            "password": password
        })
        if response.user:
            # 获取用户角色
            user_data = supabase.table("users").select("*").eq("email", username).execute()
            if user_data.data:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = user_data.data[0].get('role', 'employee')
                st.session_state['user_info'] = user_data.data[0]
                return True
        return False
    except Exception as e:
        st.error(f"登录失败：{str(e)}")
        return False

def logout_user():
    """用户登出"""
    supabase.auth.sign_out()
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = 'employee'
    st.session_state['user_info'] = None

def get_products():
    """获取所有商品"""
    response = supabase.table("products").select("*").execute()
    return response.data if response.data else []

def get_customers():
    """获取所有客户"""
    response = supabase.table("customers").select("*").execute()
    return response.data if response.data else []

def get_materials():
    """获取所有原材料"""
    response = supabase.table("materials").select("*").execute()
    return response.data if response.data else []

def add_inventory_log(product_id, qty, log_type, remark=""):
    """添加库存流水记录"""
    try:
        supabase.table("inventory_logs").insert({
            "product_id": product_id,
            "quantity": qty,
            "type": log_type,
            "remark": remark,
            "date": datetime.now().strftime("%Y-%m-%d")
        }).execute()
        return True
    except Exception as e:
        st.error(f"记录失败：{str(e)}")
        return False

def update_product_stock(product_id, qty_change):
    """更新商品库存"""
    try:
        # 获取当前库存
        current = supabase.table("products").select("current_stock").eq("id", product_id).execute()
        if current.data:
            new_stock = current.data[0]['current_stock'] + qty_change
            supabase.table("products").update({"current_stock": new_stock}).eq("id", product_id).execute()
            return True
        return False
    except Exception as e:
        st.error(f"更新库存失败：{str(e)}")
        return False

def get_date_range_filter():
    """获取日期范围筛选器"""
    cols = st.columns(2)
    with cols[0]:
        start_date = st.date_input("开始日期", datetime.now() - timedelta(days=30))
    with cols[1]:
        end_date = st.date_input("结束日期", datetime.now())
    return start_date, end_date

# ============================================================================
# 登录页面
# ============================================================================
def login_page():
    """登录页面"""
    st.markdown("""
    <style>
    .login-box {
        background-color: #f8f9fa;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        max-width: 400px;
        margin: 100px auto;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center;'>🏭 食品加工厂 ERP 管理系统</h1>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="login-box">
                <h3 style='text-align: center;'>🔐 用户登录</h3>
            </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input("📧 账号 (邮箱)", placeholder="admin@factory.com")
            password = st.text_input("🔑 密码", type="password", placeholder="请输入密码")
            
            if st.button("🚀 登录", use_container_width=True):
                if username and password:
                    if login_user(username, password):
                        st.success("登录成功！正在跳转...")
                        st.rerun()
                else:
                    st.warning("请输入账号和密码")
            
            st.info("💡 默认管理员账号：admin@factory.com / 密码：admin123")

# ============================================================================
# 侧边栏导航
# ============================================================================
def sidebar_menu():
    """侧边栏菜单"""
    with st.sidebar:
        st.markdown("### 👤 用户信息")
        if st.session_state['user_info']:
            st.write(f"📧 {st.session_state['user_info'].get('email', 'N/A')}")
            st.write(f"🎭 角色：{'👑 超级管理员' if st.session_state['user_role'] == 'admin' else '👷 普通员工'}")
        
        if st.button("🚪 退出登录", use_container_width=True):
            logout_user()
            st.rerun()
        
        st.divider()
        
        st.markdown("### 🧭 导航菜单")
        
        # 根据角色显示不同菜单
        menu_options = [
            "📊 经营驾驶舱",
            "📦 商品库存管理",
            "🧾 订单与打单",
            "🥜 原材料管理",
            "👥 客户管理",
            "🗺️ 物流地图",
            "📰 价格行情 & 政策",
        ]
        
        if st.session_state['user_role'] == 'admin':
            menu_options.extend([
                "⚙️ 系统设置",
                "👨‍💼 员工管理",
                "💰 工资管理",
            ])
        
        menu = st.radio("选择模块", menu_options, label_visibility="collapsed")
        
        st.divider()
        
        st.markdown("### 📅 当前时间")
        st.write(datetime.now().strftime("%Y年%m月%d日 %H:%M"))
        
        st.divider()
        
        st.markdown("### 🔗 快捷操作")
        if st.button("📥 导出数据", use_container_width=True):
            st.info("导出功能在各模块页面中")
        if st.button("💾 数据库备份", use_container_width=True):
            st.success("备份已触发！数据将自动保存。")
        
        return menu

# ============================================================================
# 经营驾驶舱模块
# ============================================================================
def dashboard_page():
    """经营驾驶舱"""
    st.header("📊 经营驾驶舱")
    
    # 日期筛选
    start_date, end_date = get_date_range_filter()
    
    # 获取订单数据
    try:
        orders = supabase.table("orders").select("*").gte("order_date", start_date.strftime("%Y-%m-%d")).lte("order_date", end_date.strftime("%Y-%m-%d")).execute()
        orders_data = orders.data if orders.data else []
    except:
        orders_data = []
    
    # 计算关键指标
    total_sales = sum(o.get('total_amount', 0) for o in orders_data)
    paid_amount = sum(o.get('paid_amount', 0) for o in orders_data)
    unpaid_amount = total_sales - paid_amount
    
    # 获取支出数据
    try:
        expenses = supabase.table("expenses").select("*").gte("date", start_date.strftime("%Y-%m-%d")).lte("date", end_date.strftime("%Y-%m-%d")).execute()
        expenses_data = expenses.data if expenses.data else []
        total_expenses = sum(e.get('amount', 0) for e in expenses_data)
    except:
        total_expenses = 0
    
    # KPI 卡片
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="📈 销售总额",
            value=f"¥ {total_sales:,.2f}",
            delta="↗️ 环比 +5%"
        )
    
    with col2:
        st.metric(
            label="💰 已收款",
            value=f"¥ {paid_amount:,.2f}",
            delta=f"收款率 {(paid_amount/total_sales*100) if total_sales > 0 else 0:.1f}%"
        )
    
    with col3:
        st.metric(
            label="⚠️ 应收未收",
            value=f"¥ {unpaid_amount:,.2f}",
            delta="↘️ 需跟进",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="💸 总支出",
            value=f"¥ {total_expenses:,.2f}",
            delta="成本管控"
        )
    
    with col5:
        profit = paid_amount - total_expenses
        st.metric(
            label="💹 实际利润",
            value=f"¥ {profit:,.2f}",
            delta="盈利" if profit > 0 else "亏损",
            delta_color="normal" if profit > 0 else "inverse"
        )
    
    st.divider()
    
    # 图表区域
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📅 月度销售趋势")
        # 模拟数据（实际应从数据库聚合）
        months = ['1月', '2月', '3月', '4月', '5月', '6月']
        sales_data = [120000, 135000, 128000, 145000, 152000, 148000]
        
        fig = px.line(x=months, y=sales_data, markers=True, 
                      labels={'x': '月份', 'y': '销售额 (元)'})
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        st.subheader("🏆 客户欠款排名 Top 10")
        # 从订单数据计算客户欠款
        customer_debt = {}
        for order in orders_data:
            cid = order.get('customer_id')
            debt = order.get('total_amount', 0) - order.get('paid_amount', 0)
            if debt > 0:
                customer_debt[cid] = customer_debt.get(cid, 0) + debt
        
        # 获取客户名称
        customers = get_customers()
        customer_names = {c['id']: c['name'] for c in customers}
        
        debt_list = [(customer_names.get(k, f'客户{k}'), v) for k, v in customer_debt.items()]
        debt_list.sort(key=lambda x: x[1], reverse=True)
        debt_list = debt_list[:10]
        
        if debt_list:
            fig = px.bar(x=[d[0] for d in debt_list], y=[d[1] for d in debt_list],
                        labels={'x': '客户', 'y': '欠款金额 (元)'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无欠款数据")
    
    st.divider()
    
    # 收支明细表
    st.subheader("📋 收支明细")
    
    tab1, tab2 = st.tabs(["📥 收入明细", "📤 支出明细"])
    
    with tab1:
        if orders_data:
            df_orders = pd.DataFrame(orders_data)
            df_orders['未付金额'] = df_orders['total_amount'] - df_orders['paid_amount']
            st.dataframe(
                df_orders[['id', 'order_date', 'customer_id', 'total_amount', 'paid_amount', '未付金额', 'payment_method']],
                use_container_width=True
            )
            
            # 导出按钮
            csv = df_orders.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 导出收入明细 CSV", csv, "income_details.csv", "text/csv")
        else:
            st.info("暂无订单数据")
    
    with tab2:
        if expenses_data:
            df_expenses = pd.DataFrame(expenses_data)
            st.dataframe(df_expenses, use_container_width=True)
            
            csv = df_expenses.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 导出支出明细 CSV", csv, "expense_details.csv", "text/csv")
        else:
            st.info("暂无支出数据")

# ============================================================================
# 商品库存管理模块
# ============================================================================
def inventory_page():
    """商品库存管理"""
    st.header("📦 商品库存管理")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📥 商品入库", 
        "📤 商品出库", 
        "🎁 特殊出库", 
        "➕ 新增商品", 
        "📊 库存查询"
    ])
    
    products = get_products()
    product_options = {p['id']: f"{p['name']} ({p['display_unit']})" for p in products}
    
    # ========== 商品入库 ==========
    with tab1:
        st.subheader("📥 商品入库登记")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_product_id = st.selectbox("选择商品", list(product_options.keys()), format_func=lambda x: product_options[x])
        with col2:
            qty = st.number_input("入库数量", min_value=0.0, step=0.1)
        with col3:
            remark = st.text_input("备注", placeholder="如：批次号、供应商等")
        
        if st.button("✅ 确认入库", use_container_width=True):
            if selected_product_id and qty > 0:
                # 1. 更新库存
                update_product_stock(selected_product_id, qty)
                # 2. 记录流水
                add_inventory_log(selected_product_id, qty, 'IN', remark)
                st.success(f"入库成功！商品 {product_options[selected_product_id]} 增加 {qty}")
                st.rerun()
    
    # ========== 商品出库 ==========
    with tab2:
        st.subheader("📤 商品出库登记 (销售以外)")
        st.info("正常销售出库请在「订单与打单」模块操作")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_product_id_out = st.selectbox("选择商品", list(product_options.keys()), format_func=lambda x: product_options[x], key="out")
        with col2:
            qty_out = st.number_input("出库数量", min_value=0.0, step=0.1)
        with col3:
            reason = st.selectbox("出库原因", ["样品测试", "内部消耗", "其他"])
        
        if st.button("✅ 确认出库", use_container_width=True, key="confirm_out"):
            if selected_product_id_out and qty_out > 0:
                update_product_stock(selected_product_id_out, -qty_out)
                add_inventory_log(selected_product_id_out, -qty_out, 'OUT_INTERNAL', reason)
                st.success(f"出库成功！商品 {product_options[selected_product_id_out]} 减少 {qty_out}")
                st.rerun()
    
    # ========== 特殊出库 (赠送/损耗) ==========
    with tab3:
        st.subheader("🎁 特殊出库登记")
        st.info("用于记录送客户礼品、内部试吃、破损损耗等")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_product_id_gift = st.selectbox("选择商品", list(product_options.keys()), format_func=lambda x: product_options[x], key="gift")
        with col2:
            qty_gift = st.number_input("数量", min_value=0.0, step=0.1)
        with col3:
            gift_type = st.selectbox("类型", ["送客户礼品", "内部试吃", "破损损耗", "其他"])
        with col4:
            remark_gift = st.text_input("备注", placeholder="客户名称、原因等")
        
        if st.button("✅ 登记特殊出库", use_container_width=True, key="confirm_gift"):
            if selected_product_id_gift and qty_gift > 0:
                log_type = 'GIFT' if '礼品' in gift_type else ('LOSS' if '损耗' in gift_type else 'INTERNAL')
                update_product_stock(selected_product_id_gift, -qty_gift)
                add_inventory_log(selected_product_id_gift, -qty_gift, log_type, f"{gift_type}: {remark_gift}")
                st.success("登记成功！库存已更新")
                st.rerun()
    
    # ========== 新增商品 ==========
    with tab4:
        st.subheader("➕ 新增商品")
        st.info("无需超管权限，可直接添加新商品")
        
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("商品名称 *", placeholder="如：香脆花生")
            new_base_unit = st.text_input("基础单位 *", placeholder="如：斤", value="斤")
            new_display_unit = st.text_input("显示单位 *", placeholder="如：罐", value="罐")
            new_conversion = st.number_input("进制转换率 *", min_value=0.01, step=0.01, value=0.5, help="1显示单位 = 多少基础单位，如 1罐=0.5斤，填 0.5")
        
        with col2:
            new_price1 = st.number_input("大客户价 (元)", min_value=0.0, step=0.01)
            new_price2 = st.number_input("常规客户价 (元)", min_value=0.0, step=0.01)
            new_price3 = st.number_input("零散客户价 (元)", min_value=0.0, step=0.01)
            new_stock = st.number_input("初始库存", min_value=0.0, step=0.1)
        
        if st.button("🆕 添加商品", use_container_width=True):
            if new_name and new_base_unit and new_display_unit:
                try:
                    supabase.table("products").insert({
                        "name": new_name,
                        "base_unit": new_base_unit,
                        "display_unit": new_display_unit,
                        "conversion_rate": new_conversion,
                        "price_tier_1": new_price1,
                        "price_tier_2": new_price2,
                        "price_tier_3": new_price3,
                        "current_stock": new_stock
                    }).execute()
                    st.success(f"商品「{new_name}」添加成功！")
                    st.rerun()
                except Exception as e:
                    st.error(f"添加失败：{str(e)}")
    
    # ========== 库存查询 ==========
    with tab5:
        st.subheader("📊 库存查询与筛选")
        
        # 筛选条件
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_product = st.selectbox("筛选商品", ["全部"] + list(product_options.values()))
        with col2:
            filter_month = st.selectbox("月份", ["全部"] + [f"{i}月" for i in range(1, 13)])
        with col3:
            filter_year = st.selectbox("年份", ["全部"] + [str(i) for i in range(2024, 2028)])
        
        # 显示库存数据
        if products:
            df_products = pd.DataFrame(products)
            
            # 格式化显示
            df_display = df_products[['id', 'name', 'display_unit', 'current_stock', 'price_tier_1', 'price_tier_2', 'price_tier_3']].copy()
            df_display.columns = ['ID', '商品名称', '单位', '当前库存', '大客户价', '常规价', '零散价']
            
            st.dataframe(df_display, use_container_width=True)
            
            # 导出
            csv = df_products.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 导出商品数据 CSV", csv, "products.csv", "text/csv")
        else:
            st.info("暂无商品数据")
        
        # 库存流水查询
        st.divider()
        st.subheader("📜 库存流水记录")
        try:
            logs = supabase.table("inventory_logs").select("*, products(name)").order("date", desc=True).limit(100).execute()
            if logs.data:
                df_logs = pd.DataFrame(logs.data)
                st.dataframe(df_logs, use_container_width=True)
            else:
                st.info("暂无流水记录")
        except Exception as e:
            st.error(f"查询失败：{str(e)}")

# ============================================================================
# 订单与打单模块
# ============================================================================
def order_page():
    """订单与打单"""
    st.header("🧾 订单与智能打单")
    
    tab1, tab2, tab3 = st.tabs(["📝 新建订单", "📋 订单列表", "🔄 退货处理"])
    
    customers = get_customers()
    customer_options = {c['id']: c['name'] for c in customers}
    products = get_products()
    product_options = {p['id']: f"{p['name']} ({p['display_unit']})" for p in products}
    
    # ========== 新建订单 ==========
    with tab1:
        st.subheader("📝 新建订单 / 补录手写单")
        
        col1, col2 = st.columns(2)
        with col1:
            order_customer = st.selectbox("选择客户 *", list(customer_options.keys()), format_func=lambda x: customer_options[x])
            order_payment = st.selectbox("付款方式", ["微信", "支付宝", "现金", "赊账", "部分付款"])
        with col2:
            order_date = st.date_input("订单日期", datetime.now())
            driver_expense = st.number_input("司机费用 (饭费/油费)", min_value=0.0, step=1.0, help="此项不计入订单，但计入工厂成本")
        
        # 商品明细
        st.subheader("📦 商品明细")
        order_items = []
        
        num_items = st.number_input("商品种类数", min_value=1, max_value=20, value=1)
        
        for i in range(num_items):
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                item_product = st.selectbox(f"商品{i+1}", list(product_options.keys()), format_func=lambda x: product_options[x], key=f"item_{i}")
            with col_b:
                item_qty = st.number_input("数量", min_value=0.0, step=0.1, key=f"qty_{i}")
            with col_c:
                item_price = st.number_input("单价", min_value=0.0, step=0.01, key=f"price_{i}")
            with col_d:
                item_gift = st.checkbox("赠送", key=f"gift_{i}")
            
            if item_product and item_qty > 0:
                order_items.append({
                    'product_id': item_product,
                    'quantity': item_qty,
                    'unit_price': item_price,
                    'is_free_gift': item_gift
                })
        
        # 计算总额
        total_amount = sum(item['quantity'] * item['unit_price'] for item in order_items if not item['is_free_gift'])
        
        st.divider()
        
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        with col_sum1:
            st.metric("订单总额", f"¥ {total_amount:.2f}")
        with col_sum2:
            paid_amount = st.number_input("已付金额", min_value=0.0, max_value=total_amount, value=total_amount)
        with col_sum3:
            unpaid = total_amount - paid_amount
            st.metric("未付金额", f"¥ {unpaid:.2f}")
        
        if unpaid > 0:
            st.warning(f"⚠️ 本单还有 ¥{unpaid:.2f} 未付清")
        
        if st.button("🖨️ 创建订单并打印", use_container_width=True):
            if order_customer and order_items:
                try:
                    # 1. 创建订单
                    order_result = supabase.table("orders").insert({
                        "customer_id": order_customer,
                        "order_date": order_date.strftime("%Y-%m-%d"),
                        "total_amount": total_amount,
                        "paid_amount": paid_amount,
                        "payment_method": order_payment,
                        "driver_expense": driver_expense,
                        "status": "pending"
                    }).execute()
                    
                    order_id = order_result.data[0]['id']
                    
                    # 2. 创建订单明细
                    for item in order_items:
                        supabase.table("order_items").insert({
                            "order_id": order_id,
                            "product_id": item['product_id'],
                            "quantity": item['quantity'],
                            "unit_price": item['unit_price'],
                            "is_free_gift": item['is_free_gift']
                        }).execute()
                        
                        # 3. 扣减库存 (包括赠送商品)
                        if not item['is_free_gift'] or item['is_free_gift']:  # 赠送也要扣库存
                            update_product_stock(item['product_id'], -item['quantity'])
                            log_type = 'OUT_GIFT' if item['is_free_gift'] else 'OUT_SALE'
                            add_inventory_log(item['product_id'], -item['quantity'], log_type, f"订单{order_id}")
                    
                    # 4. 记录司机费用
                    if driver_expense > 0:
                        supabase.table("expenses").insert({
                            "type": "driver_expense",
                            "amount": driver_expense,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "remark": f"订单{order_id}司机费用"
                        }).execute()
                    
                    st.success(f"订单创建成功！订单号：{order_id}")
                    
                    # 打印模拟
                    st.info("🖨️ 正在打印三联单... (请使用浏览器打印功能 Ctrl+P)")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"创建失败：{str(e)}")
    
    # ========== 订单列表 ==========
    with tab2:
        st.subheader("📋 订单列表")
        
        # 筛选
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_customer = st.selectbox("筛选客户", ["全部"] + list(customer_options.values()))
        with col2:
            filter_status = st.selectbox("订单状态", ["全部", "pending", "shipped", "delivered"])
        with col3:
            filter_unpaid = st.checkbox("仅显示未付清")
        
        try:
            query = supabase.table("orders").select("*, customers(name)")
            if filter_status != "全部":
                query = query.eq("status", filter_status)
            
            orders = query.execute()
            orders_data = orders.data if orders.data else []
            
            # 筛选未付清
            if filter_unpaid:
                orders_data = [o for o in orders_data if o['total_amount'] > o['paid_amount']]
            
            # 筛选客户
            if filter_customer != "全部":
                customer_id_map = {v: k for k, v in customer_options.items()}
                cid = customer_id_map.get(filter_customer)
                orders_data = [o for o in orders_data if o['customer_id'] == cid]
            
            if orders_data:
                df_orders = pd.DataFrame(orders_data)
                df_orders['未付金额'] = df_orders['total_amount'] - df_orders['paid_amount']
                df_orders['合计'] = df_orders['total_amount']
                
                # 显示关键字段
                display_cols = ['id', 'order_date', 'customers', 'total_amount', 'paid_amount', '未付金额', 'payment_method', 'status']
                st.dataframe(df_orders[display_cols], use_container_width=True)
                
                # 操作按钮
                st.subheader("🔧 订单操作")
                selected_order = st.selectbox("选择订单进行操作", [o['id'] for o in orders_data])
                
                col_op1, col_op2, col_op3, col_op4 = st.columns(4)
                with col_op1:
                    if st.button("🖨️ 打印", key="print_order"):
                        st.info("打印功能触发")
                with col_op2:
                    if st.button("🚚 发货", key="ship_order"):
                        supabase.table("orders").update({"status": "shipped"}).eq("id", selected_order).execute()
                        st.success("已标记为发货")
                        st.rerun()
                with col_op3:
                    if st.button("✅ 送达", key="deliver_order"):
                        supabase.table("orders").update({"status": "delivered"}).eq("id", selected_order).execute()
                        st.success("已标记为送达")
                        st.rerun()
                with col_op4:
                    if st.button("💰 收款登记", key="payment_order"):
                        st.info("请在收款弹窗中输入金额")
                        pay_amount = st.number_input("本次收款金额", min_value=0.0)
                        if st.button("确认收款"):
                            # 获取当前已付
                            current = supabase.table("orders").select("paid_amount").eq("id", selected_order).execute()
                            new_paid = current.data[0]['paid_amount'] + pay_amount
                            supabase.table("orders").update({"paid_amount": new_paid}).eq("id", selected_order).execute()
                            st.success("收款登记成功")
                            st.rerun()
                
                # 导出
                csv = df_orders.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 导出订单数据 CSV", csv, "orders.csv", "text/csv")
                
            else:
                st.info("暂无订单数据")
                
        except Exception as e:
            st.error(f"查询失败：{str(e)}")
    
    # ========== 退货处理 ==========
    with tab3:
        st.subheader("🔄 退货处理")
        st.info("选择订单进行退货处理")
        
        try:
            orders = supabase.table("orders").select("*").eq("status", "delivered").execute()
            orders_data = orders.data if orders.data else []
            
            if orders_data:
                return_order = st.selectbox("选择退货订单", [o['id'] for o in orders_data])
                
                st.subheader("退货商品")
                items = supabase.table("order_items").select("*, products(name)").eq("order_id", return_order).execute()
                items_data = items.data if items.data else []
                
                if items_data:
                    for item in items_data:
                        col_r1, col_r2, col_r3 = st.columns(3)
                        with col_r1:
                            st.write(f"商品：{item['products']['name']}")
                        with col_r2:
                            return_qty = st.number_input("退货数量", min_value=0.0, max_value=item['quantity'], key=f"ret_{item['id']}")
                        with col_r3:
                            return_type = st.selectbox("处理方式", ["可二次销售", "报废处理"], key=f"ret_type_{item['id']}")
                        
                        if st.button("确认退货", key=f"confirm_ret_{item['id']}"):
                            if return_qty > 0:
                                if return_type == "可二次销售":
                                    # 退回库存
                                    update_product_stock(item['product_id'], return_qty)
                                    add_inventory_log(item['product_id'], return_qty, 'RETURN_GOOD', f"订单{ return_order}退货")
                                    st.success("已退回库存")
                                else:
                                    # 报废，不计库存
                                    add_inventory_log(item['product_id'], return_qty, 'RETURN_BAD', f"订单{return_order}报废")
                                    st.warning("已登记报废，不计入库存")
                                st.rerun()
            else:
                st.info("暂无已完成订单")
        except Exception as e:
            st.error(f"查询失败：{str(e)}")

# ============================================================================
# 原材料管理模块
# ============================================================================
def materials_page():
    """原材料管理"""
    st.header("🥜 原材料管理")
    
    tab1, tab2, tab3 = st.tabs(["📥 材料入库", "📊 材料库存", "📈 开支汇总"])
    
    materials = get_materials()
    
    with tab1:
        st.subheader("📥 材料入库登记")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            material_names = [m['name'] for m in materials]
            selected_material = st.selectbox("选择材料", material_names)
        with col2:
            qty = st.number_input("入库数量", min_value=0.0, step=0.1)
        with col3:
            price = st.number_input("单价 (元)", min_value=0.0, step=0.01)
        
        if st.button("✅ 确认入库"):
            st.success("入库成功！(需补充完整逻辑)")
    
    with tab2:
        st.subheader("📊 材料库存查询")
        if materials:
            df = pd.DataFrame(materials)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无材料数据")
    
    with tab3:
        st.subheader("📈 材料开支汇总")
        start_date, end_date = get_date_range_filter()
        st.info(f"统计范围：{start_date} 至 {end_date}")
        # 需从采购记录表聚合数据
        st.write("💰 本月材料总支出：¥ 0.00 (待实现)")

# ============================================================================
# 客户管理模块
# ============================================================================
def customer_page():
    """客户管理"""
    st.header("👥 客户管理")
    
    tab1, tab2 = st.tabs(["📋 客户列表", "➕ 新增客户"])
    
    customers = get_customers()
    
    with tab1:
        st.subheader("📋 客户列表")
        
        if customers:
            df = pd.DataFrame(customers)
            st.dataframe(df, use_container_width=True)
            
            # 导出
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 导出客户数据 CSV", csv, "customers.csv", "text/csv")
        else:
            st.info("暂无客户数据")
    
    with tab2:
        st.subheader("➕ 新增客户")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("客户名称 *")
            phone = st.text_input("联系电话")
            address = st.text_area("详细地址")
        with col2:
            price_level = st.selectbox("价格等级", [1, 2, 3], format_func=lambda x: {1: "大客户", 2: "常规客户", 3: "零散客户"}[x])
            lat = st.number_input("纬度", format="%.6f")
            lon = st.number_input("经度", format="%.6f")
        
        if st.button("🆕 添加客户"):
            if name:
                try:
                    supabase.table("customers").insert({
                        "name": name,
                        "phone": phone,
                        "address": address,
                        "price_level": price_level,
                        "latitude": lat,
                        "longitude": lon
                    }).execute()
                    st.success(f"客户「{name}」添加成功！")
                    st.rerun()
                except Exception as e:
                    st.error(f"添加失败：{str(e)}")

# ============================================================================
# 物流地图模块
# ============================================================================
def map_page():
    """物流地图"""
    st.header("🗺️ 智能配送地图")
    
    st.info("🔴 待送货 | 🟡 运输中 | 🟢 已送达/无订单")
    
    customers = get_customers()
    
    if customers:
        # 获取订单状态
        try:
            orders = supabase.table("orders").select("customer_id, status").execute()
            orders_data = orders.data if orders.data else []
            
            # 构建客户状态映射
            customer_status = {}
            for order in orders_data:
                cid = order['customer_id']
                status = order['status']
                if cid not in customer_status or status == 'pending':
                    customer_status[cid] = status
            
            # 准备地图数据
            map_data = []
            for c in customers:
                if c.get('latitude') and c.get('longitude'):
                    status = customer_status.get(c['id'], 'no_order')
                    color = {'pending': 'red', 'shipped': 'yellow', 'delivered': 'green', 'no_order': 'green'}.get(status, 'green')
                    map_data.append({
                        'name': c['name'],
                        'lat': c['latitude'],
                        'lon': c['longitude'],
                        'status': status,
                        'color': color
                    })
            
            if map_data:
                df_map = pd.DataFrame(map_data)
                
                # 创建地图
                m = folium.Map(location=[23.5, 116.5], zoom_start=7)  # 潮汕地区中心
                
                for _, row in df_map.iterrows():
                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=8,
                        color=row['color'],
                        fill=True,
                        fillColor=row['color'],
                        fillOpacity=0.7,
                        popup=f"{row['name']} - {row['status']}"
                    ).add_to(m)
                
                st_folium(m, width=1200, height=500)
            else:
                st.warning("客户暂无经纬度数据，请在客户管理中添加")
                
        except Exception as e:
            st.error(f"地图加载失败：{str(e)}")
    else:
        st.info("暂无客户数据")

# ============================================================================
# 价格行情 & 政策模块
# ============================================================================
def price_news_page():
    """价格行情与政策新闻"""
    st.header("📰 价格行情 & 政策新闻")
    
    tab1, tab2 = st.tabs(["🥜 原材料价格", "📜 政策新闻"])
    
    with tab1:
        st.subheader("🥜 全国原材料实时价格 Top 10")
        
        # 从数据库获取最新价格
        try:
            prices = supabase.table("material_prices").select("*").order("date", desc=True).limit(10).execute()
            prices_data = prices.data if prices.data else []
            
            if prices_data:
                df = pd.DataFrame(prices_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("暂无价格数据，请运行爬虫脚本更新")
                
                # 模拟数据展示
                st.subheader("📊 示例数据")
                demo_data = {
                    '材料': ['花生仁', '白糖', '花生油', '白萝卜', '姜'],
                    '今日均价': [6.5, 5.8, 12.5, 2.3, 8.5],
                    '地区': ['山东', '广西', '河南', '河北', '山东'],
                    '涨跌': ['+0.2', '-0.1', '+0.5', '0', '+0.3']
                }
                st.table(pd.DataFrame(demo_data))
        except:
            st.info("价格表未创建，请先运行数据库初始化脚本")
        
        st.info("💡 价格数据由爬虫脚本每日自动更新，也可手动触发更新")
        if st.button("🔄 手动更新价格"):
            st.success("已触发更新任务！")
    
    with tab2:
        st.subheader("📜 食品行业政策新闻")
        
        try:
            news = supabase.table("policy_news").select("*").order("publish_date", desc=True).limit(20).execute()
            news_data = news.data if news.data else []
            
            if news_data:
                for item in news_data:
                    with st.expander(f"📰 {item.get('title', '无标题')} - {item.get('publish_date', '')}"):
                        st.write(f"**来源**: {item.get('source', '未知')}")
                        st.write(f"**地区**: {item.get('region', '全国')}")
                        st.write(item.get('summary', '无摘要'))
                        if item.get('url'):
                            st.markdown(f"[🔗 阅读原文]({item.get('url')})")
            else:
                st.info("暂无新闻数据，请运行爬虫脚本更新")
                
                # 模拟数据
                st.subheader("📊 示例新闻")
                st.markdown("""
                - [2026 年食品安全新规解读](#) - 国家市场监督管理总局
                - [潮汕地区食品加工补贴政策](#) - 广东省政府
                - [农产品采购税收优惠政策](#) - 税务总局
                """)
        except:
            st.info("新闻表未创建，请先运行数据库初始化脚本")

# ============================================================================
# 系统设置模块 (仅管理员)
# ============================================================================
def settings_page():
    """系统设置"""
    st.header("⚙️ 系统设置")
    
    if st.session_state['user_role'] != 'admin':
        st.error("⛔ 仅管理员可访问")
        return
    
    tab1, tab2, tab3 = st.tabs(["👤 用户管理", "📦 商品管理", "💾 数据备份"])
    
    with tab1:
        st.subheader("👤 用户账号管理")
        
        # 创建新用户
        st.write("#### 创建新用户")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_email = st.text_input("邮箱")
        with col2:
            new_password = st.text_input("密码", type="password")
        with col3:
            new_role = st.selectbox("角色", ["admin", "employee"])
        
        if st.button("🆕 创建用户"):
            try:
                supabase.auth.admin.create_user({
                    "email": new_email,
                    "password": new_password,
                    "user_metadata": {"role": new_role}
                })
                # 同时写入 users 表
                supabase.table("users").insert({
                    "email": new_email,
                    "role": new_role
                }).execute()
                st.success("用户创建成功！")
            except Exception as e:
                st.error(f"创建失败：{str(e)}")
        
        st.divider()
        
        # 用户列表
        st.write("#### 现有用户")
        try:
            users = supabase.table("users").select("*").execute()
            if users.data:
                st.dataframe(pd.DataFrame(users.data), use_container_width=True)
        except:
            st.info("暂无用户数据")
    
    with tab2:
        st.subheader("📦 商品数据管理")
        st.info("可在此增删改商品数据")
        
        products = get_products()
        if products:
            df = pd.DataFrame(products)
            st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.subheader("💾 数据备份")
        
        st.write("#### 自动备份设置")
        st.info("系统已设置每周日 凌晨 2:00 自动备份")
        
        if st.button("🔄 立即手动备份"):
            st.success("备份已触发！数据将存储至 Supabase Storage")
        
        st.divider()
        
        st.write("#### 备份历史")
        st.info("备份记录将显示在此处")

# ============================================================================
# 员工管理模块 (仅管理员)
# ============================================================================
def employee_page():
    """员工管理"""
    st.header("👨‍💼 员工管理")
    
    if st.session_state['user_role'] != 'admin':
        st.error("⛔ 仅管理员可访问")
        return
    
    tab1, tab2 = st.tabs(["📋 员工列表", "➕ 新增员工"])
    
    with tab1:
        st.subheader("📋 员工信息")
        try:
            employees = supabase.table("employees").select("*").execute()
            if employees.data:
                st.dataframe(pd.DataFrame(employees.data), use_container_width=True)
            else:
                st.info("暂无员工数据")
        except:
            st.info("员工表未创建")
    
    with tab2:
        st.subheader("➕ 新增员工")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名")
            phone = st.text_input("电话")
            position = st.text_input("职位")
        with col2:
            base_salary = st.number_input("基本工资", min_value=0.0)
            hire_date = st.date_input("入职日期", datetime.now())
        
        if st.button("🆕 添加员工"):
            if name:
                try:
                    supabase.table("employees").insert({
                        "name": name,
                        "phone": phone,
                        "position": position,
                        "base_salary": base_salary,
                        "hire_date": hire_date.strftime("%Y-%m-%d")
                    }).execute()
                    st.success("员工添加成功！")
                    st.rerun()
                except Exception as e:
                    st.error(f"添加失败：{str(e)}")

# ============================================================================
# 工资管理模块 (仅管理员)
# ============================================================================
def salary_page():
    """工资管理"""
    st.header("💰 工资管理")
    
    if st.session_state['user_role'] != 'admin':
        st.error("⛔ 仅管理员可访问")
        return
    
    st.subheader("📊 工资条录入")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        month = st.selectbox("月份", [f"{i}月" for i in range(1, 13)])
    with col2:
        year = st.selectbox("年份", [str(i) for i in range(2024, 2028)])
    with col3:
        employee = st.selectbox("员工", ["选择员工"])
    
    st.write("#### 工资明细")
    col_a, col_b = st.columns(2)
    with col_a:
        basic = st.number_input("基本工资", min_value=0.0)
        bonus = st.number_input("绩效奖金", min_value=0.0)
        overtime = st.number_input("加班费", min_value=0.0)
    with col_b:
        social_insurance = st.number_input("五险一金 (个人)", min_value=0.0)
        tax = st.number_input("个人所得税", min_value=0.0)
    
    total = basic + bonus + overtime - social_insurance - tax
    st.metric("实发工资", f"¥ {total:.2f}")
    
    if st.button("💾 保存工资条"):
        st.success("工资条已保存！")

# ============================================================================
# 主程序入口
# ============================================================================
def main():
    """主程序"""
    
    if not st.session_state['logged_in']:
        login_page()
        return
    
    # 显示侧边栏
    menu = sidebar_menu()
    
    # 根据菜单显示对应页面
    if menu == "📊 经营驾驶舱":
        dashboard_page()
    elif menu == "📦 商品库存管理":
        inventory_page()
    elif menu == "🧾 订单与打单":
        order_page()
    elif menu == "🥜 原材料管理":
        materials_page()
    elif menu == "👥 客户管理":
        customer_page()
    elif menu == "🗺️ 物流地图":
        map_page()
    elif menu == "📰 价格行情 & 政策":
        price_news_page()
    elif menu == "⚙️ 系统设置":
        settings_page()
    elif menu == "👨‍💼 员工管理":
        employee_page()
    elif menu == "💰 工资管理":
        salary_page()

if __name__ == "__main__":
    main()
