"""Tools de Contas a Pagar — endpoint: /financas/contapagar/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_contas_pagar(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 50)"] = 20,
        filtrar_por_status: Annotated[
            Optional[str],
            "Status: CANCELADO | PAGO | LIQUIDADO | EMABERTO | PAGTO_PARCIAL | ATRASADO | AVENCER",
        ] = None,
        filtrar_por_data_de: Annotated[Optional[str], "Data de vencimento inicial (dd/mm/aaaa)"] = None,
        filtrar_por_data_ate: Annotated[Optional[str], "Data de vencimento final (dd/mm/aaaa)"] = None,
        filtrar_cliente: Annotated[Optional[int], "Código OMIE do fornecedor"] = None,
        filtrar_conta_corrente: Annotated[Optional[int], "Código da conta corrente"] = None,
        ordenar_por: Annotated[str, "Ordenação: CODIGO | CODIGO_INTEGRACAO | DATA_VENCIMENTO"] = "DATA_VENCIMENTO",
        ordem_descrescente: Annotated[str, "Ordem decrescente: S ou N"] = "N",
    ) -> dict:
        """Lista contas a pagar com filtros de status, período e fornecedor."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "ordenar_por": ordenar_por,
            "ordem_descrescente": ordem_descrescente,
        }
        if filtrar_por_status:
            params["filtrar_por_status"] = filtrar_por_status
        if filtrar_por_data_de:
            params["filtrar_por_data_de"] = filtrar_por_data_de
        if filtrar_por_data_ate:
            params["filtrar_por_data_ate"] = filtrar_por_data_ate
        if filtrar_cliente:
            params["filtrar_cliente"] = filtrar_cliente
        if filtrar_conta_corrente:
            params["filtrar_conta_corrente"] = filtrar_conta_corrente
        return await client.call("financas/contapagar/", "ListarContasPagar", params)

    @mcp.tool()
    async def consultar_conta_pagar(
        ctx: Context,
        codigo_lancamento_omie: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
    ) -> dict:
        """Consulta detalhes de uma conta a pagar específica."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_lancamento_omie:
            params["codigo_lancamento_omie"] = codigo_lancamento_omie
        if codigo_lancamento_integracao:
            params["codigo_lancamento_integracao"] = codigo_lancamento_integracao
        return await client.call("financas/contapagar/", "ConsultarContaPagar", params)

    @mcp.tool()
    async def incluir_conta_pagar(
        ctx: Context,
        codigo_cliente_fornecedor: Annotated[int, "Código OMIE do fornecedor"],
        data_vencimento: Annotated[str, "Data de vencimento (dd/mm/aaaa)"],
        valor_documento: Annotated[float, "Valor do documento"],
        codigo_categoria: Annotated[str, "Código da categoria financeira (ex: 1.01.01)"],
        data_previsao: Annotated[str, "Data prevista para pagamento (dd/mm/aaaa)"],
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração próprio"] = None,
        numero_documento: Annotated[Optional[str], "Número do documento/nota fiscal"] = None,
        data_emissao: Annotated[Optional[str], "Data de emissão (dd/mm/aaaa)"] = None,
        id_conta_corrente: Annotated[Optional[int], "Código da conta corrente para pagamento"] = None,
        observacao: Annotated[Optional[str], "Observações sobre o lançamento"] = None,
        numero_pedido: Annotated[Optional[str], "Número do pedido relacionado"] = None,
    ) -> dict:
        """Cria uma nova conta a pagar no OMIE."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "codigo_cliente_fornecedor": codigo_cliente_fornecedor,
            "data_vencimento": data_vencimento,
            "valor_documento": valor_documento,
            "codigo_categoria": codigo_categoria,
            "data_previsao": data_previsao,
        }
        if codigo_lancamento_integracao:
            params["codigo_lancamento_integracao"] = codigo_lancamento_integracao
        if numero_documento:
            params["numero_documento"] = numero_documento
        if data_emissao:
            params["data_emissao"] = data_emissao
        if id_conta_corrente:
            params["id_conta_corrente"] = id_conta_corrente
        if observacao:
            params["observacao"] = observacao
        if numero_pedido:
            params["numero_pedido"] = numero_pedido
        return await client.call("financas/contapagar/", "IncluirContaPagar", params)

    @mcp.tool()
    async def lancar_pagamento(
        ctx: Context,
        codigo_conta_corrente: Annotated[int, "Código da conta corrente utilizada no pagamento"],
        valor: Annotated[float, "Valor pago"],
        data: Annotated[str, "Data do pagamento (dd/mm/aaaa)"],
        codigo_lancamento_omie: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
        desconto: Annotated[float, "Valor de desconto concedido"] = 0.0,
        juros: Annotated[float, "Valor de juros cobrado"] = 0.0,
        multa: Annotated[float, "Valor de multa cobrada"] = 0.0,
        observacao: Annotated[Optional[str], "Observações sobre o pagamento"] = None,
        conciliar_documento: Annotated[str, "Conciliar automaticamente: S ou N"] = "N",
    ) -> dict:
        """Registra o pagamento (baixa) de uma conta a pagar."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "codigo_conta_corrente": codigo_conta_corrente,
            "valor": valor,
            "data": data,
            "desconto": desconto,
            "juros": juros,
            "multa": multa,
            "conciliar_documento": conciliar_documento,
        }
        if codigo_lancamento_omie:
            params["codigo_lancamento_omie"] = codigo_lancamento_omie
        if codigo_lancamento_integracao:
            params["codigo_lancamento_integracao"] = codigo_lancamento_integracao
        if observacao:
            params["observacao"] = observacao
        return await client.call("financas/contapagar/", "LancarPagamento", params)

    @mcp.tool()
    async def cancelar_pagamento_conta_pagar(
        ctx: Context,
        codigo_lancamento_omie: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
    ) -> dict:
        """Cancela/estorna o pagamento de uma conta a pagar, revertendo a baixa."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_lancamento_omie:
            params["codigo_lancamento_omie"] = codigo_lancamento_omie
        if codigo_lancamento_integracao:
            params["codigo_lancamento_integracao"] = codigo_lancamento_integracao
        return await client.call("financas/contapagar/", "CancelarPagamento", params)

    @mcp.tool()
    async def excluir_conta_pagar(
        ctx: Context,
        codigo_lancamento_omie: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
    ) -> dict:
        """Exclui uma conta a pagar do OMIE (apenas títulos em aberto)."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_lancamento_omie:
            params["codigo_lancamento_omie"] = codigo_lancamento_omie
        if codigo_lancamento_integracao:
            params["codigo_lancamento_integracao"] = codigo_lancamento_integracao
        return await client.call("financas/contapagar/", "ExcluirContaPagar", params)
