"""Tools de Fornecedores — endpoint: /geral/clientes/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_fornecedores(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 50)"] = 20,
        apenas_fornecedor: Annotated[str, "Filtrar apenas fornecedores: S ou N"] = "S",
        filtrar_por_nome: Annotated[Optional[str], "Filtrar por nome/razão social"] = None,
        filtrar_por_cnpj: Annotated[Optional[str], "Filtrar por CNPJ/CPF"] = None,
    ) -> dict:
        """Lista fornecedores cadastrados no OMIE com paginação e filtros."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_fornecedor": apenas_fornecedor,
        }
        if filtrar_por_nome:
            params["clientesFiltro"] = {"razao_social": filtrar_por_nome}
        if filtrar_por_cnpj:
            params.setdefault("clientesFiltro", {})["cnpj_cpf"] = filtrar_por_cnpj
        return await client.call("geral/clientes/", "ListarClientes", params)

    @mcp.tool()
    async def consultar_fornecedor(
        ctx: Context,
        codigo_cliente_omie: Annotated[Optional[int], "Código do fornecedor no OMIE"] = None,
        codigo_cliente_integracao: Annotated[Optional[str], "Código de integração do fornecedor"] = None,
        cnpj_cpf: Annotated[Optional[str], "CNPJ ou CPF do fornecedor"] = None,
    ) -> dict:
        """Consulta detalhes de um fornecedor específico. Informe ao menos um dos identificadores."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_cliente_omie:
            params["codigo_cliente_omie"] = codigo_cliente_omie
        if codigo_cliente_integracao:
            params["codigo_cliente_integracao"] = codigo_cliente_integracao
        if cnpj_cpf:
            params["cnpj_cpf"] = cnpj_cpf
        return await client.call("geral/clientes/", "ConsultarCliente", params)

    @mcp.tool()
    async def incluir_fornecedor(
        ctx: Context,
        razao_social: Annotated[str, "Razão social do fornecedor"],
        cnpj_cpf: Annotated[str, "CNPJ ou CPF"],
        email: Annotated[str, "E-mail do fornecedor"],
        nome_fantasia: Annotated[Optional[str], "Nome fantasia"] = None,
        telefone1_ddd: Annotated[Optional[str], "DDD do telefone principal"] = None,
        telefone1_numero: Annotated[Optional[str], "Número do telefone principal"] = None,
        endereco: Annotated[Optional[str], "Logradouro"] = None,
        endereco_numero: Annotated[Optional[str], "Número do endereço"] = None,
        bairro: Annotated[Optional[str], "Bairro"] = None,
        cidade: Annotated[Optional[str], "Cidade"] = None,
        estado: Annotated[Optional[str], "UF (ex: SP)"] = None,
        cep: Annotated[Optional[str], "CEP"] = None,
        codigo_cliente_integracao: Annotated[Optional[str], "Código de integração próprio"] = None,
        tags: Annotated[Optional[str], "Tags separadas por vírgula (ex: fornecedor,prioritario)"] = None,
    ) -> dict:
        """Cadastra um novo fornecedor no OMIE."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "razao_social": razao_social,
            "cnpj_cpf": cnpj_cpf,
            "email": email,
            "fornecedor": "S",
        }
        if nome_fantasia:
            params["nome_fantasia"] = nome_fantasia
        if telefone1_ddd:
            params["telefone1_ddd"] = telefone1_ddd
        if telefone1_numero:
            params["telefone1_numero"] = telefone1_numero
        if endereco:
            params["endereco"] = endereco
        if endereco_numero:
            params["endereco_numero"] = endereco_numero
        if bairro:
            params["bairro"] = bairro
        if cidade:
            params["cidade"] = cidade
        if estado:
            params["estado"] = estado
        if cep:
            params["cep"] = cep
        if codigo_cliente_integracao:
            params["codigo_cliente_integracao"] = codigo_cliente_integracao
        if tags:
            params["tags"] = [{"tag": t.strip()} for t in tags.split(",")]
        return await client.call("geral/clientes/", "IncluirCliente", params)

    @mcp.tool()
    async def alterar_fornecedor(
        ctx: Context,
        codigo_cliente_omie: Annotated[Optional[int], "Código do fornecedor no OMIE"] = None,
        codigo_cliente_integracao: Annotated[Optional[str], "Código de integração"] = None,
        razao_social: Annotated[Optional[str], "Nova razão social"] = None,
        email: Annotated[Optional[str], "Novo e-mail"] = None,
        telefone1_ddd: Annotated[Optional[str], "DDD do telefone"] = None,
        telefone1_numero: Annotated[Optional[str], "Número do telefone"] = None,
        endereco: Annotated[Optional[str], "Logradouro"] = None,
        endereco_numero: Annotated[Optional[str], "Número do endereço"] = None,
        bairro: Annotated[Optional[str], "Bairro"] = None,
        cidade: Annotated[Optional[str], "Cidade"] = None,
        estado: Annotated[Optional[str], "UF (ex: SP)"] = None,
        cep: Annotated[Optional[str], "CEP"] = None,
    ) -> dict:
        """Altera dados de um fornecedor existente no OMIE."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_cliente_omie:
            params["codigo_cliente_omie"] = codigo_cliente_omie
        if codigo_cliente_integracao:
            params["codigo_cliente_integracao"] = codigo_cliente_integracao
        for field, value in [
            ("razao_social", razao_social), ("email", email),
            ("telefone1_ddd", telefone1_ddd), ("telefone1_numero", telefone1_numero),
            ("endereco", endereco), ("endereco_numero", endereco_numero),
            ("bairro", bairro), ("cidade", cidade), ("estado", estado), ("cep", cep),
        ]:
            if value is not None:
                params[field] = value
        return await client.call("geral/clientes/", "AlterarCliente", params)
