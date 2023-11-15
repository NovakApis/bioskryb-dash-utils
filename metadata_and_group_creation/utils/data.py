import json
import pprint

import dateutil.parser as parser


def parse_date_from_iso(data):
    return parser.parse(data).strftime("%m/%d/%Y")


def parse_date_to_iso(data):
    return parser.parse(data).isoformat()


def appsync_data_types() -> dict[str]:
    """
    Returns basejumper mandatory column names as keys from appsync and data types as values
    """
    return {
        "biosampleName": "Text",
        "fastqValidationStatus": "Text",
        "size": "Number",
        "r1FastqTotalReads": "Number",
        "r2FastqTotalReads": "Number",
        "r1FastqLength": "Number",
        "created": "Date",
        "lotId": "Text",
        "metadata": "Metadata",
    }


def mandatory_columns_export() -> list[str]:
    """
    Lists out the basejumper mandatory columns for export
    """
    return [
        "Biosample Name",
        "FASTQ Validation Status",
        "Size",
        "Total Number of Reads",
        "Read Length",
        "Upload Date",
        "Bioskryb Product Lot ID",
    ]


def mandatory_columns() -> list[str]:
    """
    Lists out the basejumper mandatory columns
    """
    return [
        "biosamplename",
        "fastq validation status",
        "size",
        "total number of reads",
        "read length",
        "upload date",
        "bioskryb product lot id",
    ]


def convert_columns_for_export(column_defs: list[dict]) -> list[str]:
    # pprint.pprint(column_defs)
    non_mandatory = list(
        filter(lambda x: x["field"] not in mandatory_columns(), column_defs)
    )
    return mandatory_columns_export() + list(
        map(lambda x: x["headerName"], non_mandatory)
    )


def get_alternative_value(dtype: str):
    """
    Returns the alternative value for the dtype if the value is None
    """
    if dtype == "True/False":
        return ""
    elif dtype == "Number":
        return ""
    elif dtype == "Date":
        return ""
    elif dtype == "Text":
        return ""
    elif dtype == "Metadata":
        return "{}"
    else:
        return None


def modify_mandatory_data(
    list_of_biosamples: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    This function modifies the mandatory basejumper's data to be displayed in the table

    Args:
        list_of_biosamples (list[dict]): List of biosamples from appsync
    Returns:
        column_data (list[dict]): List of columns
        list_of_biosamples (list[dict]): Modified list of biosamples

    """
    list_of_biosamples = list_of_biosamples.copy()

    # manually adding the mandatory columns and their types
    column_data = []
    column_data.append({"name": "FASTQ Validation Status", "type": "Text"})
    column_data.append({"name": "Size", "type": "Number"})
    column_data.append({"name": "Total Number of Reads", "type": "Number"})
    column_data.append({"name": "Read Length", "type": "Number"})
    column_data.append({"name": "Upload Date", "type": "Date"})
    column_data.append({"name": "Bioskryb Product Lot ID", "type": "Text"})

    for biosample in list_of_biosamples:
        # manually adding modified biosamples data from appsync to be displayed in the table
        biosample["FASTQ Validation Status"] = biosample["fastqValidationStatus"]
        biosample["Size"] = biosample["size"]
        biosample["Total Number of Reads"] = (
            biosample["r1FastqTotalReads"] + biosample["r2FastqTotalReads"]
        )
        biosample["Read Length"] = biosample["r1FastqLength"]
        biosample["Upload Date"] = biosample["created"]
        # biosample["Upload Date"] = parse_date(biosample["created"])
        biosample["Bioskryb Product Lot ID"] = biosample["lotId"]
        # removing the unnecessary data from the biosamples
        del biosample["fastqValidationStatus"]
        del biosample["size"]
        del biosample["r1FastqTotalReads"]
        del biosample["r2FastqTotalReads"]
        del biosample["r1FastqLength"]
        del biosample["created"]
        del biosample["lotId"]

    # transforming the column names to lowercase for consistency
    column_data = list(
        map(lambda x: {"name": x["name"].lower(), "type": x["type"]}, column_data)
    )

    list_of_biosamples = list(
        map(lambda x: {k.lower(): v for k, v in x.items()}, list_of_biosamples)
    )
    return column_data, list_of_biosamples


def modify_metadata(row_data: dict, metadata_columns: list[dict]) -> dict:
    """
    Modifies the metadata to be displayed in the table

    Args:
        row_data (dict): A single row of data from the appsync
        metadata_columns (list[dict]): List of metadata columns

    Returns:
        metadata (dict): A single row modified metadata to be displayed in the table
    """
    # reads string and converts it to a dictionary
    metadata = json.loads(row_data["metadata"])

    # adds date and time filters to appropriate columns
    metadata_date_columns = list(
        map(
            lambda y: y["field"],
            filter(lambda x: x["filter"] == "agDateColumnFilter", metadata_columns),
        )
    )
    for column in metadata_date_columns:
        try:
            metadata[column] = parse_date(metadata[column])
        except KeyError:
            # column doesn't contain any date
            pass
    return metadata


def column_filter_type(dtype: str) -> tuple[str, list[str]]:
    """
    Returns the filter type and the filter options for the column based on the data type

    Args:
        dtype (str): Data type of the column

    Returns:
        filter_type (str): Filter type of the column (ag grid filter type)
        filter_options (list[str]): Filter options of the column

    """
    # TODO: try to make blank and not blank work

    if dtype == "True/False":
        return "agTextColumnFilter", [
            "equals",
            "notEqual",
            # "blank",
            # "notBlank",
        ]
    elif dtype == "Number":
        return "agNumberColumnFilter", [
            "equals",
            "notEqual",
            "lessThanOrEqual",
            "greaterThan",
            "greaterThanOrEqual",
            "lessThan",
            "inRange",
            # "blank",
            # "notBlank",
        ]
    elif dtype == "Date":
        return "agDateColumnFilter", [
            "equals",
            "notEqual",
            "greaterThan",
            "lessThan",
            "inRange",
            # "blank",
            # "notBlank",
        ]
    elif dtype == "Text":
        return "agTextColumnFilter", [
            "equals",
            "notEqual",
            "contains",
            "notContains",
            "startsWith",
            "endsWith",
            # "blank",
            # "notBlank",
        ]
    else:
        return "", []


def create_column_def(col: str, dtype: str, def_addition: dict = {}) -> dict:
    """
    Creates a column definition for ag grid based on the column name and data type

    Args:
        col (str): Column name
        dtype (str): Data type of the column
        def_addition (dict): Additional column definition to be added

    Returns:
        column_def (dict): Column definition for ag grid
    """
    col = col.lower()
    header = col  # .capitalize()
    filter_type, filter_options = column_filter_type(dtype)
    default_def = {
        "headerName": header,
        "field": col,
        "filter": filter_type,
        "filterParams": {
            "filterOptions": filter_options,
            "buttons": ["apply", "clear", "reset", "cancel"],
        },
        "menuTabs": ["filterMenuTab", "columnsMenuTab", "generalMenuTab"],
    }
    # make biosample name pinned to the left and checkbox selection
    if col == "biosamplename":
        return {
            **default_def,
            **{
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
                "pinned": "left",
            },
            **def_addition,
        }
    # make size column to be displayed in megabytes
    if col == "size":
        return {
            **default_def,
            **{
                "valueFormatter": {
                    "function": "(d3.format(',')((params.data.size / (1024 * 1024)).toFixed(2))) + ' MB'"
                },
                "filterValueGetter": {
                    "function": "(params.data.size / (1024 * 1024)).toFixed(2)"
                },
            },
            **def_addition,
        }
    # make number type columns displayed separated by commas for thousands
    if dtype == "Number":
        return {
            **default_def,
            **{
                "valueFormatter": {
                    "function": f"(params.data['{col}']) ? d3.format(',')(params.data['{col}']) : ''"
                },
                # "valueFormatter": {"function": "params.data['{col}'].toLocaleString()"},
                # "filterValueGetter": {"function": "params.data['{col}']"},
            },
            **def_addition,
        }
    # make upload date column to be displayed in mm/dd/yyyy format
    if dtype == "Date":
        return {
            **default_def,
            **{
                "filterParams": {
                    "browserDatePicker": True,
                },
                # "valueGetter": {
                # },
                "valueFormatter": {
                    "function": "d3.isoParse(params.value).toLocaleDateString('en-US')"
                },
                # "filterValueGetter": {
                #     "function": "d3.isoParse(params.value).toLocaleDateString('en-US')"
                # },
            },
            **def_addition,
        }
    if filter_type:
        return {
            **default_def,
            **def_addition,
        }
    else:
        return {
            "headerName": header,
            "field": col,
            "menuTabs": ["filterMenuTab", "generalMenuTab", "columnsMenuTab"],
            **def_addition,
        }


def clean_null_values_from_appsync_response(biosamples: list[dict]) -> list[dict]:
    """
    Cleans up the biosamples data from None values

    Args:
        biosamples (list[dict]): List of biosamples from appsync
    Returns:
        biosamples (list[dict]): List of biosamples from appsync with None values cleaned up
    """
    for biosample in biosamples:
        for key, value in biosample.items():
            if value is None:
                biosample[key] = get_alternative_value(appsync_data_types()[key])

    return biosamples


def create_column_defs_and_row_data(appsync_response: dict) -> tuple[list, list]:
    """
    Creates biosample column definitions and row data for the table based on the appsync response

    Args:
        appsync_response (dict): Biosamples response from appsync for a specific project

    Returns:
        column_defs (list): List of column definitions for ag grid
        row_data (list): List of row data for ag grid
    """
    # with open("appsync_response.json", "w") as f:
    #     json.dump(appsync_response, f, indent=4)

    # clean up the data from None values
    appsync_response["biosamples"]["items"] = clean_null_values_from_appsync_response(
        appsync_response["biosamples"]["items"],
    )
    # modify the data and separate the mandatory basejumper columns and metadata/custom columns
    (
        modified_mandatory_column_data,
        modified_mandatory_row_data,
    ) = modify_mandatory_data(appsync_response["biosamples"]["items"])
    mandatory_columns = map(
        lambda x: create_column_def(x["name"], x["type"]),  # , {"pinned": "left"}),
        [{"name": "biosampleName", "type": "Text"}] + modified_mandatory_column_data,
    )
    metadata_columns = list(
        map(
            lambda x: create_column_def(x["name"], x["type"]),
            json.loads(appsync_response["biosampleMetadataColumns"])["columns"],
        )
    )
    modified_metadata_row_data = list(
        map(
            lambda x: modify_metadata(x, metadata_columns=metadata_columns),
            modified_mandatory_row_data,
        )
    )
    # merge the mandatory basejumper row data and metadata/custom row data
    row_data = map(
        lambda x: {
            **{"biosamplename": x[0]["biosamplename"]},
            **x[0],
            **x[1],
        },
        zip(modified_mandatory_row_data, modified_metadata_row_data),
    )
    # merge the mandatory basejumper columns and metadata/custom columns
    column_defs = list(mandatory_columns) + list(metadata_columns)
    # pprint.pprint(column_defs)
    row_data = list(row_data)
    return column_defs, row_data
