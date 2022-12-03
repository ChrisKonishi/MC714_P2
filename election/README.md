# Algoritmo de Eleição de Líder em anel

- Implementado como um servidor HTTP em Flask, executado em diferente containers Docker

## Requisitos
Docker e docker-compose instalados

## Build
```bash
make build
```

## Executando

- Defina no docker-compose.yml a quantidade de clientes que fazem parte da rede
  - my_id e o número do serviço devem ser coerentes, o programa assume que os serviços são numerados de 1 a n_clients
  - Mapeie uma porta distinta por serviço
- Defina em .env a quantidade de serviços em n_clients e o coordenador (líder) inicial

```bash
docker-compose up
```

- Para "matar" um dos serviços, faça uma HTTP request para o serviço, no endpoint /kill
Ex:

```bash
curl http://localhost:8081/kill
```