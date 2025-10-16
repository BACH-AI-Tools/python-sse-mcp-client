#!/usr/bin/env python3
"""
StreamableHTTP MCP 客户端示例

演示如何连接 streamableHTTP 类型的 MCP 服务器
使用用户提供的 FDA MCP 服务器配置
"""

import asyncio
import json
from typing import Dict, Any, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def connect_fda_streamable_http():
    """连接 FDA StreamableHTTP MCP 服务器"""
    
    # FDA StreamableHTTP MCP 服务器配置
    # 来自用户提供的配置
    server_config = {
        "url": "http://fda.sitmcp.kaleido.guru/mcp",
        "headers": {
            "emcp-key": "ovgTH2LxJozKlpmGNmeHOOUtYm71NMZJ",
            "emcp-usercode": "2DebiJQI"
        },
        "type": "streamableHttp"
    }
    
    server_url = server_config["url"]
    headers = server_config["headers"]
    
    print("🌐 StreamableHTTP MCP 客户端示例")
    print("=" * 60)
    print(f"📡 服务器类型: {server_config['type']}")
    print(f"📍 服务器 URL: {server_url}")
    print(f"🔑 认证头: emcp-key=***{headers['emcp-key'][-4:]}, emcp-usercode={headers['emcp-usercode']}")
    print()
    
    try:
        # 连接 StreamableHTTP MCP 服务器
        async with streamablehttp_client(
            url=server_url,
            headers=headers,
            timeout=30.0,  # HTTP 连接超时（秒）
            sse_read_timeout=300.0  # SSE 读取超时（秒）
        ) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                # ==========================================
                # 1. 初始化会话并获取服务器信息
                # ==========================================
                print("🚀 正在初始化会话...")
                init_result = await session.initialize()
                print("✅ 已成功连接到 FDA MCP 服务器！\n")
                
                print("📋 服务器信息:")
                print(f"   协议版本: {init_result.protocolVersion}")
                print(f"   服务器信息: {init_result.serverInfo}")
                
                # 显示服务器能力
                if hasattr(init_result, 'capabilities') and init_result.capabilities:
                    print(f"\n📊 服务器能力:")
                    caps = init_result.capabilities
                    if hasattr(caps, 'tools') and caps.tools:
                        print(f"   ✓ 工具支持")
                    if hasattr(caps, 'resources') and caps.resources:
                        print(f"   ✓ 资源支持")
                    if hasattr(caps, 'prompts') and caps.prompts:
                        print(f"   ✓ 提示词支持")
                    if hasattr(caps, 'logging') and caps.logging:
                        print(f"   ✓ 日志支持")
                print()
                
                # ==========================================
                # 2. 列出可用的工具
                # ==========================================
                print("🔧 可用工具列表:")
                print("-" * 40)
                tools_list = await session.list_tools()
                
                if tools_list.tools:
                    for i, tool in enumerate(tools_list.tools, 1):
                        print(f"\n{i}. 工具名称: {tool.name}")
                        if tool.description:
                            # 处理多行描述，添加缩进
                            desc_lines = tool.description.split('\n')
                            print(f"   描述: {desc_lines[0]}")
                            for line in desc_lines[1:]:
                                if line.strip():
                                    print(f"        {line}")
                        
                        # 显示参数信息
                        if hasattr(tool, 'inputSchema') and tool.inputSchema:
                            schema = tool.inputSchema
                            if isinstance(schema, dict) and 'properties' in schema:
                                print(f"   参数:")
                                for param_name, param_info in schema['properties'].items():
                                    param_type = param_info.get('type', 'unknown')
                                    param_desc = param_info.get('description', '')
                                    required = param_name in schema.get('required', [])
                                    req_mark = " [必填]" if required else " [可选]"
                                    
                                    print(f"     • {param_name} ({param_type}){req_mark}")
                                    if param_desc:
                                        # 处理多行参数描述
                                        desc_lines = param_desc.split('\n')
                                        for line in desc_lines:
                                            if line.strip():
                                                print(f"       {line}")
                else:
                    print("   (没有可用工具)")
                
                print()
                
                # ==========================================
                # 3. 列出可用的资源（如果支持）
                # ==========================================
                print("📦 可用资源列表:")
                print("-" * 40)
                try:
                    resources_list = await session.list_resources()
                    
                    if resources_list.resources:
                        for i, resource in enumerate(resources_list.resources, 1):
                            print(f"{i}. URI: {resource.uri}")
                            if hasattr(resource, 'name') and resource.name:
                                print(f"   名称: {resource.name}")
                            if hasattr(resource, 'description') and resource.description:
                                print(f"   描述: {resource.description}")
                            if hasattr(resource, 'mimeType') and resource.mimeType:
                                print(f"   MIME类型: {resource.mimeType}")
                    else:
                        print("   (没有可用资源)")
                except Exception as e:
                    print(f"   (服务器不支持资源功能或访问失败: {e})")
                
                print()
                
                # ==========================================
                # 4. 列出可用的提示词（如果支持）
                # ==========================================
                print("💬 可用提示词列表:")
                print("-" * 40)
                try:
                    prompts_list = await session.list_prompts()
                    
                    if prompts_list.prompts:
                        for i, prompt in enumerate(prompts_list.prompts, 1):
                            print(f"{i}. 名称: {prompt.name}")
                            if hasattr(prompt, 'description') and prompt.description:
                                print(f"   描述: {prompt.description}")
                            if hasattr(prompt, 'arguments') and prompt.arguments:
                                print(f"   参数:")
                                for arg in prompt.arguments:
                                    arg_required = getattr(arg, 'required', False)
                                    req_mark = " [必填]" if arg_required else " [可选]"
                                    print(f"     • {arg.name}{req_mark}")
                                    if hasattr(arg, 'description') and arg.description:
                                        print(f"       {arg.description}")
                    else:
                        print("   (没有可用提示词)")
                except Exception as e:
                    print(f"   (服务器不支持提示词功能或访问失败: {e})")
                
                print()
                
                # ==========================================
                # 5. 演示调用工具（如果有可用工具）
                # ==========================================
                if tools_list.tools:
                    print("🎯 演示：调用第一个可用工具")
                    print("-" * 40)
                    
                    # 选择第一个工具进行演示
                    first_tool = tools_list.tools[0]
                    print(f"将演示调用工具: {first_tool.name}")
                    
                    # 构造示例参数
                    demo_args = {}
                    if hasattr(first_tool, 'inputSchema') and first_tool.inputSchema:
                        schema = first_tool.inputSchema
                        if isinstance(schema, dict) and 'properties' in schema:
                            # 根据工具名称提供合适的参数
                            if first_tool.name == "search_drug_labels":
                                # 只提供必要的参数，避免 count 和 skip 冲突
                                demo_args = {
                                    "search": "aspirin",
                                    "limit": 3
                                }
                            elif first_tool.name in ["get_drug_adverse_reactions", "get_drug_warnings", "get_drug_indications"]:
                                # 这些工具需要 drug_name 参数
                                demo_args = {
                                    "drug_name": "aspirin",
                                    "limit": 2
                                }
                            elif first_tool.name == "ae_pipeline_rag":
                                # RAG 工具的参数
                                demo_args = {
                                    "drug": "aspirin",
                                    "query": "What are the main side effects?",
                                    "top_k": 3
                                }
                            else:
                                # 通用参数生成逻辑（只为必填参数提供值）
                                required_params = schema.get('required', [])
                                for param_name in required_params:
                                    param_info = schema['properties'].get(param_name, {})
                                    param_type = param_info.get('type', 'string')
                                    
                                    if 'search' in param_name.lower() or 'query' in param_name.lower():
                                        demo_args[param_name] = "aspirin"
                                    elif 'drug' in param_name.lower() or 'name' in param_name.lower():
                                        demo_args[param_name] = "aspirin"
                                    elif 'limit' in param_name.lower():
                                        demo_args[param_name] = 3
                                    elif param_type == 'string':
                                        demo_args[param_name] = "示例文本"
                                    elif param_type == 'number' or param_type == 'integer':
                                        demo_args[param_name] = 1
                                    elif param_type == 'boolean':
                                        demo_args[param_name] = True
                    
                    print(f"调用参数: {json.dumps(demo_args, ensure_ascii=False, indent=2)}")
                    print()
                    
                    try:
                        # 调用工具
                        print("⏳ 正在调用工具...")
                        result = await session.call_tool(
                            first_tool.name,
                            arguments=demo_args
                        )
                        
                        print("✅ 工具调用成功！")
                        print("\n📄 返回结果:")
                        
                        # 处理返回结果
                        if result.content:
                            for idx, content in enumerate(result.content):
                                if hasattr(content, 'text'):
                                    # 格式化显示文本内容
                                    text = content.text
                                    # 尝试解析为 JSON 以美化显示
                                    try:
                                        json_data = json.loads(text)
                                        print(f"\n内容 {idx + 1} (JSON):")
                                        print(json.dumps(json_data, ensure_ascii=False, indent=2)[:1000])
                                        if len(json.dumps(json_data)) > 1000:
                                            print("... (结果已截断)")
                                    except:
                                        # 非 JSON 格式，直接显示文本
                                        print(f"\n内容 {idx + 1} (文本):")
                                        if len(text) > 500:
                                            print(text[:500])
                                            print(f"... (结果太长，已截断。完整结果有 {len(text)} 字符)")
                                        else:
                                            print(text)
                                elif hasattr(content, 'data'):
                                    print(f"\n内容 {idx + 1} (数据):")
                                    print(content.data)
                        else:
                            print("   (工具返回空结果)")
                        
                    except Exception as e:
                        print(f"❌ 工具调用失败: {e}")
                        import traceback
                        print("\n错误详情:")
                        traceback.print_exc()
                
                print()
                print("=" * 60)
                print("✨ StreamableHTTP MCP 连接测试完成！")
                print("   服务器连接正常，所有功能已测试。")
                
    except ConnectionError as e:
        print(f"\n❌ 连接错误: {e}")
        print("   请检查:")
        print("   1. 服务器地址是否正确")
        print("   2. 网络连接是否正常")
        print("   3. 认证信息是否有效")
    except TimeoutError as e:
        print(f"\n⏱️ 连接超时: {e}")
        print("   服务器响应时间过长，请稍后重试")
    except Exception as e:
        print(f"\n❌ 发生错误: {type(e).__name__}")
        print(f"   错误信息: {e}")
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()


async def test_specific_tool(tool_name: str, arguments: Dict[str, Any]):
    """测试特定的工具调用"""
    
    server_config = {
        "url": "http://fda.sitmcp.kaleido.guru/mcp",
        "headers": {
            "emcp-key": "ovgTH2LxJozKlpmGNmeHOOUtYm71NMZJ",
            "emcp-usercode": "2DebiJQI"
        }
    }
    
    print(f"\n🔬 测试工具: {tool_name}")
    print(f"   参数: {json.dumps(arguments, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        async with streamablehttp_client(
            url=server_config["url"],
            headers=server_config["headers"],
            timeout=30.0,
            sse_read_timeout=300.0
        ) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 调用工具
                result = await session.call_tool(tool_name, arguments=arguments)
                
                print("✅ 调用成功！")
                if result.content:
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print("\n返回内容:")
                            print(content.text[:1000])
                            if len(content.text) > 1000:
                                print("... (已截断)")
                
    except Exception as e:
        print(f"❌ 错误: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("   StreamableHTTP MCP 客户端示例程序")
    print("   使用 FDA MCP 服务器")
    print("=" * 60 + "\n")
    
    try:
        # 运行主要的连接和测试
        asyncio.run(connect_fda_streamable_http())
        
        # 可选：测试特定工具
        # 取消注释下面的代码来测试特定工具
        # asyncio.run(test_specific_tool(
        #     tool_name="search_drug_labels",
        #     arguments={"search": "ibuprofen", "limit": 2}
        # ))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断程序")
    except Exception as e:
        print(f"\n\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
