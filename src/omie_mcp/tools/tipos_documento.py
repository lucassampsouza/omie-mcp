"""Tools de Tipos de Documento — endpoint: /geral/tiposdoc/"""

import time
import unicodedata
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP, Context

# PesquisarTipoDocumento não é paginado e a base padrão do OMIE tem ~290 tipos.
# Sem limite, uma listagem sem filtro devolveria a tabela inteira.
LIMITE_PADRAO = 50

# A tabela é mantida pelo OMIE e praticamente não muda. Guardá-la em memória é o
# que viabiliza buscar por descrição: o filtro é aplicado localmente, então duas
# pesquisas seguidas gerariam a mesma requisição e a segunda seria recusada com
# "Consumo redundante detectado".
CACHE_TTL_SEGUNDOS = 600


def _normalizar(texto: str) -> str:
    """Minúsculas e sem acentos, para casar 'salario' com '13o. Salário'."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).casefold()


def register(mcp: FastMCP) -> None:
    cache: dict = {"tipos": [], "expira_em": 0.0}

    async def _obter_tipos(client) -> list[dict]:
        agora = time.monotonic()
        if cache["tipos"] and agora < cache["expira_em"]:
            return cache["tipos"]
        # O parâmetro "codigo" do OMIE faz busca exata; para pesquisar por texto
        # é preciso trazer a tabela toda e filtrar aqui.
        resposta = await client.call(
            "geral/tiposdoc/", "PesquisarTipoDocumento", {"codigo": ""}, lista_vazia_ok=True
        )
        tipos = resposta.get("tipo_documento_cadastro", [])
        if tipos:
            cache["tipos"] = tipos
            cache["expira_em"] = agora + CACHE_TTL_SEGUNDOS
        return tipos

    @mcp.tool()
    async def listar_tipos_documento(
        ctx: Context,
        descricao: Annotated[
            Optional[str],
            "Filtrar pela descrição (busca parcial, ignora acentos e maiúsculas). "
            "Ex: 'boleto', 'salario'",
        ] = None,
        limite: Annotated[int, "Máximo de tipos a retornar"] = LIMITE_PADRAO,
    ) -> dict:
        """
        Lista os tipos de documento do OMIE — os códigos usados no tipo de documento
        (tag cCodigo/cTipo) ao lançar contas a pagar, contas a receber e lançamentos
        bancários. Ex: BOL (Boleto), NF (Nota Fiscal), ADI (Adiantamento).

        O endpoint do OMIE devolve a tabela inteira de uma vez (~290 registros) e não
        tem filtro por descrição, então o filtro e o limite são aplicados aqui, sobre
        uma cópia em memória da tabela. O campo `total_encontrado` informa quantos
        casaram antes do corte por `limite`.

        A tabela é mantida pelo OMIE: a API é somente leitura, não há inclusão,
        alteração nem exclusão de tipos de documento.
        """
        client = ctx.request_context.lifespan_context["omie"]
        tipos = await _obter_tipos(client)
        if descricao:
            alvo = _normalizar(descricao)
            tipos = [t for t in tipos if alvo in _normalizar(t.get("descricao", ""))]
        return {
            "total_encontrado": len(tipos),
            "registros": min(len(tipos), limite),
            "tipo_documento_cadastro": tipos[:limite],
        }

    @mcp.tool()
    async def consultar_tipo_documento(
        ctx: Context,
        codigo: Annotated[str, "Código exato do tipo de documento (ex: BOL, NF, ADI)"],
    ) -> dict:
        """
        Consulta um tipo de documento pelo código exato.
        Use listar_tipos_documento com o filtro `descricao` quando não souber o código.
        """
        client = ctx.request_context.lifespan_context["omie"]
        return await client.call(
            "geral/tiposdoc/", "ConsultarTipoDocumento", {"codigo": codigo}
        )
