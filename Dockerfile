FROM docker.io/python:3.12 as build
WORKDIR /build
ADD . .
RUN pip install poetry
RUN poetry build

FROM docker.io/python:3.12-slim
WORKDIR /app
COPY --from=build /build/dist/*.whl .
RUN pip install *.whl && rm *.whl

CMD ["rq-autoscaler"]
