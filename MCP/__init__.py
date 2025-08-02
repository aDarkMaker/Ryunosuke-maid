import os
import json
import importlib.util
import subprocess

def load_tools():
    tools = {}
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mcp_dir = os.path.join(project_root, 'MCP')
    
    print(f"[MCP] 工具目录: {mcp_dir}")

    toolist_path = os.path.join(mcp_dir, 'toolist.json')
    if not os.path.exists(toolist_path):
        print(f"[MCP] 警告: 未找到工具清单 {toolist_path}")
        return tools
        
    print(f"[MCP] 找到工具清单: {toolist_path}")
    with open(toolist_path, 'r', encoding='utf-8') as f:
        toolist = json.load(f)
    
    print(f"[MCP] 加载工具: {[t['name'] for t in toolist.get('tools', [])]}")
    
    for tool in toolist.get('tools', []):
        tool_name = tool['name']
        tool_type = tool.get('type', 'python') 

        if tool_type == 'python':
            module_path = os.path.join(mcp_dir, f"{tool_name}.py")
            if os.path.exists(module_path):
                print(f"[MCP] 加载Python工具: {module_path}")
                try:
                    spec = importlib.util.spec_from_file_location(tool_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    tools[tool_name] = getattr(module, tool_name)
                    print(f"[MCP] 成功加载Python工具: {tool_name}")
                except Exception as e:
                    print(f"[MCP] 加载Python工具失败: {str(e)}")
            else:
                print(f"[MCP] 错误: 未找到Python工具 {tool_name} 的实现文件")

        elif tool_type == 'nodejs':
            js_path = os.path.join(mcp_dir, f"{tool_name}.js")
            if os.path.exists(js_path):
                print(f"[MCP] 加载Node.js工具: {js_path}")

                def node_tool_wrapper(*args, **kwargs):
                    """执行Node.js工具的函数包装器"""
                    try:
                        params = {}
                        if args: params['args'] = args
                        if kwargs: params.update(kwargs)

                        result = subprocess.run(
                            ['node', js_path, json.dumps(params)],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )

                        if result.returncode == 0:
                            return json.loads(result.stdout)
                        else:
                            return {"success": False, "error": result.stderr}
                    except Exception as e:
                        return {"success": False, "error": str(e)}
                
                tools[tool_name] = node_tool_wrapper
                print(f"[MCP] 成功加载Node.js工具: {tool_name}")
            else:
                print(f"[MCP] 错误: 未找到Node.js工具 {tool_name} 的实现文件")
    
    print(f"[MCP] 已加载工具: {list(tools.keys())}")
    return tools
