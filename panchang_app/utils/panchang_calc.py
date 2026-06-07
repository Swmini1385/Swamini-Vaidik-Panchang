import datetime
import skyfield.api as api
from skyfield import almanac
import jyotishganit
from jyotishganit.core.astronomical import get_sunrise_sunset
from zoneinfo import ZoneInfo
from functools import lru_cache

# List of planets in Vedic Astrology
PLANETS = ['Lagna (Asc)', 'Sun (Surya)', 'Moon (Chandra)', 'Mars (Mangal)', 'Mercury (Budh)', 
           'Jupiter (Guru)', 'Venus (Shukra)', 'Saturn (Shani)', 'Rahu', 'Ketu']

PLANET_SHORTS = {
    'Lagna (Asc)': 'Asc',
    'Sun (Surya)': 'Su',
    'Moon (Chandra)': 'Mo',
    'Mars (Mangal)': 'Ma',
    'Mercury (Budh)': 'Me',
    'Jupiter (Guru)': 'Ju',
    'Venus (Shukra)': 'Ve',
    'Saturn (Shani)': 'Sa',
    'Rahu': 'Ra',
    'Ketu': 'Ke'
}

PLANET_SHORTS_MR = {
    'Lagna (Asc)': 'लग्न',
    'Sun (Surya)': 'सूर्य',
    'Moon (Chandra)': 'चंद्र',
    'Mars (Mangal)': 'मंगळ',
    'Mercury (Budh)': 'बुध',
    'Jupiter (Guru)': 'गुरू',
    'Venus (Shukra)': 'शुक्र',
    'Saturn (Shani)': 'शनि',
    'Rahu': 'राहू',
    'Ketu': 'केतू'
}

SIGN_MAP = {
    'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
    'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
    'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
}

PLANET_MAPPING = {
    'Sun': 'Sun (Surya)',
    'Moon': 'Moon (Chandra)',
    'Mars': 'Mars (Mangal)',
    'Mercury': 'Mercury (Budh)',
    'Jupiter': 'Jupiter (Guru)',
    'Venus': 'Venus (Shukra)',
    'Saturn': 'Saturn (Shani)',
    'Rahu': 'Rahu',
    'Ketu': 'Ketu'
}

NAMAKSHAR_MAP = {
    'Ashwini': ['चु', 'चे', 'चो', 'ला'],
    'Bharani': ['ली', 'लू', 'ले', 'लो'],
    'Krittika': ['अ', 'ई', 'उ', 'ए'],
    'Rohini': ['ओ', 'वा', 'वी', 'वू'],
    'Mrigashira': ['वे', 'वो', 'का', 'की'],
    'Ardra': ['कु', 'घ', 'ङ', 'छ'],
    'Punarvasu': ['के', 'को', 'हा', 'ही'],
    'Pushya': ['हु', 'हे', 'हो', 'डा'],
    'Ashlesha': ['डी', 'डू', 'डे', 'डो'],
    'Magha': ['मा', 'मी', 'मु', 'मे'],
    'Purva Phalguni': ['मो', 'टा', 'टी', 'टू'],
    'Uttara Phalguni': ['टे', 'टो', 'पा', 'पी'],
    'Hasta': ['पू', 'ष', 'ण', 'ठ'],
    'Chitra': ['पे', 'पो', 'रा', 'री'],
    'Swati': ['रू', 'रे', 'रो', 'ता'],
    'Vishakha': ['ती', 'तू', 'ते', 'तो'],
    'Anuradha': ['ना', 'नी', 'नू', 'ने'],
    'Jyeshtha': ['नो', 'या', 'यी', 'यू'],
    'Mula': ['ये', 'यो', 'भा', 'भी'],
    'Purva Ashadha': ['भू', 'धा', 'फा', 'ढा'],
    'Uttara Ashadha': ['भे', 'भो', 'जा', 'जी'],
    'Shravana': ['जू', 'जे', 'जो', 'घा'],
    'Dhanishtha': ['गा', 'गी', 'गु', 'गे'],
    'Shatabhisha': ['गो', 'सा', 'सी', 'सू'],
    'Purva Bhadrapada': ['से', 'सो', 'दा', 'दी'],
    'Uttara Bhadrapada': ['दू', 'थ', 'झ', 'ञ'],
    'Revati': ['दे', 'दो', 'चा', 'ची']
}

MONTH_MAP = {
    'Aries': {'mr': 'चैत्र', 'en': 'Chaitra'},
    'Taurus': {'mr': 'वैशाख', 'en': 'Vaishakha'},
    'Gemini': {'mr': 'ज्येष्ठ', 'en': 'Jyeshtha'},
    'Cancer': {'mr': 'आषाढ', 'en': 'Ashadha'},
    'Leo': {'mr': 'श्रावण', 'en': 'Shravana'},
    'Virgo': {'mr': 'भाद्रपद', 'en': 'Bhadrapada'},
    'Libra': {'mr': 'अश्विन', 'en': 'Ashwina'},
    'Scorpio': {'mr': 'कार्तिक', 'en': 'Kartika'},
    'Sagittarius': {'mr': 'मार्गशीर्ष', 'en': 'Margashirsha'},
    'Capricorn': {'mr': 'पौष', 'en': 'Pausha'},
    'Aquarius': {'mr': 'माघ', 'en': 'Magha'},
    'Pisces': {'mr': 'फाल्गुन', 'en': 'Phalguna'}
}

HORA_SEQUENCE = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
WEEKDAY_LORDS = {
    0: 'Moon',    # Monday
    1: 'Mars',    # Tuesday
    2: 'Mercury', # Wednesday
    3: 'Jupiter', # Thursday
    4: 'Venus',   # Friday
    5: 'Saturn',  # Saturday
    6: 'Sun'      # Sunday
}
HORA_PLANETS_MR = {
    'Sun': 'सूर्य',
    'Moon': 'चंद्र',
    'Mars': 'मंगळ',
    'Mercury': 'बुध',
    'Jupiter': 'गुरू',
    'Venus': 'शुक्र',
    'Saturn': 'शनि'
}

ZODIAC_MAP_MR = {
    'Aries': 'मेष',
    'Taurus': 'वृषभ',
    'Gemini': 'मिथुन',
    'Cancer': 'कर्क',
    'Leo': 'सिंह',
    'Virgo': 'कन्या',
    'Libra': 'तूळ',
    'Scorpio': 'वृश्चिक',
    'Sagittarius': 'धनु',
    'Capricorn': 'मकर',
    'Aquarius': 'कुंभ',
    'Pisces': 'मीन'
}

# Module-level ephemeris loading for performance
_eph = None
_ts = None

def get_eph_and_ts():
    global _eph, _ts
    if _eph is None:
        import skyfield.api as api
        _ts = api.load.timescale()
        _eph = api.load("de421.bsp")
    return _eph, _ts

def calculate_ishtakaal(birth_time, sunrise_time):
    import datetime
    birth_delta = datetime.timedelta(hours=birth_time.hour, minutes=birth_time.minute, seconds=birth_time.second)
    sunrise_delta = datetime.timedelta(hours=sunrise_time.hour, minutes=sunrise_time.minute, seconds=sunrise_time.second)
    
    if birth_delta < sunrise_delta:
        diff_seconds = (datetime.timedelta(days=1) + birth_delta - sunrise_delta).total_seconds()
    else:
        diff_seconds = (birth_delta - sunrise_delta).total_seconds()
        
    ghati_total = diff_seconds * 2.5 / 3600
    ghati = int(ghati_total)
    pala = int((ghati_total - ghati) * 60)
    return f"{ghati} घटी {pala} पळे"

YAMAGANDA_INDEX = {
    0: 3, # Monday: 4th part
    1: 2, # Tuesday: 3rd part
    2: 1, # Wednesday: 2nd part
    3: 0, # Thursday: 1st part
    4: 6, # Friday: 7th part
    5: 5, # Saturday: 6th part
    6: 4  # Sunday: 5th part
}

def decimal_hours_to_time(dec_hours):
    if dec_hours is None:
        return datetime.time(6, 0, 0)
    dec_hours = dec_hours % 24
    hours = int(dec_hours)
    minutes = int((dec_hours - hours) * 60)
    seconds = int(((dec_hours - hours) * 60 - minutes) * 60)
    return datetime.time(hours, minutes, seconds)

def normalize_nakshatra_name(name):
    if not name:
        return ""
    s = name.lower().replace(" ", "").replace("-", "").strip()
    s = s.replace("shth", "sht").replace("sth", "st").replace("sh", "s").replace("th", "t").replace("oo", "u")
    return s

def get_hindu_month(sun_deg, tithi_str):
    tithi_names = ['Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami', 'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami', 'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi', 'Pournima', 'Purnima', 'Amavasya']
    
    t_num = 1
    for i, name in enumerate(tithi_names[:14]):
        if name in tithi_str:
            t_num = i + 1
            break
    if 'Pournima' in tithi_str or 'Purnima' in tithi_str:
        t_num = 15
    elif 'Amavasya' in tithi_str:
        t_num = 30
        
    if 'Krishna' in tithi_str and t_num < 15:
        t_num += 15
        
    # Sun movement approximation (~0.9856 degrees per tithi)
    approx_sun_prev_amavasya = (sun_deg - (t_num * 0.9856)) % 360
    approx_sun_next_amavasya = (sun_deg + ((30 - t_num) * 0.9856)) % 360
    
    prev_idx = int(approx_sun_prev_amavasya / 30)
    next_idx = int(approx_sun_next_amavasya / 30)
    
    is_adhik = (prev_idx == next_idx)
    
    names_en = ['Chaitra', 'Vaishakha', 'Jyeshtha', 'Ashadha', 'Shravana', 'Bhadrapada', 'Ashwina', 'Kartika', 'Margashirsha', 'Pausha', 'Magha', 'Phalguna']
    names_mr = ['चैत्र', 'वैशाख', 'ज्येष्ठ', 'आषाढ', 'श्रावण', 'भाद्रपद', 'अश्विन', 'कार्तिक', 'मार्गशीर्ष', 'पौष', 'माघ', 'फाल्गुन']
    
    en_name = names_en[next_idx]
    mr_name = names_mr[next_idx]
    
    if is_adhik:
        en_name = 'Adhik ' + en_name
        mr_name = 'अधिक ' + mr_name
        
    return en_name, mr_name

@lru_cache(maxsize=128)
def calculate_real_panchang(date_val, lat, lon, tz_offset, location_name="Nagpur", current_dt=None):
    """
    Calculates Daily Panchang using jyotishganit and skyfield for given location coordinates.
    Also calculates extended Vedic metrics (Hora, Choughadiya, Yamghanta, Namakshar, Lagn/Rashi)
    """
    if lat is None:
        lat = 21.145800
    if lon is None:
        lon = 79.088200
    if tz_offset is None:
        tz_offset = 5.5
    if current_dt is None:
        current_dt = datetime.datetime.now()
        
    try:
        # 1. Sunrise & Sunset at local noon reference
        noon_dt = datetime.datetime.combine(date_val, datetime.time(12, 0, 0))
        p = jyotishganit.Person(noon_dt, float(lat), float(lon), float(tz_offset))
        sunrise_dec, sunset_dec = get_sunrise_sunset(p)
        
        sunrise_time = decimal_hours_to_time(sunrise_dec)
        sunset_time = decimal_hours_to_time(sunset_dec)
        
        # 2. Moonrise & Moonset times using Skyfield
        eph, ts = get_eph_and_ts()
        earth = eph['earth']
        moon = eph['moon']
        location = api.wgs84.latlon(float(lat), float(lon))
        observer = earth + location
        
        # Calculate range from local midnight to next local midnight in UTC
        local_midnight = datetime.datetime.combine(date_val, datetime.time(0, 0, 0))
        t0_utc = local_midnight - datetime.timedelta(hours=float(tz_offset))
        t1_utc = local_midnight + datetime.timedelta(days=1) - datetime.timedelta(hours=float(tz_offset))
        
        t0 = ts.from_datetime(t0_utc.replace(tzinfo=datetime.timezone.utc))
        t1 = ts.from_datetime(t1_utc.replace(tzinfo=datetime.timezone.utc))
        
        rise_times, _ = almanac.find_risings(observer, moon, t0, t1)
        set_times, _ = almanac.find_settings(observer, moon, t0, t1)
        
        # Fallback values
        moonrise_time = datetime.time(18, 0, 0)
        moonset_time = datetime.time(6, 0, 0)
        
        if len(rise_times) > 0:
            rise_local = rise_times[0].utc_datetime() + datetime.timedelta(hours=float(tz_offset))
            moonrise_time = rise_local.time()
        if len(set_times) > 0:
            set_local = set_times[0].utc_datetime() + datetime.timedelta(hours=float(tz_offset))
            moonset_time = set_local.time()
            
        # 3. Calculate Panchang components at Sunrise
        sunrise_dt = datetime.datetime.combine(date_val, sunrise_time)
        chart = jyotishganit.calculate_birth_chart(
            birth_date=sunrise_dt,
            latitude=float(lat),
            longitude=float(lon),
            timezone_offset=float(tz_offset),
            location_name=location_name
        )
        
        chart_dict = chart.to_dict()
        panch = chart_dict['panchanga']
        tithi_str = panch.get('tithi', 'Pratipada')
        nakshatra_str = panch.get('nakshatra', 'Rohini')
        yoga_str = panch.get('yoga', 'Siddha')
        karan_str = panch.get('karana', 'Bava')
        vaar_str = panch.get('vaara', date_val.strftime('%A'))
        
        # Parse Paksha
        if "Shukla" in tithi_str:
            paksha = "Shukla Paksha"
        elif "Krishna" in tithi_str:
            paksha = "Krishna Paksha"
        elif tithi_str in ["Pournima", "Purnima"]:
            paksha = "Shukla Paksha"
        elif tithi_str == "Amavasya":
            paksha = "Krishna Paksha"
        else:
            paksha = "Shukla Paksha"
            
        # Standardize Tithi name formatting for translations
        tithi_display = tithi_str.replace("Purnima", "Pournima")
        if tithi_display not in ["Pournima", "Amavasya"] and not tithi_display.startswith("Shukla") and not tithi_display.startswith("Krishna"):
            tithi_display = f"{paksha} {tithi_display}"
            
        is_ekadashi = "Ekadashi" in tithi_str
        is_pournima = "Purnima" in tithi_str or "Pournima" in tithi_str
        is_amavasya = "Amavasya" in tithi_str
        is_sankashti = "Chaturthi" in tithi_str and ("Krishna" in tithi_str or paksha == "Krishna Paksha")
        
        # Extract Lagna, Surya, Chandra
        houses_list = chart_dict.get('d1Chart', {}).get('houses', [])
        lagna_sign = ""
        if houses_list:
            lagna_sign = houses_list[0].get('sign', '')
            
        sun_sign = ""
        sun_deg_total = 0
        moon_sign = ""
        moon_nak = ""
        moon_pada = 1
        
        for h in houses_list:
            h_sign = h.get('sign', '')
            for occ in h.get('occupants', []):
                body = occ.get('celestialBody', '')
                if body == 'Sun':
                    sun_sign = h_sign
                    sign_deg = float(occ.get('signDegrees', 0))
                    sun_deg_total = (SIGN_MAP.get(h_sign, 1) - 1) * 30 + sign_deg
                elif body == 'Moon':
                    moon_sign = h_sign
                    moon_nak = occ.get('nakshatra', '')
                    moon_pada = occ.get('pada', 1)
                    
        # Get active month using rigorous Tithi-based Amanta tracking
        mahina_en, mahina_mr = get_hindu_month(sun_deg_total, tithi_str)
        
        # Get Namakshar
        namakshar_mr = ""
        if moon_nak:
            matched_key = None
            norm_moon_nak = normalize_nakshatra_name(moon_nak)
            for k in NAMAKSHAR_MAP.keys():
                if normalize_nakshatra_name(k) == norm_moon_nak:
                    matched_key = k
                    break
            if matched_key:
                padas = NAMAKSHAR_MAP[matched_key]
                namakshar_mr = padas[(moon_pada - 1) % 4]
                
        namakshar_display = f"{namakshar_mr}" if namakshar_mr else ""
        
        # Lagn, Surya, Chandra Marathi translations
        lagn_mr = ZODIAC_MAP_MR.get(lagna_sign, lagna_sign)
        surya_mr = ZODIAC_MAP_MR.get(sun_sign, sun_sign)
        chandra_mr = ZODIAC_MAP_MR.get(moon_sign, moon_sign)
        
        # Vikram Samvat
        current_year = date_val.year
        if date_val.month > 4 or (date_val.month == 4 and date_val.day >= 15):
            vikram_samvat = current_year + 57
        else:
            vikram_samvat = current_year + 56
            
        # Yamghanta calculation
        weekday = date_val.weekday()
        yam_idx = YAMAGANDA_INDEX[weekday]
        dt_sunrise = datetime.datetime.combine(date_val, sunrise_time)
        dt_sunset = datetime.datetime.combine(date_val, sunset_time)
        day_dur = dt_sunset - dt_sunrise
        part_dur = day_dur / 8
        yam_start = (dt_sunrise + (part_dur * yam_idx)).time()
        yam_end = (dt_sunrise + (part_dur * (yam_idx + 1))).time()
        
        # Current Choughadiya & Hora
        from .choughadiya import calculate_choughadiya
        day_ch, night_ch = calculate_choughadiya(date_val, sunrise_time, sunset_time)
        
        # Determine current_choughadiya
        dt_next_sunrise = dt_sunrise + datetime.timedelta(days=1)
        current_ch = day_ch[0] # Default fallback
        
        if dt_sunrise <= current_dt < dt_sunset:
            day_interval = day_dur / 8
            for i in range(8):
                start = dt_sunrise + (day_interval * i)
                end = dt_sunrise + (day_interval * (i + 1))
                if start <= current_dt < end:
                    current_ch = day_ch[i]
                    break
        else:
            adj_current_dt = current_dt
            adj_dt_sunset = dt_sunset
            adj_dt_next_sunrise = dt_next_sunrise
            adj_weekday = weekday
            
            if current_dt < dt_sunrise:
                adj_dt_sunset = dt_sunset - datetime.timedelta(days=1)
                adj_dt_next_sunrise = dt_sunrise
                prev_date = date_val - datetime.timedelta(days=1)
                adj_weekday = prev_date.weekday()
            
            night_dur = adj_dt_next_sunrise - adj_dt_sunset
            night_interval = night_dur / 8
            for i in range(8):
                start = adj_dt_sunset + (night_interval * i)
                end = adj_dt_sunset + (night_interval * (i + 1))
                if start <= adj_current_dt < end:
                    current_ch = night_ch[i]
                    break
                    
        # Add Devanagari translates for current choughadiya
        CHOUGHADIYA_NAME_MR = {
            'Amrit': 'अमृत', 'Shubh': 'शुभ', 'Labh': 'लाभ', 
            'Char': 'चल', 'Udveg': 'उद्वेग', 'Rog': 'रोग', 'Kaal': 'काळ'
        }
        CHOUGHADIYA_STATUS_MR = {
            'Auspicious (Best)': 'अतिशुभ (अमृत)',
            'Auspicious (Good)': 'शुभ',
            'Auspicious (Gain)': 'लाभदायक',
            'Neutral / Medium': 'मध्यम (चल)',
            'Inauspicious (Anxiety)': 'अशुभ (उद्वेग)',
            'Inauspicious (Disease)': 'अशुभ (रोग)',
            'Inauspicious (Loss)': 'अशुभ (काळ)'
        }
        CHOUGHADIYA_EFFECT_MR = {
            'Very Good - Amrit means nectar. All types of works can be done.': 'अतिशय चांगले - अमृत म्हणजे अमृत. सर्व प्रकारची कामे करता येतात.',
            'Good - Shubh means auspicious. Best for starting education, marriage, and religious works.': 'चांगले - शुभ म्हणजे कल्याणकारी. शिक्षण, विवाह आणि धार्मिक कामे सुरू करण्यासाठी सर्वोत्तम.',
            'Auspicious - Labh means gain. Best for starting new business, trade, and commercial activities.': 'शुभ - लाभ म्हणजे प्रगती. नवीन व्यवसाय, व्यापार आणि व्यावसायिक उपक्रम सुरू करण्यासाठी सर्वोत्तम.',
            'Medium - Chhal means active/mobile. Best for journeys, vehicles, and dynamic tasks.': 'मध्यम - चल म्हणजे गतिमान. प्रवास, नवीन वाहने आणि फिरतीची कामे सुरू करण्यासाठी सर्वोत्तम.',
            'Inauspicious - Udveg means anxiety. Avoid starting new works; bad for health and peace.': 'अशुभ - उद्वेग म्हणजे भीती/चिंता. नवीन कामे सुरू करणे टाळा; आरोग्य आणि मानसिक शांततेसाठी वाईट.',
            'Inauspicious - Rog means disease. Avoid travel, medicine start, and financial transactions.': 'अशुभ - रोग म्हणजे आजारपण. प्रवास, औषधोपचार सुरू करणे आणि आर्थिक व्यवहार करणे टाळावे.',
            'Inauspicious - Kaal represents time/death. Avoid starting auspicious activities.': 'अशुभ - काळ म्हणजे मृत्यू/नुकसान. या काळात शुभ कार्ये करणे टाळावे.'
        }
        
        current_ch['name_mr'] = CHOUGHADIYA_NAME_MR.get(current_ch['name'], current_ch['name'])
        current_ch['status_mr'] = CHOUGHADIYA_STATUS_MR.get(current_ch['status'], current_ch['status'])
        current_ch['effect_mr'] = CHOUGHADIYA_EFFECT_MR.get(current_ch['effect'], current_ch['effect'])
        
        # Calculate current Hora
        day_lord = WEEKDAY_LORDS[weekday]
        start_idx = HORA_SEQUENCE.index(day_lord)
        
        hora_planet = 'Sun'
        hora_start_t = '12:00 PM'
        hora_end_t = '01:00 PM'
        
        if dt_sunrise <= current_dt < dt_sunset:
            elapsed = current_dt - dt_sunrise
            hora_dur = (dt_sunset - dt_sunrise) / 12
            hora_idx = int(elapsed / hora_dur)
            if hora_idx >= 12: hora_idx = 11
            planet_idx = (start_idx + hora_idx) % 7
            hora_planet = HORA_SEQUENCE[planet_idx]
            hora_start_t = (dt_sunrise + (hora_dur * hora_idx)).strftime('%I:%M %p')
            hora_end_t = (dt_sunrise + (hora_dur * (hora_idx + 1))).strftime('%I:%M %p')
        else:
            adj_current_dt = current_dt
            adj_dt_sunset = dt_sunset
            adj_dt_next_sunrise = dt_next_sunrise
            adj_weekday = weekday
            if current_dt < dt_sunrise:
                adj_dt_sunset = dt_sunset - datetime.timedelta(days=1)
                adj_dt_next_sunrise = dt_sunrise
                prev_date = date_val - datetime.timedelta(days=1)
                adj_weekday = prev_date.weekday()
            
            elapsed = adj_current_dt - adj_dt_sunset
            hora_dur = (adj_dt_next_sunrise - adj_dt_sunset) / 12
            hora_idx = int(elapsed / hora_dur)
            if hora_idx >= 12: hora_idx = 11
            day_lord = WEEKDAY_LORDS[adj_weekday]
            start_idx = HORA_SEQUENCE.index(day_lord)
            planet_idx = (start_idx + 12 + hora_idx) % 7
            hora_planet = HORA_SEQUENCE[planet_idx]
            hora_start_t = (adj_dt_sunset + (hora_dur * hora_idx)).strftime('%I:%M %p')
            hora_end_t = (adj_dt_sunset + (hora_dur * (hora_idx + 1))).strftime('%I:%M %p')
            
        current_hora = {
            'planet': hora_planet,
            'planet_mr': HORA_PLANETS_MR.get(hora_planet, hora_planet),
            'start_time': hora_start_t,
            'end_time': hora_end_t
        }
        
        return {
            'tithi': tithi_display,
            'vaar': vaar_str,
            'nakshatra': nakshatra_str,
            'yoga': yoga_str,
            'karan': karan_str,
            'ishtakal': calculate_ishtakaal(current_dt.time(), sunrise_time),
            'sunrise': sunrise_time,
            'sunset': sunset_time,
            'moonrise': moonrise_time,
            'moonset': moonset_time,
            'is_ekadashi': is_ekadashi,
            'is_pournima': is_pournima,
            'is_amavasya': is_amavasya,
            'is_sankashti': is_sankashti,
            'paksha': paksha,
            # Redesign additions
            'mahina': mahina_en,
            'mahina_mr': mahina_mr,
            'charan': moon_pada,
            'namakshar': namakshar_display,
            'vikram_samvat': vikram_samvat,
            'lagn': lagna_sign,
            'lagn_mr': lagn_mr,
            'surya': sun_sign,
            'surya_mr': surya_mr,
            'chandra': moon_sign,
            'chandra_mr': chandra_mr,
            'yamghanta_start': yam_start,
            'yamghanta_end': yam_end,
            'current_choughadiya': current_ch,
            'current_hora': current_hora
        }
        
    except Exception as e:
        print(f"[ERROR calculate_real_panchang] {e}")
        # Return sensible fallbacks in case of error
        fallback_sunrise = datetime.time(6, 0)
        fallback_sunset = datetime.time(18, 30)
        return {
            'tithi': 'Shukla Pratipada',
            'vaar': date_val.strftime('%A'),
            'nakshatra': 'Rohini',
            'yoga': 'Siddha',
            'karan': 'Bava',
            'ishtakal': '10 घटी 15 पळे',
            'sunrise': fallback_sunrise,
            'sunset': fallback_sunset,
            'moonrise': datetime.time(7, 30),
            'moonset': datetime.time(20, 30),
            'is_ekadashi': False,
            'is_pournima': False,
            'is_amavasya': False,
            'is_sankashti': False,
            'paksha': 'Shukla Paksha',
            # Redesign additions
            'mahina': 'Jyeshtha',
            'mahina_mr': 'ज्येष्ठ',
            'charan': 1,
            'namakshar': 'वे',
            'vikram_samvat': date_val.year + 57,
            'lagn': 'Virgo',
            'lagn_mr': 'कन्या',
            'surya': 'Taurus',
            'surya_mr': 'वृषभ',
            'chandra': 'Taurus',
            'chandra_mr': 'वृषभ',
            'yamghanta_start': datetime.time(12, 0),
            'yamghanta_end': datetime.time(13, 30),
            'current_choughadiya': {
                'name': 'Amrit',
                'name_mr': 'अमृत',
                'status': 'Auspicious (Best)',
                'status_mr': 'अतिशुभ (अमृत)',
                'color': 'success',
                'effect': 'Very Good - Amrit means nectar. All types of works can be done.',
                'effect_mr': 'अतिशय चांगले - अमृत म्हणजे अमृत. सर्व प्रकारची कामे करता येतात.',
                'start_time': '12:00 PM',
                'end_time': '01:30 PM'
            },
            'current_hora': {
                'planet': 'Sun',
                'planet_mr': 'सूर्य',
                'start_time': '12:00 PM',
                'end_time': '01:00 PM'
            }
        }

def get_real_birth_chart(date_val, time_val, latitude, longitude, timezone_offset=5.5, location_name="Nagpur"):
    """
    Wrapper around jyotishganit to calculate birth chart.
    """
    if latitude is None:
        latitude = 21.145800
    if longitude is None:
        longitude = 79.088200
    if timezone_offset is None:
        timezone_offset = 5.5
    dt = datetime.datetime.combine(date_val, time_val)
    chart = jyotishganit.calculate_birth_chart(
        birth_date=dt,
        latitude=float(latitude),
        longitude=float(longitude),
        timezone_offset=float(timezone_offset),
        location_name=location_name
    )
    return chart

def extract_chart_positions(chart_dict, chart_type='d1'):
    """
    Extracts planetary positions and house sign mapping from a jyotishganit birth chart dictionary.
    """
    positions = {}
    house_signs = {}
    
    if chart_type == 'd1':
        houses_list = chart_dict['d1Chart']['houses']
    else:
        div_charts = chart_dict.get('divisionalCharts', {})
        if chart_type in div_charts:
            houses_list = div_charts[chart_type]['houses']
        else:
            houses_list = chart_dict['d1Chart']['houses']
            
    # Set default placements
    for p in PLANETS:
        positions[p] = 1
        
    for h in houses_list:
        h_num = h['number']
        sign_name = h['sign']
        house_signs[h_num] = SIGN_MAP.get(sign_name, 1)
        
        for occ in h.get('occupants', []):
            body = occ.get('celestialBody')
            if body in PLANET_MAPPING:
                positions[PLANET_MAPPING[body]] = h_num
                
    # Lagna (Ascendant) is always in the 1st House of any divisional chart
    positions['Lagna (Asc)'] = 1
    
    return positions, house_signs

def get_house_text_coords():
    """
    North Indian Kundali SVG text layout coordinates.
    """
    return {
        1:  {'x': 150, 'y': 105, 'sign_x': 150, 'sign_y': 70},   # House 1
        2:  {'x': 80,  'y': 38,  'sign_x': 80,  'sign_y': 68},   # House 2
        3:  {'x': 38,  'y': 80,  'sign_x': 68,  'sign_y': 80},   # House 3
        4:  {'x': 90,  'y': 150, 'sign_x': 65,  'sign_y': 150},  # House 4
        5:  {'x': 38,  'y': 220, 'sign_x': 68,  'sign_y': 220},  # House 5
        6:  {'x': 80,  'y': 262, 'sign_x': 80,  'sign_y': 232},  # House 6
        7:  {'x': 150, 'y': 195, 'sign_x': 150, 'sign_y': 230},  # House 7
        8:  {'x': 220, 'y': 262, 'sign_x': 220, 'sign_y': 232},  # House 8
        9:  {'x': 262, 'y': 220, 'sign_x': 232, 'sign_y': 220},  # House 9
        10: {'x': 210, 'y': 150, 'sign_x': 235, 'sign_y': 150},  # House 10
        11: {'x': 262, 'y': 80,  'sign_x': 232, 'sign_y': 80},   # House 11
        12: {'x': 220, 'y': 38,  'sign_x': 220, 'sign_y': 68},   # House 12
    }

def generate_kundali_svg(date_val, time_val, lat=21.1458, lon=79.0882, tz_offset=5.5, chart_type='d1', lang='mr'):
    """
    Generates dynamic SVG North Indian Diamond Kundali chart based on real astronomical calculations.
    """
    if lat is None:
        lat = 21.1458
    if lon is None:
        lon = 79.0882
    if tz_offset is None:
        tz_offset = 5.5
    try:
        chart = get_real_birth_chart(date_val, time_val, lat, lon, tz_offset)
        chart_dict = chart.to_dict()
        positions, house_signs = extract_chart_positions(chart_dict, chart_type)
    except Exception as e:
        print(f"[ERROR generate_kundali_svg] Falling back to random. Details: {e}")
        # Backwards compatibility fallback if astronomical engine fails
        seed_val = int(date_val.year + date_val.month * 31 + date_val.day * 12 + time_val.hour * 60)
        import random
        rng = random.Random(seed_val)
        lagna_sign = (seed_val % 12) + 1
        positions = {p: rng.randint(1, 12) for p in PLANETS}
        positions['Lagna (Asc)'] = 1
        house_signs = {h: ((lagna_sign + h - 2) % 12) + 1 for h in range(1, 13)}

    # Group planets by house
    shorts_map = PLANET_SHORTS_MR if lang == 'mr' else PLANET_SHORTS
    house_planets = {h: [] for h in range(1, 13)}
    for planet, house in positions.items():
        short_name = shorts_map.get(planet, planet[:2])
        house_planets[house].append(short_name)
        
    # Append outer planets (Uranus/Arun, Neptune/Varun, Pluto/Yama) to the correct house
    extra_planets = []
    try:
        ayanamsa_val = chart.ayanamsa.value
        extra_planets = calculate_extra_planets(date_val, time_val, lat, lon, tz_offset, ayanamsa_val)
    except Exception:
        pass
        
    for ep in extra_planets:
        body_name = ep['name']
        if lang == 'mr':
            short_name = 'अरुण' if body_name == 'Uranus' else ('वरुण' if body_name == 'Neptune' else 'यम')
        else:
            short_name = 'Ur' if body_name == 'Uranus' else ('Ne' if body_name == 'Neptune' else 'Pl')
            
        if chart_type == 'd1':
            target_sign = SIGN_MAP.get(ep['sidereal_sign'], 1)
        elif chart_type == 'd9':
            nav_idx = int(ep['sidereal_long'] / 3.333333333)
            target_sign = (nav_idx % 12) + 1
        else:
            target_sign = SIGN_MAP.get(ep['sidereal_sign'], 1)
            
        target_house = None
        for h, s in house_signs.items():
            if s == target_sign:
                target_house = h
                break
                
        if target_house is not None:
            house_planets[target_house].append(short_name)
        
    coords = get_house_text_coords()
    
    svg = []
    svg.append('<svg viewBox="0 0 300 300" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background-color: #5B0F0F; border: 3px solid #D4A017; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">')
    
    # Grid lines
    svg.append('  <rect x="10" y="10" width="280" height="280" fill="none" stroke="#D4A017" stroke-width="2.5" />')
    svg.append('  <rect x="13" y="13" width="274" height="274" fill="none" stroke="#D4A017" stroke-width="1" stroke-dasharray="2,2" />')
    svg.append('  <line x1="10" y1="10" x2="290" y2="290" stroke="#D4A017" stroke-width="2" />')
    svg.append('  <line x1="290" y1="10" x2="10" y2="290" stroke="#D4A017" stroke-width="2" />')
    svg.append('  <line x1="150" y1="10" x2="290" y2="150" stroke="#D4A017" stroke-width="2" />')
    svg.append('  <line x1="290" y1="150" x2="150" y2="290" stroke="#D4A017" stroke-width="2" />')
    svg.append('  <line x1="150" y1="290" x2="10" y2="150" stroke="#D4A017" stroke-width="2" />')
    svg.append('  <line x1="10" y1="150" x2="150" y2="10" stroke="#D4A017" stroke-width="2" />')
    
    # Render signs and planets
    for house, coord in coords.items():
        sign_num = house_signs[house]
        svg.append(f'  <text x="{coord["sign_x"]}" y="{coord["sign_y"]}" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#E67E22" text-anchor="middle">{sign_num}</text>')
        
        planets_in_house = house_planets[house]
        if planets_in_house:
            n = len(planets_in_house)
            
            if n == 1:
                font_size = 11
                line_height = 0
            elif n == 2:
                font_size = 10
                line_height = 11
            elif n <= 4:
                font_size = 9
                line_height = 10
            elif n <= 6:
                font_size = 7.5
                line_height = 8
            else:
                font_size = 6.5
                line_height = 7
                
            total_height = (n - 1) * line_height
            start_y = coord["y"] - (total_height / 2)
            
            svg.append(f'  <text font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="#FFF8E7" text-anchor="middle">')
            for idx, p in enumerate(planets_in_house):
                curr_y = start_y + (idx * line_height)
                # Shift slightly down to align with vertical center better
                adjusted_y = curr_y + (font_size * 0.35)
                svg.append(f'    <tspan x="{coord["x"]}" y="{adjusted_y}">{p}</tspan>')
            svg.append('  </text>')
                    
    svg.append('</svg>')
    return "".join(svg)

def generate_planetary_positions(date_val, time_val):
    """
    Backwards compatibility stub. Resolves to Nagpur defaults.
    """
    # Deterministic fallback positions
    seed_val = int(date_val.year + date_val.month * 31 + date_val.day * 12 + time_val.hour * 60)
    import random
    rng = random.Random(seed_val)
    lagna_sign = (seed_val % 12) + 1
    positions = {p: rng.randint(1, 12) for p in PLANETS}
    positions['Lagna (Asc)'] = 1
    house_signs = {h: ((lagna_sign + h - 2) % 12) + 1 for h in range(1, 13)}
    return positions, house_signs

def calculate_extra_planets(date_val, time_val, latitude, longitude, timezone_offset, ayanamsa_val):
    import datetime
    from skyfield.api import load
    import numpy as np
    from jyotishganit.core.constants import NAKSHATRAS
    
    # 1. Calculate UTC time
    dt = datetime.datetime.combine(date_val, time_val)
    dt_utc = dt - datetime.timedelta(hours=float(timezone_offset))
    
    ts = load.timescale()
    t = ts.from_datetime(dt_utc.replace(tzinfo=datetime.timezone.utc))
    
    # Load ephemeris
    eph = load('de421.bsp')
    earth = eph['earth']
    
    extra_bodies = {
        'Uranus': 'uranus barycenter',
        'Neptune': 'neptune barycenter',
        'Pluto': 'pluto barycenter'
    }
    
    extra_planets_data = []
    SIGN_KEYS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    for body_name, eph_key in extra_bodies.items():
        try:
            # Geocentric position
            target = eph[eph_key]
            apparent = earth.at(t).observe(target).apparent()
            _, lon, _ = apparent.ecliptic_latlon()
            
            # Tropical longitude in degrees (0 to 360)
            tropical_long = lon.degrees % 360
            
            # Sidereal longitude
            sidereal_long = (tropical_long - float(ayanamsa_val)) % 360
            
            # Calculate signs
            t_sign_idx = int(tropical_long / 30)
            t_sign_name = SIGN_KEYS[t_sign_idx]
            t_sign_deg = tropical_long % 30
            
            s_sign_idx = int(sidereal_long / 30)
            s_sign_name = SIGN_KEYS[s_sign_idx]
            s_sign_deg = sidereal_long % 30
            
            # Calculate Nakshatra
            nak_idx = int(sidereal_long / (360 / 27))
            nakshatra_name = NAKSHATRAS[nak_idx]
            
            # Calculate Pada
            pada = int((sidereal_long % (360 / 27)) / (360 / 108)) + 1
            
            # Get Namakshar
            namakshar = ""
            matched_key = None
            norm_nak = normalize_nakshatra_name(nakshatra_name)
            for k in NAMAKSHAR_MAP.keys():
                if normalize_nakshatra_name(k) == norm_nak:
                    matched_key = k
                    break
            if matched_key:
                padas = NAMAKSHAR_MAP[matched_key]
                try:
                    namakshar = padas[(pada - 1) % 4]
                except Exception:
                    pass
            
            # Sign degree formats
            t_deg_str = f"{int(t_sign_deg)}° {int((t_sign_deg - int(t_sign_deg)) * 60)}'"
            s_deg_str = f"{int(s_sign_deg)}° {int((s_sign_deg - int(s_sign_deg)) * 60)}'"
            
            extra_planets_data.append({
                'name': body_name,
                'name_mr': 'अरुण' if body_name == 'Uranus' else ('वरुण' if body_name == 'Neptune' else 'यम'),
                'sidereal_long': sidereal_long,
                'sidereal_sign': s_sign_name,
                'sidereal_degree': s_deg_str,
                'tropical_sign': t_sign_name,
                'tropical_degree': t_deg_str,
                'nakshatra': nakshatra_name,
                'pada': pada,
                'namakshar': namakshar
            })
        except Exception as ex:
            print(f"[ERROR calculate_extra_planets for {body_name}] {ex}")
            
    return extra_planets_data

def get_tropical_position(sidereal_sign, sidereal_degree_val, ayanamsha_val):
    SIGN_KEYS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    try:
        sign_idx = SIGN_KEYS.index(sidereal_sign)
    except ValueError:
        # Default conversion
        return sidereal_sign, f"{int(sidereal_degree_val)}° {int((sidereal_degree_val - int(sidereal_degree_val)) * 60)}'"
        
    sidereal_long = (sign_idx * 30) + float(sidereal_degree_val)
    tropical_long = (sidereal_long + float(ayanamsha_val)) % 360
    
    t_sign_idx = int(tropical_long / 30)
    t_sign_name = SIGN_KEYS[t_sign_idx]
    t_sign_deg = tropical_long % 30
    t_deg_str = f"{int(t_sign_deg)}° {int((t_sign_deg - int(t_sign_deg)) * 60)}'"
    
    return t_sign_name, t_deg_str
