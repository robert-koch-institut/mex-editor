from typing import cast

import reflex as rx

from mex.editor.components import render_value
from mex.editor.consent.layout import page
from mex.editor.consent.state import ConsentState
from mex.editor.search.main import search_result


def resources() -> rx.Component:
    """Render a list of the users resources."""
    return rx.vstack(
        rx.text(
            "DATENBESTÄNDE & DATENSÄTZE",
        ),
        rx.vstack(
            rx.foreach(
                ConsentState.user_resources,
                search_result,
            ),
        ),
        style={
            "textAlign": "center",
            "marginBottom": "var(--space-8)",
        },
        custom_attrs={"data-testid": "user-resources"},
    )


def projects() -> rx.Component:
    """Render a list of the users projects."""
    return rx.vstack(
        rx.text(
            "PROJEKTE",
        ),
        rx.vstack(
            rx.foreach(
                ConsentState.user_projects,
                search_result,
            ),
        ),
        style={
            "textAlign": "center",
            "marginBottom": "var(--space-4)",
        },
        custom_attrs={"data-testid": "user-projects"},
    )


def user_data() -> rx.Component:
    """Render the user data section with name and email."""
    return rx.vstack(
        rx.text(
            f"{ConsentState.display_name}",
            style={
                "fontWeight": "var(--font-weight-bold)",
                "fontSize": "var(--font-size-6)",
            },
        ),
        rx.text(
            f"{ConsentState.user_mail}",
            style={"color": "var(--gray-12)"},
        ),
        rx.text(
            f"{ConsentState.user_orcidID}",
            style={"color": "var(--gray-12)"},
        ),
        style={
            "textAlign": "center",
            "marginBottom": "var(--space-4)",
        },
        custom_attrs={"data-testid": "user-data"},
    )


def consent_box() -> rx.Component:
    """Render the consent box with text and buttons."""
    return rx.card(
        rx.vstack(
            rx.markdown(
                "Der Metadatenkatalog Metadata Exchange (MEx) verbessert das Auffinden "
                "von Forschungsdaten und -projekten des RKI. Mit Ihrer Einwilligung "
                "werden die mit Ihnen aktuell und zukünftigen assoziierten Projekte, "
                "Datenbestände und Publikationen in dem extern einsehbaren Katalog mit "
                "Ihrem Namen, Ihrer E-Mailadresse und ggf. Ihrer ORCID-ID "
                "veröffentlicht. <br>Wenn Sie in die Veröffentlichung Ihrer "
                "personenbezogenen Daten einwilligen möchten, klicken Sie bitte auf "
                "„Einwilligen”. Die Einwilligung kann jederzeit widerrufen werden. "
                "<br>Weitere Informationen finden Sie in unseren "
                "[Datenschutzhinweisen](https://confluence.rki.local/x/lx4NAw). <br>Sof"
                "ern Sie unsicher sind oder Fragen zu der Einwilligung haben, können "
                "Sie uns auch gerne kontaktieren: [mex@rki.de](mailto:mex@rki.de). <br>"
                "Hinweis: Die Namen der Autor*innen von Publikationen werden im "
                "Metadatenkatalog standardmäßig erfasst, da diese bereits "
                "veröffentlicht sind.",
                style={"fontSize": "13px"},
            ),
            rx.hstack(
                rx.button("Einwilligen", on_click=ConsentState.submit_rule_set(True)),  # noqa: FBT003
                rx.spacer(),
                rx.button("Ablehnen", on_click=ConsentState.submit_rule_set(False)),  # noqa: FBT003
            ),
            style={
                "justifyContent": "center",
                "display": "flex",
                "width": "100%",
                "align": "center",
                "justify": "center",
            },
        ),
        style={
            "backgroundColor": "rgba(173, 216, 230, 0.2)",
            "padding": "16px",
        },
        custom_attrs={"data-testid": "consent-box"},
    )


def consent_status() -> rx.Component:
    """Render the current consent status for the user."""
    return rx.vstack(
        rx.text(ConsentState.display_name, weight="bold"),
        rx.cond(
            ConsentState.consent_status,
            rx.hstack(
                rx.foreach(
                    ConsentState.consent_status.preview,  # type: ignore [union-attr]
                    render_value,
                )
            ),
            rx.hstack(
                rx.text(
                    "ConsentStatus: ",
                ),
                rx.spacer(direction="row"),
                rx.text(
                    "ConsentType: ",
                ),
            ),
        ),
        style={
            "width": "100%",
            "align": "center",
            "justify": "center",
        },
        custom_attrs={"data-testid": "consent-status"},
    )


def pagination() -> rx.Component:
    """Render pagination for navigating results."""
    return rx.center(
        rx.button(
            rx.text("Previous"),
            on_click=[
                ConsentState.go_to_previous_page,
                ConsentState.scroll_to_top,
                ConsentState.get_all_data,
                ConsentState.resolve_identifiers,
            ],
            disabled=ConsentState.disable_previous_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-previous-button"},
            style={"minWidth": "10%"},
        ),
        rx.select(
            ConsentState.total_pages,
            value=cast("rx.vars.NumberVar", ConsentState.current_page).to_string(),
            on_change=[
                ConsentState.set_page,
                ConsentState.scroll_to_top,
                ConsentState.get_all_data,
                ConsentState.resolve_identifiers,
            ],
            custom_attrs={"data-testid": "pagination-page-select"},
        ),
        rx.button(
            rx.text("Next"),
            on_click=[
                ConsentState.go_to_next_page,
                ConsentState.scroll_to_top,
                ConsentState.get_all_data,
                ConsentState.resolve_identifiers,
            ],
            disabled=ConsentState.disable_next_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-next-button"},
            style={"minWidth": "10%"},
        ),
        spacing="4",
        style={"width": "100%"},
    )


def index() -> rx.Component:
    """Return the index for the merge and extracted search component."""
    return page(
        rx.vstack(
            user_data(),
            projects(),
            resources(),
            pagination(),
            rx.spacer(direction="column"),
            rx.box(
                consent_box(),
                style={
                    "justifyContent": "center",
                    "display": "flex",
                    "width": "100%",
                },
            ),
            consent_status(),
            style={
                "width": "100%",
                "align": "center",
                "justify": "center",
                "flex-grow": "1",
            },
            custom_attrs={"data-testid": "consent-index"},
        ),
    )
