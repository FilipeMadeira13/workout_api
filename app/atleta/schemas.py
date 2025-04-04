from pydantic import Field, PositiveFloat
from typing import Annotated, Optional

from app.contrib.schemas import BaseSchema, OutMixin
from app.categorias.schemas import CategoriaIn
from app.centro_treinamento.schemas import CentroTreinamentoAtleta


class Atleta(BaseSchema):
    nome: Annotated[
        str, Field(description="Nome do atleta", examples=["João"], max_length=50)
    ]
    cpf: Annotated[
        str, Field(description="CPF do atleta", examples=["12345678900"], max_length=11)
    ]
    idade: Annotated[int, Field(description="Idade do atleta", examples=[28])]
    peso: Annotated[PositiveFloat, Field(description="Peso do atleta", examples=[79.0])]
    altura: Annotated[
        PositiveFloat, Field(description="Altura do atleta", examples=[1.87])
    ]
    sexo: Annotated[
        str, Field(description="Sexo do atleta", examples=["M"], max_length=1)
    ]
    categoria: Annotated[CategoriaIn, Field(description="Categoria do atleta")]
    centro_treinamento: Annotated[
        CentroTreinamentoAtleta, Field(description="Centro de treinamento do atleta")
    ]


class AtletaIn(Atleta):
    pass


class AtletaOut(Atleta, OutMixin):
    pass


class AtletaUpdate(BaseSchema):
    nome: Annotated[
        Optional[str],
        Field(None, description="Nome do atleta", examples=["João"], max_length=50),
    ]
    idade: Annotated[
        Optional[int], Field(None, description="Idade do atleta", examples=[28])
    ]
