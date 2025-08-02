import os
import json
import importlib.util

def load_tools():
    tools = {}
    mcp_dir = os.path.join(os.path.dirname(__file__), '..', 'MCP')
    
    # 加载工具清单
    toolist_path = os.path.join(mcp_dir, 'toolist.json')
    if os.path.exists(toolist_path):
        with open(toolist_path, 'r', encoding='utf-8') as f:
            toolist = json.load(f)
            
        for tool in toolist.get('tools', []):
            tool_name = tool['name']
            module_path = os.path.join(mcp_dir, f"{tool_name}.py")
            
            if os.path.exists(module_path):
                spec = importlib.util.spec_from_file_location(tool_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                tools[tool_name] = getattr(module, tool_name, None)
    
    return tools
