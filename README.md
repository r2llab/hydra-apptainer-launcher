# Hydra Apptainer Launcher

A custom Hydra launcher plugin that extends [`hydra-submitit-launcher`](https://github.com/facebookresearch/hydra/tree/main/plugins/hydra_submitit_launcher)'s `SlurmLauncher` to run jobs inside an [Apptainer](https://apptainer.org/) container on SLURM clusters.

## How it works

When the `apptainer` launcher is selected, it:

1. Writes a small bash wrapper script to the sweep directory:
   ```bash
   #!/bin/bash
   apptainer run --nv /path/to/image.sif python "$@"
   ```
2. Passes the wrapper path to `submitit` as the Python interpreter override (`python` kwarg).
3. Delegates all SLURM scheduling to the standard `SlurmLauncher`.

## Installation

```bash
pip install hydra-apptainer-launcher
```

Or in editable/development mode:

```bash
git clone <repo-url>
pip install -e hydra-apptainer-launcher/
```

## Usage

Select the launcher via the `hydra/launcher=apptainer` config group override:

```bash
python my_app.py --multirun \
    hydra/launcher=apptainer \
    hydra.launcher.apptainer_image=/path/to/image.sif \
    hydra.launcher.partition=compute \
    param=1,2,3
```

Or set it as the default in your app config:

```yaml
# conf/config.yaml
defaults:
  - override hydra/launcher: apptainer

hydra:
  launcher:
    apptainer_image: /path/to/image.sif
    apptainer_args: "--nv"
    partition: compute
    timeout_min: 60
```

## Configuration reference

All parameters from [`SlurmQueueConf`](https://hydra.cc/docs/plugins/submitit_launcher/) are supported, plus:

| Parameter | Default | Description |
|---|---|---|
| `apptainer_image` | `None` | Path to the `.sif` image file. If `None`, runs without Apptainer. |
| `apptainer_args` | `"--nv"` | Extra arguments passed to `apptainer run`. |

See the [`examples/simple_app/`](examples/simple_app/) directory for a complete working example.
