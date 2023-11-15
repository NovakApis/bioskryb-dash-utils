import os
import pprint
import sys

from dash import Dash
from dotenv import load_dotenv
from layout.main import get_components

# sys.path.insert(0, f"{(os.path.dirname(os.path.realpath(__file__)))}/")
# pprint.pprint(sys.path)


load_dotenv()


app = Dash(__name__)

project_id = "d8fe6919-08c9-44d4-b6c7-4015f4da19ed"
project_id = "e390948c-ee85-4ba3-a1dd-fd08c9cc942b"
PAYLOAD = {
    "project_id": project_id,
    "app_sync_endpoint": os.environ["APP_SYNC_GRAPHQL_ENDPOINT"],
    "app_sync_user": {
        "username": os.environ["APP_SYNC_USER_USERNAME"],
        "password": os.environ["APP_SYNC_USER_PASSWORD"],
        "clientId": os.environ["APP_SYNC_USER_CLIENT_ID"],
        "appClientSecret": os.environ["APP_SYNC_USER_APP_CLIENT_SECRET"],
    },
}

pprint.pprint(PAYLOAD)

main_view, import_callbacks, ids = get_components()

app.layout = main_view(payload=PAYLOAD)

import_callbacks(app)


if __name__ == "__main__":
    app.run_server(debug=True)
