from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_roles
from app.repositories.convenio_repository import (
    create_convenio,
    get_convenio_by_id,
    list_convenios,
    update_convenio,
)
from app.schemas.convenio import (
    ConvenioCreate,
    ConvenioDetail,
    ConvenioListItem,
    ConvenioUpdate,
)

router = APIRouter(prefix="/convenios", tags=["convenios"])


@router.get("", response_model=list[ConvenioListItem])
def get_convenios(_: dict = Depends(require_roles("admin", "editor", "viewer"))):
    return list_convenios()


@router.get("/{convenio_id}", response_model=ConvenioDetail)
def get_convenio(
    convenio_id: int,
    _: dict = Depends(require_roles("admin", "editor", "viewer")),
):
    convenio = get_convenio_by_id(convenio_id)

    if convenio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convenio nao encontrado.",
        )

    return convenio


@router.post("", response_model=ConvenioDetail, status_code=status.HTTP_201_CREATED)
def post_convenio(
    payload: ConvenioCreate,
    _: dict = Depends(require_roles("admin", "editor")),
):
    return create_convenio(payload.model_dump())


@router.put("/{convenio_id}", response_model=ConvenioDetail)
def put_convenio(
    convenio_id: int,
    payload: ConvenioUpdate,
    _: dict = Depends(require_roles("admin", "editor")),
):
    convenio = update_convenio(convenio_id, payload.model_dump())

    if convenio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convenio nao encontrado.",
        )

    return convenio
