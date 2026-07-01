import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="mex",
    disable_plugins=[SitemapPlugin],
    telemetry_enabled=False,
)
