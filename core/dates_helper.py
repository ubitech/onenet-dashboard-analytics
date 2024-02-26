from datetime import timezone, timedelta, datetime
import pytz
import pandas as pd


class DatesHelper:
    @staticmethod
    def get_datetime(timestamp: str, fmt: str) -> datetime:
        '''
        Transforms a string of a given format to a `datetime` object

        :param `str` timestamp: The timestamp as a string
        :param `str` fmt: The format of the string

        :return `datetime`: The datetime object
        '''
        return datetime.strptime(timestamp, fmt)

    @staticmethod
    def get_formatted_date(timestamp: datetime, fmt: str) -> str:
        '''
        Formats a `datetime` to a given format

        :param `datetime` timestamp: The datetime to be formatted
        :param `str` fmt: The format required

        :return `str`: The formatted date
        '''
        return timestamp.strftime(fmt)

    @staticmethod
    def get_previous_day_datetime(previous_days: int = 1) -> datetime:
        '''
        Get a previous (to today) day's datetime

        :param `int` previous_days: The number of previous than today days to get the datetime

        :return `datetime`: The datetime of a previous day
        '''
        return datetime.now(tz=timezone.utc) - timedelta(days=previous_days)

    @staticmethod
    def get_full_day_timestamps(date: datetime, fmt: str) -> tuple:
        '''
        Returns two formatted strings that denotes the start and the end of a given date

        :param `datetime` date: The date that we need to get its start and end
        :param `str` fmt: The format required for the returned strings

        :return `tuple`: A tuple of two strings which represent the start and end of a day
        '''
        start = date.replace(hour=0, minute=0, second=0)
        end = date.replace(hour=23, minute=59, second=59)
        return (
            DatesHelper.get_formatted_date(start, fmt),
            DatesHelper.get_formatted_date(end, fmt)
        )

    @staticmethod
    def calculate_dates_list(num_of_days: int, fmt: str, last_date: datetime = None) -> list:
        '''
        Creates a list containing `num_of_days` consecutive dates, with a given format and the 
        last date is the one specified in `last_date`

        :param `int` num_of_days: How many dates to return
        :param `str` fmt: The format of the dates
        :param `datetime` last_date: What should be the last date returned, 
            if not set (`None` by default) the current day is set

        :return `list`: A list of formatted dates
        '''
        if last_date is None:
            last_date = datetime.now(tz=timezone.utc)
        last_date_formatted = last_date.strftime(fmt)
        pandas_index = pd.date_range(
            end=last_date_formatted, periods=num_of_days, freq='1D'
        )
        dates = pd.Series(pandas_index.format(fmt)).tolist()[1:]
        return dates

    @staticmethod
    def find_all_close_timestamps(timestamps: list, time_limit: int, fmt: str) -> list:
        '''
        Group timestamps that are close

        :param `list` timestamps: A list of `str` that represents timestamps
        :param `int` time_limit: The upper time limit interval in minutes
        :param `str` fmt: The format of the string timestamps passed in `timestamps` parameter

        :return `list`: The list of the grouped timestamps
        '''
        # transform all strings to actual timestamps
        actual_timestamps = [
            DatesHelper.get_datetime(t, fmt) for t in timestamps
        ]
        close_timestamps = []
        group_of_timestamps = []
        upper_limit = None
        for idx, timestamp in enumerate(actual_timestamps):
            # if upper_limit is not set, set it and if timestamp is greater than the upper_limit 
            # store the current group to the list and create a new group for the next timestamps
            if upper_limit is None or timestamp > upper_limit:
                if len(group_of_timestamps) > 0:
                    close_timestamps.append(group_of_timestamps)
                    group_of_timestamps = []
                upper_limit = timestamp + timedelta(minutes=time_limit)
            group_of_timestamps.append(timestamps[idx])
        return close_timestamps

    @staticmethod
    def is_daylight_saving_time(timezone: str) -> bool:
        '''
        Checks whether the given timezone practices daylight saving currently

        :param `str` timezone: The timezone that needs to be checked, e.g. 'Europe/Athens'

        :return `bool`: The result of the check
        '''
        return pytz.timezone(timezone).localize(datetime.now()).dst() != timedelta(0)
