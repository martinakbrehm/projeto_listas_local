"""
test_data_processor.py
-----------------------
Testes para data_processor.py: helpers internos e pipeline processar().

Cobertura:
  - _apenas_digitos: remoção de não dígitos
  - _eh_celular:     celular válido, fixo, dígito 3 != 9, comprimento errado
  - _eh_fixo:        fixo válido, celular, comprimento errado
  - _tem_telefone_do_tipo: cada tipo nos 6 campos, sem telefone
  - _tem_email_valido:     com email, sem email, email inválido
  - processar(): retorno de tupla, filtro por tipo, CBO, email, quantidade
  - colunas_saida(): presença de colunas esperadas, ausência de score/renda
"""
from unittest.mock import patch

import pandas as pd
import pytest

from data_processor import (
    _apenas_digitos,
    _eh_celular,
    _eh_fixo,
    _normalizar_str,
    _tem_email_valido,
    _tem_telefone_do_tipo,
    colunas_saida,
    processar,
)


# ============================================================
# _APENAS_DIGITOS
# ============================================================

class TestApenasDigitos:
    def test_numero_puro(self):
        assert _apenas_digitos("11987654321") == "11987654321"

    def test_mascara_cpf(self):
        assert _apenas_digitos("321.654.987-00") == "32165498700"

    def test_mascara_telefone(self):
        assert _apenas_digitos("(11) 98765-4321") == "11987654321"

    def test_none_retorna_vazio(self):
        assert _apenas_digitos(None) == ""

    def test_vazio_retorna_vazio(self):
        assert _apenas_digitos("") == ""

    def test_texto_sem_numero(self):
        assert _apenas_digitos("abc-def") == ""


# ============================================================
# _NORMALIZAR_STR
# ============================================================

class TestNormalizarStr:
    def test_maiusculo(self):
        assert _normalizar_str("sao paulo") == "SAO PAULO"

    def test_strip(self):
        assert _normalizar_str("  CENTRO  ") == "CENTRO"

    def test_none_retorna_vazio(self):
        assert _normalizar_str(None) == ""


# ============================================================
# _EH_CELULAR
# ============================================================

class TestEhCelular:
    def test_celular_valido(self):
        assert _eh_celular("11987654321") is True

    def test_celular_rj(self):
        assert _eh_celular("21956781234") is True

    def test_celular_mg(self):
        assert _eh_celular("31912345678") is True

    def test_fixo_nao_e_celular(self):
        assert _eh_celular("1132165498") is False   # 10 dígitos

    def test_terceiro_digito_nao_9(self):
        # DDD 11, 3o dígito = 1 → não é celular
        assert _eh_celular("11187654321") is False

    def test_terceiro_digito_8(self):
        assert _eh_celular("11887654321") is False

    def test_curto_invalido(self):
        assert _eh_celular("1198765432") is False   # 10 dígitos, 3o é 9 mas curto

    def test_longo_invalido(self):
        assert _eh_celular("119876543210") is False  # 12 dígitos

    def test_vazio_invalido(self):
        assert _eh_celular("") is False

    def test_none_invalido(self):
        assert _eh_celular(None) is False

    def test_com_mascara(self):
        # (11) 98765-4321 → digits=11987654321
        assert _eh_celular("(11) 98765-4321") is True


# ============================================================
# _EH_FIXO
# ============================================================

class TestEhFixo:
    def test_fixo_valido(self):
        assert _eh_fixo("1132165498") is True

    def test_fixo_rj(self):
        assert _eh_fixo("2132165498") is True

    def test_celular_nao_e_fixo(self):
        assert _eh_fixo("11987654321") is False   # 11 dígitos

    def test_curto_invalido(self):
        assert _eh_fixo("113216549") is False     # 9 dígitos

    def test_longo_invalido(self):
        assert _eh_fixo("113216549834") is False  # 12 dígitos

    def test_vazio_invalido(self):
        assert _eh_fixo("") is False


# ============================================================
# _TEM_TELEFONE_DO_TIPO
# ============================================================

def _make_row_tel(**telefones) -> pd.Series:
    """Cria pd.Series com campos de telefone."""
    base = {f"TELEFONE_{i}": None for i in range(1, 7)}
    base.update(telefones)
    return pd.Series(base)


class TestTemTelefoneTipo:
    def test_celular_em_tel1(self):
        row = _make_row_tel(TELEFONE_1="11987654321")
        assert _tem_telefone_do_tipo(row, "movel") is True

    def test_celular_em_tel3(self):
        row = _make_row_tel(TELEFONE_3="11987654321")
        assert _tem_telefone_do_tipo(row, "movel") is True

    def test_fixo_em_tel2(self):
        row = _make_row_tel(TELEFONE_2="1132165498")
        assert _tem_telefone_do_tipo(row, "fixo") is True

    def test_sem_telefone_retorna_false(self):
        row = _make_row_tel()
        assert _tem_telefone_do_tipo(row, "movel") is False
        assert _tem_telefone_do_tipo(row, "fixo") is False

    def test_so_fixo_nao_e_movel(self):
        row = _make_row_tel(TELEFONE_1="1132165498")
        assert _tem_telefone_do_tipo(row, "movel") is False

    def test_so_celular_nao_e_fixo(self):
        row = _make_row_tel(TELEFONE_1="11987654321")
        assert _tem_telefone_do_tipo(row, "fixo") is False

    def test_ambos_aceita_celular(self):
        row = _make_row_tel(TELEFONE_1="11987654321")
        assert _tem_telefone_do_tipo(row, "ambos") is True

    def test_ambos_aceita_fixo(self):
        row = _make_row_tel(TELEFONE_1="1132165498")
        assert _tem_telefone_do_tipo(row, "ambos") is True

    def test_ambos_sem_telefone_retorna_false(self):
        row = _make_row_tel()
        assert _tem_telefone_do_tipo(row, "ambos") is False

    def test_celular_em_todos_6_campos(self):
        row = _make_row_tel(
            TELEFONE_1=None, TELEFONE_2=None, TELEFONE_3=None,
            TELEFONE_4=None, TELEFONE_5=None, TELEFONE_6="11987654321",
        )
        assert _tem_telefone_do_tipo(row, "movel") is True


# ============================================================
# _TEM_EMAIL_VALIDO
# ============================================================

class TestTemEmailValido:
    def test_email1_valido(self):
        row = pd.Series({"EMAIL_1": "usuario@dominio.com", "EMAIL_2": None})
        assert _tem_email_valido(row) is True

    def test_email2_valido(self):
        row = pd.Series({"EMAIL_1": None, "EMAIL_2": "outro@email.com.br"})
        assert _tem_email_valido(row) is True

    def test_sem_email(self):
        row = pd.Series({"EMAIL_1": None, "EMAIL_2": None})
        assert _tem_email_valido(row) is False

    def test_email_sem_arroba(self):
        row = pd.Series({"EMAIL_1": "emailsemarroba.com", "EMAIL_2": None})
        assert _tem_email_valido(row) is False

    def test_ambos_invalidos(self):
        row = pd.Series({"EMAIL_1": "invalido", "EMAIL_2": "tambem_invalido"})
        assert _tem_email_valido(row) is False


# ============================================================
# PROCESSAR — pipeline completo (mockando limpar_dataframe)
# ============================================================

def _free_cleaner(df):
    """Substituto de limpar_dataframe que retorna o df sem modificar."""
    from data_cleaner import relatorio_html
    r = {
        "total_inicial": len(df), "removidos_cpf": 0, "removidos_nome": 0,
        "removidos_validacao": 0, "removidos_email": 0, "removidos_telefone": 0,
        "total_final": len(df),
    }
    return df.copy(), r


def _mock_processar(df, filtros):
    """Chama processar() com limpar_dataframe substituído por _free_cleaner."""
    with patch("data_processor.limpar_dataframe", side_effect=_free_cleaner):
        return processar(df, filtros)


def _make_df(rows: list[dict]) -> pd.DataFrame:
    defaults = {f"TELEFONE_{i}": None for i in range(1, 7)}
    defaults.update({"EMAIL_1": None, "EMAIL_2": None, "CBO": None})
    filled = [{**defaults, **r} for r in rows]
    return pd.DataFrame(filled)


class TestProcessar:
    def test_retorna_tupla(self):
        df = _make_df([{"TELEFONE_1": "11987654321"}])
        result = _mock_processar(df, {"tipo_telefone": "movel", "quantidade": 0})
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_df_vazio_retorna_tupla_vazia(self):
        df, html = processar(pd.DataFrame(), {})
        assert df.empty
        assert html == ""

    def test_filtro_movel_remove_fixos(self):
        df = _make_df([
            {"TELEFONE_1": "11987654321"},   # celular ✓
            {"TELEFONE_1": "1132165498"},    # fixo ✗
        ])
        df_out, _ = _mock_processar(df, {"tipo_telefone": "movel", "quantidade": 0})
        assert len(df_out) == 1

    def test_filtro_fixo_remove_celulares(self):
        df = _make_df([
            {"TELEFONE_1": "11987654321"},   # celular ✗
            {"TELEFONE_1": "1132165498"},    # fixo ✓
        ])
        df_out, _ = _mock_processar(df, {"tipo_telefone": "fixo", "quantidade": 0})
        assert len(df_out) == 1

    def test_sem_filtro_tipo_tel_mantem_todos(self):
        df = _make_df([
            {"TELEFONE_1": "11987654321"},
            {"TELEFONE_1": "1132165498"},
        ])
        # "ambos" não deve remover nenhum
        df_out, _ = _mock_processar(df, {"tipo_telefone": "ambos", "quantidade": 0})
        assert len(df_out) == 2

    def test_filtro_cbo(self):
        # CBO não está disponível no banco atual, então filtro não é aplicado
        df = _make_df([
            {"TELEFONE_1": "11987654321", "CBO": "252515"},
            {"TELEFONE_1": "21987654321", "CBO": "999999"},
        ])
        df_out, _ = _mock_processar(df, {
            "tipo_telefone": "ambos", "cbos": ["252515"], "quantidade": 0
        })
        # Como CBO não existe, filtro não é aplicado e mantém todos
        assert len(df_out) == 2

    def test_filtro_cbo_vazio_mantem_todos(self):
        df = _make_df([
            {"TELEFONE_1": "11987654321", "CBO": "252515"},
            {"TELEFONE_1": "21987654321", "CBO": "999999"},
        ])
        df_out, _ = _mock_processar(df, {
            "tipo_telefone": "ambos", "cbos": [], "quantidade": 0
        })
        assert len(df_out) == 2

    def test_quantidade_limita_registros(self):
        rows = [{"TELEFONE_1": f"119000{str(i).zfill(5)}"} for i in range(10)]
        df = _make_df(rows)
        df_out, _ = _mock_processar(df, {"tipo_telefone": "ambos", "quantidade": 3})
        assert len(df_out) == 3

    def test_quantidade_zero_sem_limite(self):
        rows = [{"TELEFONE_1": f"119000{str(i).zfill(5)}"} for i in range(5)]
        df = _make_df(rows)
        df_out, _ = _mock_processar(df, {"tipo_telefone": "ambos", "quantidade": 0})
        assert len(df_out) == 5

    def test_email_preferencial_ordena_com_email_primeiro(self):
        df = _make_df([
            {"TELEFONE_1": "11987654321", "EMAIL_1": None},
            {"TELEFONE_1": "21987654321", "EMAIL_1": "usuario@email.com"},
        ])
        df_out, _ = _mock_processar(df, {
            "tipo_telefone": "ambos", "quantidade": 0, "email": "preferencial"
        })
        # Primeiro registro deve ter email
        assert "@" in str(df_out.iloc[0]["EMAIL_1"])

    def test_resultado_reseta_index(self):
        df = _make_df([{"TELEFONE_1": "11987654321"}, {"TELEFONE_1": "21987654321"}])
        df_out, _ = _mock_processar(df, {"tipo_telefone": "movel", "quantidade": 0})
        assert list(df_out.index) == list(range(len(df_out)))

    def test_relatorio_html_e_string(self):
        df = _make_df([{"TELEFONE_1": "11987654321"}])
        _, html = _mock_processar(df, {"tipo_telefone": "movel", "quantidade": 0})
        assert isinstance(html, str)


# ============================================================
# COLUNAS_SAIDA
# ============================================================

class TestColunasSaida:
    def test_retorna_lista(self):
        assert isinstance(colunas_saida(), list)

    def test_colunas_obrigatorias_presentes(self):
        cols = colunas_saida()
        for c in ("NOME", "CPF", "TELEFONE_1", "UF", "CIDADE", "BAIRRO"):
            assert c in cols, f"Coluna '{c}' ausente"

    def test_email_presente_por_padrao(self):
        cols = colunas_saida(com_email=True)
        assert "EMAIL_1" in cols
        assert "EMAIL_2" in cols

    def test_sem_email_ausente(self):
        cols = colunas_saida(com_email=False)
        assert "EMAIL_1" not in cols
        assert "EMAIL_2" not in cols

    def test_sem_score(self):
        cols = colunas_saida()
        assert "SCORE" not in cols

    def test_sem_renda(self):
        cols = colunas_saida()
        assert "RENDA" not in cols

    def test_todos_telefones_presentes(self):
        cols = colunas_saida()
        for i in range(1, 7):
            assert f"DDD_{i}" in cols
            assert f"TELEFONE_{i}" in cols
