FROM postgres:14

ARG DB_REPL_USER
ARG DB_REPL_PASSWORD
ARG DB_DATABASE

RUN apt update && apt install sed
COPY init.sql /init.sql
RUN sed -i 's/replaceDB_REPL_USER/'"$DB_REPL_USER"'/g' /init.sql
RUN sed -i 's/replaceDB_REPL_PASSWORD/'"$DB_REPL_PASSWORD"'/g' /init.sql
RUN sed -i 's/replaceDB_DATABASE/'"$DB_DATABASE"'/g' /init.sql
RUN mv /init.sql /docker-entrypoint-initdb.d/init.sql


RUN echo "wal_level=replica" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "hot_standby=on" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "max_wal_senders=10" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "max_replication_slots=10" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "hot_standby_feedback=on" >> /usr/share/postgresql/postgresql.conf.sample
RUN echo "log_replication_commands=on" >> /usr/share/postgresql/postgresql.conf.sample
