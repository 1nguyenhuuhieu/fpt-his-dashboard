from datetime import date, datetime, timedelta
from dateutil.relativedelta import *


# Tính % tăng, giảm
def get_change(current, previous):
    if not current:
        current = 0
    if not previous:
        previous = 0
    if current == previous:
        return (current == previous, 0)
    try:
        return (current > previous, round((abs(current - previous) / previous) * 100, 1))
    except ZeroDivisionError:
        return (current > previous, 0)


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
    
    def sunday(self):
        return self.monday() + timedelta(days=6)
    
    def lastweek_monday(self):
        return self.today - timedelta(days=self.today.weekday() + 7)
    
    def lastweek_sunday(self):
        return self.today - timedelta(days=self.today.weekday() + 8)
    
    def last2week_monday(self):
        return self.today - timedelta(days=self.today.weekday() + 14)
    
    def last2week_sunday(self):
        return self.today - timedelta(days=self.today.weekday() + 15)

    def first_day_month(self):
        return self.today.replace(day=1)
    
    def end_day_month(self):
        return self.today.replace(day=1) + relativedelta(months=1) + timedelta(days=-1)
    
    def first_day_2month(self):
        return self.first_day_month() + relativedelta(months=-1)
    
    def end_day_2month(self):
        return self.first_day_2month() + relativedelta(months=1) + timedelta(days=-1)
    
    def first_day_year(self):
        return self.today.replace(day=1, month=1)
    
    def end_day_year(self):
        return self.first_day_year() + relativedelta(years=1) + timedelta(days=-1)
    
    def first_day_2year(self):
        return self.today.replace(day=1, month=1) + relativedelta(years=-1)
    
    def end_day_2year(self):
        return self.first_day_year() + timedelta(days=-1)
    

class MoneyCard:
    def __init__(self, current, previous):
        self.current = current
        self.previous = previous
        self.icon = 'fa-solid fa-money-bill'
        self.title = 'Tổng doanh thu'
        self.link = 'revenue'

    def current_format(self):
        return f'{round(self.current*0.001)*1000:,} đ'
    
    def previous_format(self):
        return f'{self.previous:,}'
    
    def is_increased(self):
        return get_change(self.current, self.previous)[0]
    
    def percent(self):
        return get_change(self.current, self.previous)[1]