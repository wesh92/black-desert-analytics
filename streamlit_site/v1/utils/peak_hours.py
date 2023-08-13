import pendulum
import polars as pl
from utils.bdolytics_hook.bdolytics import _convert_from_epoch
from utils.bdolytics_hook.models.analytics import BDOlyticsAnalyticsModel

def define_peak_hours(regions: list[str] = None) -> list[tuple[pendulum.time, pendulum.time]]:
    """Define the peak hours for the given region(s)."""
    if regions is None:
        regions = ["NA", "EU", "SA", "SEA", "TW", "KR", "RU", "JP", "MENA"]
    elif isinstance(regions, str):
        regions = [regions.upper()]
    elif isinstance(regions, list):
        pass
    else:
        raise ValueError(f"Invalid type for regions: {type(regions)}")

    # Define the peak hours for each region
    peak_hours = {
        "NA": (pendulum.time(17, 0), pendulum.time(23, 0)),
        "EU": (pendulum.time(19, 0), pendulum.time(21, 0)),
        "SA": (pendulum.time(17, 0), pendulum.time(19, 0)),
        "SEA": (pendulum.time(15, 0), pendulum.time(17, 0)),
        "TW": (pendulum.time(13, 0), pendulum.time(15, 0)),
        "KR": (pendulum.time(11, 0), pendulum.time(13, 0)),
        "RU": (pendulum.time(9, 0), pendulum.time(11, 0)),
        "JP": (pendulum.time(7, 0), pendulum.time(9, 0)),
        "MENA": (pendulum.time(5, 0), pendulum.time(7, 0)),
    }

    # Return the peak hours for the given region(s)
    return [peak_hours[region.upper()] for region in regions]

def filter_for_times(data: list[BDOlyticsAnalyticsModel], time_ranges: list[tuple[pendulum.time, pendulum.time]]) -> pl.DataFrame:
    """Filter the data for the given time ranges and shape into desired format."""
    # Organize data into a dictionary with dates as keys
    date_to_epochs = {}
    for item in data:
        dt_time = _convert_from_epoch(item.epoch_timestamp).time()
        date = _convert_from_epoch(item.epoch_timestamp).date()
        if date in date_to_epochs:
            date_to_epochs[date].append((item.epoch_timestamp, dt_time))
        else:
            date_to_epochs[date] = [(item.epoch_timestamp, dt_time)]

    # Calculate max and min epochs for each date within time ranges
    result_data = []
    for date, epochs_with_time in date_to_epochs.items():
        valid_epochs = []
        for epoch_timestamp, dt_time in epochs_with_time:
            for start_time, end_time in time_ranges:
                if start_time <= dt_time <= end_time:
                    valid_epochs.append(epoch_timestamp)
                    break  # Break once a valid time range is found

        if valid_epochs:
            max_epoch = max(valid_epochs)
            min_epoch = min(valid_epochs)
            result_data.append({"date": date, "max_epoch": max_epoch, "min_epoch": min_epoch})

    # Create a Polars DataFrame from the result data
    return pl.DataFrame(result_data)