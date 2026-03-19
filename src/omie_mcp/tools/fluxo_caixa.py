"""Tools de Fluxo de Caixa e Resumo Financeiro — endpoints: /financas/caixa/ e /financas/resumo/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def consultar_fluxo_caixa(
        ctx: Context,
        ano: Annotated[int, "Ano de referência (ex: 2025)"],
        mes: Annotated[int, "Mês de referência (1-12)"],
    ) -> dict:
        """
        Consulta o fluxo de caixa do mês, comparando valores previstos vs realizados
        por categoria financeira.
        """
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call(
            "financas/caixa/",
            "ListarOrcamentos",
            {"nAno": ano, "nMes": mes},
        )

    @mcp.tool()
    async def obter_resumo_financeiro(
        ctx: Context,
        data_inicio: Annotated[str, "Data inicial (dd/mm/aaaa)"],
        data_fim: Annotated[str, "Data final (dd/mm/aaaa)"],
    ) -> dict:
        """
        Obtém um resumo financeiro consolidado do período, incluindo totais
        de contas a pagar, a receber e saldo bancário.
        """
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call(
            "financas/resumo/",
            "ObterResumoFinancas",
            {"dDtInicio": data_inicio, "dDtFim": data_fim},
        )

    @mcp.tool()
    async def listar_titulos_em_aberto(
        ctx: Context,
        tipo: Annotated[str, "Tipo de título: PAGAR | RECEBER | TODOS"] = "TODOS",
        data_vencimento_de: Annotated[Optional[str], "Vencimento inicial (dd/mm/aaaa)"] = None,
        data_vencimento_ate: Annotated[Optional[str], "Vencimento final (dd/mm/aaaa)"] = None,
    ) -> dict:
        """
        Lista todos os títulos financeiros em aberto (contas a pagar e/ou receber não liquidadas).
        Útil para visão geral de compromissos pendentes.
        """
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {"cTipo": tipo}
        if data_vencimento_de:
            params["dDtVencDe"] = data_vencimento_de
        if data_vencimento_ate:
            params["dDtVencAte"] = data_vencimento_ate
        return await client.call("financas/resumo/", "ObterListaEmAberto", params)

    @mcp.tool()
    async def pesquisar_lancamentos_financeiros(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 50)"] = 20,
        tipo: Annotated[
            str,
            "Tipo de lançamento: CP (contas pagar) | CR (contas receber) | CC (conta corrente) | TODOS",
        ] = "TODOS",
        data_de: Annotated[Optional[str], "Data inicial (dd/mm/aaaa)"] = None,
        data_ate: Annotated[Optional[str], "Data final (dd/mm/aaaa)"] = None,
        codigo_cliente: Annotated[Optional[int], "Código OMIE do cliente/fornecedor"] = None,
        status: Annotated[
            Optional[str],
            "Status: CANCELADO | PAGO | LIQUIDADO | EMABERTO | ATRASADO | AVENCER",
        ] = None,
    ) -> dict:
        """
        Pesquisa lançamentos financeiros de forma unificada (pagar + receber + bancário).
        Ideal para visão consolidada das finanças.
        """
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "nPagina": pagina,
            "nRegPorPagina": registros_por_pagina,
            "cTipo": tipo,
        }
        if data_de:
            params["dDtDe"] = data_de
        if data_ate:
            params["dDtAte"] = data_ate
        if codigo_cliente:
            params["nCodCliente"] = codigo_cliente
        if status:
            params["cStatus"] = status
        return await client.call("financas/pesquisartitulos/", "PesquisarLancamentos", params)
