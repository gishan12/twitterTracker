def triangulate(coordinates):
    better_list = coordinates[0]
    lon = (better_list[0][0] + better_list[2][0])/2
    lat = (better_list[0][1] + better_list[1][1])/2
    #LONGITUDES.append(lon)
    #LATITUDES.append(lat)
    a = [lon,lat]
    return a
    