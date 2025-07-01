Sistema de Asistencias UNDAV

- Requisitos

    * Docker
    * Docker Compose

- Levantar el sistema

    * docker compose up --build

- Usar la linea de comandos de MySQL

    * docker exec -it sistema_asistencia-db-1 mysql -uUndav -p123456788 Undav

- Reiniciar contenedores

    * docker compose restart frontend
    * docker compose restart backend