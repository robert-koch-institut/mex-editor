import reflex as rx

from mex.editor.consent.layout import page
from mex.editor.consent.state import ConsentState
from mex.editor.search.main import search_result


def resources() -> rx.Component:
    """Render a list of the users resources."""
    return rx.vstack(
        rx.text(
            "DATENBESTÄNDE & DATENSÄTZE",
        ),
        rx.hstack(
            rx.foreach(
                ConsentState.user_resources,
                search_result,
            ),
        ),
        style={
            "textAlign": "center",
            "marginBottom": "var(--space-4)",
        },
    )


def bib_resources() -> rx.Component:
    """Render a list of the users bibliography."""
    return rx.vstack(
        rx.text(
            "PUBLIKATIONEN",
        ),
        rx.hstack(
            rx.foreach(
                ConsentState.user_bib_resources,
                search_result,
            ),
        ),
        style={
            "textAlign": "center",
            "marginBottom": "var(--space-4)",
        },
    )


def projects() -> rx.Component:
    """Render a list of the users projects."""
    return rx.vstack(
        rx.text(
            "PROJEKTE",
        ),
        rx.hstack(
            rx.foreach(
                ConsentState.user_projects,
                search_result,
            ),
        ),
        style={
            "textAlign": "center",
            "marginBottom": "var(--space-4)",
        },
    )


def user_data() -> rx.Component:
    """Render the user data section with name and email."""
    return rx.vstack(
        rx.text(
            f"{ConsentState.display_name}",
            style={
                "fontWeight": "var(--font-weight-bold)",
                "fontSize": "var(--font-size-3)",
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
                "veröffentlicht. Wenn Sie in die Veröffentlichung Ihrer "
                "personenbezogenen Daten einwilligen möchten, klicken Sie bitte auf "
                "„Einwilligen”. Die Einwilligung kann jederzeit widerrufen werden. "
                "Weitere Informationen finden Sie in unseren "
                "[Datenschutzhinweisen](https://confluence.rki.local/x/lx4NAw). Sofern "
                "Sie unsicher sind oder Fragen zu der Einwilligung haben, können Sie "
                "uns auch gerne kontaktieren: [mex@rki.de](mailto:mex@rki.de)",
                size="1",
            ),
            rx.hstack(
                rx.button("Einwilligen"),
                rx.spacer(),
                rx.button("Ablehnen"),
            ),
            style={
                "justifyContent": "center",
                "display": "flex",
                "width": "100%",
                "align": "center",
                "justify": "center",
            },
        ),
    )


def index() -> rx.Component:
    """Return the index for the merge and extracted search component."""
    return page(
        rx.vstack(
            user_data(),
            projects(),
            resources(),
            bib_resources(),
            rx.box(
                consent_box(),
                style={
                    "justifyContent": "center",
                    "display": "flex",
                    "width": "100%",
                },
            ),
            style={
                "width": "100%",
                "align": "center",
                "justify": "center",
                "flex-grow": "1",
            },
        ),
    )
