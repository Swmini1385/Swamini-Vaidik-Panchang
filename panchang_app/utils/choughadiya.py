import datetime

# Choughadiya types and their attributes
CHOUGHADIYA_DETAILS = {
    'Amrit': {'status': 'Auspicious (Best)', 'color': 'success', 'effect': 'Very Good - Amrit means nectar. All types of works can be done.'},
    'Shubh': {'status': 'Auspicious (Good)', 'color': 'primary', 'effect': 'Good - Shubh means auspicious. Best for starting education, marriage, and religious works.'},
    'Labh': {'status': 'Auspicious (Gain)', 'color': 'info', 'effect': 'Auspicious - Labh means gain. Best for starting new business, trade, and commercial activities.'},
    'Char': {'status': 'Neutral / Medium', 'color': 'warning', 'effect': 'Medium - Chhal means active/mobile. Best for journeys, vehicles, and dynamic tasks.'},
    'Udveg': {'status': 'Inauspicious (Anxiety)', 'color': 'danger', 'effect': 'Inauspicious - Udveg means anxiety. Avoid starting new works; bad for health and peace.'},
    'Rog': {'status': 'Inauspicious (Disease)', 'color': 'danger', 'effect': 'Inauspicious - Rog means disease. Avoid travel, medicine start, and financial transactions.'},
    'Kaal': {'status': 'Inausicous (Loss)', 'color': 'secondary', 'effect': 'Inauspicious - Kaal represents time/death. Avoid starting auspicious activities.'},
}

# Choughadiya sequences for each day of the week
# Days: Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
DAY_CHOUGHADIYA_SEQUENCE = {
    0: ['Amrit', 'Kaal', 'Shubh', 'Rog', 'Udveg', 'Char', 'Labh', 'Amrit'], # Monday
    1: ['Rog', 'Udveg', 'Char', 'Labh', 'Amrit', 'Kaal', 'Shubh', 'Rog'],     # Tuesday
    2: ['Labh', 'Amrit', 'Kaal', 'Shubh', 'Rog', 'Udveg', 'Char', 'Labh'],     # Wednesday
    3: ['Shubh', 'Rog', 'Udveg', 'Char', 'Labh', 'Amrit', 'Kaal', 'Shubh'],     # Thursday
    4: ['Char', 'Labh', 'Amrit', 'Kaal', 'Shubh', 'Rog', 'Udveg', 'Char'],     # Friday
    5: ['Kaal', 'Shubh', 'Rog', 'Udveg', 'Char', 'Labh', 'Amrit', 'Kaal'],     # Saturday
    6: ['Udveg', 'Char', 'Labh', 'Amrit', 'Kaal', 'Shubh', 'Rog', 'Udveg'],     # Sunday
}

NIGHT_CHOUGHADIYA_SEQUENCE = {
    0: ['Char', 'Labh', 'Amrit', 'Kaal', 'Shubh', 'Rog', 'Udveg', 'Char'], # Monday
    1: ['Kaal', 'Shubh', 'Rog', 'Udveg', 'Char', 'Labh', 'Amrit', 'Kaal'],     # Tuesday
    2: ['Udveg', 'Char', 'Labh', 'Amrit', 'Kaal', 'Shubh', 'Rog', 'Udveg'],     # Wednesday
    3: ['Amrit', 'Kaal', 'Shubh', 'Rog', 'Udveg', 'Char', 'Labh', 'Amrit'],     # Thursday
    4: ['Rog', 'Udveg', 'Char', 'Labh', 'Amrit', 'Kaal', 'Shubh', 'Rog'],     # Friday
    5: ['Labh', 'Amrit', 'Kaal', 'Shubh', 'Rog', 'Udveg', 'Char', 'Labh'],     # Saturday
    6: ['Shubh', 'Amrit', 'Char', 'Rog', 'Kaal', 'Udveg', 'Labh', 'Shubh'],     # Sunday
}

def calculate_choughadiya(date_val, sunrise, sunset):
    """
    Calculates the Day and Night Choughadiya for a given date, sunrise, and sunset times.
    date_val: datetime.date
    sunrise: datetime.time
    sunset: datetime.time
    """
    weekday = date_val.weekday() # Monday=0, Sunday=6
    
    # Base datetime objects for calculation
    dt_sunrise = datetime.datetime.combine(date_val, sunrise)
    dt_sunset = datetime.datetime.combine(date_val, sunset)
    
    # If sunset is before sunrise (highly unlikely unless cross-day input, but safe-check)
    if dt_sunset <= dt_sunrise:
        dt_sunset += datetime.timedelta(days=1)
        
    day_duration = dt_sunset - dt_sunrise
    day_interval = day_duration / 8
    
    # Calculate Day Choughadiyas
    day_choughadiyas = []
    day_names = DAY_CHOUGHADIYA_SEQUENCE[weekday]
    
    for i in range(8):
        start = dt_sunrise + (day_interval * i)
        end = dt_sunrise + (day_interval * (i + 1))
        name = day_names[i]
        details = CHOUGHADIYA_DETAILS[name]
        day_choughadiyas.append({
            'index': i + 1,
            'name': name,
            'status': details['status'],
            'color': details['color'],
            'effect': details['effect'],
            'start_time': start.strftime('%I:%M %p'),
            'end_time': end.strftime('%I:%M %p')
        })
        
    # Calculate Night Choughadiyas
    # Night is between sunset and next day's sunrise. 
    # Approximating next sunrise as today's sunrise + 24 hours.
    dt_next_sunrise = dt_sunrise + datetime.timedelta(days=1)
    night_duration = dt_next_sunrise - dt_sunset
    night_interval = night_duration / 8
    
    night_choughadiyas = []
    night_names = NIGHT_CHOUGHADIYA_SEQUENCE[weekday]
    
    for i in range(8):
        start = dt_sunset + (night_interval * i)
        end = dt_sunset + (night_interval * (i + 1))
        name = night_names[i]
        details = CHOUGHADIYA_DETAILS[name]
        night_choughadiyas.append({
            'index': i + 1,
            'name': name,
            'status': details['status'],
            'color': details['color'],
            'effect': details['effect'],
            'start_time': start.strftime('%I:%M %p'),
            'end_time': end.strftime('%I:%M %p')
        })
        
    return day_choughadiyas, night_choughadiyas
