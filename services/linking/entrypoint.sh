#!/bin/bash
# Set umask so all files created at runtime are world-writable.
# UID/GID matching is handled by docker-compose (user: "${UID}:${GID}"),
# so there is no need to create users or chown anything here.
umask 000
exec "$@"
