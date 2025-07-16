import reflex as rx

from mex.editor.settings import EditorSettings

settings = EditorSettings.get()
config = rx.Config(
    app_name="mex",
    frontend_port=settings.editor_frontend_port,
    deploy_url=settings.editor_frontend_deploy_url,
    backend_port=settings.editor_api_port,
    api_url=settings.editor_api_deploy_url,
    telemetry_enabled=False,
)
