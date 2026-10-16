"""Tools de Contas do DRE — endpoint: /geral/dre/"""

from typing import Annotated
from mcp.server.fastmcp import FastMCP, Context

# O OMIE só aceita vincular uma categoria a contas do DRE analíticas: nível 3,
# exibíveis e não totalizadoras.
NIVEL_DRE_ANALITICO = 3


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def listar_contas_dre(
        ctx: Context,
        apenas_ativas: Annotated[bool, "Trazer somente as contas ativas do DRE"] = True,
        apenas_vinculaveis: Annotated[
            bool,
            "Trazer somente as contas aceitas como codigo_dre de uma categoria "
            "(nível 3, exibíveis e não totalizadoras)",
        ] = False,
    ) -> dict:
        """
        Lista a estrutura de contas do DRE (Demonstrativo de Resultados do Exercício).

        Este endpoint não é paginado: devolve a estrutura inteira em `dreLista`, com
        `codigoDRE`, `descricaoDRE`, `nivelDRE` (1 a 3), `sinalDRE` (+ ou -),
        `totalizaDRE` e `naoExibirDRE`.

        Níveis 1 e 2 são totalizadores da apresentação do relatório; só o nível 3
        recebe categorias. Use apenas_vinculaveis=True para obter direto os códigos
        válidos em incluir_categoria/alterar_categoria.

        A API do OMIE é somente leitura para o DRE: a estrutura é mantida no ERP,
        não há métodos de inclusão, alteração ou exclusão de contas do DRE.
        """
        client = ctx.request_context.lifespan_context["omie"]
        resposta = await client.call(
            "geral/dre/",
            "ListarCadastroDRE",
            {"apenasContasAtivas": "S" if apenas_ativas else "N"},
            lista_vazia_ok=True,
        )
        contas = resposta.get("dreLista", [])
        if apenas_vinculaveis:
            contas = [
                conta
                for conta in contas
                if conta.get("nivelDRE") == NIVEL_DRE_ANALITICO
                and conta.get("naoExibirDRE") == "N"
                and conta.get("totalizaDRE") == "N"
            ]
        # Normaliza a resposta: com lista_vazia_ok o client devolve o formato
        # paginado genérico, que não vale para este endpoint.
        return {"totalRegistros": len(contas), "dreLista": contas}
