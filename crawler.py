# ============================================================================
# 🕷️ 原材料价格 & 政策新闻 爬虫脚本
# 功能：每日自动抓取全国农产品价格和政策新闻，存入 Supabase
# 运行方式：python crawler.py 或 设置定时任务
# ============================================================================

import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import time

# 加载环境变量
load_dotenv()

# Supabase 连接
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================================================
# 目标材料列表
# ============================================================================
TARGET_MATERIALS = [
    "花生仁",
    "白糖", 
    "花生油",
    "植物油",
    "白萝卜",
    "姜"
]

# ============================================================================
# 价格数据源 (模拟真实 API)
# ============================================================================
def fetch_material_prices():
    """
    抓取全国农产品批发市场价格
    实际使用时需替换为真实 API 或网站
    """
    prices = []
    
    # 模拟数据源 (实际应调用真实 API)
    # 推荐数据源:
    # 1. 农业农村部全国农产品批发市场价格信息系统
    # 2. 中国农产品价格网
    # 3. 各省市农业厅官网
    
    mock_data = [
        {"name": "花生仁", "price": 6.5, "region": "山东", "change": "+0.2"},
        {"name": "白糖", "price": 5.8, "region": "广西", "change": "-0.1"},
        {"name": "花生油", "price": 12.5, "region": "河南", "change": "+0.5"},
        {"name": "白萝卜", "price": 2.3, "region": "河北", "change": "0"},
        {"name": "姜", "price": 8.5, "region": "山东", "change": "+0.3"},
        {"name": "植物油", "price": 11.2, "region": "湖北", "change": "+0.1"},
    ]
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    for item in mock_data:
        prices.append({
            "material_name": item["name"],
            "price": item["price"],
            "region": item["region"],
            "price_change": item["change"],
            "date": today,
            "source": "全国农产品批发网",
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return prices

# ============================================================================
# 政策新闻数据源
# ============================================================================
def fetch_policy_news():
    """
    抓取食品行业相关政策新闻
    实际使用时需替换为真实 API 或网站
    """
    news_list = []
    
    # 推荐数据源:
    # 1. 国家市场监督管理总局官网
    # 2. 国家卫生健康委员会
    # 3. 农业农村部
    # 4. 各省市市场监管局
    # 5. 中国政府网政策栏目
    
    mock_news = [
        {
            "title": "2026 年食品安全国家标准实施公告",
            "source": "国家市场监督管理总局",
            "region": "全国",
            "summary": "新版食品安全国家标准将于 2026 年 4 月 1 日起正式实施，涉及食品添加剂、污染物限量等多项内容。",
            "url": "http://www.samr.gov.cn/example1",
            "publish_date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "广东省食品加工企业补贴政策发布",
            "source": "广东省政府",
            "region": "广东",
            "summary": "对符合条件的食品加工企业给予设备购置补贴，最高可达投资额的 30%。",
            "url": "http://www.gd.gov.cn/example2",
            "publish_date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "农产品采购增值税优惠政策延续",
            "source": "国家税务总局",
            "region": "全国",
            "summary": "农产品采购增值税抵扣政策延续至 2027 年底，减轻企业税负。",
            "url": "http://www.chinatax.gov.cn/example3",
            "publish_date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "潮汕地区特色食品产业发展规划",
            "source": "汕头市政府",
            "region": "潮汕",
            "summary": "发布潮汕特色食品产业发展五年规划，支持传统食品企业数字化转型。",
            "url": "http://www.shantou.gov.cn/example4",
            "publish_date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "食品生产许可管理办法修订",
            "source": "市场监管总局",
            "region": "全国",
            "summary": "简化食品生产许可流程，推行电子证书，提高审批效率。",
            "url": "http://www.samr.gov.cn/example5",
            "publish_date": datetime.now().strftime("%Y-%m-%d")
        }
    ]
    
    for item in mock_news:
        news_list.append({
            "title": item["title"],
            "source": item["source"],
            "region": item["region"],
            "summary": item["summary"],
            "url": item["url"],
            "publish_date": item["publish_date"],
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return news_list

# ============================================================================
# 潮汕地区企业信息 (静态数据，可定期更新)
# ============================================================================
def get_chaoshan_companies():
    """获取潮汕地区相关产业公司信息"""
    companies = [
        {
            "name": "汕头市 XX 食品有限公司",
            "industry": "花生制品",
            "phone": "0754-8888XXXX",
            "address": "汕头市龙湖区 XX 路 XX 号",
            "contact": "张经理"
        },
        {
            "name": "揭阳市 XX 粮油加工厂",
            "industry": "植物油加工",
            "phone": "0663-8666XXXX",
            "address": "揭阳市榕城区 XX 工业区",
            "contact": "李总"
        },
        {
            "name": "潮州市 XX 调味品有限公司",
            "industry": "调味品",
            "phone": "0768-2333XXXX",
            "address": "潮州市湘桥区 XX 大道",
            "contact": "陈主任"
        }
    ]
    return companies

# ============================================================================
# 数据存入 Supabase
# ============================================================================
def save_prices_to_db(prices):
    """将价格数据存入数据库"""
    try:
        for price in prices:
            supabase.table("material_prices").insert(price).execute()
        print(f"✅ 成功存入 {len(prices)} 条价格数据")
        return True
    except Exception as e:
        print(f"❌ 价格数据存入失败：{str(e)}")
        return False

def save_news_to_db(news_list):
    """将新闻数据存入数据库"""
    try:
        for news in news_list:
            supabase.table("policy_news").insert(news).execute()
        print(f"✅ 成功存入 {len(news_list)} 条新闻数据")
        return True
    except Exception as e:
        print(f"❌ 新闻数据存入失败：{str(e)}")
        return False

def save_companies_to_db(companies):
    """将公司信息存入数据库"""
    try:
        for company in companies:
            supabase.table("chaoshan_companies").insert(company).execute()
        print(f"✅ 成功存入 {len(companies)} 条企业数据")
        return True
    except Exception as e:
        print(f"❌ 企业数据存入失败：{str(e)}")
        return False

# ============================================================================
# 主函数
# ============================================================================
def main():
    """主执行函数"""
    print("=" * 60)
    print("🕷️ 原材料价格 & 政策新闻 爬虫脚本")
    print(f"⏰ 执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 抓取价格数据
    print("\n📊 正在抓取原材料价格数据...")
    prices = fetch_material_prices()
    save_prices_to_db(prices)
    
    # 2. 抓取政策新闻
    print("\n📰 正在抓取政策新闻数据...")
    news = fetch_policy_news()
    save_news_to_db(news)
    
    # 3. 更新企业信息 (每月执行一次)
    if datetime.now().day == 1:  # 每月 1 号执行
        print("\n🏢 正在更新企业信息...")
        companies = get_chaoshan_companies()
        save_companies_to_db(companies)
    
    print("\n" + "=" * 60)
    print("✅ 爬虫任务完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()