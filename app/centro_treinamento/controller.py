from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException, Query
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page, Params  # type: ignore
from fastapi_pagination.ext.sqlalchemy import paginate  # type: ignore

from app.contrib.dependencies import DatabaseDependency
from app.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from app.centro_treinamento.models import CentroTreinamentoModel

router = APIRouter()


@router.post(
    "/",
    summary="Criar novo centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency,
    centro_treinamento_in: CentroTreinamentoIn = Body(...),
) -> CentroTreinamentoOut:
    try:
        centro_treinamento_out = CentroTreinamentoOut(
            id=uuid4(), **centro_treinamento_in.model_dump()
        )
        centro_treinamento_model = CentroTreinamentoModel(
            **centro_treinamento_out.model_dump()
        )

        db_session.add(centro_treinamento_model)
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um centro de treinamento com o nome: {centro_treinamento_in.nome}",
        )
    except Exception:
        await db_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao inserir os dados no banco.",
        )

    return centro_treinamento_out


@router.get(
    "/",
    summary="Consultar todos os centros de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=Page[CentroTreinamentoOut],
)
async def query(db_session: DatabaseDependency, limit: int = Query(10, ge=1, le=100, description="Número de itens por página"), offset: int = Query(0, ge=0, description="Número de itens para pular")) -> Page[CentroTreinamentoOut]:  # type: ignore

    params = Params(limit=limit, offset=offset)

    query = select(CentroTreinamentoModel)

    paginated_results = await paginate(db_session, query, params)

    result_page = Page(
        items=[
            CentroTreinamentoOut.model_validate(item)
            for item in paginated_results.items
        ],
        total=paginated_results.total,
        page=paginated_results.page,
        size=paginated_results.size,
    )

    return result_page


@router.get(
    "/{id}",
    summary="Consulta um centro de treinamento pelo id",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento: CentroTreinamentoOut = (
        (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id)))
        .scalars()
        .first()
    )  # type: ignore

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro de treinamento não encontrado no id: {id}",
        )

    return centro_treinamento
