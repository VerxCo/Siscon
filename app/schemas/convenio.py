from pydantic import BaseModel, Field


class ConvenioListItem(BaseModel):
    id: int
    nome: str
    nome_normalizado: str
    ativo: bool


class ConvenioDetail(BaseModel):
    id: int
    nome: str
    nome_normalizado: str
    ativo: bool
    criado_em: str | None = None
    atualizado_em: str | None = None


class ConvenioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    nome_normalizado: str = Field(min_length=2, max_length=255)
    ativo: bool = True


class ConvenioUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    nome_normalizado: str = Field(min_length=2, max_length=255)
    ativo: bool = True
