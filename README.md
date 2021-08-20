

## Principais tecnologias usadas 
- **Infra**: docker, docker-compose, pipenv
- **DB**: postgres
- **Backend**: Django, Django Rest Framework
- **CI**: Github Actions.
- **Test**: coverage
- **Lint**: pycodestyle, pylint, pylint_django
- **Consulta**: Requests



## Instalação

O Projeto possui docker e docker-compose, para ser instalado deve seguir o compose que se encontra na raiz do projeto
Nele se encontra uma configuração do projeto em Django e um Banco de Dados em Postgres

### OBS: So esta com .env no repositório para facilitar a instala.

```bash 
    docker-compose build
    docker-compose up
```

## Rotas

|Verb  |URI Pattern              
:----:|-------------------------|
| POST  | /prescriptions

## Uso/Exemplo

Realize um Post para o endpoint /prescriptions 
```bash
curl -X POST \
  http://localhost:8000/prescriptions \
  -H 'Content-Type: application/json' \
  -d '{
  "clinic": {
    "id": 1
  },
  "physician": {
    "id": 1
  },
  "patient": {
    "id": 1
  },
  "text": "Dipirona 1x ao dia"
}'
```

  
## Executar os Testes

Para executar os testes com docker-compose

```bash
  docker-compose run django python manage.py test
```

  
## Relacionado


[Página do Desafio](https://github.com/iclinic/iclinic-python-challenge)

  