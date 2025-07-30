import docker, docker.errors
import os, subprocess
from typing import List, Optional

class EntrypointResolver:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except docker.errors.APIError:
            raise SystemError
        
    def get_entrypoint(self, image_name: str) -> Optional[List[str]]:
        try:
            image = self.client.images.get(image_name)
            entrypoint = image.attrs['Config'].get('Entrypoint') or []
            cmd = image.attrs['Config'].get('Cmd') or []
            return entrypoint + cmd
        except Exception as e:
            print(f"Error fetching image metadata from Podman: {e}")
            return None
        
    def build_rootfs(self, base_image:str):
        with open("Containerfile", 'w') as fp:
            fp.write(f"FROM {base_image}\n")
        containerfile:str = os.path.join(os.getcwd(), "Containerfile")
        
        subprocess.run(['docker', 'build', '.', '-f', containerfile, '-o', 'rootfs'],)

if __name__ == "__main__":
    #uri = '/var/folders/k7/rflqttnx07d1cy2fchj1ts7w0000gn/T/podman/podman-machine-default-api.sock'
    resolver = EntrypointResolver()
    entrypoints = resolver.get_entrypoint("docker.io/library/nginx:latest")
    resolver.build_rootfs("docker.io/library/nginx:latest")
    print(entrypoints)