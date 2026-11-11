# Kubernetes CronJob lab

I built this lab to get hands-on with Kubernetes beyond course material. It runs a small containerized job on a schedule on a local kind cluster, and shows three things a real scheduled job needs:

- configuration from a ConfigMap
- a credential from a Secret
- state that survives between runs, on a PersistentVolumeClaim (PVC)

Then I break it on purpose and record how I found each problem. That part's in [Troubleshooting](#troubleshooting).

## What you need

I ran everything on Windows 11 in PowerShell, with:

- Docker Desktop, with the engine running (Docker client 24.0.6)
- `kubectl` client v1.28.2
- `kind` v0.33.0, which created a node running Kubernetes v1.37.0

> **Version skew:** `kubectl` is only supported within one minor version of the cluster, and mine was far outside that. Everything in this lab still worked, but upgrade `kubectl` before you rely on it (`winget upgrade Kubernetes.kubectl` on Windows).

## What's in the repo

- `app/app.py`: a tiny Python job. It prints a greeting from the ConfigMap, confirms the Secret is set without printing it, and counts its runs in a file on the volume.
- `Dockerfile`: packages the app as the image `lab-job:0.1`.
- `manifests/configmap.yaml`, `manifests/pvc.yaml`, `manifests/cronjob.yaml`: the Kubernetes objects. The CronJob runs every two minutes so you don't wait long to see it work.

## Run it

Run each command on its own line, from the repo root. (PowerShell treats a line with several commands and commas as one command, and fails.)

### 1. Create the cluster

```
kind create cluster --name cronjob-lab
```

### 2. Build the image and load it into the cluster

```
docker build -t lab-job:0.1 .
kind load docker-image lab-job:0.1 --name cronjob-lab
```

kind runs Kubernetes inside Docker containers, so its node can't see images in your local Docker. `kind load` copies the image in. Skip it and the pod can't pull the image.

### 3. Create the ConfigMap, PVC and Secret

```
kubectl apply -f manifests/configmap.yaml -f manifests/pvc.yaml
kubectl create secret generic lab-secret --from-literal=API_TOKEN=demo-not-a-real-secret
```

The token is a dummy value. Never put a real credential in a lab.

### 4. Create the CronJob and trigger a run

You don't have to wait for the schedule. Create a job from the CronJob by hand:

```
kubectl apply -f manifests/cronjob.yaml
kubectl create job --from=cronjob/lab-cron good-1
kubectl logs job/good-1
```

What I got:

```
Greeting: Hello from a ConfigMap
API_TOKEN is set (22 characters; value not printed)
This is run number 1 (state file: /state/runs.txt)
```

If `logs` says the container is still starting, wait a few seconds and run it again. `kubectl get pods` shows the pod as `Completed` when it's done:

```
NAME           READY   STATUS      RESTARTS   AGE
good-1-htm49   0/1     Completed   0          61s
```

### 5. Confirm state survives between runs

Each job runs in a brand-new pod, so the run count only goes up if the volume keeps the file.

```
kubectl create job --from=cronjob/lab-cron good-2
kubectl logs job/good-2
kubectl delete jobs --all
kubectl create job --from=cronjob/lab-cron good-3
kubectl logs job/good-3
```

`good-2` printed run number 2. Then I deleted every job and its pod, and `good-3` still printed:

```
This is run number 3 (state file: /state/runs.txt)
```

The pods are gone; the PVC kept the state.

### 6. Look inside the volume (optional)

To read the state file directly, I ran a throwaway pod that mounts the same PVC and prints the file:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: peek
spec:
  restartPolicy: Never
  containers:
    - name: peek
      image: lab-job:0.1
      imagePullPolicy: IfNotPresent
      command: ["cat", "/state/runs.txt"]
      volumeMounts:
        - name: state
          mountPath: /state
  volumes:
    - name: state
      persistentVolumeClaim:
        claimName: lab-state
```

```
kubectl apply -f peek.yaml
kubectl logs peek
kubectl delete pod peek
```

[TODO: paste what `kubectl logs peek` printed.]

### 7. Clean up

To stop the schedule but keep everything, add `suspend: true` under `spec:` in `manifests/cronjob.yaml` and apply it again. To remove everything:

```
kind delete cluster --name cronjob-lab
```

## Troubleshooting

I broke the lab on purpose to see what each failure looks like and which command points to the cause.

### Wrong image tag

**What I did:** changed the image in `manifests/cronjob.yaml` to `lab-job:9.9`, a tag that doesn't exist, then applied it and ran a job.

```
kubectl apply -f manifests/cronjob.yaml
kubectl create job --from=cronjob/lab-cron broken-1
kubectl get pods
```

**Symptom:** [TODO: the STATUS you saw for `broken-1`, for example `ErrImagePull`, then `ImagePullBackOff`.]

**How I found the cause:** `kubectl describe pod <pod-name>`, using the real pod name from `get pods`. The Events section at the bottom said [TODO: the event message you saw].

**Fix:** set the image back to `lab-job:0.1`, apply, delete `broken-1`, and run a good job. [TODO: confirm what `good-4` printed.]

### Missing Secret

**What I did:** deleted the Secret, then ran a job.

```
kubectl delete secret lab-secret
kubectl create job --from=cronjob/lab-cron nosecret-1
kubectl get pods
```

**Symptom:** the pod never started:

```
NAME               READY   STATUS                       RESTARTS   AGE
nosecret-1-bx7wv   0/1     CreateContainerConfigError   0          10s
```

This is different from the image failure. The image was fine; Kubernetes blocked the container before it started because configuration it needed was missing.

**How I found the cause:** `kubectl describe pod nosecret-1-bx7wv`. [TODO: the event message you saw.]

**Fix:** re-create the Secret, delete the failed job, and run a good job:

```
kubectl create secret generic lab-secret --from-literal=API_TOKEN=demo-not-a-real-secret
kubectl delete job nosecret-1
kubectl create job --from=cronjob/lab-cron good-5
kubectl logs job/good-5
```

[TODO: confirm what `good-5` printed. The failed job never ran the app, so I expected run number 5.]

### Deleting a PVC that's still in use

In an earlier run, I deleted the PVC while jobs that used it still existed. The claim got stuck in `Terminating`, and the next job sat in `Pending` because it couldn't mount a volume. Kubernetes won't remove a claim while any pod still uses it. Delete the jobs first, then the PVC, then re-apply `manifests/pvc.yaml`.

### PowerShell gotchas

- **Several commands on one line fail.** I pasted a list of commands separated by commas, and `kind` read it as one command: `ERROR: unknown shorthand flag: 't' in -t`. Run one command per line.
- **Placeholder names are taken literally.** `kubectl describe pod nosecret-1-...` returned `pods "nosecret-1-..." not found`. Copy the real pod name from `kubectl get pods`.

## What this lab doesn't cover

- It's a single-node cluster on one laptop, not a production setup.
- Images go in with `kind load`, not from a container registry.
- The Secret is only base64-encoded in the cluster. That's not real secret management.
- There's no networking: no Service, no network policy, no traffic between pods.
- My `kubectl` was several versions behind the cluster (see [What you need](#what-you-need)).
