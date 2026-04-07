"""
test_data_cleaner.py
--------------------
Testes para data_cleaner.py: validações individuais e pipeline limpar_dataframe().

Cobertura:
  - _validar_cpf:       CPF inválido, sequência repetida, CPF de teste, válido
  - _validar_email:     sem @, domínio sem ponto, válido, vazio (aceito)
  - _validar_telefone:  < 10 dígitos, todos iguais, DDD 00, válido, vazio (aceito)
  - _validar_nome:      curto, numérico, string inválida, válido
  - _eh_string_invalida: "EM VALIDACAO", "N/A", sequência repetida, valor normal
  - limpar_dataframe:   contagens do relatório, remoções esperadas
"""
import pandas as pd
import pytest

# Importações diretas das funções privadas para testes unitários
from data_cleaner import (
    _eh_string_invalida,
    _validar_cpf,
    _validar_email,
    _validar_nome,
    _validar_telefone,
    limpar_dataframe,
    relatorio_html,
)


# ============================================================
# _EH_STRING_INVALIDA
# ============================================================

class TestEhStringInvalida:
    def test_em_validacao_invalido(self):
        assert _eh_string_invalida("EM VALIDACAO") is True

    def test_em_validacao_com_acento(self):
        assert _eh_string_invalida("EM VALIDAÇÃO") is True

    def test_nao_informado(self):
        assert _eh_string_invalida("NAO INFORMADO") is True

    def test_nsa(self):
        assert _eh_string_invalida("NSA") is True

    def test_fulano(self):
        assert _eh_string_invalida("FULANO") is True

    def test_sequencia_repetida_invalida(self):
        assert _eh_string_invalida("AAAAAAA") is True

    def test_string_vazia_invalida(self):
        assert _eh_string_invalida("") is True

    def test_none_retorna_false(self):
        # None/NaN são tratados separadamente — não é "string inválida"
        assert _eh_string_invalida(None) is False

    def test_nome_valido(self):
        assert _eh_string_invalida("JOAO DA SILVA") is False

    def test_bairro_valido(self):
        assert _eh_string_invalida("JARDIM BOTANICO") is False

    def test_cidade_valida(self):
        assert _eh_string_invalida("SAO PAULO") is False


# ============================================================
# _VALIDAR_CPF
# ============================================================

class TestValidarCpf:
    def test_todos_zeros_invalido(self):
        assert _validar_cpf("00000000000") is False

    def test_sequencia_repetida_invalido(self):
        assert _validar_cpf("11111111111") is False
        assert _validar_cpf("99999999999") is False

    def test_cpf_teste_classico_invalido(self):
        assert _validar_cpf("12345678901") is False

    def test_cpf_curto_invalido(self):
        assert _validar_cpf("123456789") is False

    def test_cpf_longo_invalido(self):
        assert _validar_cpf("123456789012") is False

    def test_cpf_none_invalido(self):
        assert _validar_cpf(None) is False

    def test_cpf_nan_invalido(self):
        assert _validar_cpf(float("nan")) is False

    def test_cpf_com_pontuacao_valido(self):
        # CPF com máscara — dígitos extraídos devem ser 11
        assert _validar_cpf("321.654.987-00") is True

    def test_cpf_valido_sem_pontuacao(self):
        assert _validar_cpf("32165498700") is True

    def test_cpf_valido_diferente(self):
        assert _validar_cpf("74185296300") is True


# ============================================================
# _VALIDAR_EMAIL
# ============================================================

class TestValidarEmail:
    def test_sem_arroba_invalido(self):
        assert _validar_email("emailsemarroba.com") is False

    def test_dominio_sem_ponto_invalido(self):
        assert _validar_email("usuario@dominio") is False

    def test_sem_usuario_invalido(self):
        assert _validar_email("@dominio.com") is False

    def test_string_invalida_invalida(self):
        assert _validar_email("EM VALIDACAO") is False

    def test_email_valido(self):
        assert _validar_email("usuario@dominio.com") is True

    def test_email_com_subdominio_valido(self):
        assert _validar_email("x@sub.dominio.com.br") is True

    def test_none_aceito(self):
        # Email vazio/None é aceito — filtragem de email vazio é separada
        assert _validar_email(None) is True

    def test_nan_aceito(self):
        import numpy as np
        assert _validar_email(np.nan) is True


# ============================================================
# _VALIDAR_TELEFONE
# ============================================================

class TestValidarTelefone:
    def test_menos_de_10_digitos_invalido(self):
        assert _validar_telefone("11987654") is False

    def test_mais_de_11_digitos_invalido(self):
        assert _validar_telefone("119876543210") is False

    def test_todos_iguais_invalido(self):
        assert _validar_telefone("11111111111") is False

    def test_ddd_00_invalido(self):
        assert _validar_telefone("00987654321") is False

    def test_celular_valido(self):
        assert _validar_telefone("11987654321") is True

    def test_fixo_valido(self):
        assert _validar_telefone("1132165498") is True

    def test_none_aceito(self):
        assert _validar_telefone(None) is True

    def test_string_vazia_aceita(self):
        assert _validar_telefone("") is True


# ============================================================
# _VALIDAR_NOME
# ============================================================

class TestValidarNome:
    def test_nome_curto_invalido(self):
        assert _validar_nome("AB") is False

    def test_apenas_numeros_invalido(self):
        assert _validar_nome("12345678") is False

    def test_fulano_invalido(self):
        assert _validar_nome("FULANO") is False

    def test_em_validacao_invalido(self):
        assert _validar_nome("EM VALIDACAO") is False

    def test_none_invalido(self):
        assert _validar_nome(None) is False

    def test_nome_valido_simples(self):
        assert _validar_nome("JOAO SILVA") is True

    def test_nome_valido_composto(self):
        assert _validar_nome("MARIA DE FATIMA SOUZA") is True


# ============================================================
# LIMPAR_DATAFRAME — pipeline completo
# ============================================================

class TestLimparDataframe:
    def test_dataframe_vazio_retorna_vazio(self):
        df = pd.DataFrame()
        df_limpo, relatorio = limpar_dataframe(df)
        assert df_limpo.empty

    def test_registros_validos_mantidos(self, df_valido):
        df_limpo, relatorio = limpar_dataframe(df_valido)
        assert len(df_limpo) == len(df_valido)
        assert relatorio["removidos_cpf"] == 0
        assert relatorio["removidos_nome"] == 0
        assert relatorio["removidos_validacao"] == 0

    def test_cpf_zero_removido(self):
        df = pd.DataFrame([{
            "NOME": "FULANO DA SILVA", "CPF": "00000000000",
            "BAIRRO": "CENTRO", "CIDADE": "SAO PAULO", "UF": "SP",
            "ENDERECO": "RUA A", "TELEFONE_1": "11987654321",
            "EMAIL_1": None,
        }])
        df_limpo, r = limpar_dataframe(df)
        assert r["removidos_cpf"] == 1

    def test_em_validacao_removido(self):
        df = pd.DataFrame([{
            "NOME": "EM VALIDACAO", "CPF": "32165498700",
            "BAIRRO": "CENTRO", "CIDADE": "SAO PAULO", "UF": "SP",
            "ENDERECO": "RUA A", "TELEFONE_1": "11987654321",
            "EMAIL_1": None,
        }])
        df_limpo, r = limpar_dataframe(df)
        assert r["removidos_validacao"] >= 1
        assert len(df_limpo) == 0

    def test_email_invalido_sobrescrito_nao_remove_registro(self):
        df = pd.DataFrame([{
            "NOME": "JOAO SILVA", "CPF": "32165498700",
            "BAIRRO": "CENTRO", "CIDADE": "SAO PAULO", "UF": "SP",
            "ENDERECO": "RUA A", "TELEFONE_1": "11987654321",
            "EMAIL_1": "email-sem-arroba",
        }])
        df_limpo, r = limpar_dataframe(df)
        # Registro permanece, mas email é anulado
        assert len(df_limpo) == 1
        assert df_limpo.iloc[0]["EMAIL_1"] is None
        assert r["removidos_email"] >= 1

    def test_telefone_invalido_sobrescrito_nao_remove_registro(self):
        df = pd.DataFrame([{
            "NOME": "JOAO SILVA", "CPF": "32165498700",
            "BAIRRO": "CENTRO", "CIDADE": "SAO PAULO", "UF": "SP",
            "ENDERECO": "RUA A", "TELEFONE_1": "11111111111",  # todos iguais
            "EMAIL_1": "joao@email.com",
        }])
        df_limpo, r = limpar_dataframe(df)
        assert len(df_limpo) == 1
        assert df_limpo.iloc[0]["TELEFONE_1"] is None
        assert r["removidos_telefone"] >= 1

    def test_relatorio_contagens_corretas(self, df_com_sujeiras):
        df_limpo, r = limpar_dataframe(df_com_sujeiras)
        assert r["total_inicial"] == len(df_com_sujeiras)
        assert r["total_final"] == len(df_limpo)
        assert r["total_final"] < r["total_inicial"]  # deve ter removido algo
        # Somando tudo: cada registro pode ser removido por um motivo predominante,
        # mas o relatório contabiliza todos os filtros passados
        assert r["removidos_cpf"] + r["removidos_nome"] + r["removidos_validacao"] > 0

    def test_relatorio_html_retorna_string(self, df_valido):
        _, r = limpar_dataframe(df_valido)
        html = relatorio_html(r)
        assert isinstance(html, str)
        assert "<strong>" in html
        assert "Limpeza de dados" in html
