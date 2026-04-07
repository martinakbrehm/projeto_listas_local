"""
conftest.py
-----------
Fixtures compartilhadas entre todos os módulos de teste.
"""
import pandas as pd
import pytest


# ============================================================
# DataFrame base — campos mínimos necessários
# ============================================================

def _make_row(**overrides) -> dict:
    """Retorna um registro PF válido com valores padrão substituíveis."""
    base = {
        "NOME":            "JOAO DA SILVA",
        "CPF":             "32165498700",   # CPF fictício estruturalmente válido
        "TELEFONE_1":      "11987654321",   # celular
        "TELEFONE_2":      None,
        "TELEFONE_3":      None,
        "TELEFONE_4":      None,
        "TELEFONE_5":      None,
        "TELEFONE_6":      None,
        "GENERO":          "M",
        "DATA_NASCIMENTO": "1985-03-20",
        "ENDERECO":        "RUA DAS FLORES",
        "NUM_END":         "123",
        "COMPLEMENTO":     None,
        "BAIRRO":          "JARDIM BOTANICO",
        "CIDADE":          "SAO PAULO",
        "UF":              "SP",
        "CEP":             "01310100",
        "EMAIL_1":         "joao@email.com",
        "EMAIL_2":         None,
        "CBO":             "252515",
    }
    base.update(overrides)
    return base


@pytest.fixture
def df_valido():
    """DataFrame com 3 registros válidos e distintos."""
    rows = [
        _make_row(CPF="32165498700", NOME="JOAO DA SILVA",   TELEFONE_1="11987654321"),
        _make_row(CPF="65432198700", NOME="MARIA SOUZA",     TELEFONE_1="21956781234", GENERO="F"),
        _make_row(CPF="74185296300", NOME="CARLOS PEREIRA",  TELEFONE_1="31912345678"),
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def df_com_sujeiras():
    """DataFrame misturando registros válidos e sujeiras conhecidas."""
    rows = [
        _make_row(CPF="32165498700", NOME="JOAO DA SILVA"),
        _make_row(CPF="00000000000", NOME="EM VALIDACAO"),          # CPF zero + sujeira
        _make_row(CPF="12345678901", NOME="FULANO DE TAL"),         # CPF teste + nome sujeira
        _make_row(CPF="74185296300", NOME="CARLOS PEREIRA", EMAIL_1="email-invalido"),
        _make_row(CPF="85296374100", NOME="A",               TELEFONE_1="00000000000"),  # nome curto + tel inv.
        _make_row(CPF="96385274100", NOME="MARIA SANTOS",   BAIRRO="NAO INFORMADO"),    # bairro inválido
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def df_misturado_telefones():
    """DataFrame com celulares, fixos e números inválidos."""
    rows = [
        _make_row(CPF="11122233344", NOME="CELULAR VALIDO",   TELEFONE_1="11987654321"),  # celular
        _make_row(CPF="22233344455", NOME="FIXO VALIDO",      TELEFONE_1="1132165498"),   # fixo (10 dig)
        _make_row(CPF="33344455566", NOME="CELULAR E FIXO",   TELEFONE_1="11987654321", TELEFONE_2="1132165498"),
        _make_row(CPF="44455566677", NOME="SEM TELEFONE",     TELEFONE_1=None),
        _make_row(CPF="55566677788", NOME="NUMERO INVALIDO",  TELEFONE_1="11187654321"),  # 3o dig != 9
    ]
    # Corrigir CPFs para não serem sequências repetidas (passam no _validar_cpf)
    rows[0]["CPF"] = "32165498701"
    rows[1]["CPF"] = "32165498702"
    rows[2]["CPF"] = "32165498703"
    rows[3]["CPF"] = "32165498704"
    rows[4]["CPF"] = "32165498705"
    return pd.DataFrame(rows)


@pytest.fixture
def filtros_basicos() -> dict:
    """Filtros mínimos para consulta de teste."""
    return {
        "ufs":           ["SP"],
        "cidades":       ["SAO PAULO"],
        "bairros":       [],
        "genero":        "ambos",
        "idade_min":     25,
        "idade_max":     55,
        "email":         "nao_filtrar",
        "tipo_telefone": "movel",
        "cbos":          [],
        "quantidade":    100,
    }
