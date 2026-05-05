import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path

# Proje dizin yollarını ayarla
_backend_dir = Path(__file__).resolve().parents[1]
_venv_python = _backend_dir / "venv" / "bin" / "python"
_server_script = _backend_dir / "mcp_pdf_server.py"

# MCP Sunucu parametreleri
server_params = StdioServerParameters(
    command=str(_venv_python),
    args=[str(_server_script)],
    env=os.environ.copy()
)

async def read_pdf_via_mcp(file_path: str) -> str:
    """
    Dosya yolunu alarak MCP sunucusu üzerinden PDF içeriğini okur.
    """
    try:
        print(f"DEBUG: Connecting to MCP Server at {_server_script}")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 'read_pdf_content' aracını çağır
                result = await session.call_tool(
                    "read_pdf_content", 
                    arguments={"file_path": str(file_path)}
                )
                
                if result and hasattr(result, 'content'):
                    # FastMCP returns content as a list of TextContent or ImageContent
                    return result.content[0].text
                return "MCP sunucusundan beklenen formatta yanıt alınamadı."
                
    except Exception as e:
        print(f"MCP CLIENT ERROR: {str(e)}")
        return f"MCP Client Hatası: {str(e)}"


def read_pdf_via_mcp_sync(file_path: str) -> str:
    """
    Senkron kodlar içinden çağrılabilecek yardımcı fonksiyon.
    """
    return asyncio.run(read_pdf_via_mcp(file_path))
