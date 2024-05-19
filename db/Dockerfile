FROM postgres:14

ENV POSTGRES_PASSWORD="Qq12345"
ENV POSTGRES_DB="bot_database"
ENV POSTGRES_USER="postgres"

ENV DB_REPL_USER="repl_user"
ENV DB_REPL_PASSWORD="repl_user"
ENV DB_REPL_HOST="192.168.0.92"
ENV DB_PORT="5432"
ENV RM_PORT="5433"

COPY init.sql /docker-entrypoint-initdb.d/

RUN apt-get update && \
    apt-get install -y openssh-server && \
    sed -i "s|\${DB_REPL_USER}|${DB_REPL_USER}|g" /docker-entry-point-initdb.d/init.sql && \
    sed "s|\${DB_REPL_PASSWORD}|${DB_REPL_PASSWORD}|g" /docker-entry-point-initdb.d/init.sql && \
    useradd --create-home --shell /bin/bash user -p "$(openssl passwd -1 user)"

EXPOSE ${DB_PORT}
