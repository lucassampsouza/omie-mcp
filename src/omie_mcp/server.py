"""MCP Server para integração com o OMIE ERP."""

import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from .client import OmieClient
from .tools import fornecedores, contas_pagar, contas_receber, lancamentos_cc, contas_correntes, fluxo_caixa

# Busca .env no diretório atual e em ~/.config/omie-mcp/ (útil para uso via uvx)
load_dotenv()
load_dotenv(os.path.expanduser("~/.config/omie-mcp/.env"))


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
    instructions=(
        "Servidor MCP para controle financeiro no ERP OMIE. "
        "Permite gerenciar: fornecedores, contas a pagar, contas a receber, "
        "lançamentos bancários, extrato de contas correntes e fluxo de caixa. "
        "Datas devem ser informadas no formato dd/mm/aaaa."
    ),
    lifespan=lifespan,
)

# Registra todas as ferramentas financeiras
fornecedores.register(mcp)
contas_pagar.register(mcp)
contas_receber.register(mcp)
lancamentos_cc.register(mcp)
contas_correntes.register(mcp)
fluxo_caixa.register(mcp)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
