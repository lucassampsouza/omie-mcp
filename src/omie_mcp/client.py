"""Cliente HTTP para a API do OMIE ERP."""

import httpx
from typing import Any


OMIE_BASE_URL = "https://app.omie.com.br/api/v1"


class OmieClient:
    """Cliente para chamadas à API REST do OMIE."""

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self._http = httpx.AsyncClient(timeout=30.0)

    async def call(self, endpoint: str, call: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Executa uma chamada à API do OMIE.

        Args:
            endpoint: Caminho do endpoint (ex: "geral/clientes/")
            call:     Nome do método da API (ex: "ListarClientes")
            params:   Parâmetros específicos do método

        Returns:
            Resposta da API como dicionário.
        """
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params or {}],
        }

        url = f"{OMIE_BASE_URL}/{endpoint}"
        response = await self._http.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def aclose(self):
        await self._http.aclose()
