import reflex as rx

config = rx.Config(
    app_name="mex",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    tailwind=None,
    telemetry_enabled=False,
) #type: ignore[no-untyped-call]
