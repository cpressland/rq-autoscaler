"""RQ Autoscaler main module."""
from __future__ import annotations

from math import ceil

from kr8s.objects import Deployment
from loguru import logger
from pydantic import RedisDsn
from pydantic_settings import BaseSettings
from redis import Redis
from rq import Queue


class Settings(BaseSettings):
    """Settings for RQ Autoscaler."""

    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")
    deployment: str
    queue: str
    min_replicas: int
    max_replicas: int
    tasks_per_replica: int


settings = Settings()


class Autoscaler:
    """RQ Autoscaler."""

    def __init__(self) -> None:
        """Initialize RQ Autoscaler."""
        self.redis = Redis.from_url(str(settings.redis_url))
        self.deployment_namespace, self.deployment_name = settings.deployment.split("/")
        self.queue_name = settings.queue
        self.min_replicas = settings.min_replicas
        self.max_replicas = settings.max_replicas
        self.tasks_per_replica = settings.tasks_per_replica

    def get_queue_length(self) -> int:
        """Return the number of tasks on the queue."""
        queue_length = len(Queue(self.queue_name, connection=self.redis))
        logger.info(f"Queue Name: {self.queue_name}, Queue Length: {queue_length}")
        return queue_length

    def determine_replica_count(self) -> int:
        """Return the ideal number of replicas."""
        queue_length = self.get_queue_length()
        replicas = ceil(queue_length / self.tasks_per_replica)
        if replicas < self.min_replicas:
            replicas = self.min_replicas
        elif replicas > self.max_replicas:
            replicas = self.max_replicas
        logger.info(f"Ideal Replica Count: {replicas}")
        return replicas

    def run(self) -> None:
        """Run the autoscaler."""
        replicas = self.determine_replica_count()
        deployment = Deployment(self.deployment_name, namespace=self.deployment_namespace)
        deployment.scale(replicas)


def cli() -> None:
    """Run the autoscaler from CLI."""
    Autoscaler().run()
