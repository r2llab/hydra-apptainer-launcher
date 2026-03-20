# Copyright (c) 2024. All Rights Reserved
from dataclasses import dataclass, field
from typing import Optional

from hydra.core.config_store import ConfigStore
from hydra_plugins.hydra_submitit_launcher.config import SlurmQueueConf


@dataclass
class ApptainerSlurmConf(SlurmQueueConf):
    """
    Extends SlurmQueueConf with Apptainer-specific parameters.
    """

    _target_: str = (
        "hydra_plugins.hydra_apptainer_launcher.apptainer_launcher.ApptainerSlurmLauncher"
    )

    # Path to the Apptainer .sif image file (required)
    apptainer_image: Optional[str] = None

    # Extra arguments passed to `apptainer run`
    apptainer_args: str = "--nv"


# Register in ConfigStore so Hydra discovers it as `hydra/launcher=apptainer`
ConfigStore.instance().store(
    group="hydra/launcher",
    name="apptainer",
    node=ApptainerSlurmConf(),
    provider="hydra-apptainer-launcher",
)
