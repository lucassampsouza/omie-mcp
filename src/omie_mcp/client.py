"""Cliente HTTP para a API do OMIE ERP."""

import httpx
from typing import Any


OMIE_BASE_URL = "https://app.omie.com.br/api/v1"

# O OMIE sinaliza "nenhum registro encontrado" com HTTP 500 + este faultcode.
# Não é um erro: é uma lista vazia.
FAULTCODE_SEM_REGISTROS = "5113"


class OmieError(Exception):
    """Erro retornado pela API do OMIE (faultstring/faultcode)."""

    def __init__(self, status_code: int, faultcode: str, faultstring: str, call: str):
        self.status_code = status_code
        self.faultcode = faultcode
        self.faultstring = faultstring
        self.call = call
        super().__init__(f"[{call}] HTTP {status_code} {faultcode}: {faultstring}")

    @property
    def sem_registros(self) -> bool:
        return FAULTCODE_SEM_REGISTROS in self.faultcode


class OmieClient:
    """Cliente para chamadas à API REST do OMIE."""

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self._http = httpx.AsyncClient(timeout=30.0)

    async def call(
        self,
        endpoint: str,
        call: str,
        params: dict[str, Any] | None = None,
        *,
        lista_vazia_ok: bool = False,
    ) -> dict[str, Any]:
        """
        Executa uma chamada à API do OMIE.

        Args:
            endpoint:       Caminho do endpoint (ex: "geral/clientes/")
            call:           Nome do método da API (ex: "ListarClientes")
            params:         Parâmetros específicos do método
            lista_vazia_ok: Traduz "não existem registros" (500/5113) numa lista
                            vazia em vez de erro. Use nos métodos de listagem.

        Returns:
            Resposta da API como dicionário.

        Raises:
            OmieError: quando a API retorna um faultstring.
        """
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params or {}],
        }

        url = f"{OMIE_BASE_URL}/{endpoint}"
        response = await self._http.post(url, json=payload)

        try:
            body = response.json()
        except ValueError:
            response.raise_for_status()
            raise OmieError(response.status_code, "", response.text[:500], call)

        # O OMIE devolve erros de validação como HTTP 500 com um faultstring
        # descritivo. Sem isto, o erro chega ao usuário como um 500 opaco.
        if isinstance(body, dict) and "faultstring" in body:
            erro = OmieError(
                response.status_code,
                str(body.get("faultcode", "")),
                str(body["faultstring"]).strip(),
                call,
            )
            if lista_vazia_ok and erro.sem_registros:
                return {"registros": 0, "total_de_registros": 0, "total_de_paginas": 0, "lista": []}
            raise erro

        response.raise_for_status()
        return body

    async def aclose(self):
        await self._http.aclose()
