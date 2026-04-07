"""
test_query_builder.py
---------------------
Testes para query_builder.py: estrutura SQL, params e descrição de filtros.

Cobertura:
  - build_query: ValueError sem UF, cláusulas WHERE corretas, params corretos
  - Gênero M/F/ambos
  - Idade padrão e customizada
  - Email obrigatório / sem filtro
  - Bairros e cidades
  - Ausência total de score e renda no SQL gerado
  - descrever_filtros_db: saída legível correta
"""
import pytest

from query_builder import IDADE_MAX_PADRAO, IDADE_MIN_PADRAO, build_query, descrever_filtros_db


# ============================================================
# HELPERS
# ============================================================

def _sql_params(filtros: dict) -> tuple[str, list]:
    return build_query(filtros)


BASE_FILTROS = {
    "ufs":           ["SP"],
    "cidades":       [],
    "bairros":       [],
    "genero":        "ambos",
    "idade_min":     None,
    "idade_max":     None,
    "email":         "nao_filtrar",
    "tipo_telefone": "movel",     # irrelevante para o banco
    "cbos":          [],
    "quantidade":    100,
}


# ============================================================
# VALIDAÇÃO BÁSICA
# ============================================================

class TestBuildQueryBasico:
    def test_sem_uf_levanta_valueerror(self):
        with pytest.raises(ValueError, match="UF"):
            build_query({**BASE_FILTROS, "ufs": []})

    def test_sql_retorna_string(self):
        sql, _ = build_query(BASE_FILTROS)
        assert isinstance(sql, str)

    def test_params_retorna_lista(self):
        _, params = build_query(BASE_FILTROS)
        assert isinstance(params, list)

    def test_select_presente(self):
        sql, _ = build_query(BASE_FILTROS)
        assert sql.strip().upper().startswith("SELECT")

    def test_from_tabela_correta(self):
        sql, _ = build_query(BASE_FILTROS)
        assert "latest_contacts" in sql.lower() or "lc" in sql

    def test_where_presente(self):
        sql, _ = build_query(BASE_FILTROS)
        assert "WHERE" in sql.upper()


# ============================================================
# FILTRO DE UF
# ============================================================

class TestUfFilter:
    def test_uf_unico_em_params(self):
        sql, params = build_query({**BASE_FILTROS, "ufs": ["SP"]})
        assert "SP" in params

    def test_uf_multiplos_em_params(self):
        sql, params = build_query({**BASE_FILTROS, "ufs": ["SP", "RJ", "MG"]})
        assert "SP" in params
        assert "RJ" in params
        assert "MG" in params

    def test_uf_multiplos_generates_placeholders(self):
        sql, _ = build_query({**BASE_FILTROS, "ufs": ["SP", "RJ"]})
        # % placeholders para 2 UFs
        assert sql.count("%s") >= 2

    def test_uf_convertido_para_maiusculo(self):
        sql, params = build_query({**BASE_FILTROS, "ufs": ["sp"]})
        assert "SP" in params
        assert "sp" not in params

    def test_uf_in_clause(self):
        sql, _ = build_query(BASE_FILTROS)
        assert "IN" in sql.upper()


# ============================================================
# FILTRO DE CIDADE
# ============================================================

class TestCidadeFilter:
    def test_sem_cidade_sem_clausula_cidade(self):
        sql, params = build_query({**BASE_FILTROS, "cidades": []})
        assert "CURITIBA" not in sql

    def test_com_cidade_em_params(self):
        sql, params = build_query({**BASE_FILTROS, "cidades": ["CURITIBA"]})
        assert "CURITIBA" in params

    def test_com_multiplas_cidades(self):
        sql, params = build_query({**BASE_FILTROS, "cidades": ["SAO PAULO", "CAMPINAS"]})
        assert "SAO PAULO" in params
        assert "CAMPINAS" in params


# ============================================================
# FILTRO DE BAIRRO
# ============================================================

class TestBairroFilter:
    def test_sem_bairro_sem_clausula_bairro(self):
        sql, params = build_query({**BASE_FILTROS, "bairros": []})
        assert "CENTRO" not in params

    def test_com_bairro_em_params(self):
        sql, params = build_query({**BASE_FILTROS, "bairros": ["CENTRO"]})
        assert "CENTRO" in params

    def test_bairro_convertido_para_maiusculo(self):
        sql, params = build_query({**BASE_FILTROS, "bairros": ["jardim botanico"]})
        assert "JARDIM BOTANICO" in params


# ============================================================
# FILTRO DE GÊNERO
# ============================================================

class TestGeneroFilter:
    def test_genero_ambos_sem_like(self):
        sql, params = build_query({**BASE_FILTROS, "genero": "ambos"})
        # Sem LIKE para gênero
        assert "LIKE" not in sql.upper()

    def test_genero_feminino_like_f(self):
        sql, params = build_query({**BASE_FILTROS, "genero": "F"})
        assert "LIKE" in sql.upper()
        assert "%F%" in params

    def test_genero_masculino_like_m(self):
        sql, params = build_query({**BASE_FILTROS, "genero": "M"})
        assert "LIKE" in sql.upper()
        assert "%M%" in params

    def test_genero_feminino_palavra(self):
        sql, params = build_query({**BASE_FILTROS, "genero": "FEMININO"})
        assert "%F%" in params

    def test_genero_masculino_palavra(self):
        sql, params = build_query({**BASE_FILTROS, "genero": "MASCULINO"})
        assert "%M%" in params


# ============================================================
# FILTRO DE IDADE
# ============================================================

class TestIdadeFilter:
    def test_idade_padrao_presente(self):
        sql, params = build_query({**BASE_FILTROS, "idade_min": None, "idade_max": None})
        assert "BETWEEN" in sql.upper()
        assert IDADE_MAX_PADRAO in params
        assert IDADE_MIN_PADRAO in params

    def test_idade_customizada(self):
        sql, params = build_query({**BASE_FILTROS, "idade_min": 30, "idade_max": 50})
        assert 50 in params
        assert 30 in params

    def test_idade_min_nunca_abaixo_do_padrao(self):
        # Passar idade_min=5 deve ser corrigido para IDADE_MIN_PADRAO (18)
        sql, params = build_query({**BASE_FILTROS, "idade_min": 5, "idade_max": 60})
        assert IDADE_MIN_PADRAO in params    # 18 deve estar presente
        assert 5 not in params              # 5 não deve entrar

    def test_intervalo_data_nascimento_between(self):
        sql, _ = build_query(BASE_FILTROS)
        assert "data_nascimento" in sql.lower()
        assert "INTERVAL" in sql.upper()
        assert "YEAR" in sql.upper()


# ============================================================
# FILTRO DE EMAIL
# ============================================================

class TestEmailFilter:
    def test_sem_filtro_email_sem_is_null(self):
        sql, _ = build_query({**BASE_FILTROS, "email": "nao_filtrar"})
        assert "IS NOT NULL" not in sql.upper()
        assert "IS NULL" not in sql.upper()

    def test_email_obrigatorio_is_not_null(self):
        sql, _ = build_query({**BASE_FILTROS, "email": "obrigatorio"})
        assert "IS NOT NULL" in sql.upper()

    def test_email_nao_sem_is_null(self):
        # 'nao' = cliente não quer email; mantemos sem filtro para não limitar
        sql, _ = build_query({**BASE_FILTROS, "email": "nao"})
        assert "IS NULL" not in sql.upper()


# ============================================================
# AUSÊNCIA DE SCORE / RENDA
# ============================================================

class TestSemScoreRenda:
    def test_sem_score_no_sql(self):
        sql, params = build_query(BASE_FILTROS)
        assert "score" not in sql.lower()
        assert "SCORE" not in sql.upper()

    def test_sem_renda_no_sql(self):
        sql, params = build_query(BASE_FILTROS)
        assert "renda" not in sql.lower()
        assert "RENDA" not in sql.upper()

    def test_score_filtros_ignorados_silenciosamente(self):
        # Mesmo que alguém passe score_min/max, não deve entrar no SQL
        filtros_com_score = {**BASE_FILTROS, "score_min": 500, "score_max": 900}
        sql, params = build_query(filtros_com_score)
        assert "score" not in sql.lower()
        assert 500 not in params
        assert 900 not in params


# ============================================================
# DESCREVER_FILTROS_DB
# ============================================================

class TestDescreverFiltrosDb:
    def test_retorna_string(self):
        desc = descrever_filtros_db(BASE_FILTROS)
        assert isinstance(desc, str)

    def test_contem_uf(self):
        desc = descrever_filtros_db({**BASE_FILTROS, "ufs": ["PR"]})
        assert "PR" in desc

    def test_contem_cidade_quando_informada(self):
        desc = descrever_filtros_db({**BASE_FILTROS, "cidades": ["CURITIBA"]})
        assert "CURITIBA" in desc

    def test_sem_cidade_nao_aparece(self):
        desc = descrever_filtros_db({**BASE_FILTROS, "cidades": []})
        assert "Cidade" not in desc

    def test_contem_faixa_etaria(self):
        desc = descrever_filtros_db({**BASE_FILTROS, "idade_min": 25, "idade_max": 45})
        assert "25" in desc
        assert "45" in desc

    def test_email_obrigatorio_aparece(self):
        desc = descrever_filtros_db({**BASE_FILTROS, "email": "obrigatorio"})
        assert "mail" in desc.lower()
