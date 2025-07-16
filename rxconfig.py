import reflex as rx

config = rx.Config(
    app_name="mex",
    telemetry_enabled=False,
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
