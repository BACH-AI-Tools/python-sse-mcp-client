#!/usr/bin/env python3
"""
SSE MCP 客户端示例

演示如何连接 SSE 类型的 MCP 服务器（通过 HTTP）
"""

import asyncio
import json

from mcp import ClientSession
from mcp.client.sse import sse_client


async def connect_openfda_mcp():
    """连接 OpenFDA MCP 服务器"""
    
    # OpenFDA MCP 服务器配置
    server_url = "http://openfda.mcp.kaleido.guru/sse"
    headers = {
        "emcp-key": "DGBBWP0neHpDf8MH5l6QIVeRpmBOkZB1",
        "emcp-usercode": "2DebiJQI"
    }
    
    print("🌐 SSE MCP 客户端示例")
    print("=" * 60)
    print(f"📡 正在连接到: {server_url}")
    print()
    
    try:
        # 连接 SSE MCP 服务器
        async with sse_client(
            url=server_url,
            headers=headers,
            timeout=10.0,  # HTTP 超时（秒）
            sse_read_timeout=300.0  # SSE 读取超时（秒）
        ) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化会话
                init_result = await session.initialize()
                print("✅ 已连接到 OpenFDA MCP 服务器\n")
                
                # ==========================================
                # 1. 获取服务器信息
                # ==========================================
                print("📋 服务器信息:")
                print(f"   协议版本: {init_result.protocolVersion}")
                print(f"   服务器信息: {init_result.serverInfo}")
                if hasattr(init_result, 'capabilities'):
                    print(f"   服务器能力: {init_result.capabilities}")
                print()
                
                # ==========================================
                # 2. 列出可用的工具
                # ==========================================
                print("🔧 可用工具列表:")
                tools_list = await session.list_tools()
                
                if tools_list.tools:
                    for i, tool in enumerate(tools_list.tools, 1):
                        print(f"\n{i}. {tool.name}")
                        if tool.description:
                            print(f"   描述: {tool.description}")
                        if hasattr(tool, 'inputSchema') and tool.inputSchema:
                            # 显示参数信息
                            schema = tool.inputSchema
                            if isinstance(schema, dict) and 'properties' in schema:
                                print(f"   参数:")
                                for param_name, param_info in schema['properties'].items():
                                    param_type = param_info.get('type', 'unknown')
                                    param_desc = param_info.get('description', '')
                                    required = param_name in schema.get('required', [])
                                    req_mark = " (必填)" if required else " (可选)"
                                    print(f"     • {param_name}: {param_type}{req_mark}")
                                    if param_desc:
                                        print(f"       {param_desc}")
                else:
                    print("   (没有可用工具)")
                
                print()
                
                # ==========================================
                # 3. 列出可用的资源（如果服务器支持）
                # ==========================================
                print("📦 可用资源列表:")
                try:
                    resources_list = await session.list_resources()
                    
                    if resources_list.resources:
                        for i, resource in enumerate(resources_list.resources, 1):
                            print(f"   {i}. {resource.uri}")
                            if hasattr(resource, 'name') and resource.name:
                                print(f"      名称: {resource.name}")
                            if hasattr(resource, 'description') and resource.description:
                                print(f"      描述: {resource.description}")
                    else:
                        print("   (没有可用资源)")
                except Exception as e:
                    print(f"   (服务器不支持资源功能: {e})")
                
                print()
                
                # ==========================================
                # 4. 列出可用的提示词（如果服务器支持）
                # ==========================================
                print("💬 可用提示词列表:")
                try:
                    prompts_list = await session.list_prompts()
                    
                    if prompts_list.prompts:
                        for i, prompt in enumerate(prompts_list.prompts, 1):
                            print(f"   {i}. {prompt.name}")
                            if hasattr(prompt, 'description') and prompt.description:
                                print(f"      描述: {prompt.description}")
                    else:
                        print("   (没有可用提示词)")
                except Exception as e:
                    print(f"   (服务器不支持提示词功能: {e})")
                
                print()
                
                # ==========================================
                # 5. 演示调用工具：搜索阿司匹林的药品标签
                # ==========================================
                if tools_list.tools:
                    print("🎯 演示：调用工具搜索阿司匹林（aspirin）")
                    print()
                    
                    try:
                        # 调用 search_drug_labels 工具
                        result = await session.call_tool(
                            "search_drug_labels",
                            arguments={
                                "search": "aspirin",
                                "limit": 2
                            }
                        )
                        
                        print("   ✅ 调用成功！")
                        print("   结果:")
                        for content in result.content:
                            if hasattr(content, 'text'):
                                # 截取前 500 字符，避免输出太长
                                text = content.text
                                if len(text) > 500:
                                    print(f"   {text[:500]}...")
                                    print(f"   (结果太长，已截断。完整结果有 {len(text)} 字符)")
                                else:
                                    print(f"   {text}")
                        print()
                    except Exception as e:
                        print(f"   ❌ 工具调用失败: {e}")
                        print()
                
                print("✨ 连接测试完成！")
                
    except Exception as e:
        print(f"\n❌ 连接失败: {type(e).__name__}")
        print(f"   错误信息: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    try:
        asyncio.run(connect_openfda_mcp())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

