import subprocess, os, socket, sys
import time, glob, pathlib
from utils import Server, Location
from common.shell_utils import sh
from common.rpc.secrets import get_secret
from utils import get_server_pid, get_active_servers

HOSTNAME = "cs61a.org"
NGINX_PORT = os.environ.get("PORT", "8001")


def main():
    """Start the Sandbox and IDE servers."""
    print("Starting NGINX...", file=sys.stderr)
    sh("nginx")

    print("Starting sandbox...", file=sys.stderr)
    sandbox_port = get_open_port()
    sb = subprocess.Popen(
        ["gunicorn", "-b", f":{sandbox_port}", "-w", "4", "sandbox:app", "-t", "3000"],
        env=os.environ,
    )
    proxy(f"sb.{HOSTNAME} *.sb.{HOSTNAME}", sandbox_port, f"sb.{HOSTNAME}")
    proxy(f"*.sb.pr.{HOSTNAME}", sandbox_port, f"sb.pr.{HOSTNAME}")

    print("Starting IDE...", file=sys.stderr)
    ide_port = get_open_port()
    ide = subprocess.Popen(
        ["gunicorn", "-b", f":{ide_port}", "-w", "4", "ide:app", "-t", "3000"],
        env=os.environ,
    )
    proxy(f"ide.{HOSTNAME}", ide_port, f"ide.{HOSTNAME}")
    proxy(f"*.ide.pr.{HOSTNAME}", ide_port, f"ide.pr.{HOSTNAME}")

    print("Writing NGINX default config...", file=sys.stderr)
    with open(f"/etc/nginx/sites-enabled/default", "w") as f:
        f.write(
            DEFAULT_SERVER.format(
                ide_port=ide_port, sb_port=sandbox_port, nginx_port=NGINX_PORT
            )
        )

    sh("nginx", "-s", "reload")

    if not os.path.exists("/save/root/berkeley-cs61a"):
        print("Cloning good copy of 61A repo...", file=sys.stderr)
        sh(
            "git",
            "clone",
            f"https://{get_secret(secret_name='GITHUB_IDE_TOKEN')}@github.com/Cal-CS-61A-Staff/berkeley-cs61a",
            "/save/root/berkeley-cs61a",
        )
    print("Checking out latest good copy commit..", file=sys.stderr)
    sh("git", "pull", cwd="/save/root/berkeley-cs61a")

    print("Ready.", file=sys.stderr)

    while True:
        servers = get_active_servers()
        now = time.time()

        for server in servers:
            heartbeat = pathlib.Path(
                f"/save/{server}/.local/share/code-server/heartbeat"
            )
            last_beat = heartbeat.stat().st_mtime

            if now - last_beat > 900:
                pid = get_server_pid(server)
                print(f"Killing {server} for idling...", file=sys.stderr)
                sh("kill", pid.decode("utf-8")[:-1])
                print(f"Killed.", file=sys.stderr)
        print("Cleanup complete. Sleeping for 900 seconds...", file=sys.stderr)
        time.sleep(900)


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))

    s.listen(1)
    port = s.getsockname()[1]

    s.close()
    return port


def proxy(domain, port, fn):
    conf = Server(
        Location(
            "/",
            include="proxy_params",
            proxy_pass=f"http://127.0.0.1:{port}",
        ),
        listen=NGINX_PORT,
        server_name=domain,
    )

    with open(f"/etc/nginx/sites-enabled/{fn}", "w") as f:
        f.write(str(conf))


DEFAULT_SERVER = """
server {{
    location / {{
        include proxy_params;
        if ($http_x_forwarded_for_host ~ "^(.*)ide.(pr.)?cs61a.org(.*)") {{
            proxy_pass http://127.0.0.1:{ide_port};
        }}
        if ($http_x_forwarded_for_host ~ "^(.*)sb.(pr.)?cs61a.org(.*)") {{
            proxy_pass http://127.0.0.1:{sb_port};
        }}
    }}
    listen {nginx_port} default_server;
    server_name _;
}}
"""


if __name__ == "__main__":
    main()
