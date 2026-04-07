# Configuração de Credenciais do Banco

## Arquivo Seguro: `config_db.py`

As credenciais do banco de dados MySQL foram movidas para um arquivo separado e seguro chamado `config_db.py`.

### Por que separado?

- **Segurança**: Evita que credenciais sejam versionadas no Git (arquivo ignorado pelo `.gitignore`).
- **Flexibilidade**: Permite configurações diferentes por ambiente (desenvolvimento, produção).
- **Isolamento**: Credenciais não misturadas com código de negócio.

### Como configurar

1. **Edite o arquivo `config_db.py`**:
   ```python
   DB_HOST = "seu_host_mysql"      # Ex: "localhost" ou "db.contatus.com"
   DB_USER = "seu_usuario"         # Nome do usuário MySQL
   DB_PASSWORD = "sua_senha_real"  # SENHA REAL — ALTERE IMEDIATAMENTE
   DB_NAME = "latest_contacts"     # Nome do banco (provavelmente já correto)
   DB_PORT = 3306                  # Porta MySQL (padrão: 3306)
   ```

2. **Teste a conexão**:
   ```bash
   python -c "from config_db import DB_CONFIG; print('Credenciais carregadas com sucesso')"
   ```

3. **Execute a aplicação**:
   ```bash
   python app.py
   ```

### Validações de Segurança

- O arquivo inclui uma validação que impede execução com senha padrão.
- Se `DB_PASSWORD == "senha"`, a aplicação falha ao iniciar com erro claro.

### Permissões Recomendadas (Windows)

- Defina o arquivo como **somente leitura** para o usuário que executa a aplicação.
- Evite compartilhar o arquivo por e-mail ou armazenamento não seguro.

### Exemplo de Uso em Código

```python
from config_db import DB_CONFIG
import mysql.connector

conn = mysql.connector.connect(**DB_CONFIG)
```

---

**IMPORTANTE**: Nunca commite `config_db.py` no Git. Ele está listado no `.gitignore` para prevenir acidentes.