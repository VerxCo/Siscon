from app.db.connection import get_db_connection


def list_consignatarias() -> list[dict]:
    query = '''
        select id, nome, ativo
        from public.consignatarias
        order by nome asc
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    return [{"id": row[0], "nome": row[1], "ativo": row[2]} for row in rows]


def get_consignataria_by_id(consignataria_id: int) -> dict | None:
    query = '''
        select id, nome, ativo, criado_em::text, atualizado_em::text
        from public.consignatarias
        where id = %s
        limit 1
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (consignataria_id,))
            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "ativo": row[2],
        "criado_em": row[3],
        "atualizado_em": row[4],
    }


def create_consignataria(data: dict) -> dict:
    query = '''
        insert into public.consignatarias (nome, ativo)
        values (%s, %s)
        returning id, nome, ativo, criado_em::text, atualizado_em::text
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (data["nome"], data["ativo"]))
            row = cursor.fetchone()
            connection.commit()

    return {
        "id": row[0],
        "nome": row[1],
        "ativo": row[2],
        "criado_em": row[3],
        "atualizado_em": row[4],
    }


def update_consignataria(consignataria_id: int, data: dict) -> dict | None:
    query = '''
        update public.consignatarias
        set nome = %s, ativo = %s, atualizado_em = now()
        where id = %s
        returning id, nome, ativo, criado_em::text, atualizado_em::text
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (data["nome"], data["ativo"], consignataria_id))
            row = cursor.fetchone()
            connection.commit()

    if row is None:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "ativo": row[2],
        "criado_em": row[3],
        "atualizado_em": row[4],
    }
