# Workout API

Desafio feito pela DIO no eu tive que realizar as segunites tarefas:

```
- adicionar query parameters nos endpoints
    - atleta
        - nome
        - cpf
- customizar response de retorno de endpoints
    - get all
        - atleta
            - nome
            - centro_treinamento
            - categoria
- Manipular exceção de integridade dos dados em cada módulo/tabela
    - sqlalchemy.exc.IntegrityError e devolver a seguinte mensagem: “Já existe um atleta cadastrado com o cpf: x”
    - status_code: 303
- Adicionar paginação utilizando a lib: fastapi-pagination
    - limit e offset
```

## Descrição

Esta API fornece um sistema de gerenciamento para atletas, categorias e centros de treinamento, permitindo o cadastro, consulta, atualização e remoção de informações relacionadas a treinamentos. Desenvolvida com FastAPI e SQLAlchemy, oferece endpoints RESTful com suporte a paginação e tratamento robusto de erros.

## Funcionalidades

- Gerenciamento completo de atletas (CRUD)
- Associação de atletas a categorias e centros de treinamento
- Validação de dados com Pydantic
- Tratamento de exceções para integridade de dados
- Paginação de resultados com limit e offset
- Respostas otimizadas para consultas frequentes

## Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web de alta performance
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para interação com banco de dados
- [Pydantic](https://docs.pydantic.dev/) - Validação de dados e serialização
- [Uvicorn](https://www.uvicorn.org/) - Servidor ASGI para execução da aplicação

## Execução da API

Para executar o projeto, utilizei a pyenv, com a versão 3.11.4 do python para o ambiente virtual.

Caso opte por usar pyenv, após instalar, execute:
```
pyenv virtualenv 3.11.4 workoutapi
pyenv activate workoutapi
pip install -r requirements.txt
```

Para subir o banco de dados, caso não tenha o docker-compose instalado, faça a instalação e logo em seguida, execute:
```
docker-compose up -d
```

Para criar uma migration nova, execute:
```
make create-migrations d="nome_da_migration"
```

Para criar o banco de dados, execute:
```
make run-migrations
```

## API

Para subir a API, execute:
```
make run
```