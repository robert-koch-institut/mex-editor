import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from mex.editor.settings import EditorSettings

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator

settings = EditorSettings.get()

CLIENT = Path(__file__).parent.resolve() / "client"
CLIENT_DIST = settings.client_dir / settings.base_href.strip("/")
STATIC_DIR = CLIENT_DIST / "browser"
CLIENT_NODE_MODULES = CLIENT / "node_modules"
NODE_VIRTUAL_ENV = CLIENT / ".nodeenv"
NODE_BIN_DIR = NODE_VIRTUAL_ENV / ("Scripts" if sys.platform == "win32" else "bin")
NODE_BIN = NODE_BIN_DIR / ("node.exe" if sys.platform == "win32" else "node")


def _get_node_env() -> dict[str, str]:
    """Return environment variables for the nodeenv."""
    env = os.environ.copy()
    env["NODE_PATH"] = f"{CLIENT_NODE_MODULES}"
    env["NPM_CONFIG_PREFIX"] = f"{CLIENT}"
    env["PATH"] = f"{NODE_BIN_DIR}{os.pathsep}{env['PATH']}"
    return env


def _get_npm_command() -> list[str]:
    """Return the npm command."""
    if sys.platform == "win32":
        return [
            f"{NODE_BIN}",
            f"{NODE_BIN_DIR / 'node_modules' / 'npm' / 'bin' / 'npm-cli.js'}",
        ]
    return ["npm"]


def _get_npx_command() -> list[str]:
    """Return the npx command."""
    if sys.platform == "win32":
        return [
            f"{NODE_BIN}",
            f"{NODE_BIN_DIR / 'node_modules' / 'npm' / 'bin' / 'npx-cli.js'}",
        ]
    return ["npx"]


def exec_npm(npm_args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Execute an npm command using the nodeenv environment."""
    return subprocess.run(  # noqa: S603
        [*_get_npm_command(), *npm_args],
        check=True,
        env=_get_node_env(),
        cwd=CLIENT,
    )


def exec_npx(npx_args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Execute an npx command using the nodeenv environment."""
    return subprocess.run(  # noqa: S603
        [*_get_npx_command(), *npx_args],
        check=True,
        env=_get_node_env(),
        cwd=CLIENT,
    )


def exec_py(py_args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Execute a python module as a subprocess using the current executable."""
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", *py_args],
        check=True,
    )


@contextmanager
def npm_watch() -> Generator[subprocess.Popen[bytes]]:
    """Start `npm run watch` and terminate it on exit."""
    process = subprocess.Popen(  # noqa: S603
        [
            *_get_npm_command(),
            "run",
            "watch",
            "--",
            "--output-path",
            str(CLIENT_DIST),
        ],
        env=_get_node_env(),
        cwd=CLIENT,
    )
    try:
        yield process
    finally:
        process.terminate()
        process.wait()


def npm() -> None:
    """Run npm commands via `uv run run-npm ...`."""
    try:
        exec_npm(sys.argv[1:])
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from None


def npx() -> None:
    """Run npx commands via `uv run run-npx ...`."""
    try:
        exec_npx(sys.argv[1:])
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from None


def install() -> None:
    """Install nodeenv and npm dependencies."""
    exec_py(["nodeenv", f"{NODE_VIRTUAL_ENV}", "--force"])
    exec_npm(["clean-install"])


def build() -> None:
    """Build the angular frontend."""
    exec_npm(
        [
            "run",
            "build",
            "--",
            "--output-path",
            str(CLIENT_DIST),
            "--base-href",
            settings.base_href,
        ]
    )


def install_and_build() -> None:
    """Install dependencies and build the angular frontend."""
    install()
    build()
