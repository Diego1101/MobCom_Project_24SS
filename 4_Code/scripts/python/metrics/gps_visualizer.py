class GPSVisualizer:

    # taken from: https://github.com/tisljaricleo/GPS-visualization-Python
    # more info: https://towardsdatascience.com/simple-gps-data-visualization-using-python-and-open-street-maps-50f992e9b676
    @staticmethod
    def scale_to_img(latitude: float, longitude: float, image_width: int, image_height: int) -> 'tuple[int, int]':
        """
        Conversion from latitude and longitude to the image pixels.
        :param lat_lon: GPS record to draw (lat1, lon1).
        :param h_w: Size of the map image (w, h).
        :return: Tuple containing x and y coordinates to draw on map image.
        """
        # https://gamedev.stackexchange.com/questions/33441/how-to-convert-a-number-from-one-min-max-set-to-another-min-max-set/33445
        # min, max longitude of the map section "/resource/esslingen_map.png"
        old = (48.71143, 48.78043)
        new = (0, image_height)
        y = ((latitude - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]

        # min, max latitude of the map section "resources/esslingen_map.png"
        old = (9.27843, 9.43005)
        new = (0, image_width)
        x = ((longitude - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
        # y must be reversed because the orientation of the image in the matplotlib.
        # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
        return int(x), image_height - int(y)
