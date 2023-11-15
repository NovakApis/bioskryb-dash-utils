import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify


def html_header(name):
    return dmc.Header(
        html_2el_layout(
            html.Img(src="./assets/bioskryb_logo.png"),
            html.H1(name, style={"color": "white"}),
        ),
        height=120,
        style={"backgroundColor": "rgb(18, 40, 77)"},
    )


def html_2el_layout(element1, element2):
    return html.Div(children=[element1, element2], style=two_col_style())


def two_col_style():
    return {
        "display": "grid",
        "gridTemplateColumns": "35% 65%",
        "margin-right": "30px",
        "margin-left": "10px",
        "margin-top": "10px",
    }


def three_col_style():
    return {
        "display": "grid",
        "gridTemplateColumns": "30% 30% 40%",
        "margin-right": "30px",
        "margin-left": "10px",
    }


def header_colors():
    return {"bg_color": "#12284d", "font_color": "white", "light_logo": True}


PRIMARY_COLOR = "#12284d"
SECONDARY_COLOR = "#4682b4"


def default_margins():
    return dict(l=10, r=10, t=10, b=10)


def html_section_header(name, id):
    return html.Div(
        id=id,
        style={
            "width": "100%",
            "background": header_colors()["bg_color"],
            "color": header_colors()["font_color"],
            "margin-right": "0px",
            "margin-left": "0px",
            "margin-bottom": "0px",
        },
        children=[
            html.Div(
                name,
                className="sample-header",
                style={
                    "display": "none",
                },
            )
        ],
    )


def build_button(id, button_text, button_icon=None):
    return dmc.Button(
        button_text,
        id=id,
        leftIcon=[DashIconify(icon=button_icon)] if button_icon else None,
        variant="outline",
        size="md",
        radius="lg",
        color="violet",
        style={
            "margin-right": "15px",
            "margin-left": "15px",
            "borderRadius": 5,
            "border": "1px solid rgba(112, 72, 232, 0.15)",
            "font-weight": "400",
        },
    )


def html_button(id, text, parent_style={}, **kwargs):
    return html.Div(
        children=[
            html.Button(
                text,
                id=id,
                n_clicks=0,
                className="gene_download_button",
                **kwargs,
            ),
        ],
        style=parent_style,
    )
