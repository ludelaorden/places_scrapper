import pandas as pd
import plotly.express as px
import os


def showMap(fig):
    """
    This function is responsible for opening the map in the browser. The HTML file is saved with specified name.

    :param fig:
    :return:
    """
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # open the browser
    fig.show()

    # save the page as an HTML file
    htmlSavingDirectory = 'savedVisualisations/'
    htmlFilename = "measure_points_visualisation_v1"
    fig.write_html(htmlSavingDirectory + htmlFilename + ".html")


def setPlaces(points):
    """
    This function is responsible for visualisation of points on the map.

    :param points: DataFrame containing information about the points to visualise.
    :return: figure of type scatter_mapbox (from plotly.express library)
    """
    points['size'] = 1000
    points['color'] = 1

    color_scale = [(0, 'green'), (1, 'red')]

    fig = px.scatter_mapbox(points,
                            lat="lat",
                            lon="lon",
                            hover_name="title",
                            # hover_data=["title", "size"],
                            # color_continuous_scale=px.colors.sequential.Plasma,
                            color='type',
                            size="size",
                            zoom=10,
                            height=800,
                            width=1200)

    return fig


def visualiseCollectedPoints():
    """
    This function allows visualising collected points using measure points. All CSV files from the database
    directory are read and the data is converted into DataFrames.
    """
    # read all files from directory
    path = "database"
    files = os.listdir(path)

    all_places = pd.DataFrame()
    # loop through each file
    for filename in files:
        print("filename:", filename)
        df = pd.read_csv(path + '/' + filename, index_col=False)
        frames = [all_places, df]
        all_places = pd.concat(frames)

    print(all_places.info())

    # set places on the map
    placesMap = setPlaces(all_places)

    # open map in browser
    showMap(placesMap)


def visualiseMeasurePoints(pointsDirectory, numberOfRows, numberOfColumns):
    """
    This function allows visualising points used to collect places from Google Maps.

    :param pointsDirectory: directory where csv files with generated points are saved
    :param numberOfRows: number of rows in measure points dataset
    :param numberOfColumns: number of columns in measure points dataset
    """
    measurePoints = pd.read_csv(pointsDirectory + "measure_points_" + str(numberOfRows) + 'r_' + str(numberOfColumns) + 'c'+ ".csv", index_col=False)
    measurePoints['type'] = 'measure point'
    measurePoints['title'] = 'measure point'
    map = setPlaces(measurePoints)
    showMap(map)


if __name__ == "__main__":
    pointsDirectory = 'generatedPoints/'
    # number of "steps" (resolution of the division of the area --> greater value gives more details)
    numberOfColumns = 1
    numberOfRows = 1

    #visualiseCollectedPoints()
    visualiseMeasurePoints(pointsDirectory, numberOfRows, numberOfColumns)
