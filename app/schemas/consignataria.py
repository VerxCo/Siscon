from pydantic import BaseModel, Field


class ConsignatariaListItem(BaseModel):
    id: int
    nome: str
    ativo: bool


class ConsignatariaDetail(BaseModel):
    id: int
    nome: str
    ativo: bool
    criado_em: str | None = None
    atualizado_em: str | None = None


class ConsignatariaCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    ativo: bool = True


class ConsignatariaUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    ativo: bool = True
