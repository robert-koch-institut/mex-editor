from pathlib import Path
from typing import cast

import reflex as rx

from mex.editor.components import render_value
from mex.editor.consent.layout import page
from mex.editor.consent.state import ConsentState
from mex.editor.search.main import search_result

CONSENT_MD = Path("assets/consent_de.md").read_text(encoding="utf-8")


def resources() -> rx.Component:
    """Render a list of the users resources."""
    return rx.vstack(
        rx.text(
            "DATENBESTÄNDE & DATENSÄTZE",
            weight="bold",
        ),
        rx.vstack(
            rx.foreach(
                ConsentState.user_resources,
                search_result,
            ),
        ),
        style=rx.Style(
            textAlign="center",
            marginBottom="var(--space-8)",
        ),
        custom_attrs={"data-testid": "user-resources"},
    )


def projects() -> rx.Component:
    """Render a list of the users projects."""
    return rx.vstack(
        rx.text(
            "PROJEKTE",
            weight="bold",
        ),
        rx.vstack(
            rx.foreach(
                ConsentState.user_projects,
                search_result,
            ),
        ),
        style=rx.Style(
            textAlign="center",
            marginBottom="var(--space-4)",
        ),
        custom_attrs={"data-testid": "user-projects"},
    )


def user_data() -> rx.Component:
    """Render the user data section with name and email."""
    return rx.cond(
        ConsentState.merged_login_person,
        rx.vstack(
            rx.text(
                ConsentState.merged_login_person["fullName"],  # type: ignore[index]
                style=rx.Style(
                    fontWeight="var(--font-weight-bold)",
                    fontSize="var(--font-size-6)",
                ),
            ),
            rx.text(
                ConsentState.merged_login_person["email"],  # type: ignore[index]
                style=rx.Style(
                    color="var(--gray-12)",
                ),
            ),
            rx.text(
                ConsentState.merged_login_person["orcidId"],  # type: ignore[index]
                style=rx.Style(
                    color="var(--gray-12)",
                ),
            ),
            style=rx.Style(
                textAlign="center",
                marginBottom="var(--space-4)",
            ),
            custom_attrs={"data-testid": "user-data"},
        ),
        rx.text("Loading user data...", custom_attrs={"data-testid": "user-data"}),
    )


def consent_box() -> rx.Component:
    """Render the consent box with text and buttons."""
    return rx.card(
        rx.vstack(
            rx.markdown(
                CONSENT_MD,
                style=rx.Style({"fontSize": "13px", "lineHeight": "1.5"}),
            ),
            rx.hstack(
                rx.button(
                    "Einwilligen",
                    on_click=ConsentState.submit_rule_set(consented=True),  # type: ignore[misc]
                ),
                rx.spacer(),
                rx.button(
                    "Ablehnen",
                    on_click=ConsentState.submit_rule_set(consented=False),  # type: ignore[misc]
                ),
            ),
            style=rx.Style(
                justifyContent="center",
                display="flex",
                width="100%",
                align="center",
                justify="center",
            ),
        ),
        style=rx.Style(
            backgroundColor="rgba(173, 216, 230, 0.2)",
            padding="16px",
        ),
        custom_attrs={"data-testid": "consent-box"},
    )


def consent_status() -> rx.Component:
    """Render the current consent status for the user."""
    return rx.cond(
        ConsentState.merged_login_person,
        rx.vstack(
            rx.text(ConsentState.merged_login_person["fullName"], weight="bold"),  # type: ignore[index]
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
            style=rx.Style(
                width="100%",
                align="center",
                justify="center",
            ),
            custom_attrs={"data-testid": "consent-status"},
        ),
        rx.text(
            "Loading consent status...", custom_attrs={"data-testid": "consent-status"}
        ),
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
            style=rx.Style(minWidth="10%"),
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
            style=rx.Style(minWidth="10%"),
        ),
        spacing="4",
        style=rx.Style(width="100%"),
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
                style=rx.Style(
                    justifyContent="center",
                    display="flex",
                    width="100%",
                ),
            ),
            consent_status(),
            style=rx.Style(
                width="100%",
                align="center",
                justify="center",
                flexGrow="1",
            ),
            custom_attrs={"data-testid": "consent-index"},
        ),
    )
