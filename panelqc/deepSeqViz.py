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
app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO, dbc_css])

# system arguments
if len(sys.argv) > 1:
    dirname = sys.argv[1]
    regionFiles = glob(os.path.join(dirname, "Panel_regionQC_*"))
    summaryFiles = glob(os.path.join(dirname, "Sample_summaryQC_*"))


def getRegionQC(regionFiles):
    """Concat QCs across files with sample names"""
    dfList = []
    for file in regionFiles:
        sampleDf = pd.read_csv(file, sep="\t", low_memory=False)

        sample = os.path.basename(file).split(".")[0].replace(
                "Panel_regionQC_", ""
            ).replace(".tsv", "").replace("Sample_summaryQC_", "")
        sampleDf['Sample'] = sample
        dfList.append(sampleDf)
    return pd.concat(dfList).reset_index(drop=True)


def getSampleMeanSd(df, sample):
    """Get mean and 2SD cut-off for the sample"""
    mean = list(df.loc[df['Sample'].str.contains(sample), 'sampleMean'])[0]
    sd = list(df.loc[df['Sample'].str.contains(sample), 'sampleSD'])[0]
    mean2sd = mean - 2*sd
    return mean, mean2sd


def generateScatterPlot(samplesDf, x, y, template=None, labels=None):
    if labels is None:
        labels = {
            'Sample': 'Sample(s)',
            'fold_80': 'Fold-80',
            'CV': 'Coefficient of variation',
            'sampleMean': 'Average depth of coverage',
            'sampleMedian': 'Median depth of coverage',
            'uniformityOfCoverage': 'Uniformity of Coverage',
        }
    lnFig = px.line(
        data_frame=samplesDf.sort_values(by=y),
        x=x, y=y
    )
    return px.scatter(
        data_frame=samplesDf.sort_values(by=y),
        x=x, y=y, labels=labels,
        marginal_y='box', template=template,
    ).update_yaxes(rangemode="tozero").add_traces(lnFig.data)


def generateFigureCard(title, id, fig):
    return [
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                dcc.Graph(
                    id=id,
                    figure=fig
                ),
            ]
        ),
    ]


def generateInfoCard(title, header, para=""):
    return [
            dbc.CardHeader(header),
            dbc.CardBody([
                html.H5(title, className="card-title"),
                html.P(
                    para,
                    className="card-text",
                ),
            ]),
    ]


regionDf = getRegionQC(regionFiles)

colOrder = [
    "Sample", "Chr", "Start", "End", "Gene", "RegionLength", "paddedLength",
    "Mean", "SD", "basecount_2SD", "basecount_1.5SD", "basecount_1SD"
]

regionDf = regionDf[colOrder]
uniqueRegionsDf = regionDf[[
    "Chr", "Start", "End", "Gene", "RegionLength"
]].drop_duplicates()

nGenes = uniqueRegionsDf.loc[
    uniqueRegionsDf['RegionLength'] > 1, 'Gene'
].nunique()

ngRegions = len(uniqueRegionsDf[uniqueRegionsDf['RegionLength'] > 1])
noSnps = len(uniqueRegionsDf[uniqueRegionsDf['RegionLength'] == 1])

samplesDf = getRegionQC(summaryFiles)
samplesDf.rename(columns={
    'cut_1pt5SD': 'cut_1.5SD',
    'Pcntbase_1.5SD': 'Pcntbase_1pt5SD'
}, inplace=True)
samples = list(samplesDf['Sample'].unique())

minDepth = regionDf.Mean.min()
maxDepth = regionDf.Mean.max()
output = []

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
    {'field': 'sampleMedian', 'minWidth': 80,
     'headerTooltip': "Median depth of coverage across all the "
     "panel positions"},
    {'field': 'CV', 'minWidth': 80,
     'headerTooltip': "Coefficient of variation of  depth of coverage across"
     " all the panel positions"},
    {'field': 'uniformityOfCoverage', 'minWidth': 80,
     'headerTooltip': "Uniformity of depth of coverage across"
     " all the panel positions"},
    {'field': 'fold_80', 'minWidth': 80,
     'headerTooltip': "Fold-80. The fold of additional sequencing required to"
     " ensure that 80% of the target bases achieve Average depth of coverage"},
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
            samples,
            samples[0:2],
            id="sample",
            clearable=False,
            multi=True,
            searchable=True
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

row1 = dbc.Row(
    [
        dbc.Col(dbc.Card(generateInfoCard(
            title=f"{samplesDf['Sample'].nunique()}",
            header="#Samples in the cohort"
        ), color="primary", outline=True), width=2),
        dbc.Col(dbc.Card(generateInfoCard(
            title=f"{round(uniqueRegionsDf['RegionLength'].sum()/1e6, 2)} "
            "Mbp",
            header="Size of the panel"
        ), color="primary", outline=True), width=2),
        dbc.Col(dbc.Card(generateInfoCard(
            title=f"{nGenes}",
            header="Number of Genes"
        ), color="primary", outline=True), width=2),
        dbc.Col(dbc.Card(generateInfoCard(
            title=f"{ngRegions}",
            header="Number of Gene Regions"
        ), color="primary", outline=True), width=3),
        dbc.Col(dbc.Card(generateInfoCard(
            title=f"{noSnps}",
            header="Number of SNPs outside gene regions",
        ), color="primary", outline=True), width=3),
    ],

    className="mb-3",
)

row2 = dbc.Row(
    [
        dbc.Col(dbc.Card(generateFigureCard(
            title="Average Depth of Coverage", id='adc',
            fig=generateScatterPlot(
                samplesDf=samplesDf, x='Sample', y='sampleMean',
            )
        ), color="primary", outline=True, id="adcCard"), width=6),
        dbc.Col(dbc.Card(generateFigureCard(
            title="Uniformity of Coverage", id='uoc', fig=generateScatterPlot(
                samplesDf=samplesDf, x='Sample', y='uniformityOfCoverage',
            )
        ), color="primary", outline=True, id="uocCard"), width=6),
    ],
    className="mb-3",
)

row3 = dbc.Row(
    [
        dbc.Col(dbc.Card(generateFigureCard(
            title="Coefficient of variation", id='cv',
            fig=generateScatterPlot(
                samplesDf=samplesDf, x='Sample', y='CV',
            )
        ), color="primary", outline=True, id="cvCard"), width=6),
        dbc.Col(dbc.Card(generateFigureCard(
            title="Fold-80", id='f80', fig=generateScatterPlot(
                samplesDf=samplesDf, x='Sample', y='fold_80',
            )
        ), color="primary", outline=True, id="f80Card"), width=6),
    ],
    className="mb-3",
)


cards = html.Div([html.Br(), row1, row2, row3])

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
], label="Sample QC", activeTabClassName="fw-bold fst-italic")

tab_summaryMetrics = dbc.Tab([
    dbc.Row([
        cards,
    ]),

], label="Cohort QC", activeTabClassName="fw-bold fst-italic")

tabs = dbc.Card(dbc.Tabs([tab_summaryMetrics, tab_regionQc, tab_tableBrowser]))

app.layout = dbc.Container(
    [
        header,
        dbc.Row([
            dbc.Col(
                [
                    ThemeChangerAIO(
                        aio_id="theme",
                        radio_props={"value": dbc.themes.COSMO},
                        button_props={"color": "dark"},
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
    Output("qcPlots", "children"),
    Output("adcCard", "children"),
    Output("uocCard", "children"),
    Output("cvCard", "children"),
    Output("f80Card", "children"),
    Input("regionTable", "rowData"),
    Input("sample", "value"),
    Input("depth", "value"),
    Input("numBins", "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def updateRegionTable(vdata, sample, depth, numBins, theme):
    dff = pd.DataFrame(vdata) if vdata else regionDf
    nSamples = [sample] if type(sample) == 'str' else list(sample)
    template = template_from_url(theme)
    dff = regionDf if sample == 'All' else dff[
        regionDf['Sample'].isin(nSamples)
    ]
    dff = dff[dff.Mean.between(depth[0], depth[1])]
    output = []
    for sampleName in dff.Sample.unique():
        tfg = px.histogram(
            data_frame=dff[dff['Sample'] == sampleName], x="Mean",
            title=sampleName,  marginal="box",
            template=template, nbins=numBins
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
    adcFig = generateFigureCard(
            title="Average Depth of Coverage", id='adc',
            fig=generateScatterPlot(
                samplesDf=samplesDf, x='Sample', y='sampleMean',
                template=template
            )
        )

    uocFig = generateFigureCard(
            title="Uniformity of Coverage", id='uoc', fig=generateScatterPlot(
                samplesDf=samplesDf, x='Sample', y='uniformityOfCoverage',
                template=template
            )
        )

    cvFig = generateFigureCard(
            title="Coefficient of variation", id='cv',
            fig=generateScatterPlot(
                samplesDf=samplesDf, x='Sample', y='CV', template=template
            )
        )

    f80Fig = generateFigureCard(
            title="Fold-80", id='f80', fig=generateScatterPlot(
                samplesDf=samplesDf, x='Sample', y='fold_80', template=template
            )
        )

    return output, adcFig, uocFig, cvFig, f80Fig


@callback(
    Output("download", "data"),
    Input("dnldButton", "n_clicks"),
    State("regionTable", "virtualRowData"),
    prevent_initial_call=True,
)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_csv, "filtered.csv")


if __name__ == "__main__":
    app.run_server(debug=True)
