import os
import pprint
import sys

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_design_kit as ddk
import dash_mantine_components as dmc
from dash import Dash, Input, Output, State, dcc, html, no_update
from static.ids import IDs
from utils.layout_utils import html_button

BASE_ID = IDs.GROUP_SELECTION_BASE_ID.value
METADATA_AND_GROUP_CREATION_BASE_ID = IDs.METADATA_AND_GROUP_CREATION_BASE_ID.value


def get_biosample_id_column() -> str:
    """
    This function is used to get the biosample id column name
    """
    return "Select all groups"


def get_select_groups_table_id() -> str:
    """
    This function is used to get the select groups table id
    """
    return BASE_ID + "table"


def get_select_groups_generate_button() -> str:
    """
    This function is used to get the select groups button id
    """
    return BASE_ID + "generate_button"


def group_selection_button() -> html.Div:
    """
    Div that contains all need components for the group selection.

    The Store that contains the selected groups is stored in the
    layout/metadata_and_group_creation.py -> metadata_and_group_creation_button

    """

    button = html_button(
        id=BASE_ID + "button",
        text="Group selection",
        parent_style={"margin-bottom": "1rem"},
    )
    return html.Div([button, group_selection_modal()])


def table() -> dag.AgGrid:
    """
    Creates an empty table for the group selection modal

    Returns:
        dag.AgGrid: The table for the group selection modal
    """
    COLUMN_NAME = get_biosample_id_column()
    COLUMN_DEFS = [
        {
            "field": COLUMN_NAME,
            "checkboxSelection": True,
            "headerCheckboxSelection": True,
            "headerCheckboxSelectionFilteredOnly": True,
        }
    ]
    table = dag.AgGrid(
        id=get_select_groups_table_id(),
        columnDefs=COLUMN_DEFS,
        columnSize="sizeToFit",
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            # "floatingFilter": True,
        },
        dashGridOptions={
            "enableCellTextSelection": True,
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
        },
        rowData=[],
    )
    return table


def group_selection_modal() -> dmc.Modal:
    """
    Modal that contains the table and the button to view the selected groups.

    Returns:
        dmc.Modal: The modal for the group selection
    """
    modal = dmc.Modal(
        centered=True,
        overflow="outside",
        closeButtonLabel="Close",
        closeOnClickOutside=True,
        closeOnEscape=True,
        withFocusReturn=True,
        # fullScreen=True,
        size="30%",
        id=BASE_ID + "modal",
        children=[
            html_button(
                id=BASE_ID + "back_button",
                text="Back",
                parent_style={"margin-bottom": "1rem"},
            ),
            table(),
            html_button(
                id=BASE_ID + "generate_button",
                text="View selected groups",
                parent_style={"margin-top": "1rem"},
            ),
        ],
    )
    return modal


def import_group_selection_callbacks(app: Dash):
    @app.callback(
        Output(
            METADATA_AND_GROUP_CREATION_BASE_ID + "modal",
            "opened",
            allow_duplicate=True,
        ),
        Output(BASE_ID + "modal", "opened"),
        Input(BASE_ID + "back_button", "n_clicks"),
        prevent_initial_call=True,
    )
    def metadata_and_group_creation_modal_open(n_clicks) -> tuple[bool, bool]:
        """
        Callback to open and close the modal
        """
        if n_clicks:
            return True, False
        return no_update, no_update

    @app.callback(
        Output(
            BASE_ID + "modal",
            "opened",
            allow_duplicate=True,
        ),
        Input(BASE_ID + "button", "n_clicks"),
        Input(BASE_ID + "continue", "n_clicks"),
        State(BASE_ID + "modal", "opened"),
        prevent_initial_call=True,
    )
    def group_selection_modal_open(
        n_clicks: int, n_clicks_1: int, is_open: bool
    ) -> bool:
        """
        Callback to open and close the modal
        """
        if n_clicks:
            return not is_open
        if n_clicks_1:
            return not is_open
        return is_open
