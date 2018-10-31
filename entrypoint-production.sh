#!/usr/bin/env bash

set -e

gunicorn pdf_microservice.server:app --bind=${HOST}:${PORT}
