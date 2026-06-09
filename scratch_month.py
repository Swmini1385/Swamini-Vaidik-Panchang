import datetime
from panchang_app.utils.panchang_calc import get_hindu_month

dts = [
    datetime.date(2023, 7, 10), # Shravana / Adhik Shravana? 2023 had Adhik Shravan
    datetime.date(2023, 8, 20), # Nija Shravana
    datetime.date(2024, 4, 10), # Chaitra
    datetime.date(2024, 1, 15), # Pausha / Magha
]

for d in dts:
    print(d, get_hindu_month(d))
