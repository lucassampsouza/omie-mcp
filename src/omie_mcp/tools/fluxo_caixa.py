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
        data: Annotated[str, "Data de referência do resumo (dd/mm/aaaa)"],
        exibir_categoria: Annotated[bool, "Detalhar os valores por categoria financeira"] = False,
        apenas_resumo: Annotated[bool, "Retornar somente os totais, sem os lançamentos"] = True,
    ) -> dict:
        """
        Obtém o resumo financeiro consolidado numa data de referência, incluindo
        totais de contas a pagar, a receber e saldo bancário.
        Observação: o OMIE calcula este resumo para um único dia, não para um período.
        """
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call(
            "financas/resumo/",
            "ObterResumoFinancas",
            {
                "dDia": data,
                "lApenasResumo": apenas_resumo,
                "lExibirCategoria": exibir_categoria,
            },
        )

    @mcp.tool()
    async def listar_titulos_em_aberto(
        ctx: Context,
        tipo: Annotated[str, "Tipo de título: PAGAR | RECEBER"],
        data: Annotated[Optional[str], "Data de referência (dd/mm/aaaa)"] = None,
        codigo_cliente: Annotated[Optional[int], "Filtrar por código OMIE do cliente/fornecedor"] = None,
        nome_cliente: Annotated[Optional[str], "Filtrar por nome do cliente/fornecedor"] = None,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 50)"] = 20,
    ) -> dict:
        """
        Lista os títulos financeiros em aberto (não liquidados) de um tipo.
        O OMIE atende um tipo por chamada: use PAGAR ou RECEBER.
        """
        client = ctx.request_context.lifespan_context["omie"]
        tipos = {"PAGAR": "P", "RECEBER": "R"}
        if tipo.upper() not in tipos:
            raise ValueError(f"tipo deve ser PAGAR ou RECEBER, recebido: {tipo!r}")
        params: dict = {
            "cTipo": tipos[tipo.upper()],
            "nPagina": pagina,
            "nRegPorPagina": registros_por_pagina,
        }
        if data:
            params["dDia"] = data
        if codigo_cliente:
            params["nCodCliente"] = codigo_cliente
        if nome_cliente:
            params["cNomeCliente"] = nome_cliente
        return await client.call(
            "financas/resumo/", "ObterListaEmAberto", params, lista_vazia_ok=True
        )

    @mcp.tool()
    async def pesquisar_lancamentos_financeiros(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 50)"] = 20,
        natureza: Annotated[
            Optional[str],
            "Natureza do título: PAGAR | RECEBER. Omita para trazer ambos.",
        ] = None,
        vencimento_de: Annotated[Optional[str], "Vencimento inicial (dd/mm/aaaa)"] = None,
        vencimento_ate: Annotated[Optional[str], "Vencimento final (dd/mm/aaaa)"] = None,
        emissao_de: Annotated[Optional[str], "Emissão inicial (dd/mm/aaaa)"] = None,
        emissao_ate: Annotated[Optional[str], "Emissão final (dd/mm/aaaa)"] = None,
        codigo_cliente: Annotated[Optional[int], "Código OMIE do cliente/fornecedor"] = None,
        codigo_conta_corrente: Annotated[Optional[int], "Filtrar por conta corrente"] = None,
        status: Annotated[
            Optional[str],
            "Status: CANCELADO | PAGO | LIQUIDADO | EMABERTO | ATRASADO | AVENCER",
        ] = None,
    ) -> dict:
        """
        Pesquisa lançamentos financeiros de forma unificada (contas a pagar + a receber).
        Ideal para visão consolidada das finanças.
        """
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "nPagina": pagina,
            "nRegPorPagina": registros_por_pagina,
        }
        if natureza:
            naturezas = {"PAGAR": "P", "RECEBER": "R"}
            if natureza.upper() not in naturezas:
                raise ValueError(f"natureza deve ser PAGAR ou RECEBER, recebido: {natureza!r}")
            params["cNatureza"] = naturezas[natureza.upper()]
        if vencimento_de:
            params["dDtVencDe"] = vencimento_de
        if vencimento_ate:
            params["dDtVencAte"] = vencimento_ate
        if emissao_de:
            params["dDtEmisDe"] = emissao_de
        if emissao_ate:
            params["dDtEmisAte"] = emissao_ate
        if codigo_cliente:
            params["nCodCliente"] = codigo_cliente
        if codigo_conta_corrente:
            params["nCodCC"] = codigo_conta_corrente
        if status:
            params["cStatus"] = status
        return await client.call(
            "financas/pesquisartitulos/", "PesquisarLancamentos", params, lista_vazia_ok=True
        )
