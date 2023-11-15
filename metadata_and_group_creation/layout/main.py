import os
import pprint

from dash import Dash, html
from dotenv import load_dotenv
from layout.group_selection import (
    get_biosample_id_column,
    get_select_groups_generate_button,
    get_select_groups_table_id,
    group_selection_button,
    import_group_selection_callbacks,
)
from layout.metadata_and_group_creation import (
    get_group_store_id,
    import_metadata_and_group_creation_callbacks,
    metadata_and_group_creation_button,
)


def main_view(payload: dict):
    """
    The main view
    Args:
        payload: dict - dictionary object containing data from the project
    Returns:
        html.Div: The main view containing 'metadata and group creation'
        and 'group selection'
    """
    return html.Div(
        children=[
            metadata_and_group_creation_button(payload=payload),
            group_selection_button(),
        ],
        style={
            "position": "absolute",
            "top": "50%",
            "left": "50%",
            "transform": "translate(-50%, -50%)",
            "display": "flex",
            "flex-direction": "column",
            "align-items": "center",
        },
    )


def gather_callbacks(app: Dash) -> None:
    """
    Gather all the callbacks

    Args:
        app: Dash - The dash app

    Imports:
        import_metadata_and_group_creation_callbacks
        import_group_selection_callbacks
    """
    import_metadata_and_group_creation_callbacks(app)
    import_group_selection_callbacks(app)


def get_components():
    """
    Get the components for the main view and the callbacks

    ---
    """
    # all needed component ids
    ids: dict[str, str | dict[str, str]] = {
        "group_store_id": get_group_store_id(),
        "select_groups": {
            "table_id": get_select_groups_table_id(),
            "table_column_name": get_biosample_id_column(),
            "generate_button_id": get_select_groups_generate_button(),
        },
    }

    return main_view, gather_callbacks, ids
