"""Tools de Fornecedores — endpoint: /geral/clientes/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context


def _add_optional_fields(params: dict, fields: list[tuple[str, object]]) -> None:
    for field, value in fields:
        if value is not None:
            params[field] = value


def _parse_tags(tags: str | None) -> list[dict[str, str]] | None:
    if not tags:
        return None
    parsed_tags = [{"tag": tag.strip()} for tag in tags.split(",") if tag.strip()]
    return parsed_tags or None


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_fornecedores(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 50)"] = 20,
        apenas_fornecedor: Annotated[str, "Filtrar apenas fornecedores: S ou N"] = "S",
        apenas_importado_api: Annotated[str, "Exibir apenas registros importados pela API: S ou N"] = "N",
        filtrar_por_nome: Annotated[Optional[str], "Filtrar por nome/razão social"] = None,
        filtrar_por_cnpj: Annotated[Optional[str], "Filtrar por CNPJ/CPF"] = None,
        filtrar_por_codigo_omie: Annotated[Optional[int], "Filtrar pelo código OMIE do fornecedor"] = None,
        filtrar_por_codigo_integracao: Annotated[Optional[str], "Filtrar pelo código de integração"] = None,
        exibir_caracteristicas: Annotated[str, "Exibir características do fornecedor: S ou N"] = "N",
        exibir_obs: Annotated[str, "Exibir observações do fornecedor: S ou N"] = "N",
    ) -> dict:
        """Lista fornecedores cadastrados no OMIE com paginação e filtros."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_fornecedor": apenas_fornecedor,
            "apenas_importado_api": apenas_importado_api,
            "exibir_caracteristicas": exibir_caracteristicas,
            "exibir_obs": exibir_obs,
        }
        clientes_filtro = {}
        if filtrar_por_nome:
            clientes_filtro["razao_social"] = filtrar_por_nome
        if filtrar_por_cnpj:
            clientes_filtro["cnpj_cpf"] = filtrar_por_cnpj
        if filtrar_por_codigo_omie:
            clientes_filtro["codigo_cliente_omie"] = filtrar_por_codigo_omie
        if filtrar_por_codigo_integracao:
            clientes_filtro["codigo_cliente_integracao"] = filtrar_por_codigo_integracao
        if clientes_filtro:
            params["clientesFiltro"] = clientes_filtro
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
        email: Annotated[Optional[str], "E-mail do fornecedor"] = None,
        nome_fantasia: Annotated[Optional[str], "Nome fantasia"] = None,
        telefone1_ddd: Annotated[Optional[str], "DDD do telefone principal"] = None,
        telefone1_numero: Annotated[Optional[str], "Número do telefone principal"] = None,
        endereco: Annotated[Optional[str], "Logradouro"] = None,
        endereco_numero: Annotated[Optional[str], "Número do endereço"] = None,
        bairro: Annotated[Optional[str], "Bairro"] = None,
        cidade: Annotated[Optional[str], "Cidade"] = None,
        estado: Annotated[Optional[str], "UF (ex: SP)"] = None,
        cep: Annotated[Optional[str], "CEP"] = None,
        complemento: Annotated[Optional[str], "Complemento do endereço"] = None,
        contato: Annotated[Optional[str], "Nome da pessoa de contato"] = None,
        homepage: Annotated[Optional[str], "Website do fornecedor"] = None,
        inscricao_estadual: Annotated[Optional[str], "Inscrição estadual"] = None,
        inscricao_municipal: Annotated[Optional[str], "Inscrição municipal"] = None,
        optante_simples_nacional: Annotated[Optional[str], "Optante pelo Simples Nacional: S ou N"] = None,
        contribuinte: Annotated[Optional[str], "Contribuinte de ICMS: S ou N"] = None,
        observacao: Annotated[Optional[str], "Observações internas"] = None,
        dados_bancarios_codigo_banco: Annotated[Optional[str], "Código do banco do fornecedor"] = None,
        dados_bancarios_agencia: Annotated[Optional[str], "Agência bancária do fornecedor"] = None,
        dados_bancarios_conta_corrente: Annotated[Optional[str], "Conta corrente do fornecedor"] = None,
        dados_bancarios_chave_pix: Annotated[Optional[str], "Chave PIX do fornecedor"] = None,
        codigo_cliente_integracao: Annotated[Optional[str], "Código de integração próprio"] = None,
        tags: Annotated[Optional[str], "Tags separadas por vírgula (ex: fornecedor,prioritario)"] = None,
    ) -> dict:
        """Cadastra um novo fornecedor no OMIE."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "razao_social": razao_social,
            "cnpj_cpf": cnpj_cpf,
            "fornecedor": "S",
        }
        _add_optional_fields(params, [
            ("email", email),
            ("nome_fantasia", nome_fantasia),
            ("telefone1_ddd", telefone1_ddd),
            ("telefone1_numero", telefone1_numero),
            ("endereco", endereco),
            ("endereco_numero", endereco_numero),
            ("bairro", bairro),
            ("cidade", cidade),
            ("estado", estado),
            ("cep", cep),
            ("complemento", complemento),
            ("contato", contato),
            ("homepage", homepage),
            ("inscricao_estadual", inscricao_estadual),
            ("inscricao_municipal", inscricao_municipal),
            ("optante_simples_nacional", optante_simples_nacional),
            ("contribuinte", contribuinte),
            ("observacao", observacao),
            ("codigo_cliente_integracao", codigo_cliente_integracao),
        ])
        dados_bancarios = {}
        _add_optional_fields(dados_bancarios, [
            ("codigo_banco", dados_bancarios_codigo_banco),
            ("agencia", dados_bancarios_agencia),
            ("conta_corrente", dados_bancarios_conta_corrente),
            ("doc_titular", cnpj_cpf),
            ("nome_titular", razao_social),
            ("cChavePix", dados_bancarios_chave_pix),
        ])
        if any([
            dados_bancarios_codigo_banco,
            dados_bancarios_agencia,
            dados_bancarios_conta_corrente,
            dados_bancarios_chave_pix,
        ]):
            params["dadosBancarios"] = dados_bancarios
        parsed_tags = _parse_tags(tags)
        if parsed_tags:
            params["tags"] = parsed_tags
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
        complemento: Annotated[Optional[str], "Complemento do endereço"] = None,
        contato: Annotated[Optional[str], "Nome da pessoa de contato"] = None,
        homepage: Annotated[Optional[str], "Website do fornecedor"] = None,
        inscricao_estadual: Annotated[Optional[str], "Inscrição estadual"] = None,
        inscricao_municipal: Annotated[Optional[str], "Inscrição municipal"] = None,
        optante_simples_nacional: Annotated[Optional[str], "Optante pelo Simples Nacional: S ou N"] = None,
        contribuinte: Annotated[Optional[str], "Contribuinte de ICMS: S ou N"] = None,
        observacao: Annotated[Optional[str], "Observações internas"] = None,
        tags: Annotated[Optional[str], "Tags separadas por vírgula"] = None,
    ) -> dict:
        """Altera dados de um fornecedor existente no OMIE."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {}
        if codigo_cliente_omie:
            params["codigo_cliente_omie"] = codigo_cliente_omie
        if codigo_cliente_integracao:
            params["codigo_cliente_integracao"] = codigo_cliente_integracao
        _add_optional_fields(params, [
            ("razao_social", razao_social),
            ("email", email),
            ("telefone1_ddd", telefone1_ddd),
            ("telefone1_numero", telefone1_numero),
            ("endereco", endereco),
            ("endereco_numero", endereco_numero),
            ("bairro", bairro),
            ("cidade", cidade),
            ("estado", estado),
            ("cep", cep),
            ("complemento", complemento),
            ("contato", contato),
            ("homepage", homepage),
            ("inscricao_estadual", inscricao_estadual),
            ("inscricao_municipal", inscricao_municipal),
            ("optante_simples_nacional", optante_simples_nacional),
            ("contribuinte", contribuinte),
            ("observacao", observacao),
        ])
        parsed_tags = _parse_tags(tags)
        if parsed_tags:
            params["tags"] = parsed_tags
        return await client.call("geral/clientes/", "AlterarCliente", params)

    @mcp.tool()
    async def upsert_fornecedor(
        ctx: Context,
        razao_social: Annotated[str, "Razão social do fornecedor"],
        cnpj_cpf: Annotated[str, "CNPJ ou CPF usado como chave de atualização"],
        email: Annotated[Optional[str], "E-mail do fornecedor"] = None,
        nome_fantasia: Annotated[Optional[str], "Nome fantasia"] = None,
        codigo_cliente_integracao: Annotated[Optional[str], "Código de integração próprio"] = None,
        telefone1_ddd: Annotated[Optional[str], "DDD do telefone principal"] = None,
        telefone1_numero: Annotated[Optional[str], "Número do telefone principal"] = None,
        endereco: Annotated[Optional[str], "Logradouro"] = None,
        endereco_numero: Annotated[Optional[str], "Número do endereço"] = None,
        bairro: Annotated[Optional[str], "Bairro"] = None,
        cidade: Annotated[Optional[str], "Cidade"] = None,
        estado: Annotated[Optional[str], "UF (ex: SP)"] = None,
        cep: Annotated[Optional[str], "CEP"] = None,
        observacao: Annotated[Optional[str], "Observações internas"] = None,
        tags: Annotated[Optional[str], "Tags separadas por vírgula"] = None,
    ) -> dict:
        """Inclui ou atualiza fornecedor pelo CNPJ/CPF no OMIE."""
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "razao_social": razao_social,
            "cnpj_cpf": cnpj_cpf,
            "fornecedor": "S",
        }
        _add_optional_fields(params, [
            ("email", email),
            ("nome_fantasia", nome_fantasia),
            ("codigo_cliente_integracao", codigo_cliente_integracao),
            ("telefone1_ddd", telefone1_ddd),
            ("telefone1_numero", telefone1_numero),
            ("endereco", endereco),
            ("endereco_numero", endereco_numero),
            ("bairro", bairro),
            ("cidade", cidade),
            ("estado", estado),
            ("cep", cep),
            ("observacao", observacao),
        ])
        parsed_tags = _parse_tags(tags)
        if parsed_tags:
            params["tags"] = parsed_tags
        return await client.call("geral/clientes/", "UpsertClienteCpfCnpj", params)
