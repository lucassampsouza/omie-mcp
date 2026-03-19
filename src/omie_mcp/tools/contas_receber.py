"""Tools de Contas a Receber — endpoint: /financas/contareceber/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_contas_receber(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 50)"] = 20,
        filtrar_por_status: Annotated[
            Optional[str],
            "Status: CANCELADO | RECEBIDO | LIQUIDADO | EMABERTO | RECEB_PARCIAL | ATRASADO | AVENCER",
        ] = None,
        filtrar_por_data_de: Annotated[Optional[str], "Data de vencimento inicial (dd/mm/aaaa)"] = None,
        filtrar_por_data_ate: Annotated[Optional[str], "Data de vencimento final (dd/mm/aaaa)"] = None,
        filtrar_por_emissao_de: Annotated[Optional[str], "Data de emissão inicial (dd/mm/aaaa)"] = None,
        filtrar_por_emissao_ate: Annotated[Optional[str], "Data de emissão final (dd/mm/aaaa)"] = None,
        filtrar_cliente: Annotated[Optional[int], "Código OMIE do cliente"] = None,
        filtrar_conta_corrente: Annotated[Optional[int], "Código da conta corrente"] = None,
        filtrar_apenas_titulos_em_aberto: Annotated[str, "Apenas títulos em aberto: S ou N"] = "N",
        ordenar_por: Annotated[
            str,
            "Ordenação: CODIGO | DATA_EMISSAO | DATA_VENCIMENTO | DATA_PAGAMENTO",
        ] = "DATA_VENCIMENTO",
        ordem_descrescente: Annotated[str, "Ordem decrescente: S ou N"] = "N",
    ) -> dict:
        """Lista contas a receber com filtros de status, período e cliente."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "ordenar_por": ordenar_por,
            "ordem_descrescente": ordem_descrescente,
            "filtrar_apenas_titulos_em_aberto": filtrar_apenas_titulos_em_aberto,
        }
        if filtrar_por_status:
            params["filtrar_por_status"] = filtrar_por_status
        if filtrar_por_data_de:
            params["filtrar_por_data_de"] = filtrar_por_data_de
        if filtrar_por_data_ate:
            params["filtrar_por_data_ate"] = filtrar_por_data_ate
        if filtrar_por_emissao_de:
            params["filtrar_por_emissao_de"] = filtrar_por_emissao_de
        if filtrar_por_emissao_ate:
            params["filtrar_por_emissao_ate"] = filtrar_por_emissao_ate
        if filtrar_cliente:
            params["filtrar_cliente"] = filtrar_cliente
        if filtrar_conta_corrente:
            params["filtrar_conta_corrente"] = filtrar_conta_corrente
        return await client.call("financas/contareceber/", "ListarContasReceber", params)

    @mcp.tool()
    async def consultar_conta_receber(
        ctx: Context,
        codigo_lancamento_omie: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
    ) -> dict:
        """Consulta detalhes de uma conta a receber específica."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_lancamento_omie:
            params["codigo_lancamento_omie"] = codigo_lancamento_omie
        if codigo_lancamento_integracao:
            params["codigo_lancamento_integracao"] = codigo_lancamento_integracao
        return await client.call("financas/contareceber/", "ConsultarContaReceber", params)

    @mcp.tool()
    async def incluir_conta_receber(
        ctx: Context,
        codigo_cliente_fornecedor: Annotated[int, "Código OMIE do cliente"],
        data_vencimento: Annotated[str, "Data de vencimento (dd/mm/aaaa)"],
        valor_documento: Annotated[float, "Valor do documento"],
        codigo_categoria: Annotated[str, "Código da categoria financeira (ex: 1.01.01)"],
        data_previsao: Annotated[str, "Data prevista para recebimento (dd/mm/aaaa)"],
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração próprio"] = None,
        numero_documento: Annotated[Optional[str], "Número do documento/nota fiscal"] = None,
        data_emissao: Annotated[Optional[str], "Data de emissão (dd/mm/aaaa)"] = None,
        id_conta_corrente: Annotated[Optional[int], "Código da conta corrente"] = None,
        codigo_vendedor: Annotated[Optional[int], "Código do vendedor"] = None,
        observacao: Annotated[Optional[str], "Observações"] = None,
        numero_pedido: Annotated[Optional[str], "Número do pedido relacionado"] = None,
        numero_parcela: Annotated[Optional[str], "Número da parcela (ex: 001/003)"] = None,
    ) -> dict:
        """Cria uma nova conta a receber no OMIE."""
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
        if codigo_vendedor:
            params["codigo_vendedor"] = codigo_vendedor
        if observacao:
            params["observacao"] = observacao
        if numero_pedido:
            params["numero_pedido"] = numero_pedido
        if numero_parcela:
            params["numero_parcela"] = numero_parcela
        return await client.call("financas/contareceber/", "IncluirContaReceber", params)

    @mcp.tool()
    async def lancar_recebimento(
        ctx: Context,
        codigo_conta_corrente: Annotated[int, "Código da conta corrente onde o valor foi recebido"],
        valor: Annotated[float, "Valor recebido"],
        data: Annotated[str, "Data do recebimento (dd/mm/aaaa)"],
        codigo_lancamento_omie: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
        desconto: Annotated[float, "Valor de desconto concedido"] = 0.0,
        juros: Annotated[float, "Valor de juros cobrado"] = 0.0,
        multa: Annotated[float, "Valor de multa cobrada"] = 0.0,
        observacao: Annotated[Optional[str], "Observações sobre o recebimento"] = None,
        conciliar_documento: Annotated[str, "Conciliar automaticamente: S ou N"] = "N",
    ) -> dict:
        """Registra o recebimento (baixa) de uma conta a receber."""
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
        return await client.call("financas/contareceber/", "LancarRecebimento", params)

    @mcp.tool()
    async def cancelar_recebimento(
        ctx: Context,
        codigo_lancamento_omie: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
    ) -> dict:
        """Cancela/estorna o recebimento de uma conta a receber, revertendo a baixa."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_lancamento_omie:
            params["codigo_lancamento_omie"] = codigo_lancamento_omie
        if codigo_lancamento_integracao:
            params["codigo_lancamento_integracao"] = codigo_lancamento_integracao
        return await client.call("financas/contareceber/", "CancelarRecebimento", params)

    @mcp.tool()
    async def excluir_conta_receber(
        ctx: Context,
        codigo_lancamento_omie: Annotated[Optional[int], "Código do lançamento no OMIE"] = None,
        codigo_lancamento_integracao: Annotated[Optional[str], "Código de integração do lançamento"] = None,
    ) -> dict:
        """Exclui uma conta a receber do OMIE (apenas títulos em aberto)."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_lancamento_omie:
            params["codigo_lancamento_omie"] = codigo_lancamento_omie
        if codigo_lancamento_integracao:
            params["codigo_lancamento_integracao"] = codigo_lancamento_integracao
        return await client.call("financas/contareceber/", "ExcluirContaReceber", params)
