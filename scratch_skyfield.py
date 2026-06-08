import time
import datetime
from zoneinfo import ZoneInfo
from skyfield.api import load
import jyotishganit

ts = load.timescale()
eph = load("de421.bsp")
earth = eph['earth']
sun = eph['sun']
moon = eph['moon']

def test():
    dt = datetime.datetime.now()
    
    st = time.time()
    chart = jyotishganit.calculate_birth_chart(
        birth_date=dt,
        latitude=21.1458,
        longitude=79.0882,
        timezone_offset=5.5,
        location_name="Nagpur"
    )
    ayanamsa = chart.ayanamsa.value
    print(f"Jyotishganit time: {time.time() - st:.4f}s")
    print(f"Jyotishganit Tithi: {chart.to_dict()['panchanga']['tithi']}")
    
    st = time.time()
    for i in range(100):
        t = ts.from_datetime(dt.replace(tzinfo=datetime.timezone.utc))
        astrometric_sun = earth.at(t).observe(sun)
        _, slon, _ = astrometric_sun.apparent().ecliptic_latlon()
        
        astrometric_moon = earth.at(t).observe(moon)
        _, mlon, _ = astrometric_moon.apparent().ecliptic_latlon()
        
        nir_sun = (slon.degrees - ayanamsa) % 360
        nir_moon = (mlon.degrees - ayanamsa) % 360
        
        tithi_idx = int(((nir_moon - nir_sun + 360) % 360) / 12)
        yoga_idx = int((nir_sun + nir_moon) / 13.33333333) % 27
        nak_idx = int(nir_moon / 13.33333333) % 27
        karan_idx = int(((nir_moon - nir_sun + 360) % 360) / 6)
        
    print(f"Skyfield 100 calls time: {time.time() - st:.4f}s")
    print(f"Skyfield Tithi index: {tithi_idx}")

test()
