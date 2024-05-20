FROM postgres:14

ARG DB_REPL_USER
ARG POSTGRES_PASSWORD

RUN echo "#!/bin/bash" > /usr/local/bin/init.sh && \
    echo "rm -rf /var/lib/postgresql/data/*" >> /usr/local/bin/init.sh && \
    echo "until PGPASSWORD=\${POSTGRES_PASSWORD} pg_basebackup --pgdata=/var/lib/postgresql/data --host=\${POSTGRES_HOST} --username=\${DB_REPL_USER}; do" >> /usr/local/bin/init.sh && \
    echo "  echo 'Waiting for primary to connect...'" >> /usr/local/bin/init.sh && \
    echo "  echo 'Replica not ready, trying again...'" >> /usr/local/bin/init.sh && \
    echo "  sleep 1" >> /usr/local/bin/init.sh && \
    echo "done" >> /usr/local/bin/init.sh && \
    echo "echo 'Backup done, starting replica...'" >> /usr/local/bin/init.sh && \
    echo "chown -R postgres:postgres /var/lib/postgresql/data" >> /usr/local/bin/init.sh && \
    echo "chmod 700 /var/lib/postgresql/data" >> /usr/local/bin/init.sh && \
    echo "su - postgres -c '/usr/lib/postgresql/14/bin/postgres -D /var/lib/postgresql/data'" >> /usr/local/bin/init.sh
    
RUN chmod +x /usr/local/bin/init.sh

CMD ["/usr/local/bin/init.sh"]

CMD ["postgres"]
