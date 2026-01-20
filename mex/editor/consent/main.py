from typing import cast

import reflex as rx

from mex.editor.components import render_value
from mex.editor.consent.layout import page
from mex.editor.consent.state import ConsentState
from mex.editor.search_reference_dialog import search_results_list


def resources() -> rx.Component:
    """Render a list of the users resources."""
    return rx.vstack(
        rx.text(
            ConsentState.label_resources_title,
            weight="bold",
            style=rx.Style(
                textTransform="uppercase",
            ),
        ),
        search_results_list(ConsentState.user_resources),
        consent_pagination("resources"),
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
            ConsentState.label_projects_title,
            weight="bold",
            style=rx.Style(
                textTransform="uppercase",
            ),
        ),
        search_results_list(ConsentState.user_projects),
        consent_pagination("projects"),
        style=rx.Style(
            textAlign="center",
            marginBottom="var(--space-4)",
        ),
        custom_attrs={"data-testid": "user-projects"},
    )


def user_data() -> rx.Component:
    """Render the user data section with name and email."""
    return rx.cond(
        ConsentState.is_loading,
        rx.text(
            ConsentState.label_user_data_loading,
            custom_attrs={"data-testid": "user-data"},
        ),
        rx.vstack(
            rx.text(
                ConsentState.merged_login_person.full_name,  # type: ignore  [union-attr]
                style=rx.Style(
                    fontWeight="var(--font-weight-bold)",
                    fontSize="var(--font-size-6)",
                ),
            ),
            rx.text(
                ConsentState.merged_login_person.email,  # type: ignore [union-attr]
                style=rx.Style(
                    color="var(--gray-12)",
                ),
            ),
            rx.text(
                ConsentState.merged_login_person.orcid_id,  # type: ignore [union-attr]
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
    )


def consent_box() -> rx.Component:
    """Render the consent box with text and buttons."""
    return rx.card(
        rx.vstack(
            rx.markdown(
                ConsentState.consent_md,
                style=rx.Style({"fontSize": "var(--font-size-2)"}),
            ),
            rx.hstack(
                rx.button(
                    ConsentState.label_consent_box_consent_button,
                    on_click=ConsentState.submit_rule_set("consent"),  # type: ignore[operator]
                    custom_attrs={"data-testid": "accept-consent-button"},
                ),
                rx.spacer(),
                rx.button(
                    ConsentState.label_consent_box_no_consent_button,
                    on_click=ConsentState.submit_rule_set("denial"),  # type: ignore[operator]
                    custom_attrs={"data-testid": "denial-consent-button"},
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
            backgroundColor="var(--accent-3)",
            padding="16px",
        ),
        custom_attrs={"data-testid": "consent-box"},
    )


def consent_status() -> rx.Component:
    """Render the current consent status for the user."""
    return rx.cond(
        ConsentState.merged_login_person,
        rx.vstack(
            rx.text(ConsentState.merged_login_person.full_name, weight="bold"),  # type: ignore [union-attr]
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
            ConsentState.label_consent_status_loading,
            custom_attrs={"data-testid": "consent-status"},
        ),
    )


def consent_pagination(category: str) -> rx.Component:
    """Render pagination for navigating results dynamically."""
    return rx.center(
        rx.button(
            rx.text(ConsentState.label_pagination_previous_button),
            on_click=[
                ConsentState.go_to_previous_page(category),  # type: ignore[operator]
                ConsentState.scroll_to_top,
                ConsentState.fetch_data(category),  # type: ignore[operator]
                ConsentState.resolve_identifiers,
            ],
            disabled=getattr(ConsentState, f"disable_{category}_previous_page"),
            variant="surface",
            custom_attrs={"data-testid": f"{category}-pagination-previous-button"},
            style=rx.Style(minWidth="10%"),
        ),
        rx.select(
            getattr(ConsentState, f"{category}_total_pages"),
            value=cast(
                "rx.vars.NumberVar", getattr(ConsentState, f"{category}_current_page")
            ).to_string(),
            on_change=[
                getattr(ConsentState, f"set_{category}_page"),
                ConsentState.scroll_to_top,  # type: ignore[operator]
                ConsentState.fetch_data(category),  # type: ignore[operator]
                ConsentState.resolve_identifiers,
            ],
            custom_attrs={"data-testid": f"{category}-pagination-page-select"},
        ),
        rx.button(
            rx.text(ConsentState.label_pagination_next_button),
            on_click=[
                ConsentState.go_to_next_page(category),  # type: ignore[operator]
                ConsentState.scroll_to_top,
                ConsentState.fetch_data(category),  # type: ignore[operator]
                ConsentState.resolve_identifiers,
            ],
            disabled=getattr(ConsentState, f"disable_{category}_next_page"),
            variant="surface",
            custom_attrs={"data-testid": f"{category}-pagination-next-button"},
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
