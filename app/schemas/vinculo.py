from pydantic import BaseModel


class VinculoListItem(BaseModel):
    id: int
    convenio_id: int
    consignataria_id: int
    produto_nome: str | None = None
    status_acesso: str | None = None
    qtd_servidores: int | None = None
    cnpj: str | None = None
    possui_base: bool | None = None
    possui_portal: bool | None = None
    link_portal: str | None = None
    data_solicitacao: str | None = None
    possui_robo: bool | None = None
    faz_na_amigoz: bool | None = None
    margem_online: bool | None = None
    fonte_aba: str | None = None
    fonte_linha: int | None = None
    ativo: bool


class VinculoDetail(BaseModel):
    id: int
    convenio_id: int
    consignataria_id: int
    produto_nome: str | None = None
    qtd_servidores: int | None = None
    cnpj: str | None = None
    possui_base: bool | None = None
    possui_portal: bool | None = None
    link_portal: str | None = None
    status_acesso: str | None = None
    status_acesso_id: int | None = None
    data_solicitacao: str | None = None
    possui_robo: bool | None = None
    faz_na_amigoz: bool | None = None
    margem_online: bool | None = None
    fonte_aba: str | None = None
    fonte_linha: int | None = None
    observacao: str | None = None
    ativo: bool


class VinculoCreate(BaseModel):
    convenio_id: int
    consignataria_id: int
    produto_nome: str | None = None
    qtd_servidores: int | None = None
    cnpj: str | None = None
    possui_base: bool | None = None
    possui_portal: bool | None = None
    link_portal: str | None = None
    fonte_aba: str | None = None
    fonte_linha: int | None = None
    status_acesso_id: int | None = None
    data_solicitacao: str | None = None
    possui_robo: bool | None = None
    faz_na_amigoz: bool | None = None
    margem_online: bool | None = None
    observacao: str | None = None
    ativo: bool = True


class VinculoUpdate(VinculoCreate):
    pass
