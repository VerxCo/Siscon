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


def delete_consignataria(consignataria_id: int) -> dict | None:
    select_query = '''
        select id, nome, ativo, criado_em::text, atualizado_em::text
        from public.consignatarias
        where id = %s
        limit 1
    '''
    linked_convenios_query = '''
        select distinct convenio_id
        from public.convenio_consignatarias
        where consignataria_id = %s
        order by convenio_id asc
    '''
    delete_vinculos_query = '''
        delete from public.convenio_consignatarias
        where consignataria_id = %s
    '''
    delete_query = '''
        delete from public.consignatarias
        where id = %s
    '''
    orphan_convenio_query = '''
        select 1
        from public.convenio_consignatarias
        where convenio_id = %s
        limit 1
    '''
    delete_convenio_query = '''
        delete from public.convenios
        where id = %s
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(select_query, (consignataria_id,))
            row = cursor.fetchone()

            if row is None:
                return None

            cursor.execute(linked_convenios_query, (consignataria_id,))
            convenio_ids = [linked_row[0] for linked_row in cursor.fetchall()]

            cursor.execute(delete_vinculos_query, (consignataria_id,))
            vinculos_removidos = cursor.rowcount

            cursor.execute(delete_query, (consignataria_id,))
            if cursor.rowcount == 0:
                return None

            convenios_removidos = 0
            for convenio_id in convenio_ids:
                cursor.execute(orphan_convenio_query, (convenio_id,))
                if cursor.fetchone() is None:
                    cursor.execute(delete_convenio_query, (convenio_id,))
                    convenios_removidos += cursor.rowcount

            connection.commit()

    return {
        "message": "Consignataria removida com sucesso.",
        "consignataria": {
            "id": row[0],
            "nome": row[1],
            "ativo": row[2],
            "criado_em": row[3],
            "atualizado_em": row[4],
        },
        "vinculos_removidos": vinculos_removidos,
        "convenios_removidos": convenios_removidos,
    }
