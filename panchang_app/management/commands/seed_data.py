import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from panchang_app.models import Panchang, Festival, ShubhaMuhurt, LocationMaster

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds sample data into the database for Swamini Vaidik Panchang'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # 1. Create a default admin user
        admin_email = 'admin@swaminipanchang.com'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                password='adminpassword123',
                name='Vaidik Admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {admin_email} / adminpassword123'))
        else:
            self.stdout.write('Admin user already exists.')

        # 2. Create default test user
        test_email = 'test@example.com'
        if not User.objects.filter(email=test_email).exists():
            User.objects.create_user(
                email=test_email,
                password='Test@123',
                name='Test User'
            )
            self.stdout.write(self.style.SUCCESS(f'Created test user: {test_email} / Test@123'))
        else:
            self.stdout.write('Test user already exists.')

        # 2. Create sample Panchang data for the current and next month
        today = datetime.date.today()
        start_date = datetime.date(today.year, today.month, 1)
        # Seed 60 days
        seeded_days = 0
        
        tithis = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", 
                  "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", 
                  "Trayodashi", "Chaturdashi", "Pournima", "Amavasya"]
        
        nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", 
                      "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati"]
        
        yogas = ["Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda", "Sukarma", "Dhriti", 
                 "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra"]
        
        karans = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kintughna"]

        for i in range(60):
            cur_date = start_date + datetime.timedelta(days=i)
            if not Panchang.objects.filter(date=cur_date).exists():
                vaar_name = cur_date.strftime('%A')
                
                # Deterministic lookup
                tithi_idx = cur_date.day % len(tithis)
                tithi_val = tithis[tithi_idx]
                paksha = "Shukla Paksha" if (cur_date.day < 15) else "Krishna Paksha"
                full_tithi = f"{paksha} {tithi_val}" if tithi_val not in ["Pournima", "Amavasya"] else tithi_val
                
                nak_val = nakshatras[cur_date.day % len(nakshatras)]
                yoga_val = yogas[cur_date.day % len(yogas)]
                karan_val = karans[cur_date.day % len(karans)]
                
                # Check for special dates
                is_ekadashi = (tithi_val == "Ekadashi")
                is_pournima = (tithi_val == "Pournima")
                is_amavasya = (tithi_val == "Amavasya")
                is_sankashti = (tithi_val == "Chaturthi" and paksha == "Krishna Paksha")

                Panchang.objects.create(
                    date=cur_date,
                    tithi=full_tithi,
                    vaar=vaar_name,
                    nakshatra=nak_val,
                    yoga=yoga_val,
                    karan=karan_val,
                    sunrise=datetime.time(6, 2, 0),
                    sunset=datetime.time(18, 55, 0),
                    moonrise=datetime.time(7, 30, 0),
                    moonset=datetime.time(20, 40, 0),
                    is_ekadashi=is_ekadashi,
                    is_pournima=is_pournima,
                    is_amavasya=is_amavasya,
                    is_sankashti=is_sankashti
                )
                seeded_days += 1
                
        self.stdout.write(self.style.SUCCESS(f'Seeded {seeded_days} days of Panchang calculations.'))

        # 3. Create Sample Festivals (Sanwar)
        festivals = [
            # Swamini specific events
            {'name': 'श्री स्वामी समर्थ प्रकट दिन', 'date': today, 'category': 'Jayanti', 'desc': 'श्री स्वामी समर्थ महाराज यांचा प्रकट दिन सोहळा आणि पालखी उत्सव.'},
            {'name': 'महाशिवरात्री उत्सव', 'date': today + datetime.timedelta(days=4), 'category': 'Festival', 'desc': 'भगवान शंकराची आराधना आणि उपवास पूजा.'},
            {'name': 'गुढीपाडवा', 'date': today + datetime.timedelta(days=12), 'category': 'Festival', 'desc': 'हिंदू नववर्षाचा पहिला दिवस आणि गुढी पूजन.'},
            {'name': 'राम नवमी', 'date': today + datetime.timedelta(days=20), 'category': 'Jayanti', 'desc': 'प्रभू रामचंद्र जन्म सोहळा सोलापूर मंदीर.'},
            {'name': 'हनुमान जयंती', 'date': today + datetime.timedelta(days=27), 'category': 'Jayanti', 'desc': 'श्री हनुमान जन्मोत्सव आणि मारुती आराधना.'},
        ]
        
        f_count = 0
        for f in festivals:
            if not Festival.objects.filter(name=f['name'], date=f['date']).exists():
                Festival.objects.create(
                    name=f['name'],
                    date=f['date'],
                    description=f['desc'],
                    category=f['category']
                )
                f_count += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {f_count} festivals.'))

        # 4. Create Sample Shubha Muhurts
        muhurts = [
            {
                'name': 'श्री स्वामी समर्थ लग्न मुहूर्त (Vivah Muhurt)', 
                'start_time': datetime.datetime.combine(today + datetime.timedelta(days=3), datetime.time(9, 15)),
                'end_time': datetime.datetime.combine(today + datetime.timedelta(days=3), datetime.time(13, 30)),
                'category': 'Marriage',
                'desc': 'अतिशय शुभ विवाह मुहूर्त. नक्षत्र: रोहिणी, उत्तरा फाल्गुनी.'
            },
            {
                'name': 'नूतन वास्तू गृहप्रवेश (Gruh Pravesh)', 
                'start_time': datetime.datetime.combine(today + datetime.timedelta(days=8), datetime.time(10, 0)),
                'end_time': datetime.datetime.combine(today + datetime.timedelta(days=8), datetime.time(15, 0)),
                'category': 'Gruh Pravesh',
                'desc': 'नवीन वास्तूमध्ये प्रवेश करण्यासाठी शुभ काळ.'
            },
            {
                'name': 'नवीन व्यवसाय प्रारंभ (Business Start)', 
                'start_time': datetime.datetime.combine(today + datetime.timedelta(days=15), datetime.time(11, 30)),
                'end_time': datetime.datetime.combine(today + datetime.timedelta(days=15), datetime.time(14, 45)),
                'category': 'Business',
                'desc': 'नवीन दुकान, कार्यालय किंवा व्यवसायाचे उद्घाटन करणे.'
            },
            {
                'name': 'शिशु नामकरण विधी (Naming Ceremony)', 
                'start_time': datetime.datetime.combine(today + datetime.timedelta(days=22), datetime.time(8, 0)),
                'end_time': datetime.datetime.combine(today + datetime.timedelta(days=22), datetime.time(12, 0)),
                'category': 'Naming Ceremony',
                'desc': 'बाळाचे नामकरण करण्यासाठी शुभ तिथी आणि वेळ.'
            },
        ]
        
        m_count = 0
        for m in muhurts:
            if not ShubhaMuhurt.objects.filter(name=m['name'], start_time=m['start_time']).exists():
                ShubhaMuhurt.objects.create(
                    name=m['name'],
                    start_time=m['start_time'],
                    end_time=m['end_time'],
                    category=m['category'],
                    description=m['desc']
                )
                m_count += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {m_count} Shubha Muhurts.'))

        # 5. Create Sample LocationMaster data
        locations = [
            {'place_name': 'Nagpur', 'district': 'Nagpur', 'state': 'Maharashtra', 'country': 'India', 'latitude': 21.1458, 'longitude': 79.0882, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Pune', 'district': 'Pune', 'state': 'Maharashtra', 'country': 'India', 'latitude': 18.5204, 'longitude': 73.8567, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Mumbai', 'district': 'Mumbai', 'state': 'Maharashtra', 'country': 'India', 'latitude': 19.0760, 'longitude': 72.8777, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Nashik', 'district': 'Nashik', 'state': 'Maharashtra', 'country': 'India', 'latitude': 19.9975, 'longitude': 73.7898, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Kolhapur', 'district': 'Kolhapur', 'state': 'Maharashtra', 'country': 'India', 'latitude': 16.7050, 'longitude': 74.2433, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Akola', 'district': 'Akola', 'state': 'Maharashtra', 'country': 'India', 'latitude': 20.7002, 'longitude': 77.0082, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Amravati', 'district': 'Amravati', 'state': 'Maharashtra', 'country': 'India', 'latitude': 20.9374, 'longitude': 77.7796, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Nagbhid', 'district': 'Chandrapur', 'state': 'Maharashtra', 'country': 'India', 'latitude': 20.5847, 'longitude': 79.6468, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Nanded', 'district': 'Nanded', 'state': 'Maharashtra', 'country': 'India', 'latitude': 19.1383, 'longitude': 77.3210, 'timezone': 'Asia/Kolkata'},
            {'place_name': 'Nandurbar', 'district': 'Nandurbar', 'state': 'Maharashtra', 'country': 'India', 'latitude': 21.7469, 'longitude': 74.1240, 'timezone': 'Asia/Kolkata'},
        ]
        
        loc_count = 0
        for l in locations:
            if not LocationMaster.objects.filter(place_name=l['place_name']).exists():
                LocationMaster.objects.create(
                    place_name=l['place_name'],
                    district=l['district'],
                    state=l['state'],
                    country=l['country'],
                    latitude=l['latitude'],
                    longitude=l['longitude'],
                    timezone=l['timezone']
                )
                loc_count += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {loc_count} Location Master records.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
