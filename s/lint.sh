#!/usr/bin/env bash

mypy .
black --check .
ruff check .
