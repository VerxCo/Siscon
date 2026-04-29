# Siscon API

Backend Python/FastAPI para gestão de consignatárias, convênios e vínculos.

## Rodar local

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Configure as variáveis:

```powershell
$env:DATABASE_URL="postgresql://postgres.PROJECT_REF:SENHA@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"
$env:JWT_SECRET_KEY="SEU_SUPABASE_JWT_SECRET"
```

Rodar API:

```powershell
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Rodar testes:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Perfis

Usa tabela:

```sql
public.app_user_profiles (
  user_id uuid primary key references auth.users(id),
  email text,
  full_name text,
  role text check (role in ('admin', 'editor', 'viewer')),
  active boolean default true
)
```

Permissões:
- admin: tudo
- editor: cria/edita
- viewer: leitura
