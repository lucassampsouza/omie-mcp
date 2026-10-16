"""Tools de Contas Correntes e Extrato — endpoints: /geral/contacorrente/, /geral/tipocc/ e /financas/extrato/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_tipos_conta_corrente(ctx: Context) -> dict:
        """
        Lista os tipos de conta corrente do OMIE — os valores aceitos no campo de
        tipo ao cadastrar uma conta corrente (ex: CC Conta Corrente, CP Conta
        Poupança, CR Cartão de Crédito, CX Caixinha).

        Cada item traz `cCodigo` (o valor a usar), `cDescricao` e `cGrupo`, onde o
        grupo é a família da conta: CB (bancária), CX (caixa), CV (carteira
        virtual), CR (cartão) ou AC (administradora de cartões) — o mesmo domínio do
        campo `tipo` em listar_bancos.

        A tabela tem 13 registros e cabe numa página; a API do OMIE é somente
        leitura para ela.
        """
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call(
            "geral/tipocc/",
            "ListarTiposCC",
            {"pagina": 1, "registros_por_pagina": 50},
            lista_vazia_ok=True,
        )

    @mcp.tool()
    async def listar_contas_correntes(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página"] = 20,
    ) -> dict:
        """Lista todas as contas correntes/bancárias cadastradas no OMIE."""
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call(
            "geral/contacorrente/",
            "ListarResumoContasCorrentes",
            {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
            lista_vazia_ok=True,
        )

    @mcp.tool()
    async def consultar_conta_corrente(
        ctx: Context,
        codigo_conta_corrente: Annotated[Optional[int], "Código OMIE da conta corrente"] = None,
        codigo_integracao: Annotated[Optional[str], "Código de integração da conta corrente"] = None,
    ) -> dict:
        """Consulta detalhes de uma conta corrente específica."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_conta_corrente:
            params["nCodCC"] = codigo_conta_corrente
        if codigo_integracao:
            params["cCodIntCC"] = codigo_integracao
        return await client.call("geral/contacorrente/", "ConsultarContaCorrente", params)

    @mcp.tool()
    async def consultar_extrato_bancario(
        ctx: Context,
        data_inicio: Annotated[str, "Data inicial do extrato (dd/mm/aaaa)"],
        data_fim: Annotated[str, "Data final do extrato (dd/mm/aaaa)"],
        codigo_conta_corrente: Annotated[Optional[int], "Código OMIE da conta corrente"] = None,
        codigo_integracao_conta: Annotated[Optional[str], "Código de integração da conta corrente"] = None,
        exibir_apenas_saldo: Annotated[str, "Exibir apenas saldo final: S ou N"] = "N",
    ) -> dict:
        """
        Consulta o extrato bancário de uma conta corrente em um período.
        Retorna todos os lançamentos e o saldo do período.
        Informe codigo_conta_corrente ou codigo_integracao_conta — o OMIE exige um deles.
        Use listar_contas_correntes para descobrir o código (nCodCC).
        """
        client = ctx.request_context.lifespan_context["omie"]
        if not codigo_conta_corrente and not codigo_integracao_conta:
            raise ValueError(
                "Informe codigo_conta_corrente ou codigo_integracao_conta. "
                "Use listar_contas_correntes para obter o código."
            )
        params: dict = {
            "dPeriodoInicial": data_inicio,
            "dPeriodoFinal": data_fim,
            "cExibirApenasSaldo": exibir_apenas_saldo,
        }
        if codigo_conta_corrente:
            params["nCodCC"] = codigo_conta_corrente
        if codigo_integracao_conta:
            params["cCodIntCC"] = codigo_integracao_conta
        return await client.call("financas/extrato/", "ListarExtrato", params)
