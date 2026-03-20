import hydra
import os
import socket
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="conf", config_name="config", version_base="1.1")
def my_app(cfg: DictConfig) -> None:
    print(f"Running on host: {socket.gethostname()}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Configuration:\n{OmegaConf.to_yaml(cfg)}")
    
    # Simulate some work
    result = cfg.params.a + cfg.params.b
    print(f"Result of {cfg.params.a} + {cfg.params.b} = {result}")

if __name__ == "__main__":
    my_app()
