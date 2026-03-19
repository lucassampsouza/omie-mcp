"""MCP Server para integração com o OMIE ERP."""

import os
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from .client import OmieClient

load_dotenv()


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict]:
    app_key = os.environ["OMIE_APP_KEY"]
    app_secret = os.environ["OMIE_APP_SECRET"]
    client = OmieClient(app_key=app_key, app_secret=app_secret)
    try:
        yield {"omie": client}
    finally:
        await client.aclose()


mcp = FastMCP(
    name="omie-mcp",
    instructions="Servidor MCP para integração com o ERP OMIE. Permite consultar e gerenciar clientes, pedidos, financeiro e outros recursos do OMIE.",
    lifespan=lifespan,
)


# ─── Tools serão adicionadas aqui conforme a documentação da API ──────────────


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
