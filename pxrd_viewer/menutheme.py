from contextlib import contextmanager


from nicegui import ElementFilter, ui, context


def dark():
    dark = ui.dark_mode()
    dark.auto()

    # Sync plot template with dark mode
    def update_plot_template(is_dark):
        template = "plotly_dark" if is_dark else "plotly"
        with context.client.layout:
            for element in ElementFilter(kind=ui.plotly):
                fig = element.figure
                fig.update_layout(template=template)
                element.update()

    dark.on_value_change(lambda _: update_plot_template(dark.value))
    # Inject JS to listen for system theme changes
    ui.add_head_html("""
            <script>
                function emitThemeChange() {
                    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    emitEvent('theme-change', { is_dark: isDark ? "dark" : "light" });
                }
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', emitThemeChange);
                document.addEventListener('DOMContentLoaded', function() {
                    setTimeout(emitThemeChange, 100);
                });
            </script>
        """)  # noqa: E501

    # The handler function is like this, updating specific markers:
    def handle_theme_change(e):
        is_dark = e.args.get("is_dark", "dark")
        update_plot_template(is_dark)

    # Then bound it to ui
    ui.on("theme-change", lambda e: handle_theme_change(e))

    return dark


# Global registry for pages
registered_pages = []


def register_nav(display_name=None, route=None, **kwargs):
    def decorator(page):
        registered_pages.append(
            {"page": page, "name": display_name or page.__name__, "route": route}
        )
        return page

    return decorator


# Decorator to register pages and forward to ui.page
def register_nav_page(route, display_name=None, **kwargs):
    def decorator(func):
        return register_nav(display_name, route)(ui.page(route, **kwargs)(func))

    return decorator


@contextmanager
def menutheme(title: str):
    drawer = ui.left_drawer(bordered=True).props("width=225")
    with drawer:
        ui.label("Navigation")
        # Dynamically link all registered pages
        for page in registered_pages:
            ui.link(page["name"], page["page"]).classes("q-mb-sm full-width")
        ui.switch("Dark mode").bind_value(dark())
    with ui.header():
        ui.button(icon="menu", on_click=lambda: drawer.toggle())
        ui.label(title).classes("text-h6 ml-4")
    yield
