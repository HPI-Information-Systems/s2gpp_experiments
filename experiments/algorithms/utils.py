import os, grp

from timeeval.adapters import DockerAdapter


def get_docker_adapter(image: str, tag: str = "latest") -> DockerAdapter:
    group_name = grp.getgrgid(os.getegid()).gr_name
    return DockerAdapter(
        image_name=image,
        tag=tag,
        skip_pull=True,
        group_privileges=group_name
    )
