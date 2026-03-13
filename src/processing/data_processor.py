import pandas as pd

class DataProcessor:

    def __init__(self, dataframe):
        self.df = dataframe

    def process_data(self):

        df = self.df.copy()

        df["lead_time_days"] = (
            df["closed_at"] - df["created_at"]
        ).dt.days

        df["created_day_of_week"] = df["created_at"].dt.day_name()

        return df
