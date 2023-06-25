"""
DeepSeqCoverageQC Explorer
Plotly Dash app to explore DeepSeqCoverageQC data
"""

import sys
import os
from glob import glob
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback, State
import plotly.express as px
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url

# stylesheet with the .dbc class
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/\
    dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.PULSE, dbc_css])

# system arguments
if len(sys.argv) > 1:
    dirname = sys.argv[1]
    regionFiles = glob(os.path.join(dirname, "Panel_regionQC_*"))
    summaryFiles = glob(os.path.join(dirname, "Sample_summaryQC_*"))


def getRegionQC(regionFiles):
    """Concat QCs across files with sample names"""
    dfList = []
    for file in regionFiles:
        sampleDf = pd.read_csv(file, sep="\t")

        sample = os.path.basename(file).split(".")[0].replace(
                "Panel_regionQC_", ""
            ).replace(".tsv", "").replace("Sample_summaryQC_", "")
        sampleDf['Sample'] = sample
        dfList.append(sampleDf)
    return pd.concat(dfList).reset_index(drop=True)


regionDf = getRegionQC(regionFiles)

colOrder = [
    "Sample", "Chr", "Start", "End", "Gene", "RegionLength", "paddedLength",
    "Mean", "SD", "basecount_2SD", "basecount_1.5SD", "basecount_1SD"
]

regionDf = regionDf[colOrder]

samplesDf = getRegionQC(summaryFiles)
samplesDf.rename(columns={
    'cut_1pt5SD': 'cut_1.5SD',
    'Pcntbase_1.5SD': 'Pcntbase_1pt5SD'
}, inplace=True)
samples = list(samplesDf['Sample'].unique())

minDepth = regionDf.Mean.min()
maxDepth = regionDf.Mean.max()
output = []


def getSampleMeanSd(df, sample):
    mean = list(df.loc[df['Sample'].str.contains(sample), 'sampleMean'])[0]
    sd = list(df.loc[df['Sample'].str.contains(sample), 'sampleSD'])[0]
    mean2sd = mean - 2*sd
    return mean, mean2sd


for sample in regionDf.Sample.unique():
    tfg = px.histogram(
        data_frame=regionDf[regionDf['Sample'] == sample], x="Mean",
        title=sample  # template=template_from_url(theme)
    )
    mean, mean2sd = getSampleMeanSd(samplesDf, sample)
    tfg.add_vline(x=mean, line_color="magenta")
    tfg.add_vline(x=mean2sd, line_color="red")
    output.append(dcc.Graph(id='example-graph'+str(sample), figure=tfg))


header = html.H4(
    "DeepSeqCoverageQC Explorer",
    className="bg-primary text-white p-2 mb-2 text-center"
)

colDefSummaryQc = [
    {'field': 'Sample', 'type': 'text', 'filter': 'agTextColumnFilter',
     'minWidth': 150, 'headerTooltip': "Sample name"},
    {'field': 'sampleMean', 'minWidth': 80,
     'headerTooltip': "Average depth of coverage across all the "
     "panel positions"},
    {'field': 'sampleSD', 'minWidth': 80,
     'headerTooltip': "Standard deviation of depth of coverage across "
     "all the panel positions"},
    {'field': 'cut_2SD', 'minWidth': 80,
     'headerTooltip': "Cut-off value with sample average coverage - 2*SD)"},
    {'field': 'cut_1.5SD', 'minWidth': 80,
     'headerTooltip': "Cut-off value with sample average coverage - 1.5*SD)"},
    {'field': 'cut_1SD', 'minWidth': 80,
     'headerTooltip': "Cut-off value with sample average coverage - 1*SD)"},
    {'field': 'Pcntbase_2SD', 'minWidth': 80,
     'headerTooltip': "% bases with depth of covarafe > "
     "(sample average coverage - 2*SD)"},
    {'field': 'Pcntbase_1.5SD', 'minWidth': 80,
     'headerTooltip': "% bases with depth of covarafe > "
     "(sample average coverage - 1.5*SD)"},
    {'field': 'Pcntbase_1SD', 'minWidth': 80,
     'headerTooltip': "% bases with depth of covarafe > "
     "(sample average coverage - 1*SD)"},

]

tableSummary = html.Div(
    dag.AgGrid(
        id="summaryTable",
        rowData=samplesDf.to_dict("records"),
        columnDefs=colDefSummaryQc,
        defaultColDef={
            "resizable": True, "sortable": True,
            "minWidth": 120, "floatingFilter": True,
            "type": "numberColumn", "filter": "agNumberColumnFilter",
            "filterParams": {
                "buttons": ["reset", "apply"],
            },
        },
        columnSize="sizeToFit",
        dashGridOptions={"pagination": True, "paginationPageSize": 5},
        className="ag-theme-balham headers1",
        # https://dashaggrid.pythonanywhere.com/layout/themes
        style={"height": 200, "width": "100%"},
    )
)

colDefPanelQc = [
    {'field': 'Sample', 'type': 'text', 'filter': 'agTextColumnFilter',
     'minWidth': 150, 'headerTooltip': "Sample name"},
    {'field': 'Chr', 'type': 'text', 'filter': 'agTextColumnFilter',
     'minWidth': 70, 'headerTooltip': "Chromosome name"},
    {'field': 'Start', 'minWidth': 80, 'headerTooltip': "Start position"},
    {'field': 'End', 'minWidth': 80, 'headerTooltip': "End position"},
    {'field': 'Gene', 'type': 'text', 'filter': 'agTextColumnFilter',
     'headerTooltip': "Gene/Region name"},
    {'field': 'RegionLength', 'minWidth': 80,
     'headerTooltip': "Region length"},
    # {'field': 'paddedLength', 'minWidth': 80,
    # 'headerTooltip': "Padded region length"},
    {'field': 'Mean', 'minWidth': 80,
     'headerTooltip': "Average depth of coverage across region"},
    {'field': 'SD', 'minWidth': 80,
     'headerTooltip': "Standard deviation of depth of coverage across region"},
    {'field': 'basecount_2SD', 'minWidth': 80,
     'headerTooltip': "Number of bases in region having depth of coverage >"
     " (sample average coverage - 2*SD)"},
    {'field': 'basecount_1.5SD', 'minWidth': 80,
     'headerTooltip': "Number of bases in region having depth of coverage > "
     "(sample average coverage - 1.5*SD)"},
    {'field': 'basecount_1SD', 'minWidth': 80,
     'headerTooltip': "Number of bases in region having depth of coverage > "
     "(sample average coverage - 1*SD)"},
]

regionTable = html.Div(
    dag.AgGrid(
        id="regionTable",
        rowData=regionDf.to_dict("records"),
        columnDefs=colDefPanelQc,
        defaultColDef={
            "resizable": True, "sortable": True,
            "minWidth": 120, "floatingFilter": True,
            "type": "numberColumn", "filter": "agNumberColumnFilter",
            "filterParams": {
                "buttons": ["reset", "apply"],
            },
        },
        columnSize="sizeToFit",
        dashGridOptions={"pagination": True, "paginationPageSize": 20},
        className="ag-theme-balham headers1",
        # https://dashaggrid.pythonanywhere.com/layout/themes
        style={"height": 400, "width": "100%"},
    )
)

sampleDropdown = html.Div(
    [
        dbc.Label("Select Sample"),
        dcc.Dropdown(
            ['All'] + samples,
            'All',
            id="sample",
            clearable=False,
        ),
    ],
    className="mb-4",
)

nBins = html.Div(
    [
        dbc.Label("Number of bins for RegionQC Histogram"),
        dcc.Input(id="numBins", type="number", value=100),
    ],
    className="mb-4",
)

slider = html.Div(
    [
        dbc.Label("Select Mean Depth of coverage"),
        dcc.RangeSlider(
            minDepth,
            maxDepth,
            5,
            id="depth",
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
            value=[minDepth, maxDepth],
            className="p-0",
        ),
    ],
    className="mb-4",
)

tableControls = dbc.Card(
    [sampleDropdown, slider, nBins],
    body=True,
)

downloadButton = dbc.Button(
    "Download Filtered CSV", id="dnldButton", color="primary", className="me-1"
)
downloadComponent = html.Div([dcc.Download(id="download")])


# region Cards for Summary metrics tab

card_content = [
    dbc.CardHeader("Size of the Panel"),
    dbc.CardBody(
        [
            html.H5("Card title", className="card-title"),
            html.P(
                "This is some card content that we'll reuse",
                className="card-text",
            ),
        ]
    ),
]

row_1 = dbc.Row(
    [
        dbc.Col(dbc.Card(card_content, color="primary", outline=True)),
        dbc.Col(dbc.Card(card_content, color="secondary", outline=True)),
        dbc.Col(dbc.Card(card_content, color="info", outline=True)),
    ],
    className="mb-4",
)

row_2 = dbc.Row(
    [
        dbc.Col(dbc.Card(card_content, color="success", outline=True)),
        dbc.Col(dbc.Card(card_content, color="warning", outline=True)),
        dbc.Col(dbc.Card(card_content, color="danger", outline=True)),
    ],
    className="mb-4",
)

row_3 = dbc.Row(
    [
        dbc.Col(dbc.Card(card_content, color="light", outline=True)),
        dbc.Col(dbc.Card(card_content, color="dark", outline=True)),
    ]
)

cards = html.Div([html.Br(), row_1, row_2, row_3])

# endregion

tab_tableBrowser = dbc.Tab([
    html.Br(),
    html.H4("Region QC Table", style={'textAlign': 'center'}),
    dbc.Row(
       dbc.Col([downloadComponent, downloadButton], width={"size": 3}),
    ),
    html.Br(),
    dbc.Row([
        dbc.Col([regionTable], width=12),
    ]),
    html.Br(),
    html.H4("Sample Summary QC Table", style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col([tableSummary], width=12),
    ]),
], label="QC Table Browser", activeTabClassName="fw-bold fst-italic")

tab_regionQc = dbc.Tab([
    dbc.Row([
        dbc.Col([tableControls], width=3),
        dbc.Col([html.Div(children=output, id="qcPlots")], width=9)
    ]),
], label="Region QC", activeTabClassName="fw-bold fst-italic")

tab_summaryMetrics = dbc.Tab([
    dbc.Row([
        cards,
    ]),

], label="Summary Metrics", activeTabClassName="fw-bold fst-italic")

tabs = dbc.Card(dbc.Tabs([tab_tableBrowser, tab_regionQc, tab_summaryMetrics]))

app.layout = dbc.Container(
    [
        header,
        dbc.Row([
            dbc.Col(
                [
                    ThemeChangerAIO(
                        aio_id="theme", radio_props={"value": dbc.themes.PULSE}
                    )
                ]
            ),
        ], justify="end"),
        dbc.Row(
            [
                dbc.Col([tabs], width=12)
            ]
        ),
    ],
    fluid=True,
    className="dbc",
)


@callback(
    Output("regionTable", "rowData"),
    Output("qcPlots", "children"),
    Input("regionTable", "rowData"),
    Input("sample", "value"),
    Input("depth", "value"),
    Input("numBins", "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def updateRegionTable(vdata, sample, depth, numBins, theme):
    dff = pd.DataFrame(vdata) if vdata else regionDf
    dff = regionDf if sample == 'All' else dff[
        regionDf['Sample'] == sample
    ]
    dff = dff[dff.Mean.between(depth[0], depth[1])]
    output = []
    for sampleName in dff.Sample.unique():
        tfg = px.histogram(
            data_frame=dff[dff['Sample'] == sampleName], x="Mean",
            title=sampleName,  marginal="box",
            template=template_from_url(theme), nbins=numBins
        )
        mean, mean2sd = getSampleMeanSd(samplesDf, sampleName)
        tfg.add_vline(x=mean, line_color="magenta")
        tfg.add_vline(x=mean2sd, line_color="red")
        tfg.update_layout(
            bargap=0.1,
            xaxis_title="Average depth of coverage of region",
            yaxis_title="Number of regions",
        )
        output.append(
            dcc.Graph(id=f'example-graph{str(sampleName)}', figure=tfg)
        )

    return dff.to_dict("records"), output


@callback(
    Output("download", "data"),
    Input("dnldButton", "n_clicks"),
    State("regionTable", "virtualRowData"),
    prevent_initial_call=True,
)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_csv, "filtered_csv.csv")


if __name__ == "__main__":
    app.run_server(debug=True)
