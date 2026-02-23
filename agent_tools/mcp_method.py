from mcp import StdioServerParameters, stdio_client, ClientSession
from contextlib import AsyncExitStack    
import asyncio

class MCPClient:
    def __init__(self, server_script_path: str):
        self.session: ClientSession
        self.exit_stack = AsyncExitStack()
        self._mcp_methods = {}
        self._mcp_method_schema = {}
        self._client = None #to store the client session for each tool, if needed for direct calls instead of through the main session
        self.server_script_path = server_script_path
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        self.command = "python" if is_python else "node"
        self.server_params = StdioServerParameters(
            command=self.command,
            args=[server_script_path],
            env=None
        )

    async def connect(self):
        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
            await self.session.initialize()
            response = await self.session.list_tools()
            tools = response.tools
            self._mcp_methods = {tool.name: tool.description for tool in tools}
            self._client={tool.name:self.session for tool in tools}
            self._mcp_method_schema = {tool.name: tool.inputSchema for tool in tools}
            return self
        except Exception as e:
            print(f"Failed to establish connection: {e}")
            return None

    async def disconnect(self):
        await self.exit_stack.aclose()
        
    async def call_tool(self, tool_name: str, tool_args: dict):
        if tool_name not in self._mcp_methods:
            return f"Error: MCP Tool '{tool_name}' not found."
        try:
            result = await self.session.call_tool(tool_name, tool_args)
            return result
        except Exception as e:
            return f"Error executing MCP tool '{tool_name}' with arguments {tool_args}: {e}"
        

class MCPTool:
    def __init__(self):
        self.mcp_clients={} #mcp_client_name: mcp_client_object
        self.mcp_methods={}
        self.mcp_method_schema={}
        
    async def get_session(self, tool_name:str):
        if tool_name not in self.mcp_methods:
            return f"Error: MCP Tool '{tool_name}' not found."
        return self.mcp_clients.get(tool_name, None)
        
    async def add_mcp_client(self, mcp_client_path:str):
        mcp_client = MCPClient(server_script_path=mcp_client_path)
        await mcp_client.connect()
        if isinstance(mcp_client, MCPClient):
            print(f"Connected to MCP client with methods: {mcp_client._mcp_methods}")
            self.mcp_clients.update(mcp_client._mcp_client) #we can call tools
            self.mcp_methods.update(mcp_client._mcp_methods)
            self.mcp_method_schema.update(mcp_client._mcp_method_schema)
        else:
            print(f"Invalid MCP client provided: {mcp_client}. Skipping.")
    
    async def remove_mcp_client(self, mcp_client_path:str):
        if mcp_client_path in self.mcp_clients:
            mcp_client = self.mcp_clients[mcp_client_path]
            await mcp_client.disconnect()
            del self.mcp_clients[mcp_client_path]
            # Also remove associated methods and schemas
            for method_name in list(self.mcp_methods.keys()):
                if method_name in mcp_client._mcp_methods:
                    del self.mcp_methods[method_name]
                    del self.mcp_method_schema[method_name]
        else:
            print(f"MCP client '{mcp_client_path}' not found. Cannot remove.")
    
    def get_mcp_info(self):
        return list(self.mcp_methods.items())
        


    