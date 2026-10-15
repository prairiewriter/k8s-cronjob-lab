# Kubernetes CronJob lab

<!-- TODO: one or two sentences, in your own words: what this lab is and who it's for. -->

This lab runs a small containerized job on a local Kubernetes cluster (kind) on a schedule.
It shows how a CronJob gets configuration (ConfigMap), a credential (Secret), and state that
survives between runs (PersistentVolumeClaim).

## What you need

- Docker Desktop (running)
- `kubectl`
- `kind`

<!-- TODO: add the versions you actually used, from `docker version`, `kubectl version --client`, `kind version`. -->

## Steps

<!-- TODO: write each step from what you actually ran. For every step include:
     the command, what you expect to see, and the output you got (trim it, don't invent it). -->

1. Create the cluster
2. Build the image and load it into the cluster
3. Create the ConfigMap, Secret and PVC
4. Create the CronJob and trigger a run
5. Confirm state persists across runs
6. Clean up

## Troubleshooting

<!-- TODO: for each failure you provoked on purpose, record: what you did, the symptom,
     the command that revealed the cause, and the fix. -->

## What this lab doesn't cover

<!-- TODO: be specific and honest, for example: single-node local cluster, no registry, no real secret management. -->
