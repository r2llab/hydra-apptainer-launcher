# Hydra Apptainer Launcher

A custom Hydra launcher that extends `SlurmLauncher` from `hydra-submitit-launcher` to support running jobs inside Apptainer containers on SLURM clusters.

## Installation

```bash
pip install -e .
```

## Usage

In your Hydra configuration, select the `apptainer` launcher:

```yaml
defaults:
  - override hydra/launcher: apptainer

hydra:
  launcher:
    apptainer_image: /path/to/your/image.sif
    apptainer_args: "--nv --bind /data"
    # SlurmLauncher parameters
    timeout_min: 60
    partition: compute
```
