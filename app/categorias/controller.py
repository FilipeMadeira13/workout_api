from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException, Query
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page, Params  # type: ignore
from fastapi_pagination.ext.sqlalchemy import paginate  # type: ignore

from app.contrib.dependencies import DatabaseDependency
from app.categorias.schemas import CategoriaIn, CategoriaOut
from app.categorias.models import CategoriaModel

router = APIRouter()


@router.post(
    "/",
    summary="Criar nova categoria",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
)
async def post(
    db_session: DatabaseDependency, categoria_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    try:
        categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
        categoria_model = CategoriaModel(**categoria_out.model_dump())

        db_session.add(categoria_model)
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe uma categoria com o nome: {categoria_in.nome}",
        )
    except Exception:
        await db_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao inserir os dados no banco.",
        )

    return categoria_out


@router.get(
    "/",
    summary="Consultar todas as categorias",
    status_code=status.HTTP_200_OK,
    response_model=Page[CategoriaOut],
)
async def query(db_session: DatabaseDependency, limit: int = Query(10, ge=1, le=100, description="Número de itens por página"), offset: int = Query(0, ge=0, description="Número de itens para pular")) -> Page[CategoriaOut]:  # type: ignore

    params = Params(limit=limit, offset=offset)

    query = select(CategoriaModel)

    paginated_results = await paginate(db_session, query, params)

    result_page = Page(
        items=[CategoriaOut.model_validate(item) for item in paginated_results.items],
        total=paginated_results.total,
        page=paginated_results.page,
        size=paginated_results.size,
    )

    return result_page


@router.get(
    "/{id}",
    summary="Consulta uma categoria pelo id",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        (await db_session.execute(select(CategoriaModel).filter_by(id=id)))
        .scalars()
        .first()
    )  # type: ignore

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrada no id: {id}",
        )

    return categoria
