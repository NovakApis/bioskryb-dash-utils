import pprint
from functools import reduce

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_design_kit as ddk
import dash_mantine_components as dmc
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from dash_iconify import DashIconify

from layout.group_selection import get_biosample_id_column as get_group_id_column
from static.ids import IDs
from utils.appsync import fetch_table_data_from_appsync
from utils.data import (
    convert_columns_for_export,
    create_column_defs_and_row_data,
    mandatory_columns,
)
from utils.layout_utils import html_button

GROUP_SELECTION_BASE_ID = IDs.GROUP_SELECTION_BASE_ID.value
BASE_ID = IDs.METADATA_AND_GROUP_CREATION_BASE_ID.value


def get_group_store_id() -> str:
    """
    Returns the id for the group store component.
    This component is a dictionary that stores group data
    such as group name and biosamples for each group.
    ---

    The data is in the following format:
    {
        "group_name_A": ["biosample1", "biosample2", "biosample3"],

        "group_name_B": ["biosample4", "biosample5", "biosample6"],

        ...
    }
    """
    return BASE_ID + "group_store"


def select_groups_menu() -> dmc.Menu:
    return dmc.Menu(
        [
            # Button that opens the dropdown menu
            dmc.MenuTarget(
                html_button(id=BASE_ID + "select_groups_button", text="Group Selector")
            ),
            # Dropdown menu
            dmc.MenuDropdown(
                [
                    # Select all checkbox
                    dmc.Checkbox(
                        id=BASE_ID + "all_groups_checkbox",
                        label="select/deselect all",
                        value="",
                        checked=False,
                    ),
                    # Mandatory columns
                    dmc.MenuLabel("Groups"),
                    dmc.CheckboxGroup(
                        id=BASE_ID + "groups_checkbox_group",
                        orientation="vertical",
                        children=[
                            # dmc.Checkbox(
                            #     label=column_name,
                            #     value=column_name,
                            # )
                            # for column_name in mandatory_columns()
                        ],
                        # value=mandatory_columns(),
                    ),
                ],
            ),
        ],
        closeOnItemClick=False,
        trigger="hover",
    )


def select_columns_menu(custom_columns: list[str]) -> dmc.Menu:
    """
    Creates a dropdown menu for selecting columns to view in the table.
    Args:
        custom_columns: list[str] - list of custom column names from basejumper's metadata

    Returns:
        dmc.Menu - dropdown menu for selecting columns to view in the table
    """
    return dmc.Menu(
        [
            # Button that opens the dropdown menu
            dmc.MenuTarget(
                html_button(
                    id=BASE_ID + "select_columns_button", text="Column Selector"
                )
            ),
            # Dropdown menu
            dmc.MenuDropdown(
                [
                    # Select all checkbox
                    dmc.Checkbox(
                        id=BASE_ID + "metadata_all_column_checkbox",
                        label="select/deselect all",
                        value="",
                        checked=True,
                    ),
                    # Mandatory columns
                    dmc.MenuLabel("Basejumper"),
                    dmc.CheckboxGroup(
                        id=BASE_ID + "basejumper_column_checkbox_group",
                        orientation="vertical",
                        children=[
                            dmc.Checkbox(
                                label=column_name,
                                value=column_name,
                            )
                            for column_name in mandatory_columns()
                        ],
                        value=mandatory_columns(),
                    ),
                    # Metadata columns
                    dmc.MenuDivider(),
                    dmc.MenuLabel("Custom"),
                    dmc.CheckboxGroup(
                        id=BASE_ID + "custom_column_checkbox_group",
                        orientation="vertical",
                        children=[
                            dmc.Checkbox(
                                label=column_name,
                                value=column_name,
                            )
                            for column_name in custom_columns
                        ],
                        value=custom_columns,
                    ),
                ],
            ),
        ],
        closeOnItemClick=False,
        trigger="hover",
    )


def header(custom_columns: list[str]):
    """
    Creates the header for the metadata and group creation modal.

    The header is composed of three parts:
        left_side: column selection dropdown, export button, import button
        middle_side: continue button
        right_side: group selection dropdown, group name input, create/edit group button

    Args:
        custom_columns: list[str] - list of custom column names from basejumper's metadata

    Returns:
        html.Div - header for the metadata and group creation modal

    """

    column_dropdown = select_columns_menu(custom_columns=custom_columns)
    export_button = html_button(
        id=BASE_ID + "table_export_button",
        text="Export",
        style={"width": "100px"},
    )
    # TODO: implement import
    import_button = html_button(
        id=BASE_ID + "table_import_button",
        text="Import",
        style={"width": "100px"},
    )
    group_dropdown = select_groups_menu()
    # Input text field for creating/editing groups
    group_name_input = dbc.Input(
        id=BASE_ID + "group_name_input",
        placeholder="Name your group",
        type="text",
        style={"width": "200px"},
    )
    # Button for creating/editing groups
    create_edit_group_button = html_button(
        id=BASE_ID + "create_edit_group_button",
        text="+ / ✐",
        style={"width": "100px"},
    )
    left_side = html.Div(
        style={
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "flex-end",
            "gap": "1rem",
        },
        children=[
            column_dropdown,
            export_button,
            import_button,
        ],
    )
    right_side = html.Div(
        style={
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "flex-end",
            "gap": "1rem",
            # "width": "50%",
        },
        children=[
            group_dropdown,
            group_name_input,
            create_edit_group_button,
        ],
    )
    middle_side = html.Div(
        style={
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "flex-end",
            "gap": "1rem",
        },
        children=[
            html_button(
                id=BASE_ID + "restart_filters_button",
                text="Reset filters",
                style={"width": "100px"},
            ),
            html_button(
                id=GROUP_SELECTION_BASE_ID + "continue",
                text="Continue",
                style={"width": "100px"},
            ),
        ],
    )
    return html.Div(
        children=[
            left_side,
            middle_side,
            right_side,
        ],
        style={
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "flex-end",
            "margin-bottom": "1rem",
        },
    )


def table(payload: dict) -> tuple[dag.AgGrid, list[str]]:
    """
    Creates the table for the metadata and group creation modal.

    Args:
        payload: dict - dictionary object containing data from the project

    Returns:
        tuple[dag.AgGrid, list[str]] - tuple containing the table and the list of columns

    """

    # unpack the payload object for project id and appsync data
    project_id = payload["project_id"]
    app_sync_endpoint = payload["app_sync_endpoint"]
    app_sync_user = payload["app_sync_user"]

    # create the column definitions and row data for the table
    COLUMN_DEFS, ROW_DATA = create_column_defs_and_row_data(
        fetch_table_data_from_appsync(
            project_id=project_id,
            app_sync_endpoint=app_sync_endpoint,
            app_sync_user=app_sync_user,
        )
    )

    # create the table
    table = dag.AgGrid(
        # dangerously_allow_code=True,  # TODO: check if this is safe, use-case etc.
        id=BASE_ID + "table",
        columnDefs=COLUMN_DEFS,
        columnSize="autoSize",
        defaultColDef={
            "autoHeight": True,
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
        suppressDragLeaveHidesColumns=True,
        rowData=ROW_DATA,
    )

    # get the list of columns for dropdown menu that selects columns to view
    columns = list(
        filter(
            lambda x: x not in mandatory_columns(),
            list(map(lambda x: x["field"], COLUMN_DEFS)),
        )
    )
    return table, columns


def metadata_and_group_creation_button(payload: dict) -> html.Div:
    """
    Div that contains all need components for the metadata and group creation modal.

    These components include:
        dcc.Store - stores group data such as group name and biosamples for each group
        html.Button - button that opens the modal when clicked
        Modal - modal that contains the table and header for the metadata and group creation modal

    Args:
        payload: dict - dictionary object containing data from the project
    Returns:
        html.Div - div that contains all need components for the metadata and group creation modal
    """

    button = html_button(
        id=BASE_ID + "button",
        text="Metadata and group creation",
        parent_style={"margin-bottom": "1rem"},
    )
    return html.Div(
        [
            dcc.Store(get_group_store_id(), data={}),
            button,
            metadata_and_group_creation_modal(payload),
        ]
    )


def metadata_and_group_creation_modal(payload: dict) -> dmc.Modal:
    """
    Modal that contains the table and header for the metadata and group creation modal.

    Args:
        payload: dict - dictionary object containing data from the project
    Returns:
        dmc.Modal - modal that contains the table and header for the metadata and group creation modal

    """
    # create table and extract the list of columns
    table_component, custom_columns = table(payload)
    modal = dmc.Modal(
        centered=True,
        overflow="outside",
        closeButtonLabel="Close",
        closeOnClickOutside=True,
        closeOnEscape=True,
        withFocusReturn=True,
        # fullScreen=True,
        size="100%",
        id=BASE_ID + "modal",
        children=[
            group_created_alert(),
            header(custom_columns),
            table_component,
        ],
    )
    return modal


def group_created_alert():
    return dmc.Alert(
        id=BASE_ID + "group_created_alert",
        withCloseButton=True,
        hide=True,
        duration=3000,
        variant="light",
        style={"z-index:": "9999"},
    )


def create_default_groups(all_row_data: list[dict[str, str]]):
    """
    Creates the default groups for the group selection table.
    """

    default_groups_store = {
        "ALL BIOSAMPLES": list(map(lambda x: x["biosamplename"], all_row_data)),
    }

    row_data = [
        {get_group_id_column(): group_name_key}
        for group_name_key in default_groups_store.keys()
    ]

    return default_groups_store, row_data


def import_metadata_and_group_creation_callbacks(app: Dash) -> None:
    """
    Callbacks for the metadata and group creation modal.

    Args:
        app: Dash - dash app object
    Returns:
        None

    """

    """
        Commented out code is for debugging purposes
    """
    # app.clientside_callback(
    #     """
    #     function(n_clicks, n_clicks_1, is_open) {
    #         if (n_clicks) {
    #             return !is_open
    #         }
    #         if (n_clicks_1) {
    #             return !is_open
    #         }
    #         return is_open
    #     }
    #     """,
    #     Output(BASE_ID + "modal", "opened"),
    #     Input(BASE_ID + "button", "n_clicks"),
    #     Input(GROUP_SELECTION_BASE_ID + "continue", "n_clicks"),
    #     State(BASE_ID + "modal", "opened"),
    # )

    @app.callback(
        Output(BASE_ID + "modal", "opened"),
        Input(BASE_ID + "button", "n_clicks"),
        Input(GROUP_SELECTION_BASE_ID + "continue", "n_clicks"),
        State(BASE_ID + "modal", "opened"),
    )
    def open_close_modal(n_clicks, n_clicks_1, is_open):
        """
        Opens and closes the modal.
        """
        if n_clicks:
            return not is_open
        if n_clicks_1:
            return not is_open
        return is_open

    @app.callback(
        Output(BASE_ID + "table", "filterModel"),
        Input(BASE_ID + "restart_filters_button", "n_clicks"),
        State(BASE_ID + "table", "filterModel"),
        prevent_initial_call=True,
    )
    def restart_filters(n_clicks, filter_model):
        """
        Resets the filters in the table.
        """
        pprint.pprint(filter_model)
        return {}

    @app.callback(
        Output(BASE_ID + "groups_checkbox_group", "children"),
        Output(BASE_ID + "groups_checkbox_group", "value"),
        Output(BASE_ID + "table", "selectedRows"),
        Input(BASE_ID + "all_groups_checkbox", "checked"),
        Input(BASE_ID + "groups_checkbox_group", "value"),
        Input(BASE_ID + "group_store", "data"),
        State(BASE_ID + "table", "rowData"),
        State(BASE_ID + "group_name_input", "value"),
        prevent_initial_call=True,
    )
    def update_groups_checkbox_group(
        all_groups_checked,
        checked_groups,
        group_store,
        row_data,
        group_name_input,
    ):
        """
        Updates the groups checkbox group.
        """
        triggered = ctx.triggered[0]["prop_id"].split(".")[0]
        # if select all groups checkbox is clicked
        if triggered == BASE_ID + "all_groups_checkbox":
            if all_groups_checked:
                children = no_update
                selected_groups = list(group_store.keys())
            else:
                children = no_update
                selected_groups = []
        # if a group is created
        elif triggered == BASE_ID + "group_store":
            children = [
                dmc.Checkbox(
                    label=group_name,
                    value=group_name,
                )
                for group_name in group_store.keys()
            ]
            selected_groups = [group_name_input]
        # if a group is selected or deselected
        else:
            if not group_store:
                children = no_update
                selected_groups = no_update
            else:
                children = [
                    dmc.Checkbox(
                        label=group_name,
                        value=group_name,
                    )
                    for group_name in group_store.keys()
                ]
                selected_groups = checked_groups
        if selected_groups == [None]:
            # when first loading the default groups (no group is selected)
            # so we skip selecting biosamples in the table
            selected_groups = []
        # flatten all selected group biosamples and filter selected rows by those biosamples
        selected_biosamples = reduce(
            lambda acc, x: acc + x,
            [group_store[group_name] for group_name in selected_groups],
            [],
        )
        selected_rows = list(
            filter(lambda x: x["biosamplename"] in selected_biosamples, row_data)
        )
        return children, selected_groups, selected_rows

    @app.callback(
        Output(BASE_ID + "metadata_all_column_checkbox", "checked"),
        Output(BASE_ID + "basejumper_column_checkbox_group", "value"),
        Output(BASE_ID + "custom_column_checkbox_group", "value"),
        Output(BASE_ID + "table", "columnState"),
        Input(BASE_ID + "metadata_all_column_checkbox", "checked"),
        Input(BASE_ID + "basejumper_column_checkbox_group", "value"),
        Input(BASE_ID + "custom_column_checkbox_group", "value"),
        State(BASE_ID + "basejumper_column_checkbox_group", "children"),
        State(BASE_ID + "custom_column_checkbox_group", "children"),
        State(BASE_ID + "table", "columnState"),
        prevent_initial_call=True,
    )
    def checkbox_handler(
        all_columns_checked,
        basejumper_columns,
        custom_columns,
        bj_children,
        c_children,
        column_state,
    ):
        """
        Handles the checkboxes for selecting columns to view in the table.
        Shows and hides table columns based on the checkboxes.

        """
        all_columns = list(map(lambda x: x["props"]["value"], bj_children)) + list(
            map(lambda x: x["props"]["value"], c_children)
        )

        clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
        clicked_value = ctx.triggered[0]["value"]
        if clicked_id == BASE_ID + "metadata_all_column_checkbox":
            if clicked_value:
                basejumper_columns = list(
                    map(lambda x: x["props"]["value"], bj_children)
                )
                custom_columns = list(map(lambda x: x["props"]["value"], c_children))
            else:
                basejumper_columns = []
                custom_columns = []
        view_columns = basejumper_columns + custom_columns

        columns_to_hide = list(set(all_columns) - set(view_columns))
        for state in column_state:
            if state["colId"] in columns_to_hide:
                state["hide"] = True
            else:
                state["hide"] = False

        return all_columns_checked, basejumper_columns, custom_columns, column_state

    @app.callback(
        Output(BASE_ID + "group_store", "data"),
        Output(GROUP_SELECTION_BASE_ID + "table", "rowData"),
        Input(BASE_ID + "create_edit_group_button", "n_clicks"),
        State(BASE_ID + "group_name_input", "value"),
        State(BASE_ID + "table", "selectedRows"),
        State(BASE_ID + "group_store", "data"),
        State(BASE_ID + "table", "rowData"),
        prevent_initial_call=False,  # set to False so default groups are created on first load
    )
    def add_group(n_clicks, group_name, selected_rows, group_store, all_row_data):
        """
        Adds a group to the group store and group selection table.
        """
        if not ctx.triggered:
            # first time the app is loaded
            # add default groups
            default_groups_store, row_data = create_default_groups(all_row_data)
            return default_groups_store, row_data

        if not group_name or group_name.isspace() or not selected_rows:
            return no_update, no_update

        group_name = group_name.strip()

        selected_rows_biosamples = list(
            map(lambda x: x["biosamplename"], selected_rows)
        )
        group_store = {**group_store, group_name: selected_rows_biosamples}

        # pprint.pprint(group_store)
        row_data = [
            {get_group_id_column(): group_name_key}
            for group_name_key in group_store.keys()
        ]
        # pprint.pprint(row_data)

        pprint.pprint(group_store)
        pprint.pprint(row_data)
        return group_store, row_data

    @app.callback(
        Output(BASE_ID + "group_created_alert", "hide"),
        Output(BASE_ID + "group_created_alert", "title"),
        Output(BASE_ID + "group_created_alert", "children"),
        Output(BASE_ID + "group_created_alert", "color"),
        Input(BASE_ID + "create_edit_group_button", "n_clicks"),
        State(BASE_ID + "group_created_alert", "hide"),
        State(BASE_ID + "group_name_input", "value"),
        State(BASE_ID + "group_store", "data"),
        State(BASE_ID + "table", "selectedRows"),
        prevent_initial_call=True,
    )
    def alert(n_clicks, hide, group_name, existing_groups, selected_rows):
        """
        Creates an alert for when a group is created.
        """
        if not group_name or group_name.isspace():
            return (
                False,
                "Group name not provided",
                f"Please provide a name for your group",
                "red",
            )
        if not selected_rows:
            return (
                False,
                "No biosamples selected",
                f"Please select biosamples to add to your group",
                "red",
            )
        if group_name in existing_groups.keys():
            return (
                False,
                "Group overwritten",
                f"Group '{group_name}' has been overwritten",
                "yellow",
            )
        return (
            False,
            "Group created",
            f"Group '{group_name}' has been created",
            "blue",
        )

    @app.callback(
        Output(BASE_ID + "table", "exportDataAsCsv"),
        Output(BASE_ID + "table", "csvExportParams"),
        Input(BASE_ID + "table_export_button", "n_clicks"),
        State(BASE_ID + "table", "columnDefs"),
        # State(BASE_ID + "table", "rowData"),
        prevent_initial_call=True,
    )
    def export_table_as_csv(n_clicks, column_defs):
        """
        Exports the table as a csv file.
        """
        filename = "table.csv"
        # pprint.pprint(column_defs)
        # column_keys = ["biosamplename"]
        column_keys = ", ".join(convert_columns_for_export(column_defs))
        print(column_defs)
        # column_keys = list(map(lambda x: str(x), range(0,13)))
        export_params = {
            "fileName": filename,
            # "columnKeys": column_keys,
            "skipColumnHeaders": True,  # prevent the column names from being exported
            "prependContent": column_keys,  # export friendly column names as the first row
            "allColumns": True,
            "columnSeparator": ",",
            "onlySelected": False,
            "suppressQuotes": False,  # WARNING: If True, responsibility to ensure that no cells contain the column separator
        }
        if n_clicks:
            return True, export_params
        return False, no_update
        # return dcc.send_data_frame(
        #     ctx.triggered[0]["value"],
        #     filename="table.csv",
        #     mimetype="text/csv",
        # )
