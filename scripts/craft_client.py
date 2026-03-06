import requests
import json
import sys
import argparse

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
            print(f"Error from Craft MCP: {json.dumps(result_wrapper['error'], indent=2, ensure_ascii=False)}")
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

    except Exception as e:
        print(f"Failed to communicate with Craft MCP: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Craft MCP Client")
    parser.add_argument("method", help="MCP method (e.g., tools/call)")
    parser.add_argument("tool_name", help="Name of the tool to call")
    parser.add_argument("arguments", help="JSON string of arguments for the tool")
    
    args = parser.parse_args()
    
    try:
        tool_args = json.loads(args.arguments)
    except json.JSONDecodeError:
        print("Error: Arguments must be a valid JSON string.")
        sys.exit(1)
        
    params = {
        "name": args.tool_name,
        "arguments": tool_args
    }
    
    result = call_craft_mcp("tools/call", params)
    if result:
        if isinstance(result, (dict, list)):
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(result)
