import pandas as pd
import geohash2

def checkLocationOfBorderPoints(pointA, pointB):
    """
    This function checks if the border points are set correctly - pointA is the left upper corner, pointB is the
    right bottom corner.

    Latitude of pointA must be greater than the latitude of pointB.
    Longitude of pointA must be smaller than the longitude of pointB.

    Example of A and B points set up:
        Point A --> (left_top_lat, left_top_lon)
        Point B --> (right_bot_lat, right_bot_lon)

        Covered area:
        A -- -- -- -- --
        |               |
        |               |
        -- -- -- -- -- B

    :return: boolean value - True if points are set correctly
    """

    if pointA[0] > pointB[0] and pointA[1] < pointB[1]:
        # print("PointA and PointB are set correctly.")
        return True  # Points are set correctly
    else:
        errorMessage = """
        Error: PointA and PointB are set incorrectly.
        
        Latitude of pointA must be greater than the latitude of pointB.
        Longitude of pointA must be smaller than the longitude of pointB.
    
        Example of A and B points set up:
            Point A --> (left_top_lat, left_top_lon)
            Point B --> (right_bot_lat, right_bot_lon)

            Covered area:
            A -- -- -- -- --
            |               |
            |               |
            -- -- -- -- -- B
        """
        print(errorMessage)
        return False  # Points are set incorrectly
    
def convertGeohashToLatLong(var_geohash):

    lat, lon, lat_err, lon_err = geohash2.decode_exactly(var_geohash)
    lat_err = 0.00000000000001
    lon_err = 0.00000000000001
    top_left = (lat + lat_err, lon - lon_err)
    bottom_right = (lat - lat_err, lon + lon_err)

    return top_left[0], top_left[1], bottom_right[0], bottom_right[1]    

def setUpBorderPoints(savingDirectory, pointA, pointB, ):
    """
    This function generates a CSV file with border points.

    :return: DataFrame containing the location of border points: latitude and longitude
    """

    lat = [pointA[0], pointB[0]]
    lon = [pointA[1], pointB[1]]

    points = {'lat': lat, "lon": lon}
    df = pd.DataFrame(points)
    # print(df.head())
    df.to_csv(savingDirectory + 'border_points_gdansk.csv', index=False)

    return df

def setUpMeasurePoints(savingDirectory, numberOfRows, numberOfColumns, borderPoints=None):
    """
    This function generates DataFrame with latitude and longitude of measure points, based on the location of border
    points. The location of two border points is read from a CSV file.

    Example of A and B points set up:
            Point A --> (left_top_lat, left_top_lon)
            Point B --> (right_bot_lat, right_bot_lon)

            Covered area:
            A -- -- -- -- --
            |               |
            |               |
            -- -- -- -- -- B

      :return: DataFrame of points with columns: lat, lon
    """

    if borderPoints is not None:
        borderPoints = pd.read_csv(savingDirectory + 'border_points_gdansk.csv', index_col=False)
    # Point A
    left_top_lat = borderPoints.at[0, 'lat']
    left_top_lon = borderPoints.at[0, 'lon']

    # Point B
    right_bot_lat = borderPoints.at[1, 'lat']
    right_bot_lon = borderPoints.at[1, 'lon']

    # difference of A and B points' latitude and longitude
    diff_lat = left_top_lat - right_bot_lat
    diff_lon = left_top_lon - right_bot_lon

    # value of difference between generated points
    step_lat = diff_lat / numberOfRows
    step_lon = diff_lon / numberOfColumns

    # lists to save coordinates of generated points
    points_lat = []
    points_lon = []

    # generate points
    for i in range(numberOfRows):
        curr_lat = left_top_lat - i * step_lat
        for j in range(numberOfColumns):
            curr_lon = left_top_lon - j * step_lon
            points_lat.append(curr_lat)
            points_lon.append(curr_lon)

    # save to dictionary
    points_all = {'lat': points_lat, 'lon': points_lon}

    # convert dictionary to DataFrame
    points_df = pd.DataFrame(points_all)
    
    return points_df

if __name__ == "__main__":
    savingDirectory = "generatedPoints/"
    geohashPath = "master_geohash.csv"

    # Convertir la columna 'geohash' a una lista
    df = pd.read_csv(geohashPath, index_col=False)
    geohash_list = df["geohash"].tolist()

    # number of "steps" (resolution of the division of the area --> greater value gives more details)
    numberOfColumns = 1
    numberOfRows = 1

    # Crear un df vacio
    df_points_base = pd.DataFrame(columns=["lat", "lon"])

    for geohash in geohash_list:
        print(geohash)
        top_left1, top_left2, bottom_right1, bottom_right2 = convertGeohashToLatLong(geohash)    

        # Point A (left upper corner)
        pointA = (top_left1, top_left2) 

        # Point B (right bottom corner)
        pointB = (bottom_right1, bottom_right2)  

        if checkLocationOfBorderPoints(pointA, pointB):
            borderPoints = setUpBorderPoints(savingDirectory, pointA, pointB)
            points_df = setUpMeasurePoints(savingDirectory, numberOfRows, numberOfColumns, borderPoints)
            # Realizar la unión vertical
            df_points_base = pd.concat([df_points_base, points_df], ignore_index=True)
        
        df_points_base.to_csv(
        savingDirectory + "measure_points" + '_' + str(numberOfRows) + 'r_' + str(numberOfColumns) + "c" + ".csv",
        index=False)
