class PriceConverter:
    POINTS_TO_NAIRA = 1.72  # Conversion rate: 1.72 points = 1 Naira

    @staticmethod
    def convert_points(points):
        """
        Convert points to Naira.

        """
        naira = points / PriceConverter.POINTS_TO_NAIRA
        return naira

    @staticmethod
    def convert_naira(naira):
        """
        Convert Naira to points.
        """
        points = naira * PriceConverter.POINTS_TO_NAIRA
        return points
