from app.db.connection import get_db_connection


def list_vinculos() -> list[dict]:
    query = '''
        select
            cc.id,
            cc.convenio_id,
            cc.consignataria_id,
            cc.produto_nome,
            cc.qtd_servidores,
            cc.cnpj,
            cc.possui_base,
            cc.possui_portal,
            cc.link_portal,
            sa.codigo as status_acesso,
            cc.data_solicitacao::text,
            cc.possui_robo,
            cc.faz_na_amigoz,
            cc.margem_online,
            cc.fonte_aba,
            cc.fonte_linha,
            cc.ativo
        from public.convenio_consignatarias cc
        left join public.status_acesso sa on sa.id = cc.status_acesso_id
        order by cc.id desc
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "convenio_id": row[1],
            "consignataria_id": row[2],
            "produto_nome": row[3],
            "qtd_servidores": row[4],
            "cnpj": row[5],
            "possui_base": row[6],
            "possui_portal": row[7],
            "link_portal": row[8],
            "status_acesso": row[9],
            "data_solicitacao": row[10],
            "possui_robo": row[11],
            "faz_na_amigoz": row[12],
            "margem_online": row[13],
            "fonte_aba": row[14],
            "fonte_linha": row[15],
            "ativo": row[16],
        }
        for row in rows
    ]


def get_vinculo_by_id(vinculo_id: int) -> dict | None:
    query = '''
        select
            cc.id, cc.convenio_id, cc.consignataria_id, cc.produto_nome,
            cc.qtd_servidores, cc.cnpj, cc.possui_base, cc.possui_portal,
            cc.link_portal, sa.codigo as status_acesso, cc.status_acesso_id,
            cc.data_solicitacao::text, cc.possui_robo, cc.faz_na_amigoz,
            cc.margem_online, cc.fonte_aba, cc.fonte_linha, cc.observacao, cc.ativo
        from public.convenio_consignatarias cc
        left join public.status_acesso sa on sa.id = cc.status_acesso_id
        where cc.id = %s
        limit 1
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (vinculo_id,))
            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "convenio_id": row[1],
        "consignataria_id": row[2],
        "produto_nome": row[3],
        "qtd_servidores": row[4],
        "cnpj": row[5],
        "possui_base": row[6],
        "possui_portal": row[7],
        "link_portal": row[8],
        "status_acesso": row[9],
        "status_acesso_id": row[10],
        "data_solicitacao": row[11],
        "possui_robo": row[12],
        "faz_na_amigoz": row[13],
        "margem_online": row[14],
        "fonte_aba": row[15],
        "fonte_linha": row[16],
        "observacao": row[17],
        "ativo": row[18],
    }


def create_vinculo(data: dict) -> dict:
    query = '''
        insert into public.convenio_consignatarias (
            convenio_id, consignataria_id, produto_nome, qtd_servidores,
            cnpj, possui_base, possui_portal, link_portal, fonte_aba,
            fonte_linha, status_acesso_id, data_solicitacao, possui_robo,
            faz_na_amigoz, margem_online, observacao, ativo
        )
        values (
            %(convenio_id)s, %(consignataria_id)s, %(produto_nome)s,
            %(qtd_servidores)s, %(cnpj)s, %(possui_base)s, %(possui_portal)s,
            %(link_portal)s, %(fonte_aba)s, %(fonte_linha)s,
            %(status_acesso_id)s, %(data_solicitacao)s, %(possui_robo)s,
            %(faz_na_amigoz)s, %(margem_online)s, %(observacao)s, %(ativo)s
        )
        returning id
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, data)
            row = cursor.fetchone()
            connection.commit()

    return get_vinculo_by_id(row[0])


def update_vinculo(vinculo_id: int, data: dict) -> dict | None:
    data = {**data, "id": vinculo_id}

    query = '''
        update public.convenio_consignatarias
        set
            convenio_id = %(convenio_id)s,
            consignataria_id = %(consignataria_id)s,
            produto_nome = %(produto_nome)s,
            qtd_servidores = %(qtd_servidores)s,
            cnpj = %(cnpj)s,
            possui_base = %(possui_base)s,
            possui_portal = %(possui_portal)s,
            link_portal = %(link_portal)s,
            fonte_aba = %(fonte_aba)s,
            fonte_linha = %(fonte_linha)s,
            status_acesso_id = %(status_acesso_id)s,
            data_solicitacao = %(data_solicitacao)s,
            possui_robo = %(possui_robo)s,
            faz_na_amigoz = %(faz_na_amigoz)s,
            margem_online = %(margem_online)s,
            observacao = %(observacao)s,
            ativo = %(ativo)s,
            atualizado_em = now()
        where id = %(id)s
        returning id
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, data)
            row = cursor.fetchone()
            connection.commit()

    if row is None:
        return None

    return get_vinculo_by_id(row[0])


def delete_vinculo(vinculo_id: int) -> dict | None:
    select_query = '''
        select
            cc.id, cc.convenio_id, cc.consignataria_id, cc.produto_nome,
            cc.qtd_servidores, cc.cnpj, cc.possui_base, cc.possui_portal,
            cc.link_portal, sa.codigo as status_acesso, cc.status_acesso_id,
            cc.data_solicitacao::text, cc.possui_robo, cc.faz_na_amigoz,
            cc.margem_online, cc.fonte_aba, cc.fonte_linha, cc.observacao, cc.ativo
        from public.convenio_consignatarias cc
        left join public.status_acesso sa on sa.id = cc.status_acesso_id
        where cc.id = %s
        limit 1
    '''
    delete_query = '''
        delete from public.convenio_consignatarias
        where id = %s
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(select_query, (vinculo_id,))
            row = cursor.fetchone()

            if row is None:
                return None

            cursor.execute(delete_query, (vinculo_id,))
            if cursor.rowcount == 0:
                return None

            connection.commit()

    return {
        "message": "Vinculo removido com sucesso.",
        "vinculo": {
            "id": row[0],
            "convenio_id": row[1],
            "consignataria_id": row[2],
            "produto_nome": row[3],
            "qtd_servidores": row[4],
            "cnpj": row[5],
            "possui_base": row[6],
            "possui_portal": row[7],
            "link_portal": row[8],
            "status_acesso": row[9],
            "status_acesso_id": row[10],
            "data_solicitacao": row[11],
            "possui_robo": row[12],
            "faz_na_amigoz": row[13],
            "margem_online": row[14],
            "fonte_aba": row[15],
            "fonte_linha": row[16],
            "observacao": row[17],
            "ativo": row[18],
        },
    }
