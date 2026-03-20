import logging
import os
import stat
import sys
from pathlib import Path
from typing import Any, List, Optional, Sequence

import submitit
from hydra.core.singleton import Singleton
from hydra.core.utils import filter_overrides
from hydra_plugins.hydra_submitit_launcher.config import BaseQueueConf
from hydra_plugins.hydra_submitit_launcher.submitit_launcher import SlurmLauncher
from omegaconf import OmegaConf

log = logging.getLogger(__name__)


class ApptainerSlurmLauncher(SlurmLauncher):
    """
    A Hydra launcher that extends the standard SlurmLauncher to support Apptainer.
    It generates a wrapper bash script that invokes Apptainer, and passes it as
    the `python` executable to submitit via the SlurmExecutor constructor.
    """

    def launch(
        self, job_overrides: Sequence[Sequence[str]], initial_job_idx: int
    ) -> Sequence[Any]:
        assert self.config is not None

        num_jobs = len(job_overrides)
        assert num_jobs > 0

        # Pop Apptainer-specific params before they reach submitit
        params = dict(self.params)
        apptainer_image: Optional[str] = params.pop("apptainer_image", None)
        apptainer_args: str = params.pop("apptainer_args", "--nv")

        # Build the wrapper script and resolve the python override
        python_override: Optional[str] = None
        if apptainer_image:
            folder = Path(params["submitit_folder"])
            # Strip any %j / %t submitit tokens for the purpose of mkdir
            folder = Path(str(folder).split("%")[0])
            folder.mkdir(parents=True, exist_ok=True)

            script_path = folder / "apptainer_python_wrapper.sh"
            # Use the host Python executable inside the container so that the
            # pickle format always matches (avoids cross-version TypeError on
            # unpickling). The host Python prefix is bind-mounted into the
            # container via --bind so the same path is valid inside.
            #
            # The project root (parent of hydra_plugins/) is also added to
            # APPTAINERENV_PYTHONPATH, which Apptainer forwards as PYTHONPATH
            # inside the container, so the launcher module remains importable.
            host_python = sys.executable
            package_root = Path(__file__).parent.parent.parent.resolve()
            wrapper_code = (
                "#!/bin/bash\n"
                f'export APPTAINERENV_PYTHONPATH="{package_root}${{PYTHONPATH:+:$PYTHONPATH}}"\n'
                f"apptainer run {apptainer_args} --bind {host_python}:{host_python} "
                f"--bind {Path(host_python).parent.parent}:{Path(host_python).parent.parent} "
                f'{apptainer_image} {host_python} "$@"\n'
            )

            log.info(f"Creating Apptainer wrapper at {script_path}")
            script_path.write_text(wrapper_code)
            script_path.chmod(
                script_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
            )

            python_override = str(script_path.absolute())

        # --- Replicate BaseSubmititLauncher.launch() so we can inject slurm_python
        #     into the AutoExecutor constructor rather than update_parameters(). ---

        # Keys that go to AutoExecutor.__init__() rather than update_parameters()
        specific_init_keys = {"max_num_timeout"}

        init_params: dict = {"folder": params["submitit_folder"]}
        init_params.update(
            **{
                f"{self._EXECUTOR}_{x}": y
                for x, y in params.items()
                if x in specific_init_keys
            }
        )

        # Inject python as a constructor argument (slurm_python) if we have one
        if python_override is not None:
            init_params[f"{self._EXECUTOR}_python"] = python_override

        init_keys = specific_init_keys | {"submitit_folder"}
        executor = submitit.AutoExecutor(cluster=self._EXECUTOR, **init_params)

        # Remaining params go to update_parameters(); non-base ones get the executor prefix
        baseparams = set(OmegaConf.structured(BaseQueueConf).keys())
        update_params = {
            x if x in baseparams else f"{self._EXECUTOR}_{x}": y
            for x, y in params.items()
            if x not in init_keys
        }
        executor.update_parameters(**update_params)

        log.info(
            f"Submitit '{self._EXECUTOR}' sweep output dir : "
            f"{self.config.hydra.sweep.dir}"
        )
        sweep_dir = Path(str(self.config.hydra.sweep.dir))
        sweep_dir.mkdir(parents=True, exist_ok=True)
        if "mode" in self.config.hydra.sweep:
            mode = int(str(self.config.hydra.sweep.mode), 8)
            os.chmod(sweep_dir, mode=mode)

        job_params: List[Any] = []
        for idx, overrides in enumerate(job_overrides):
            idx = initial_job_idx + idx
            lst = " ".join(filter_overrides(overrides))
            log.info(f"\t#{idx} : {lst}")
            job_params.append(
                (
                    list(overrides),
                    "hydra.sweep.dir",
                    idx,
                    f"job_id_for_{idx}",
                    Singleton.get_state(),
                )
            )

        jobs = executor.map_array(self, *zip(*job_params))
        return [j.results()[0] for j in jobs]
