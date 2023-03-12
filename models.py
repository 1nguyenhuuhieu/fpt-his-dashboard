from datetime import date, datetime, timedelta
from dateutil.relativedelta import *


class DayQuery:
    def __init__(self, today):
        try:
            today = datetime.strptime(today, '%Y-%m-%d')
        except:
            today = date.today()
        self.today = today
    
    def yesterday(self):
        return self.today - timedelta(days=1)

    def monday(self):
        return self.today - timedelta(days=self.today.weekday())
    
    def lastweek_monday(self):
        return self.today - timedelta(days=self.today.weekday() + 7)
    
    def lastweek_sunday(self):
        return self.today - timedelta(days=self.today.weekday() + 6)
    
    def last2week_monday(self):
        return self.today - timedelta(days=self.today.weekday() + 14)
    
    def last2week_sunday(self):
        return self.today - timedelta(days=self.today.weekday() + 13)

    def first_day_month(self):
        return self.today.replace(day=1) + relativedelta(months=1) + timedelta(days=-1)
    
    def end_day_month(self):
        return self.today.replace(day=1)
    
    def last_day_month(self):
        return self.first_day_month(self.today) + relativedelta(months=-1)

    

        # self.yesterday = today - timedelta(days=1)
        # self.mon_day = today - timedelta(days=today.weekday())
        # self.last_week_monday = self.mon_day - timedelta(days=7)
        # self.last_week_sun_day = self.last_week_monday + timedelta(days=6)

        # self.twolast_week_monday = self.last_week_monday - timedelta(days=7)
        # self.twolast_week_sun_day = self.last_week_sun_day - timedelta(days=7)
        # self.first_month_day = today.replace(day=1)
        # self.last_first_month_day = self.first_month_day + relativedelta(months=-1)
        # self.last_end_month_day = self.first_month_day + timedelta(days=-1)
        # self.first_year_day = today.replace(day=1, month=1)
        # self.last_first_year_day = self.first_year_day + \
        #     relativedelta(years=-1)
        # self.end_last_year_day = self.first_year_day + timedelta(days=-1)
