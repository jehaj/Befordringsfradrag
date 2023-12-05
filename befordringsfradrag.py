"""Calculate your driving deduction with help from Google Timeline."""

import json
from math import acos, sin, cos
from pathlib import Path
import os


class Trip:
    """Trip describes a simplified activity segment."""
    def __init__(self,
                 start_loc: tuple[float, float],
                 end_loc: tuple[float, float],
                 distance: float) -> None:
        self.start_loc: tuple[float, float] = start_loc
        self.end_loc: tuple[float, float] = end_loc
        self.distance = distance / 1000
        # should save date

    def __repr__(self) -> str:
        return f"L({self.start_loc}, {self.end_loc}, {self.distance:.2f})"


def get_distance(here: tuple[float, float], there: tuple[float, float]) -> float:
    """Calculates the distance in kilometers between two latitude and 
       longitude coordinates."""
    # As shown at
    # https://community.powerbi.com/t5/Desktop/How-to-calculate-lat-long-distance/td-p/1488227
    lat1, lon1 = here
    lat2, lon2 = there
    return acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371


def get_json_paths(year_folder: Path) -> list[Path]:
    """Given a folder for a year return a sorted array with the JSON filepaths
       after the month order."""
    months = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]
    paths: list[Path] = list(map(Path, os.listdir(year_folder)))
    paths.sort(key=lambda x: months.index(str(x).split('_')[1].split('.')[0].lower()))
    return paths


def activity_segment_to_trip(activity_segment: dict) -> Trip:
    """Transform activity segment to trip"""
    try:
        activity_segment = activity_segment["activitySegment"]
        start_loc = (activity_segment["startLocation"]["latitudeE7"]/10000000,
                    activity_segment["startLocation"]["longitudeE7"]/10000000)
        end_loc = (activity_segment["endLocation"]["latitudeE7"]/10000000,
                    activity_segment["endLocation"]["longitudeE7"]/10000000)
        distance = activity_segment["distance"]
        return Trip(start_loc, end_loc, distance)
    except KeyError:
        return Trip((0, 0), (0, 0), 0)


if __name__ == "__main__":
    # Latitude and longitude coordinates for your workplace
    # (e.g. Institute of Computer Science).
    # Go to Google Maps and right-click on your workplace to copy
    # the coordinates and paste them in here.
    min_distance = 3
    workplace: tuple[float, float] = (56.17206821062701, 10.188144768467062)

    folderpath: Path = \
        Path("./Takeout/Lokationshistorik/Semantic Location History/")

    year_folders: list[Path] = list(map(
        lambda x: Path(folderpath, x),
        os.listdir(folderpath)))

    filepaths: list[Path] = []
    for year in year_folders:
        filepaths.extend(list(map(
        lambda x: Path(year, x),
        get_json_paths(year))))
    print(filepaths[87:])
    long_trips = []
    for filepath in filepaths[87:]:
        with open(filepath, 'r', encoding="utf-8") as file:
            document: list[dict] = json.load(file)["timelineObjects"]
            document: list[dict] = list(filter(
                lambda x: next(iter(x)) == "activitySegment",
                document))
            trips = list(map(activity_segment_to_trip, document))
            trips = list(filter(lambda x: get_distance(workplace, x.end_loc) < 2, trips))
            trips_over_min = list(filter(lambda x: x.distance > min_distance, trips))
            long_trips.extend(trips_over_min)
        # print(f"You visited work {len(trips)} time{'s' if len(trips) != 1 else ''}.")
    print(f"{len(long_trips)} of them were over {min_distance} km.")
    print("Done.")
