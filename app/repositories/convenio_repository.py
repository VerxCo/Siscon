from app.db.connection import get_db_connection


def list_convenios() -> list[dict]:
    query = '''
        select id, nome, nome_normalizado, ativo
        from public.convenios
        order by nome asc
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    return [
        {"id": row[0], "nome": row[1], "nome_normalizado": row[2], "ativo": row[3]}
        for row in rows
    ]


def get_convenio_by_id(convenio_id: int) -> dict | None:
    query = '''
        select id, nome, nome_normalizado, ativo, criado_em::text, atualizado_em::text
        from public.convenios
        where id = %s
        limit 1
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (convenio_id,))
            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "nome_normalizado": row[2],
        "ativo": row[3],
        "criado_em": row[4],
        "atualizado_em": row[5],
    }


def create_convenio(data: dict) -> dict:
    query = '''
        insert into public.convenios (nome, nome_normalizado, ativo)
        values (%s, %s, %s)
        returning id, nome, nome_normalizado, ativo, criado_em::text, atualizado_em::text
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (data["nome"], data["nome_normalizado"], data["ativo"]))
            row = cursor.fetchone()
            connection.commit()

    return {
        "id": row[0],
        "nome": row[1],
        "nome_normalizado": row[2],
        "ativo": row[3],
        "criado_em": row[4],
        "atualizado_em": row[5],
    }


def update_convenio(convenio_id: int, data: dict) -> dict | None:
    query = '''
        update public.convenios
        set nome = %s, nome_normalizado = %s, ativo = %s, atualizado_em = now()
        where id = %s
        returning id, nome, nome_normalizado, ativo, criado_em::text, atualizado_em::text
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (data["nome"], data["nome_normalizado"], data["ativo"], convenio_id),
            )
            row = cursor.fetchone()
            connection.commit()

    if row is None:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "nome_normalizado": row[2],
        "ativo": row[3],
        "criado_em": row[4],
        "atualizado_em": row[5],
    }
