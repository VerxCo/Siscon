from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_roles
from app.repositories.consignataria_repository import (
    create_consignataria,
    get_consignataria_by_id,
    list_consignatarias,
    update_consignataria,
)
from app.schemas.consignataria import (
    ConsignatariaCreate,
    ConsignatariaDetail,
    ConsignatariaListItem,
    ConsignatariaUpdate,
)

router = APIRouter(prefix="/consignatarias", tags=["consignatarias"])


@router.get("", response_model=list[ConsignatariaListItem])
def get_consignatarias(_: dict = Depends(require_roles("admin", "editor", "viewer"))):
    return list_consignatarias()


@router.get("/{consignataria_id}", response_model=ConsignatariaDetail)
def get_consignataria(
    consignataria_id: int,
    _: dict = Depends(require_roles("admin", "editor", "viewer")),
):
    consignataria = get_consignataria_by_id(consignataria_id)

    if consignataria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consignataria nao encontrada.",
        )

    return consignataria


@router.post("", response_model=ConsignatariaDetail, status_code=status.HTTP_201_CREATED)
def post_consignataria(
    payload: ConsignatariaCreate,
    _: dict = Depends(require_roles("admin", "editor")),
):
    return create_consignataria(payload.model_dump())


@router.put("/{consignataria_id}", response_model=ConsignatariaDetail)
def put_consignataria(
    consignataria_id: int,
    payload: ConsignatariaUpdate,
    _: dict = Depends(require_roles("admin", "editor")),
):
    consignataria = update_consignataria(consignataria_id, payload.model_dump())

    if consignataria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consignataria nao encontrada.",
        )

    return consignataria
