# Kubernetes CronJob lab

This lab runs a small containerized job on a local Kubernetes cluster (kind) on a schedule.
It shows how a CronJob gets configuration (ConfigMap), a credential (Secret), and state that
survives between runs (PersistentVolumeClaim).

## What you need

- Docker Desktop (running)
- `kubectl`
- `kind`

## Steps

1. Create the cluster
2. Build the image and load it into the cluster
3. Create the ConfigMap, Secret and PVC
4. Create the CronJob and trigger a run
5. Confirm state persists across runs
6. Clean up
