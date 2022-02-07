from pathlib import Path

import docker
from docker.models.containers import Container
from timeeval.adapters import DockerAdapter
from timeeval.adapters.docker import AlgorithmInterface, DATASET_TARGET_PATH, RESULTS_TARGET_PATH, SCORES_FILE_NAME, \
    MODEL_FILE_NAME
from timeeval.data_types import ExecutionType
from timeeval.resource_constraints import GB


class DistDockerAdapter(DockerAdapter):
    def _run_container(self, dataset_path: Path, args: dict) -> Container:
        client = docker.from_env()
        port = args.get("hyper_params", {}).get("local-host").split(":")[-1]

        algorithm_interface = AlgorithmInterface(
            dataInput=(Path(DATASET_TARGET_PATH) / dataset_path.name).absolute(),
            dataOutput=(Path(RESULTS_TARGET_PATH) / SCORES_FILE_NAME).absolute(),
            modelInput=(Path(RESULTS_TARGET_PATH) / MODEL_FILE_NAME).absolute(),
            modelOutput=(Path(RESULTS_TARGET_PATH) / MODEL_FILE_NAME).absolute(),
            executionType=args.get("executionType", ExecutionType.EXECUTE.value),
            customParameters=args.get("hyper_params", {}),
        )

        uid = DockerAdapter._get_uid()
        gid = DockerAdapter._get_gid(self.group)

        if not gid:
            gid = uid
        print(f"Running container '{self.image_name}:{self.tag}' with uid={uid} and gid={gid} privileges in {algorithm_interface.executionType} mode.")

        memory_limit, cpu_limit = self._get_compute_limits(args)
        cpu_shares = int(cpu_limit * 1e9)
        print(f"Restricting container to {cpu_limit} CPUs and {memory_limit / GB:.3f} GB RAM")
        print(str(self._results_path(args, absolute=True)))

        return client.containers.run(
            f"{self.image_name}:{self.tag}",
            f"execute-algorithm '{algorithm_interface.to_json_string()}'",
            volumes={
                str(dataset_path.parent.absolute()): {'bind': DATASET_TARGET_PATH, 'mode': 'ro'},
                str(self._results_path(args, absolute=True)): {'bind': RESULTS_TARGET_PATH, 'mode': 'rw'}
            },
            environment={
                "LOCAL_GID": gid,
                "LOCAL_UID": uid
            },
            mem_swappiness=0,
            mem_limit=memory_limit,
            memswap_limit=memory_limit,
            nano_cpus=cpu_shares,
            detach=True,
            ports={f'{port}/tcp': port}
        )
