"""RQ Autoscaler."""

from __future__ import annotations

from math import ceil
from pathlib import Path
from time import sleep

import typer
from kr8s.objects import Deployment
from loguru import logger as log
from redis import Redis
from rq import Queue
from typing_extensions import Annotated

cli = typer.Typer()


def queue_length(redis_url: str, queue: str) -> int:
    """Return the number of tasks on the queue."""
    return len(Queue(queue, connection=Redis.from_url(redis_url)))


def ideal_replica_count(queue_length: int, min_replicas: int, max_replicas: int, tasks_per_replica: int) -> int:
    """Return the ideal number of replicas."""
    replicas = ceil(queue_length / tasks_per_replica)
    if replicas < min_replicas:
        replicas = min_replicas
    elif replicas > max_replicas:
        replicas = max_replicas
    return replicas


@cli.command()
def autoscale(
    redis_url: Annotated[
        str,
        typer.Option(help="The URL of the Redis server", envvar="REDIS_URL"),
    ],
    deployment: Annotated[
        str,
        typer.Option(help="The name of the Kubernetes Deployment to scale", envvar="DEPLOYMENT"),
    ],
    queue: Annotated[str, typer.Option(help="The name of the RQ queue to monitor", envvar="QUEUE")],
    interval: Annotated[int, typer.Option(help="The interval in seconds to check the queue length", envvar="INTERVAL")],
    min_replicas: Annotated[
        int,
        typer.Option(help="The minimum number of replicas to scale to", envvar="MIN_REPLICAS"),
    ],
    max_replicas: Annotated[
        int,
        typer.Option(help="The maximum number of replicas to scale to", envvar="MAX_REPLICAS"),
    ],
    tasks_per_replica: Annotated[int, typer.Option(help="The number of tasks per replica", envvar="TASKS_PER_REPLICA")],
) -> None:
    """Autoscale RQ Workers based on queue size."""
    while True:
        namespace = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read_text()
        rq_length = queue_length(redis_url, queue)
        replicas = ideal_replica_count(rq_length, min_replicas, max_replicas, tasks_per_replica)
        Deployment(deployment, namespace=namespace).scale(replicas)
        log.info(f"Queue Name: {queue}, Queue length: {rq_length}, Deployment Scale: {replicas}")
        sleep(interval)
