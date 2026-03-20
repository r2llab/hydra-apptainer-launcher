# Simple Hydra Apptainer Example

This example demonstrates how to use the `hydra-apptainer-launcher` to run a Hydra application inside an Apptainer container on a SLURM cluster.

## Prerequisites

-   A SLURM-managed cluster with Apptainer installed.
-   `hydra-apptainer-launcher` installed in your Python environment.

## Setup

1.  **Build the Apptainer image**:
    Use the provided `image.def` to build the container image:
    ```bash
    apptainer build my_env.sif image.def
    ```

2.  **Configure the application**:
    Edit `conf/config.yaml` and set `hydra.launcher.apptainer_image` to the absolute path of your `my_env.sif` file.

## Running the Example

Submit a multirun job to SLURM:

```bash
python my_app.py --multirun params.a=1,2,3
```

Hydra will:
1.  Initialize the `ApptainerSlurmLauncher`.
2.  Create a wrapper script that invokes `apptainer run my_env.sif python ...`.
3.  Submit the job to SLURM via `sbatch`.
