#!/usr/bin/env python3
"""
OpenFDA MCP 服务器实用示例

展示如何使用 OpenFDA MCP 服务器查询药品信息
"""

import asyncio
import json

from mcp import ClientSession
from mcp.client.sse import sse_client


async def query_openfda():
    """查询 OpenFDA 药品数据库"""
    
    # OpenFDA MCP 服务器配置
    server_url = "http://openfda.mcp.kaleido.guru/sse"
    headers = {
        "emcp-key": "DGBBWP0neHpDf8MH5l6QIVeRpmBOkZB1",
        "emcp-usercode": "2DebiJQI"
    }
    
    print("💊 OpenFDA 药品数据库查询示例")
    print("=" * 70)
    print()
    
    async with sse_client(url=server_url, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ 已连接到 OpenFDA MCP 服务器\n")
            
            # ==========================================
            # 示例 1: 搜索布洛芬（Ibuprofen）的药品标签
            # ==========================================
            print("📋 示例 1: 搜索布洛芬（Ibuprofen）的药品信息")
            print("-" * 70)
            
            try:
                result = await session.call_tool(
                    "search_drug_labels",
                    arguments={
                        "search": "ibuprofen",
                        "limit": 1
                    }
                )
                
                data = json.loads(result.content[0].text)
                if 'results' in data and len(data['results']) > 0:
                    drug = data['results'][0]
                    
                    print(f"✅ 找到药品信息:")
                    
                    # 品牌名
                    if 'openfda' in drug and 'brand_name' in drug['openfda']:
                        print(f"   品牌名: {', '.join(drug['openfda']['brand_name'][:3])}")
                    
                    # 通用名
                    if 'openfda' in drug and 'generic_name' in drug['openfda']:
                        print(f"   通用名: {', '.join(drug['openfda']['generic_name'][:3])}")
                    
                    # 制造商
                    if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                        print(f"   制造商: {', '.join(drug['openfda']['manufacturer_name'][:2])}")
                    
                    # 适应症（截取前200字）
                    if 'indications_and_usage' in drug:
                        indications = drug['indications_and_usage'][0][:200]
                        print(f"   适应症: {indications}...")
                    
                    print()
                else:
                    print("   ❌ 未找到相关信息\n")
                    
            except Exception as e:
                print(f"   ❌ 查询失败: {e}\n")
            
            # ==========================================
            # 示例 2: 获取阿司匹林的不良反应
            # ==========================================
            print("⚠️  示例 2: 查询阿司匹林（Aspirin）的不良反应")
            print("-" * 70)
            
            try:
                result = await session.call_tool(
                    "get_drug_adverse_reactions",
                    arguments={
                        "drug_name": "aspirin",
                        "limit": 1
                    }
                )
                
                data = json.loads(result.content[0].text)
                if 'results' in data and len(data['results']) > 0:
                    drug = data['results'][0]
                    
                    if 'adverse_reactions' in drug:
                        reactions = drug['adverse_reactions'][0][:300]
                        print(f"✅ 不良反应信息:")
                        print(f"   {reactions}...")
                        print()
                    else:
                        print("   ℹ️  未找到不良反应信息\n")
                else:
                    print("   ❌ 未找到相关信息\n")
                    
            except Exception as e:
                print(f"   ❌ 查询失败: {e}\n")
            
            # ==========================================
            # 示例 3: 获取泰诺（Tylenol）的警告信息
            # ==========================================
            print("⚡ 示例 3: 查询泰诺（Tylenol/对乙酰氨基酚）的警告信息")
            print("-" * 70)
            
            try:
                result = await session.call_tool(
                    "get_drug_warnings",
                    arguments={
                        "drug_name": "acetaminophen",  # 对乙酰氨基酚的通用名
                        "limit": 1
                    }
                )
                
                data = json.loads(result.content[0].text)
                if 'results' in data and len(data['results']) > 0:
                    drug = data['results'][0]
                    
                    if 'warnings' in drug:
                        warnings = drug['warnings'][0][:300]
                        print(f"✅ 警告信息:")
                        print(f"   {warnings}...")
                        print()
                    else:
                        print("   ℹ️  未找到警告信息\n")
                else:
                    print("   ❌ 未找到相关信息\n")
                    
            except Exception as e:
                print(f"   ❌ 查询失败: {e}\n")
            
            # ==========================================
            # 示例 4: 使用 RAG 管道进行药品安全分析
            # ==========================================
            print("🔍 示例 4: 使用 RAG 分析布洛芬的心血管副作用")
            print("-" * 70)
            
            try:
                result = await session.call_tool(
                    "ae_pipeline_rag",
                    arguments={
                        "query": "cardiovascular side effects",
                        "drug": "ibuprofen",
                        "top_k": 3
                    }
                )
                
                response = result.content[0].text
                # 截取前 400 字符
                if len(response) > 400:
                    print(f"✅ 分析结果:")
                    print(f"   {response[:400]}...")
                    print(f"   (完整结果有 {len(response)} 字符)")
                else:
                    print(f"✅ 分析结果:")
                    print(f"   {response}")
                print()
                    
            except Exception as e:
                print(f"   ❌ 分析失败: {e}\n")
            
            # ==========================================
            # 示例 5: 查询多个药品
            # ==========================================
            print("📊 示例 5: 批量查询常见止痛药")
            print("-" * 70)
            
            drugs = ["aspirin", "ibuprofen", "naproxen"]
            
            for drug_name in drugs:
                try:
                    result = await session.call_tool(
                        "get_drug_indications",
                        arguments={
                            "drug_name": drug_name,
                            "limit": 1
                        }
                    )
                    
                    data = json.loads(result.content[0].text)
                    if 'results' in data and len(data['results']) > 0:
                        drug = data['results'][0]
                        
                        # 品牌名
                        brand_names = "未知"
                        if 'openfda' in drug and 'brand_name' in drug['openfda']:
                            brand_names = ', '.join(drug['openfda']['brand_name'][:2])
                        
                        print(f"   • {drug_name.capitalize()}: {brand_names}")
                    else:
                        print(f"   • {drug_name.capitalize()}: (未找到)")
                        
                except Exception as e:
                    print(f"   • {drug_name.capitalize()}: (查询失败)")
            
            print()
            print("✨ 所有查询完成！")


def main():
    """主函数"""
    try:
        asyncio.run(query_openfda())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

