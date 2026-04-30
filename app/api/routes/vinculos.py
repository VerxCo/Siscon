from fastapi import APIRouter, HTTPException, Security, status

from app.api.deps import require_roles
from app.repositories.vinculo_repository import (
    create_vinculo,
    delete_vinculo,
    get_vinculo_by_id,
    list_vinculos,
    update_vinculo,
)
from app.schemas.vinculo import (
    VinculoCreate,
    VinculoDetail,
    VinculoListItem,
    VinculoUpdate,
)

router = APIRouter(prefix="/vinculos", tags=["vinculos"])


@router.get("", response_model=list[VinculoListItem])
def get_vinculos(_: dict = Security(require_roles("admin", "editor", "viewer"))):
    return list_vinculos()


@router.get("/{vinculo_id}", response_model=VinculoDetail)
def get_vinculo(
    vinculo_id: int,
    _: dict = Security(require_roles("admin", "editor", "viewer")),
):
    vinculo = get_vinculo_by_id(vinculo_id)

    if vinculo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vinculo nao encontrado.",
        )

    return vinculo


@router.post("", response_model=VinculoDetail, status_code=status.HTTP_201_CREATED)
def post_vinculo(
    payload: VinculoCreate,
    _: dict = Security(require_roles("admin", "editor")),
):
    return create_vinculo(payload.model_dump())


@router.put("/{vinculo_id}", response_model=VinculoDetail)
def put_vinculo(
    vinculo_id: int,
    payload: VinculoUpdate,
    _: dict = Security(require_roles("admin", "editor")),
):
    vinculo = update_vinculo(vinculo_id, payload.model_dump())

    if vinculo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vinculo nao encontrado.",
        )

    return vinculo


@router.delete("/{vinculo_id}")
def delete_vinculo_route(
    vinculo_id: int,
    _: dict = Security(require_roles("admin", "editor")),
):
    vinculo = delete_vinculo(vinculo_id)

    if vinculo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vinculo nao encontrado.",
        )

    return vinculo
