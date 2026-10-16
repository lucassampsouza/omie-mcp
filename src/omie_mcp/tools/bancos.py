"""Tools de Bancos / Instituições Financeiras — endpoint: /geral/bancos/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context

# O OMIE trunca silenciosamente registros_por_pagina em 100 neste endpoint.
MAX_REGISTROS_POR_PAGINA = 100

TIPOS_CONTA = {
    "CB": "Conta Bancária",
    "CX": "Caixinha",
    "CV": "Carteira Virtual",
    "AC": "Administradora de Cartões",
}


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_bancos(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 100)"] = 50,
        nome: Annotated[
            Optional[str], "Filtrar pelo nome do banco (busca parcial, ex: 'Itau')"
        ] = None,
        tipo: Annotated[
            Optional[str],
            "Filtrar por tipo: CB (conta bancária), CX (caixinha), "
            "CV (carteira virtual) ou AC (administradora de cartões)",
        ] = None,
    ) -> dict:
        """
        Lista os bancos e instituições financeiras do OMIE — a tabela de onde vem o
        código de banco usado no cadastro de contas correntes.

        A base tem mais de 1.200 instituições, então filtre por `nome` em vez de
        paginar tudo. O filtro por `nome` já é feito pelo OMIE (busca parcial).

        Cada registro traz `codigo` (código de compensação, 3 caracteres), `nome` e
        `tipo`. A tabela é mantida pelo OMIE: a API é somente leitura.
        """
        client = ctx.request_context.lifespan_context["omie"]
        if tipo and tipo.upper() not in TIPOS_CONTA:
            raise ValueError(
                f"tipo deve ser um de {', '.join(TIPOS_CONTA)}, recebido: {tipo!r}"
            )
        params: dict = {
            "pagina": pagina,
            "registros_por_pagina": min(registros_por_pagina, MAX_REGISTROS_POR_PAGINA),
        }
        if nome:
            params["nome"] = nome
        if tipo:
            params["tipo"] = tipo.upper()
        return await client.call(
            "geral/bancos/", "ListarBancos", params, lista_vazia_ok=True
        )

    @mcp.tool()
    async def consultar_banco(
        ctx: Context,
        codigo: Annotated[str, "Código do banco (3 caracteres, ex: 001, 341, B34)"],
    ) -> dict:
        """
        Consulta uma instituição financeira pelo código, com os detalhes de
        integração: `obank_*` (integração via API para PIX, pagamentos, extratos e
        boletos), `cnab_*` (remessas CNAB), `cwr_*` (crawler), `cod_ispb` e
        `cod_compen`. Útil para saber se um banco suporta extrato ou cobrança
        automática antes de configurar a conta corrente.

        Cuidado ao interpretar o erro: para um código inexistente o OMIE responde
        "Código do banco não informado na tag [codigo]", e não que o banco não existe.
        """
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call("geral/bancos/", "ConsultarBanco", {"codigo": codigo})
