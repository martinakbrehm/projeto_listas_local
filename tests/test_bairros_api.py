"""
test_bairros_api.py
--------------------
Testes para bairros_api.py: normalização, resolução de aliases,
lógica de cache e integração com IBGE+Overpass (HTTP mockado).
"""
import time
from unittest.mock import MagicMock, patch

import pytest

import bairros_api as api
from bairros_api import (
    _cache_valido,
    _chave_cache,
    _normalizar,
    _resolver_nome_ibge,
    _salvar_cache,
    limpar_cache,
    obter_bairros,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(autouse=True)
def limpa_cache_antes_de_cada_teste():
    """Garante que o cache está vazio antes de cada teste."""
    limpar_cache()
    yield
    limpar_cache()


# Resposta IBGE simulada para São Paulo
IBGE_SAO_PAULO = [
    {
        "id": 3550308,
        "nome": "São Paulo",
        "microrregiao": {"nome": "São Paulo"},
    }
]

# Resposta Overpass simulada com 3 bairros
OVERPASS_SAO_PAULO = {
    "elements": [
        {"type": "node", "tags": {"name": "Moema",       "place": "neighbourhood"}},
        {"type": "node", "tags": {"name": "Pinheiros",   "place": "neighbourhood"}},
        {"type": "node", "tags": {"name": "Vila Madalena", "place": "suburb"}},
        {"type": "way",  "tags": {"name": "it",          "place": "neighbourhood"}},  # curto, deve ser ignorado
    ]
}


# ============================================================
# _NORMALIZAR
# ============================================================

class TestNormalizar:
    def test_remove_acento_grave(self):
        assert _normalizar("São Paulo") == "SAO PAULO"

    def test_remove_acento_agudo(self):
        assert _normalizar("Belém") == "BELEM"

    def test_maiusculo(self):
        assert _normalizar("curitiba") == "CURITIBA"

    def test_strip(self):
        assert _normalizar("  RIO  ") == "RIO"

    def test_sem_acento_mantem(self):
        assert _normalizar("FLORIANOPOLIS") == "FLORIANOPOLIS"

    def test_cedilha_removida(self):
        # Ç normalizado
        result = _normalizar("Maceió")
        assert "MACEI" in result

    def test_bh_alias(self):
        assert _normalizar("BH") == "BH"


# ============================================================
# _RESOLVER_NOME_IBGE
# ============================================================

class TestResolverNomeIbge:
    def test_bh_resolve_belo_horizonte(self):
        assert _resolver_nome_ibge("BH") == "Belo Horizonte"

    def test_bh_minusculo_resolve(self):
        assert _resolver_nome_ibge("bh") == "Belo Horizonte"

    def test_rio_resolve(self):
        assert _resolver_nome_ibge("RIO") == "Rio de Janeiro"

    def test_floripa_resolve(self):
        assert _resolver_nome_ibge("floripa") == "Florianópolis"

    def test_sampa_resolve(self):
        assert _resolver_nome_ibge("SAMPA") == "São Paulo"

    def test_nome_ja_oficial_mantem(self):
        assert _resolver_nome_ibge("Curitiba") == "Curitiba"

    def test_nome_desconhecido_retorna_original(self):
        assert _resolver_nome_ibge("Londrina") == "Londrina"


# ============================================================
# CACHE
# ============================================================

class TestCache:
    def test_cache_inexistente_invalido(self):
        assert not _cache_valido("inexistente")

    def test_cache_recente_valido(self):
        _salvar_cache("sao paulo", ["MOEMA", "PINHEIROS"])
        assert _cache_valido("sao paulo")

    def test_cache_expirado_invalido(self):
        # Salva com timestamp bem antigo (2 dias atrás)
        api._cache["expirado"] = (time.time() - 48 * 3600 - 1, ["BAIRRO"])
        assert not _cache_valido("expirado")

    def test_cache_retorna_dados_corretos(self):
        _salvar_cache("testecidade", ["ALPHA", "BETA"])
        ts, dados = api._cache["testecidade"]
        assert dados == ["ALPHA", "BETA"]

    def test_limpar_cache_esvazia(self):
        _salvar_cache("cidade1", ["BAIRRO"])
        limpar_cache()
        assert not _cache_valido("cidade1")

    def test_chave_cache_normalizada(self):
        assert _chave_cache("São Paulo") == _chave_cache("SAO PAULO")
        assert _chave_cache("curitiba") == _chave_cache("CURITIBA")


# ============================================================
# OBTER_BAIRROS — HTTP mockado
# ============================================================

class TestObterBairros:
    def _mock_ibge_e_overpass(self, ibge_resp, overpass_resp):
        """Helper que faz patch das camadas HTTP."""
        ctx_ibge     = patch("bairros_api._get_json",  return_value=ibge_resp)
        ctx_overpass = patch("bairros_api._post_json", return_value=overpass_resp)
        return ctx_ibge, ctx_overpass

    def test_retorna_lista_de_strings(self):
        ctx_ibge, ctx_ov = self._mock_ibge_e_overpass(IBGE_SAO_PAULO, OVERPASS_SAO_PAULO)
        with ctx_ibge, ctx_ov:
            bairros = obter_bairros("São Paulo")
        assert isinstance(bairros, list)
        assert all(isinstance(b, str) for b in bairros)

    def test_bairros_em_maiusculo(self):
        ctx_ibge, ctx_ov = self._mock_ibge_e_overpass(IBGE_SAO_PAULO, OVERPASS_SAO_PAULO)
        with ctx_ibge, ctx_ov:
            bairros = obter_bairros("São Paulo")
        for b in bairros:
            assert b == b.upper()

    def test_bairros_em_ordem_alfabetica(self):
        ctx_ibge, ctx_ov = self._mock_ibge_e_overpass(IBGE_SAO_PAULO, OVERPASS_SAO_PAULO)
        with ctx_ibge, ctx_ov:
            bairros = obter_bairros("São Paulo")
        assert bairros == sorted(bairros)

    def test_bairro_muito_curto_ignorado(self):
        ctx_ibge, ctx_ov = self._mock_ibge_e_overpass(IBGE_SAO_PAULO, OVERPASS_SAO_PAULO)
        with ctx_ibge, ctx_ov:
            bairros = obter_bairros("São Paulo")
        # "IT" (2 chars) deve ser ignorado
        assert "IT" not in bairros

    def test_bairros_validos_incluidos(self):
        ctx_ibge, ctx_ov = self._mock_ibge_e_overpass(IBGE_SAO_PAULO, OVERPASS_SAO_PAULO)
        with ctx_ibge, ctx_ov:
            bairros = obter_bairros("São Paulo")
        assert "MOEMA" in bairros
        assert "PINHEIROS" in bairros
        assert "VILA MADALENA" in bairros

    def test_cache_usado_na_segunda_chamada(self):
        ctx_ibge, ctx_ov = self._mock_ibge_e_overpass(IBGE_SAO_PAULO, OVERPASS_SAO_PAULO)
        mock_get  = MagicMock(return_value=IBGE_SAO_PAULO)
        mock_post = MagicMock(return_value=OVERPASS_SAO_PAULO)
        with patch("bairros_api._get_json", mock_get), \
             patch("bairros_api._post_json", mock_post):
            obter_bairros("São Paulo")   # 1ª chamada — HTTP
            obter_bairros("São Paulo")   # 2ª chamada — cache

        # HTTP deve ter sido chamado apenas 1x (cache hits na 2ª)
        assert mock_get.call_count == 1
        assert mock_post.call_count == 1

    def test_municipio_nao_encontrado_retorna_vazio(self):
        with patch("bairros_api._get_json", return_value=None):
            bairros = obter_bairros("CidadeInexistente")
        assert bairros == []

    def test_ibge_sem_resultado_retorna_vazio(self):
        with patch("bairros_api._get_json", return_value=[]):
            bairros = obter_bairros("CidadeInexistente")
        assert bairros == []

    def test_overpass_sem_elementos_retorna_vazio(self):
        ctx_ibge = patch("bairros_api._get_json",  return_value=IBGE_SAO_PAULO)
        ctx_ov   = patch("bairros_api._post_json", return_value={"elements": []})
        with ctx_ibge, ctx_ov:
            bairros = obter_bairros("São Paulo")
        assert bairros == []

    def test_alias_bh_resolve_belo_horizonte(self):
        """BH deve ser resolvido para Belo Horizonte antes de consultar IBGE."""
        ibge_bh = [{"id": 3106200, "nome": "Belo Horizonte"}]
        overpass_bh = {"elements": [
            {"type": "node", "tags": {"name": "Savassi", "place": "neighbourhood"}},
        ]}
        mock_get  = MagicMock(return_value=ibge_bh)
        mock_post = MagicMock(return_value=overpass_bh)

        with patch("bairros_api._get_json", mock_get), \
             patch("bairros_api._post_json", mock_post):
            bairros = obter_bairros("BH")

        assert "SAVASSI" in bairros
        # URL da requisição IBGE deve conter "Belo Horizonte", não "BH"
        call_url = mock_get.call_args[0][0]
        assert "Belo" in call_url or "belo" in call_url.lower()

    def test_resultado_cacheado_apos_sucesso(self):
        ctx_ibge, ctx_ov = self._mock_ibge_e_overpass(IBGE_SAO_PAULO, OVERPASS_SAO_PAULO)
        with ctx_ibge, ctx_ov:
            obter_bairros("São Paulo")
        chave = _chave_cache("São Paulo")
        assert _cache_valido(chave)
