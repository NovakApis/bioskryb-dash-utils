# metadata_and_group_creation

## Description

This module allows you to:

- generate a view that includes:
  - metadata (biosample) table
    - filter & sort it
    - import & export data to & from it
    - create groups out of selected rows
    - etc..
  - group selection table
    - select groups
    - pass the dcc.Store id that contains the selected groups

## How to use

### NOTE:

In order to use this module (gather biosample table data from the bioskryb platform), one needs to pass a **PAYLOAD** object to view_part. The **PAYLOAD** object is a dictionary in this form:

```python
PAYLOAD = {
    "project_id": project_id, # bioskryb project id
    "app_sync_endpoint": os.environ["APP_SYNC_GRAPHQL_ENDPOINT"],
    "app_sync_user": {
        "username": os.environ["APP_SYNC_USER_USERNAME"],
        "password": os.environ["APP_SYNC_USER_PASSWORD"],
        "clientId": os.environ["APP_SYNC_USER_CLIENT_ID"],
        "appClientSecret": os.environ["APP_SYNC_USER_APP_CLIENT_SECRET"], # probably not needed
    }
}
```

Example of how to use the module:

```python

...

from metadata_and_group_creation.layout.main import get_components as get_metadata_components

(
    metadata_and_group_creation_main_view,
    import_metadata_callbacks,
    metadata_exported_ids,
) = get_metadata_components()



app.layout = html.Div(
    children=[
        ...
        metadata_and_group_creation_main_view(PAYLOAD),
        ...
    ]
)

import_metadata_callbacks(app)

...

# use metadata_exported_ids to get the selected biosample ids, etc.

...

```
