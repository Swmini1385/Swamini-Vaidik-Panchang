from skyfield.api import load, wgs84
from skyfield.almanac import moon_phases, find_discrete
import datetime
import pytz

eph = load('de421.bsp')
ts = load.timescale()

def find_amavasyas(date_val):
    # Search window: 40 days before to 40 days after
    t0 = ts.utc(date_val.year, date_val.month, date_val.day - 40)
    t1 = ts.utc(date_val.year, date_val.month, date_val.day + 40)
    
    t, y = find_discrete(t0, t1, moon_phases(eph))
    
    # y == 0 is New Moon (Amavasya)
    new_moons = [t_i.utc_datetime() for t_i, y_i in zip(t, y) if y_i == 0]
    
    # Find the amavasyas around the date_val
    dt_utc = datetime.datetime.combine(date_val, datetime.time(0, 0, 0, tzinfo=datetime.timezone.utc))
    
    # Sort by distance
    new_moons.sort(key=lambda x: abs(x - dt_utc))
    
    closest = new_moons[0]
    
    if closest > dt_utc:
        next_amavasya = closest
        # The one before closest should be previous
        # We find the new moon just before closest
        prev_moons = [nm for nm in new_moons if nm < next_amavasya]
        prev_amavasya = prev_moons[-1]
    else:
        prev_amavasya = closest
        # The one after closest should be next
        next_moons = [nm for nm in new_moons if nm > prev_amavasya]
        next_amavasya = next_moons[0]
        
    return prev_amavasya, next_amavasya

def get_sun_rashi_at(dt):
    # Jyotishganit calculate sun position at dt
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swamini_panchang.settings')
    import django
    django.setup()
    import jyotishganit
    
    p = jyotishganit.Person(dt, 21.1458, 79.0882, 0.0) # UTC
    chart = p.get_birth_chart()
    for h in chart.get('d1Chart', {}).get('houses', []):
        for occ in h.get('occupants', []):
            if occ.get('celestialBody') == 'Sun':
                sign_idx = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'].index(h.get('sign', 'Aries'))
                return sign_idx

def test(date_val):
    prev_am, next_am = find_amavasyas(date_val)
    print(f"Date: {date_val}")
    print(f"Prev: {prev_am}")
    print(f"Next: {next_am}")
    
    # We must add 5.5 hours to make it IST? No, Jyotishganit Person takes local time and tz offset.
    # So if we pass UTC, we set tz offset to 0.
    # Wait, jyotishganit expects naive datetime and timezone offset.
    # We strip tzinfo
    prev_dt = prev_am.replace(tzinfo=None)
    next_dt = next_am.replace(tzinfo=None)
    
    r_prev = get_sun_rashi_at(prev_dt)
    r_next = get_sun_rashi_at(next_dt)
    
    print(f"Sun Rashi at Prev: {r_prev}")
    print(f"Sun Rashi at Next: {r_next}")
    if r_prev == r_next:
        print("Adhik Maas!")

if __name__ == '__main__':
    test(datetime.date(2026, 6, 8))
