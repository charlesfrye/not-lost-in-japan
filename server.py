from pathlib import Path

import modal
import modal.experimental

PORT = 8000
REGION = "us"
PROXY_REGION = "us-west"

app = modal.App("cci-2026.1-wk04d2-people-in-space")

here = Path(__file__).parent

image = modal.Image.debian_slim().add_local_dir(here, "/root/")

@app.cls(region=REGION, image=image, min_containers=1)
@modal.experimental.http_server(port=PORT, proxy_regions=[PROXY_REGION])
@modal.concurrent(target_inputs=100)
class Server:
    @modal.enter()
    def start(self):
        import subprocess

        subprocess.Popen(["python", "-m", "http.server", f"{PORT}"])


@app.local_entrypoint()
def ping():
    from urllib.error import HTTPError
    from urllib.request import urlopen

    url = Server._experimental_get_flash_urls()[0]  # one URL per proxy region

    this = Path(__file__).name

    print(f"requesting {this} from Modal HTTP Server at {url}")

    while True:
        try:
            print(urlopen(url + f"/{this}").read().decode("utf-8"))
            break
        except HTTPError as e:
            if e.code == 503:
                continue
            else:
                raise e
