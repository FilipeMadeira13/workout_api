from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.contrib.dependencies import DatabaseDependency
from app.atleta.schemas import AtletaIn, AtletaOut, AtletaSimplificado, AtletaUpdate
from app.atleta.models import AtletaModel
from app.categorias.models import CategoriaModel
from app.centro_treinamento.models import CentroTreinamentoModel

router = APIRouter()


@router.post(
    "/",
    summary="Criar novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def post(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria = (
        (
            await db_session.execute(
                select(CategoriaModel).filter_by(nome=categoria_nome)
            )
        )
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria {categoria_nome} não foi encontrada.",
        )

    centro_treinamento = (
        (
            await db_session.execute(
                select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome)
            )
        )
        .scalars()
        .first()
    )

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O centro de treinamento {centro_treinamento_nome} não foi encontrado.",
        )

    try:
        atleta_out = AtletaOut(
            id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump()
        )

        atleta_model = AtletaModel(
            **atleta_out.model_dump(exclude={"categoria", "centro_treinamento"})
        )
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um usuário com o cpf: {atleta_in.cpf}",
        )
    except Exception:
        await db_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao inserir os dados no banco.",
        )

    return atleta_out


@router.get(
    "/",
    summary="Consultar todos os atletas",
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaOut],
)
async def query(db_session: DatabaseDependency) -> list[AtletaOut]:  # type: ignore
    atletas: list[AtletaOut] = (
        (await db_session.execute(select(AtletaModel))).scalars().all()
    )  # type: ignore

    return [AtletaOut.model_validate(atleta) for atleta in atletas]


@router.get(
    "/simplificado",
    summary="Consultar todos os atletas apenas pelo nome, centro de treinamento e categoria",
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaSimplificado],
)
async def query(db_session: DatabaseDependency) -> list[AtletaSimplificado]:  # type: ignore
    atletas: list[AtletaSimplificado] = (
        (await db_session.execute(select(AtletaModel))).scalars().all()
    )  # type: ignore

    return [AtletaSimplificado.model_validate(atleta) for atleta in atletas]


@router.get(
    "/{id}",
    summary="Consulta um atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:  # type: ignore
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    return atleta


@router.get(
    "/by-name/{nome}",
    summary="Consulta um atleta pelo nome",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query_by_name(nome: str, db_session: DatabaseDependency) -> AtletaOut:  # type: ignore
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(nome=nome)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado pelo nome: {nome}",
        )

    return atleta


@router.get(
    "/by-cpf/{cpf}",
    summary="Consulta um atleta pelo cpf",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query_by_cpf(cpf: str, db_session: DatabaseDependency) -> AtletaOut:  # type: ignore
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(cpf=cpf)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado pelo cpf: {cpf}",
        )

    return atleta


@router.patch(
    "/{id}",
    summary="Editar um atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query(  # type: ignore
    id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.patch(
    "/by-name/{nome}",
    summary="Editar um atleta pelo nome",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query_by_name(  # type: ignore
    nome: str, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(nome=nome)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no nome: {nome}",
        )
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.patch(
    "/by-cpf/{cpf}",
    summary="Editar um atleta pelo cpf",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query_by_cpf(  # type: ignore
    cpf: str, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(cpf=cpf)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no cpf: {cpf}",
        )
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    "/{id}", summary="Deletar um atleta pelo id", status_code=status.HTTP_204_NO_CONTENT
)
async def query(id: UUID4, db_session: DatabaseDependency) -> None:  # type: ignore
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    await db_session.delete(atleta)
    await db_session.commit()


@router.delete(
    "/by-name/{nome}",
    summary="Deletar um atleta pelo nome",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def query_by_name(nome: str, db_session: DatabaseDependency) -> None:  # type: ignore
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(nome=nome)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no nome: {nome}",
        )

    await db_session.delete(atleta)
    await db_session.commit()


@router.delete(
    "/by-cpf/{cpf}",
    summary="Deletar um atleta pelo cpf",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def query_by_cpf(cpf: str, db_session: DatabaseDependency) -> None:  # type: ignore
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(cpf=cpf)))
        .scalars()
        .first()
    )  # type: ignore

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no cpf: {cpf}",
        )

    await db_session.delete(atleta)
    await db_session.commit()
