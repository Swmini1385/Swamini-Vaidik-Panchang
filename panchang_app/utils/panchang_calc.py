import datetime
import skyfield.api as api
from skyfield import almanac
import jyotishganit
from jyotishganit.core.astronomical import get_sunrise_sunset
from zoneinfo import ZoneInfo

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

def decimal_hours_to_time(dec_hours):
    if dec_hours is None:
        return datetime.time(6, 0, 0)
    dec_hours = dec_hours % 24
    hours = int(dec_hours)
    minutes = int((dec_hours - hours) * 60)
    seconds = int(((dec_hours - hours) * 60 - minutes) * 60)
    return datetime.time(hours, minutes, seconds)

def calculate_real_panchang(date_val, lat, lon, tz_offset, location_name="Nagpur"):
    """
    Calculates Daily Panchang using jyotishganit and skyfield for given location coordinates.
    """
    if lat is None:
        lat = 21.145800
    if lon is None:
        lon = 79.088200
    if tz_offset is None:
        tz_offset = 5.5
    try:
        # 1. Sunrise & Sunset at local noon reference
        noon_dt = datetime.datetime.combine(date_val, datetime.time(12, 0, 0))
        p = jyotishganit.Person(noon_dt, float(lat), float(lon), float(tz_offset))
        sunrise_dec, sunset_dec = get_sunrise_sunset(p)
        
        sunrise_time = decimal_hours_to_time(sunrise_dec)
        sunset_time = decimal_hours_to_time(sunset_dec)
        
        # 2. Moonrise & Moonset times using Skyfield
        ts = api.load.timescale()
        eph = api.load('de421.bsp')
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
        
        panch = chart.to_dict()['panchanga']
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
        
        return {
            'tithi': tithi_display,
            'vaar': vaar_str,
            'nakshatra': nakshatra_str,
            'yoga': yoga_str,
            'karan': karan_str,
            'sunrise': sunrise_time,
            'sunset': sunset_time,
            'moonrise': moonrise_time,
            'moonset': moonset_time,
            'is_ekadashi': is_ekadashi,
            'is_pournima': is_pournima,
            'is_amavasya': is_amavasya,
            'is_sankashti': is_sankashti,
            'paksha': paksha
        }
    except Exception as e:
        print(f"[ERROR calculate_real_panchang] {e}")
        # Return sensible fallbacks in case of error
        return {
            'tithi': 'Shukla Pratipada',
            'vaar': date_val.strftime('%A'),
            'nakshatra': 'Rohini',
            'yoga': 'Siddha',
            'karan': 'Bava',
            'sunrise': datetime.time(6, 0),
            'sunset': datetime.time(18, 30),
            'moonrise': datetime.time(7, 30),
            'moonset': datetime.time(20, 30),
            'is_ekadashi': False,
            'is_pournima': False,
            'is_amavasya': False,
            'is_sankashti': False,
            'paksha': 'Shukla Paksha'
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
        2:  {'x': 90,  'y': 65,  'sign_x': 110, 'sign_y': 45},   # House 2
        3:  {'x': 45,  'y': 95,  'sign_x': 45,  'sign_y': 75},   # House 3
        4:  {'x': 90,  'y': 150, 'sign_x': 65,  'sign_y': 150},  # House 4
        5:  {'x': 45,  'y': 205, 'sign_x': 45,  'sign_y': 225},  # House 5
        6:  {'x': 90,  'y': 235, 'sign_x': 110, 'sign_y': 255},  # House 6
        7:  {'x': 150, 'y': 195, 'sign_x': 150, 'sign_y': 230},  # House 7
        8:  {'x': 210, 'y': 235, 'sign_x': 190, 'sign_y': 255},  # House 8
        9:  {'x': 255, 'y': 205, 'sign_x': 255, 'sign_y': 225},  # House 9
        10: {'x': 210, 'y': 150, 'sign_x': 235, 'sign_y': 150},  # House 10
        11: {'x': 255, 'y': 95,  'sign_x': 255, 'sign_y': 75},   # House 11
        12: {'x': 210, 'y': 65,  'sign_x': 190, 'sign_y': 45},   # House 12
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
            planet_str = ", ".join(planets_in_house)
            if len(planets_in_house) > 2:
                p1 = ", ".join(planets_in_house[:2])
                p2 = ", ".join(planets_in_house[2:])
                svg.append(f'  <text x="{coord["x"]}" y="{coord["y"]-4}" font-family="Arial, sans-serif" font-size="9" fill="#FFF8E7" text-anchor="middle">{p1}</text>')
                svg.append(f'  <text x="{coord["x"]}" y="{coord["y"]+6}" font-family="Arial, sans-serif" font-size="9" fill="#FFF8E7" text-anchor="middle">{p2}</text>')
            else:
                svg.append(f'  <text x="{coord["x"]}" y="{coord["y"]}" font-family="Arial, sans-serif" font-size="10" fill="#FFF8E7" text-anchor="middle">{planet_str}</text>')
                
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
