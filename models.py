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

# Tính % so với
def get_percent(current, previous):
    if not current:
        current = 0
    if not previous:
        previous = 0
    if current == previous:
        return (True, 100)
    try:
        return (current > previous, round((current / previous) * 100, 1))
    except ZeroDivisionError:
        return (current > previous, 0)

class DayQuery:
    def __init__(self, today, time_filter,request_start, request_end):
        try:
            today = datetime.strptime(today, '%Y-%m-%d')
        except:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.today = today

        if time_filter is None:
            start = today
            end = today + timedelta(days=1)
            previous_start = start + timedelta(days=-1)
            previous_end = start
        elif time_filter == 'week':
            mon_day = self.today - timedelta(days=self.today.weekday())
            start = mon_day
            end = mon_day + timedelta(days=7)
            previous_start = start + timedelta(days=-7)
            previous_end = start
        elif time_filter == 'month':
            first_day_month = self.today.replace(day=1)
            start = first_day_month
            end = first_day_month + relativedelta(months=1)
            previous_start = start + relativedelta(months=-1)
            previous_end = start
        elif time_filter == 'year':
            first_day_year = self.today.replace(day=1, month=1)
            start = first_day_year
            end = start + relativedelta(years=1)
            previous_start = start + relativedelta(years=-1)
            previous_end = start
        elif time_filter == 'custom_filter':
            start =  request_start
            start = datetime.strptime(start, '%Y-%m-%dT%H:%M')
            end = request_end
            end = datetime.strptime(end, '%Y-%m-%dT%H:%M')
            diff = (end - start).days
            previous_start = start - timedelta(days=diff)
            previous_end = end - timedelta(days=diff)

        self.start = start
        self.end = end
        self.previous_start = previous_start
        self.previous_end = previous_end

    
    def yesterday(self):
        return self.today - timedelta(days=1)

    def monday(self):
        return self.today - timedelta(days=self.today.weekday())
    
    def sunday(self):
        return self.monday() + timedelta(days=7)
    
    def lastweek_monday(self):
        return self.today - timedelta(days=self.today.weekday() + 7)
    
    def lastweek_sunday(self):
        return self.today - timedelta(days=self.today.weekday() + 9)
    
    def last2week_monday(self):
        return self.today - timedelta(days=self.today.weekday() + 14)
    
    def last2week_sunday(self):
        return self.today - timedelta(days=self.today.weekday() + 15)

    def first_day_month(self):
        return self.today.replace(day=1)
    
    def end_day_month(self):
        return self.first_day_month() + relativedelta(months=1)
    
    def first_day_2month(self):
        return self.first_day_month() + relativedelta(months=-1)
    
    def end_day_2month(self):
        return self.first_day_2month() + relativedelta(months=1)
    
    def first_day_year(self):
        return self.today.replace(day=1, month=1)
    
    def end_day_year(self):
        return self.first_day_year() + relativedelta(years=1)
    
    def first_day_2year(self):
        return self.today.replace(day=1, month=1) + relativedelta(years=-1)

class CardWithPercent:
    def __init__(self,icon, title, current, previous):
        self.current = current
        self.previous = previous
        self.icon = icon
        self.title = title

    def current_format(self):
        return f'{round(self.current*0.001)*1000:,} đ'
    
    def previous_format(self):
        return f'{round(self.previous*0.001)*1000:,} đ'
    
    def is_increased(self):
        return get_change(self.current, self.previous)[0]
    
    def percent(self):
        return get_change(self.current, self.previous)[1]
    
class MoneyCard():
    def __init__(self, current, previous):
        self.current = current
        self.previous = previous
        self.icon = 'fa-solid fa-money-bill'
        self.title = 'Tổng doanh thu'
        self.link = 'revenue'

    def current_format(self):
        return f'{round(self.current*0.001)*1000:,} đ'
    
    def previous_format(self):
        return f'{round(self.previous*0.001)*1000:,} đ'
    
    def is_increased(self):
        return get_change(self.current, self.previous)[0]
    
    def percent(self):
        return get_change(self.current, self.previous)[1]
    
class ServiceCard:
    def __init__(self,title, current, total, icon, link):
        self.title = title
        self.current = current
        self.icon = icon
        self.link = link
        self.total = total

    def current_format(self):
        return f'{round(self.current*0.001)*1000:,} đ'
    
    def percent(self):
        return get_percent(self.current, self.total)[1]
    
class PatientHomeCard:
    def __init__(self, icon, title, current, previous, link):
        self.icon = icon
        self.title = title
        self.current = current
        self.previous = previous
        self.link = link
         
    def is_increased(self):
        return get_change(self.current, self.previous)[0]
    
    def percent(self):
        return get_change(self.current, self.previous)[1]
    
class MoneyRevenueCard(CardWithPercent):
    def __init__(self,icon,title, current, previous, extra_info):
        super().__init__(icon, title, current, previous)
        self.extra_info = extra_info

class ConfirmRevenueCard:
    def __init__(self, icon, title, visited_confirmed, hospital_confirmed, visited_money, hospital_money, bhyt_money, bntt_money):
        self.icon = icon
        self.title = title
        self.visited_confirmed = visited_confirmed
        self.hospital_confirmed = hospital_confirmed
        self.visited_money = visited_money
        self.hospital_money = hospital_money
        self.bhyt_money = bhyt_money
        self.bntt_money = bntt_money
        self.total = visited_confirmed + hospital_confirmed

    def visited_money_format(self):
        return f'{round(self.visited_money*0.001)*1000:,} đ'
    
    def hospital_money_format(self):
        return f'{round(self.hospital_money*0.001)*1000:,} đ'
    
    def visited_money_format(self):
        return f'{round(self.visited_money*0.001)*1000:,} đ'
    
    def bhyt_money_format(self):
        return f'{round(self.bhyt_money*0.001)*1000:,} đ'
    
    def bntt_money_format(self):
        return f'{round(self.bntt_money*0.001)*1000:,} đ'

    def percent(self):
        return get_percent(self.bhyt_money, self.bntt_money + self.bhyt_money)[1]
    
class BellowRevenueCard:
    def __init__(self, icon, title, current, previous, ngoaitru, avg_money, avg_confirmed, s_time, e_time):
        self.icon = icon
        self.title = title
        self.current = current
        self.previous = previous
        self.ngoaitru = ngoaitru
        self.noitru = current - ngoaitru
        self.avg_money = avg_money
        self.avg_confirmed = avg_confirmed
        self.time = f'từ {s_time.strftime("%H:%M %d-%m-%Y")} đến {e_time.strftime("%H:%M %d-%m-%Y")}'

    def current_format(self):
        return f'{round(self.current*0.001)*1000:,} đ'
    def previous_format(self):
        return f'{round(self.previous*0.001)*1000:,} đ'
    def ngoaitru_format(self):
        return f'{round(self.ngoaitru*0.001)*1000:,} đ'
    def noitru_format(self):
        return f'{round(self.noitru*0.001)*1000:,} đ'
    def avg_money_format(self):
        return f'{round(self.avg_money*0.001)*1000:,} đ'
    def avg_confirmed_format(self):
        return f'{round(self.avg_confirmed*0.001)*1000:,} đ'
    
    def is_increased(self):
        return get_percent(self.current, self.previous)[0]        
    def percent(self):
        return get_percent(self.current, self.previous)[1]
    
class TopHospitalCard(CardWithPercent):
    def __init__(self, icon, title, current, previous, new_in, old_out):
        super().__init__(icon, title, current, previous)
        self.new_in = new_in
        self.old_out = old_out
class BellowHospitalCard():
    def __init__(self, current, previous, current_title, previous_title):
        self.current = current
        self.previous = previous
        self.current_title = current_title
        self.previous_title = previous_title

    def is_increased(self):
        return get_change(self.current, self.previous)[0]
    
    def percent(self):
        return get_change(self.current, self.previous)[1]
    
class Bed():
    def __init__(self, title, current, total):
        self.title = title
        self.current = current
        self.total = total

    def percent(self):
        return get_percent(self.current, self.total)[1]
    
    def status(self):
        if self.percent() > 95: return 'hot'
        elif self.percent() > 70: return 'cool'
        elif self.percent() > 60: return 'warm'
        else: return 'ice'
    
    
    