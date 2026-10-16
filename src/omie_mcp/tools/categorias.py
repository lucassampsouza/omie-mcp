"""Tools de Categorias — endpoints: /geral/categorias/ e /geral/tipocategoria/"""

from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context

# O OMIE trunca silenciosamente registros_por_pagina em 100 neste endpoint:
# pedir 500 devolve 100 sem avisar.
MAX_REGISTROS_POR_PAGINA = 100

# Um grupo totalizador (categoria_superior válida) tem código no formato "9.99".
TAMANHO_CODIGO_GRUPO = 4

# Guarda contra loop infinito em listar_grupos_categoria caso o OMIE devolva
# total_de_paginas inconsistente.
MAX_PAGINAS_VARREDURA = 50


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_categorias(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página (máx 100)"] = 50,
        apenas_ativas: Annotated[bool, "Trazer somente categorias ativas"] = False,
        tipo: Annotated[
            Optional[str],
            "Filtrar por tipo: R (receita) ou D (despesa). "
            "Atenção: este filtro também exclui categorias inativas, totalizadoras e ocultas.",
        ] = None,
        descricao: Annotated[Optional[str], "Filtrar pela descrição da categoria"] = None,
    ) -> dict:
        """
        Lista o plano de categorias financeiras do OMIE (receitas e despesas).

        Cada categoria traz o vínculo com a conta do DRE em `codigo_dre`/`dadosDRE`,
        o grupo em `categoria_superior` e as flags `totalizadora`, `transferencia`,
        `conta_receita`, `conta_despesa` e `conta_inativa`.

        Convenção de códigos do OMIE: códigos que começam com 1 são receitas e
        com 2 são despesas.
        """
        client = ctx.request_context.lifespan_context["omie"]
        if tipo and tipo.upper() not in ("R", "D"):
            raise ValueError(f"tipo deve ser R (receita) ou D (despesa), recebido: {tipo!r}")
        params: dict = {
            "pagina": pagina,
            "registros_por_pagina": min(registros_por_pagina, MAX_REGISTROS_POR_PAGINA),
        }
        if apenas_ativas:
            params["filtrar_apenas_ativo"] = "S"
        if tipo:
            params["filtrar_por_tipo"] = tipo.upper()
        if descricao:
            params["descricao"] = descricao
        return await client.call(
            "geral/categorias/", "ListarCategorias", params, lista_vazia_ok=True
        )

    @mcp.tool()
    async def consultar_categoria(
        ctx: Context,
        codigo: Annotated[str, "Código da categoria (ex: 2.01.02)"],
    ) -> dict:
        """
        Consulta os detalhes de uma categoria pelo código, incluindo os dados da
        conta do DRE vinculada (`dadosDRE`).
        """
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call(
            "geral/categorias/", "ConsultarCategoria", {"codigo": codigo}
        )

    @mcp.tool()
    async def listar_grupos_categoria(ctx: Context) -> dict:
        """
        Lista os grupos totalizadores de categoria — exatamente os valores aceitos
        em `categoria_superior` ao criar uma categoria com incluir_categoria.

        O OMIE não oferece um filtro para isso, então esta tool varre o plano de
        categorias e devolve as entradas com `totalizadora = S` e código de 4
        caracteres (formato "9.99").
        """
        client = ctx.request_context.lifespan_context["omie"]
        grupos: list[dict] = []
        pagina = 1
        while pagina <= MAX_PAGINAS_VARREDURA:
            resposta = await client.call(
                "geral/categorias/",
                "ListarCategorias",
                {"pagina": pagina, "registros_por_pagina": MAX_REGISTROS_POR_PAGINA},
                lista_vazia_ok=True,
            )
            for categoria in resposta.get("categoria_cadastro", []):
                codigo = categoria.get("codigo", "")
                if categoria.get("totalizadora") == "S" and len(codigo) == TAMANHO_CODIGO_GRUPO:
                    grupos.append(
                        {
                            "codigo": codigo,
                            "descricao": categoria.get("descricao"),
                            "natureza": categoria.get("natureza"),
                            # 1 = receita, 2 = despesa (convenção do plano do OMIE)
                            "tipo": {"1": "R", "2": "D"}.get(codigo[0]),
                            "nao_exibir": categoria.get("nao_exibir"),
                        }
                    )
            if pagina >= (resposta.get("total_de_paginas") or 0):
                break
            pagina += 1
        return {"registros": len(grupos), "grupos": grupos}

    @mcp.tool()
    async def listar_tipos_categoria(
        ctx: Context,
        pagina: Annotated[int, "Número da página (inicia em 1)"] = 1,
        registros_por_pagina: Annotated[int, "Registros por página"] = 50,
    ) -> dict:
        """
        Lista os tipos de categoria — os valores aceitos em `tipo_categoria` ao
        incluir ou alterar uma categoria.

        Cada item traz `cCodigo` (o valor a usar), `cDescricao`, `cGrupo` e `cTipo`,
        onde cTipo é P (gasto) ou R (receita). O `cTipo` precisa ser compatível com
        a categoria: código/grupo iniciando em 1 exige cTipo R, iniciando em 2 exige
        cTipo P.
        """
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call(
            "geral/tipocategoria/",
            "ListarTipoCategoria",
            {"nPagina": pagina, "nRegPorPagina": registros_por_pagina},
            lista_vazia_ok=True,
        )

    @mcp.tool()
    async def incluir_categoria(
        ctx: Context,
        categoria_superior: Annotated[
            str, "Código do grupo totalizador que receberá a categoria (ex: 2.01)"
        ],
        descricao: Annotated[str, "Descrição da categoria (máx 50 caracteres)"],
        natureza: Annotated[
            Optional[str],
            "Natureza da conta — equivale ao campo 'Observação' da categoria no ERP (máx 50)",
        ] = None,
        tipo_categoria: Annotated[
            Optional[str], "Código do tipo de categoria (ver listar_tipos_categoria)"
        ] = None,
        codigo_dre: Annotated[
            Optional[str], "Código da conta do DRE a vincular (ver listar_contas_dre)"
        ] = None,
    ) -> dict:
        """
        Cria uma nova categoria financeira no OMIE.

        O OMIE valida os vínculos e rejeita a inclusão se eles não fecharem:
        - `categoria_superior` precisa ser um grupo totalizador (use
          listar_grupos_categoria). Grupo iniciando em 1 cria receita, em 2 despesa.
        - `tipo_categoria` precisa ter cTipo compatível: R para grupo iniciando em 1,
          P para grupo iniciando em 2 (use listar_tipos_categoria).
        - `codigo_dre` só aceita contas com nivelDRE = 3, naoExibirDRE = N e
          totalizaDRE = N (use listar_contas_dre com apenas_vinculaveis=True).

        Retorna `codigo_status` ("0" = sucesso), `descricao_status` e o `codigo`
        gerado para a categoria.
        """
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {
            "categoria_superior": categoria_superior,
            "descricao": descricao,
        }
        if natureza:
            params["natureza"] = natureza
        if tipo_categoria:
            params["tipo_categoria"] = tipo_categoria
        if codigo_dre:
            params["codigo_dre"] = codigo_dre
        return await client.call("geral/categorias/", "IncluirCategoria", params)

    @mcp.tool()
    async def alterar_categoria(
        ctx: Context,
        codigo: Annotated[str, "Código da categoria a alterar (ex: 2.01.02)"],
        descricao: Annotated[Optional[str], "Nova descrição (máx 50 caracteres)"] = None,
        natureza: Annotated[Optional[str], "Nova natureza/observação (máx 50)"] = None,
        tipo_categoria: Annotated[
            Optional[str], "Novo código do tipo de categoria (ver listar_tipos_categoria)"
        ] = None,
        codigo_dre: Annotated[
            Optional[str], "Nova conta do DRE a vincular (ver listar_contas_dre)"
        ] = None,
        inativar: Annotated[
            Optional[bool], "True inativa a categoria, False reativa. Omita para não mexer."
        ] = None,
    ) -> dict:
        """
        Altera uma categoria existente. Apenas os campos informados são enviados.

        Mesmas regras de vínculo de incluir_categoria, aplicadas sobre o `codigo`:
        código iniciando em 1 exige tipo_categoria com cTipo R, em 2 exige cTipo P;
        `codigo_dre` só aceita contas de nivelDRE 3, não totalizadoras e exibíveis.

        Não existe método de exclusão de categoria na API do OMIE — para retirar uma
        categoria de uso, chame esta tool com inativar=True.
        """
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {"codigo": codigo}
        if descricao:
            params["descricao"] = descricao
        if natureza:
            params["natureza"] = natureza
        if tipo_categoria:
            params["tipo_categoria"] = tipo_categoria
        if codigo_dre:
            params["codigo_dre"] = codigo_dre
        if inativar is not None:
            params["conta_inativa"] = "S" if inativar else "N"
        return await client.call("geral/categorias/", "AlterarCategoria", params)

    @mcp.tool()
    async def incluir_grupo_categoria(
        ctx: Context,
        descricao: Annotated[str, "Descrição do grupo (máx 50 caracteres)"],
        tipo_grupo: Annotated[str, "Tipo do grupo: R (receita) ou D (despesa)"],
        natureza: Annotated[Optional[str], "Natureza/observação do grupo (máx 50)"] = None,
    ) -> dict:
        """
        Cria um grupo totalizador de categorias — o nível que depois é usado como
        `categoria_superior` das categorias.

        O OMIE gera o código do grupo automaticamente ("1.xx" para receita,
        "2.xx" para despesa) e o devolve em `codigo`.
        """
        client = ctx.request_context.lifespan_context["omie"]
        if tipo_grupo.upper() not in ("R", "D"):
            raise ValueError(
                f"tipo_grupo deve ser R (receita) ou D (despesa), recebido: {tipo_grupo!r}"
            )
        params: dict = {"descricao": descricao, "tipo_grupo": tipo_grupo.upper()}
        if natureza:
            params["natureza"] = natureza
        return await client.call("geral/categorias/", "IncluirGrupoCategoria", params)

    @mcp.tool()
    async def alterar_grupo_categoria(
        ctx: Context,
        codigo: Annotated[str, "Código do grupo a alterar (ex: 2.01)"],
        descricao: Annotated[Optional[str], "Nova descrição (máx 50 caracteres)"] = None,
        natureza: Annotated[Optional[str], "Nova natureza/observação (máx 50)"] = None,
    ) -> dict:
        """
        Altera um grupo totalizador de categorias.
        O OMIE não permite trocar o tipo (receita/despesa) de um grupo já criado.
        """
        client = ctx.request_context.lifespan_context["omie"]
        params: dict = {"codigo": codigo}
        if descricao:
            params["descricao"] = descricao
        if natureza:
            params["natureza"] = natureza
        return await client.call("geral/categorias/", "AlterarGrupoCategoria", params)
