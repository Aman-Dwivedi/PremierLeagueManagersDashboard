"""
Author: Aman Dwivedi & Aditya Kumar
This creates a dashboard on streamlit with four visualizations
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import json


def loadDataFrame():
    """
    Loads the dataframe from the json
    """
    df = pd.DataFrame.from_dict(json.load(open("managerStats.json")), orient='index')

    maxPercentages = {"pointsEarned": max(df.to_dict()["pointsEarned"].values()),
                      "gamesPlayed": max(df.to_dict()["gamesPlayed"].values()),
                      "goalsScored": max(df.to_dict()["goalsScored"].values()),
                      "goalsConceded": max(df.to_dict()["goalsConceded"].values()),
                      "comebacks": max(df.to_dict()["comebacks"].values())}
    labels = {"pointsEarned": "Points Earned", "gamesPlayed": "Games Played",
              "goalsScored": "Goals Scored", "goalsConceded": "Goals Conceded",
              "comebacks": "Comebacks"}
    return df, maxPercentages, labels

def makeParallelCoordinate(df, labels, value):
    """
    Makes the parallel coordinate plot
    """
    fig = px.parallel_coordinates(df, color="pointsEarned",
                                  dimensions=["pointsEarned", "gamesPlayed", "goalsScored", "goalsConceded",
                                              "comebacks"], labels=labels,
                                  color_continuous_scale=px.colors.sequential.Turbo)
    fig.update_layout(
        margin=dict(l=50, r=50, t=50, b=50),
    )
    for val in value:
        row = df.loc[val].to_list()
        for i, v in enumerate(fig.data[0].dimensions):
            v.update({'constraintrange': [row[i] - row[i] / 100000, row[i]]})
    return fig


def makeRadarChart(df, maxPercentages, value):
    """
    Makes the radar chart
    """
    if value is None or len(value) == 0:
        return px.line_polar(template="plotly_dark")
    radi = []
    angle = []
    group = []
    actualVal = []
    for val in value:
        temp = df.loc[val].to_list()
        actualVal += df.loc[val].to_list()
        i = 0
        while i < len(maxPercentages.values()):
            temp[i] /= list(maxPercentages.values())[i]
            i += 1
        radi += temp
        angle += df.columns.to_list()
        group += [val] * len(df.columns.to_list())
        radi.pop(-1)
        angle.pop(-1)
        group.pop(-1)
        actualVal.pop(-1)

    radarDf = pd.DataFrame(dict(
        radi=radi,
        angle=angle,
        group=group,
        actualVal=actualVal))
    fig = px.line_polar(radarDf, r='radi', theta='angle', line_close=True, color='group', range_r=[0, 1],
                        hover_name="actualVal", template="plotly_dark", hover_data={'radi':False, 'angle': False, 'group': False})
    fig.update_traces(fill='toself', mode="markers+lines")
    fig.layout.polar.radialaxis.tickvals = []
    return fig

def makeLinePlot(df, value):
    """
    Makes the line plot
    """
    if value is None or len(value) == 0:
        return px.line()
    temp = pd.DataFrame(dict(
        x=[],
        y=[]
    ))
    fig = px.line(temp, x='x', y='y', labels={"x": "Seasons", "y": "League Table Finish", }, template="simple_white")
    for val in value:
        seasons = df.loc[val].to_dict()["leagueFinish"]
        x = []
        y = []
        i = 0
        for season in range(int(seasons[0][1][:4]), int(seasons[-1][1][:4]) + 1):
            if seasons[i][1] == f"{season}-{str(season + 1)[2:]}":
                y.append(seasons[i][0])
                i += 1
            else:
                y.append(None)
            x.append(f"{season}-{str(season + 1)[2:]}")
        annotations = []  # (x, y, text)
        i = 0
        while i < len(y):
            if y[i] == 1:
                annotations.append((x[i], y[i], "Champion!"))
            elif i < len(y) - 1 and y[i + 1] == None and y[i] and y[i] >= 18:
                annotations.append((x[i], y[i], "Relegated"))
            elif i < len(y) - 1 and y[i + 1] == None and y[i]:
                annotations.append((x[i], y[i], "Sacked/Left"))
            if i == len(y) - 1 and x[i] != "2017-18":
                annotations.append((x[i], y[i], "Sacked/Left"))
            i += 1
        fig.add_scatter(y=y, x=x, name=val)
        for annotation in annotations:
            fig.add_annotation(x=annotation[0], y=annotation[1], text=annotation[2], showarrow=False,
                               yshift=15 if annotation[2] == "Champion!" else -15)
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_type='category'
    )
    fig.update_yaxes(dtick=1)
    fig.update_traces(mode='lines+markers')
    return fig

def makeQuadrantPlot(df, yaxis, value):
    """
    Make the quadrant plot
    """
    df['pointsPerGame'] = df['pointsEarned'] / df['gamesPlayed']
    if yaxis == "goalsScoredPerGame":
        df[yaxis] = df['goalsScored'] / df['gamesPlayed']
    elif yaxis == "goalsConcededPerGame":
        df[yaxis] = df['goalsConceded'] / df['gamesPlayed']
    else:
        df[yaxis] = df['goalsScored'] - df['goalsConceded']
    fig = px.scatter(df, x="pointsPerGame", y=yaxis, template="simple_white", hover_name=df.index)
    for val in value:
        fig.add_scatter(y=[df.loc[val].to_dict()[yaxis]], x=[df.loc[val].to_dict()["pointsPerGame"]], mode="markers", name=val)
    fig.add_vline(x=1.5, line_width=1, opacity=0.5, line_color="white")
    fig.add_hline(y=0 if yaxis == "goalDifference" else 1, line_width=1, opacity=0.5, line_color="white")
    fig.update_traces(textposition='top center')
    return fig

def streamLitApp(df, maxPercentages, labels):
    """
    Makes the streamlit dashboard
    """
    st.set_page_config(layout="wide")
    st.image("title.png")
    st.title("Analysis of Managers")
    leftColumn, rightColumn = st.columns([1, 1], gap="medium")
    with rightColumn:
        value = st.multiselect(
            'Select Managers to compare',
            sorted(df.index.to_list()))
        st.subheader("Line Plot")
        linePlotFig = makeLinePlot(df, value)
        st.plotly_chart(linePlotFig, use_container_width=True)
        st.subheader("Radar Plot")
        radarPlotFig = makeRadarChart(df, maxPercentages, value)
        st.plotly_chart(radarPlotFig, use_container_width=True)

    with leftColumn:
        st.subheader("Parallel Coordinate")
        parallelCoordFig = makeParallelCoordinate(df, labels, value)
        st.markdown("")
        st.plotly_chart(parallelCoordFig, use_container_width=True)
        st.subheader("Quadrant Plot")
        yaxis = st.selectbox(
            'Select y axis',
            ["goalsScoredPerGame", "goalsConcededPerGame", "goalDifference"])
        quadrantPlotFig = makeQuadrantPlot(df, yaxis, value)
        st.plotly_chart(quadrantPlotFig, use_container_width=True)

def main():
    df, maxPercentages, labels = loadDataFrame()
    streamLitApp(df, maxPercentages, labels)

main()