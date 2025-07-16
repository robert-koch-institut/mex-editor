from pkgutil import extend_path

import reflex as rx

import mex

# Setup mex package namespace
mex.__path__ = extend_path(mex.__path__, mex.__name__)


from mex.editor.settings import EditorSettings  # noqa: E402

settings = EditorSettings.get()
config = rx.Config(
    app_name=mex.__name__,
    frontend_port=settings.editor_frontend_port,
    deploy_url=settings.editor_frontend_deploy_url,
    backend_port=settings.editor_api_port,
    api_url=settings.editor_api_deploy_url,
    telemetry_enabled=False,
)
