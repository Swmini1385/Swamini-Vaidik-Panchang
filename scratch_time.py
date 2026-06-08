import time
import datetime
import jyotishganit

dt = datetime.datetime.now()
st = time.time()
for i in range(20):
    chart = jyotishganit.calculate_birth_chart(
        birth_date=dt + datetime.timedelta(hours=i),
        latitude=21.1458,
        longitude=79.0882,
        timezone_offset=5.5,
        location_name="Nagpur"
    )
print(f"20 calls took {time.time() - st:.2f} seconds")
