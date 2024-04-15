# RQ Autoscaler

Automatically scales [RQ](https://github.com/rq/rq) based Kubernetes Deployments based on the number of items in the queue.

## Configuration

The following settings are currently available:

| Setting | Description |
| ------- | ----------- |
| REDIS_URL | The URL of the Redis Server, example: `redis://:mypassword@redis:6379/0` |
| DEPLOYMENT | The namespace and name of the deployment to use, example: `my-namespace/my-deployment` |
| QUEUE | The name of the RQ queue to use, example: `my-queue` |
| MIN_REPLICAS | The minimum number of replicas you want to allow, example: `1` |
| MAX_REPLICAS | The maximum number of replicas you want to allow, example: `100` |
| TASKS_PER_REPLICA | The split of tasks to replicas, uses `queue_length / tasks_per_replica`, example: `10000` |
| INTERVAL | How often to check queue size and perform scaling operations, example `10` |

## Usage

### Via Kustomize/Flux for Kubernetes

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - github.com/cpressland/rq-autoscaler/deploy
namespace: your-namespace
patches:
  - target:
      kind: Deployment
    patch: |
      - op: replace
        path: /spec/template/spec/containers/0/env
        value:
          - name: REDIS_URL
            value: redis://my-redis-server:6379/0
          - name: DEPLOYMENT
            value: my-deployment
          - name: QUEUE
            value: my-queue
          - name: MIN_REPLICAS
            value: "1"
          - name: MAX_REPLICAS
            value: "10"
          - name: TASKS_PER_REPLICA
            value: "10000"
          - name: INTERVAL
            value: "10"
```
