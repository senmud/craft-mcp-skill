import requests
import json
import sys
import argparse
import os

def call_craft_mcp(method, params, endpoint="https://mcp.craft.do/links/6INvnW0xzBU/mcp"):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    try:
        # Using stream=True to handle potentially large SSE responses
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30, stream=True)
        response.raise_for_status()
        
        full_data = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    full_data = decoded_line[len("data: "):]
                    break # Usually the first data block contains the full result for tools/call
        
        if not full_data:
            print("No data received from Craft MCP.")
            return None

        result_wrapper = json.loads(full_data)
        if "error" in result_wrapper:
            error = result_wrapper['error']
            error_msg = error.get('message', str(error))
            # 人性化错误提示
            if 'page not found' in error_msg.lower() or 'invalid id' in error_msg.lower():
                print("❌ 错误：文档/页面ID无效，请检查ID是否正确")
            elif 'permission' in error_msg.lower():
                print("❌ 错误：没有权限访问该文档，请检查MCP配置")
            else:
                print(f"❌ Craft MCP错误：{error_msg}")
            sys.exit(1)
            
        result = result_wrapper.get("result", {})
        
        # Craft often nests the actual tool output inside content[0].text as a JSON string
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            text_content = content[0].get("text")
            try:
                # Try to parse the nested JSON string
                return json.loads(text_content)
            except json.JSONDecodeError:
                # If it's not JSON, return the raw text
                return text_content
        
        return result

    except requests.exceptions.Timeout:
        print("❌ 错误：请求超时，请检查网络连接")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ 错误：无法连接到Craft MCP服务，请检查端点配置")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未知错误：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Craft MCP Client")
    parser.add_argument("method", help="MCP method (e.g., tools/call)")
    parser.add_argument("tool_name", help="Name of the tool to call")
    parser.add_argument("arguments", nargs='?', help="JSON string of arguments for the tool (可选，使用--file时不需要)")
    parser.add_argument("--file", help="从本地文件读取内容作为markdown，自动处理JSON转义")
    parser.add_argument("--auto-clean", action="store_true", help="写入完成后自动删除传入的--file文件")
    
    args = parser.parse_args()
    
    tool_args = {}
    if args.arguments:
        try:
            tool_args = json.loads(args.arguments)
        except json.JSONDecodeError:
            print("❌ 错误：arguments参数必须是有效的JSON字符串")
            sys.exit(1)
    
    # 处理--file参数：自动读取文件内容到markdown字段
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ 错误：文件 {args.file} 不存在")
            sys.exit(1)
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            if args.tool_name == 'markdown_add':
                tool_args['markdown'] = content
            else:
                tool_args['content'] = content
        except Exception as e:
            print(f"❌ 读取文件失败：{str(e)}")
            sys.exit(1)
    
    if not tool_args:
        print("❌ 错误：必须提供arguments或--file参数")
        sys.exit(1)
        
    params = {
        "name": args.tool_name,
        "arguments": tool_args
    }
    
    print(f"⏳ 正在调用Craft工具: {args.tool_name}...")
    result = call_craft_mcp("tools/call", params)
    if result:
        print("✅ 操作成功!")
        if isinstance(result, (dict, list)):
            # 提取有用信息显示
            if 'documents' in result and isinstance(result['documents'], list):
                for doc in result['documents']:
                    print(f"📄 文档: {doc.get('title')}")
                    print(f"🔗 ID: {doc.get('id')}")
                    if 'clickableLink' in doc:
                        print(f"🔗 访问链接: {doc.get('clickableLink')}")
            elif 'blocks' in result:
                print(f"📝 已写入 {len(result.get('blocks', []))} 个内容块")
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(result)
    
    # 自动清理临时文件
    if args.auto_clean and args.file and os.path.exists(args.file):
        try:
            os.remove(args.file)
            print(f"🧹 已自动清理临时文件: {args.file}")
        except Exception as e:
            print(f"⚠️  清理临时文件失败: {str(e)}")
