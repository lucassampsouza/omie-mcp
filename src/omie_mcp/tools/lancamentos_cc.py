"""Tools de Lançamentos em Conta Corrente (Transações Bancárias) — endpoint: /financas/contacorrentelancamentos/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_lancamentos_bancarios(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 50)"] = 20,
        codigo_conta_corrente: Annotated[Optional[int], "Filtrar por conta corrente"] = None,
        data_lancamento_de: Annotated[Optional[str], "Data de lançamento inicial (dd/mm/aaaa)"] = None,
        data_lancamento_ate: Annotated[Optional[str], "Data de lançamento final (dd/mm/aaaa)"] = None,
        data_inclusao_de: Annotated[Optional[str], "Data de inclusão inicial (dd/mm/aaaa)"] = None,
        data_inclusao_ate: Annotated[Optional[str], "Data de inclusão final (dd/mm/aaaa)"] = None,
        ordem_descrescente: Annotated[str, "Ordem decrescente: S ou N"] = "S",
    ) -> dict:
        """Lista lançamentos/transações bancárias em conta corrente."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "nPagina": pagina,
            "nRegPorPagina": registros_por_pagina,
            "cOrdemDecrescente": ordem_descrescente,
        }
        if codigo_conta_corrente:
            params["nCodCC"] = codigo_conta_corrente
        if data_lancamento_de:
            params["dtPagInicial"] = data_lancamento_de
        if data_lancamento_ate:
            params["dtPagFinal"] = data_lancamento_ate
        if data_inclusao_de:
            params["dDtIncDe"] = data_inclusao_de
        if data_inclusao_ate:
            params["dDtIncAte"] = data_inclusao_ate
        return await client.call("financas/contacorrentelancamentos/", "ListarLancCC", params)

    @mcp.tool()
    async def consultar_lancamento_bancario(
        ctx: Context,
        codigo_lancamento: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
    ) -> dict:
        """Consulta detalhes de um lançamento bancário específico."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_lancamento:
            params["nCodLanc"] = codigo_lancamento
        if codigo_lancamento_integracao:
            params["cCodIntLanc"] = codigo_lancamento_integracao
        return await client.call("financas/contacorrentelancamentos/", "ConsultaLancCC", params)

    @mcp.tool()
    async def incluir_lancamento_bancario(
        ctx: Context,
        codigo_conta_corrente: Annotated[int, "Código da conta corrente"],
        data_lancamento: Annotated[str, "Data do lançamento (dd/mm/aaaa)"],
        valor: Annotated[float, "Valor do lançamento (positivo=crédito, negativo=débito)"],
        codigo_categoria: Annotated[str, "Código da categoria financeira"],
        tipo_documento: Annotated[
            str,
            "Tipo: PIX | TED | DOC | BOL | CHQ | DEB | DIN | TRA | CRE | 99999 (outros)",
        ] = "99999",
        numero_documento: Annotated[Optional[str], "Número do documento"] = None,
        codigo_cliente: Annotated[Optional[int], "Código OMIE do cliente/fornecedor"] = None,
        codigo_conta_destino: Annotated[Optional[int], "Código da conta destino (para transferências)"] = None,
        observacao: Annotated[Optional[str], "Observações"] = None,
        codigo_integracao: Annotated[Optional[str], "Código de integração próprio"] = None,
    ) -> dict:
        """Cria um lançamento manual em conta corrente (débito ou crédito)."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "cabecalho": {
                "nCodCC": codigo_conta_corrente,
                "dDtLanc": data_lancamento,
                "nValorLanc": valor,
            },
            "detalhes": {
                "cCodCateg": codigo_categoria,
                "cTipo": tipo_documento,
            },
        }
        if numero_documento:
            params["detalhes"]["cNumDoc"] = numero_documento
        if codigo_cliente:
            params["detalhes"]["nCodCliente"] = codigo_cliente
        if observacao:
            params["detalhes"]["cObs"] = observacao
        if codigo_conta_destino:
            params["transferencia"] = {"nCodCCDestino": codigo_conta_destino}
        if codigo_integracao:
            params["cCodIntLanc"] = codigo_integracao
        return await client.call("financas/contacorrentelancamentos/", "IncluirLancCC", params)

    @mcp.tool()
    async def excluir_lancamento_bancario(
        ctx: Context,
        codigo_lancamento: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
    ) -> dict:
        """Exclui um lançamento bancário em conta corrente."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_lancamento:
            params["nCodLanc"] = codigo_lancamento
        if codigo_lancamento_integracao:
            params["cCodIntLanc"] = codigo_lancamento_integracao
        return await client.call("financas/contacorrentelancamentos/", "ExcluirLancCC", params)
