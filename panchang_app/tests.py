from django.test import TestCase
from django.contrib.auth import get_user_model
import datetime

from .models import Panchang, Festival, ShubhaMuhurt, KundaliRecord
from .utils.choughadiya import calculate_choughadiya
from .utils.milan import calculate_milan

User = get_user_model()

class CustomUserTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            name='Test User'
        )
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123',
            name='Admin User'
        )
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertEqual(superuser.name, 'Admin User')
        self.assertTrue(superuser.check_password('adminpassword123'))
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

class ChoughadiyaTests(TestCase):
    def test_choughadiya_split(self):
        date_val = datetime.date(2026, 6, 5) # Friday
        sunrise = datetime.time(6, 0, 0)
        sunset = datetime.time(18, 0, 0)
        
        day_ch, night_ch = calculate_choughadiya(date_val, sunrise, sunset)
        
        # There should be 8 divisions for day and 8 divisions for night
        self.assertEqual(len(day_ch), 8)
        self.assertEqual(len(night_ch), 8)
        
        # Verify first day choughadiya is Char (Friday Day starts with Char)
        self.assertEqual(day_ch[0]['name'], 'Char')
        # Verify first night choughadiya is Rog (Friday Night starts with Rog)
        self.assertEqual(night_ch[0]['name'], 'Rog')

class AshtakootMilanTests(TestCase):
    def test_milan_matching(self):
        # Test Ashwini (Kshatriya, Deva, Adi) vs Ashwini (same Nakshatra)
        # Should result in Nadi Dosha (Nadi score = 0) but high in others
        result = calculate_milan('Ashwini', 'Ashwini')
        self.assertEqual(result['kootas'][7]['score'], 0.0) # Nadi = 0 (same nadi)
        self.assertEqual(result['kootas'][0]['score'], 1.0) # Varna = 1 (same varna)
        self.assertEqual(result['kootas'][5]['score'], 6.0) # Gana = 6 (same gana)
        
        # Test Ashwini vs Rohini (Adi vs Antya) - different Nadis, should get 8.0
        result_diff = calculate_milan('Ashwini', 'Rohini')
        self.assertEqual(result_diff['kootas'][7]['score'], 8.0) # Nadi = 8

class AuthenticationFlowTests(TestCase):
    def test_signup_login_logout_flow(self):
        # 1. Signup a new account
        signup_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'Test@123'
        }
        # Simulate registration POST
        response = self.client.post('/signup/', data=signup_data)
        # Should redirect to login on success
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')
        
        # Verify user is created in database and is_active=True
        user_exists = User.objects.filter(email='test@example.com').exists()
        self.assertTrue(user_exists)
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('Test@123'))
        
        # 2. Login flow
        login_data = {
            'name': 'Test User', # Included because template has it
            'email': 'test@example.com',
            'password': 'Test@123',
            'remember_me': False
        }
        response = self.client.post('/login/', data=login_data)
        # Should redirect to dashboard on success
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/')
        
        # Verify session is created and dashboard can be accessed
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
        
        # 3. Logout flow
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
        # Verify dashboard is no longer accessible
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302) # Redirects to login


from .models import LocationMaster, KundaliRecord

class VaidikEnhancementsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='milan@example.com',
            password='Password123',
            name='Milan Test'
        )
        self.client.force_login(self.user)
        # Create a test LocationMaster
        LocationMaster.objects.create(
            location_name='Nagpur',
            district='Nagpur',
            state='Maharashtra',
            country='India',
            latitude=21.145800,
            longitude=79.088200,
            timezone='Asia/Kolkata'
        )

    def test_default_language_marathi(self):
        # Default language should be Marathi ('mr')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        # Verify it has Marathi UI elements
        self.assertContains(response, 'दैनिक पंचांग')

    def test_language_switch_english(self):
        # Switch language to English
        response = self.client.get('/select-language/?lang=en', follow=True)
        # Verify session language is set
        session = self.client.session
        self.assertEqual(session.get('lang'), 'en')
        # Verify it has English UI elements
        response = self.client.get('/dashboard/')
        self.assertContains(response, 'Daily Panchang')

    def test_location_autocomplete_api(self):
        # Check location search for "Nag"
        response = self.client.get('/api/locations/?q=Nag')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['place_name'], 'Nagpur')
        self.assertEqual(data[0]['timezone'], 'Asia/Kolkata')
        self.assertEqual(float(data[0]['latitude']), 21.1458)

    def test_kundali_accuracy_and_saving(self):
        # Post a complete KundaliForm with coordinates
        kundali_data = {
            'name': 'Ganesh',
            'gender': 'Male',
            'date_of_birth': '2026-06-05',
            'time_of_birth': '12:00:00',
            'place_of_birth': 'Nagpur',
            'country': 'India',
            'state': 'Maharashtra',
            'district': 'Nagpur',
            'city_village': 'Nagpur',
            'latitude': 21.145800,
            'longitude': 79.088200,
            'timezone': 'Asia/Kolkata'
        }
        response = self.client.post('/kundali/', data=kundali_data)
        # Should redirect to details
        self.assertEqual(response.status_code, 302)
        
        # Verify saved in database
        kundali = KundaliRecord.objects.get(name='Ganesh')
        self.assertEqual(kundali.place_of_birth, 'Nagpur')
        self.assertEqual(float(kundali.latitude), 21.145800)
        self.assertEqual(float(kundali.longitude), 79.088200)
        self.assertEqual(kundali.timezone, 'Asia/Kolkata')

        # Follow/GET the detail page to verify the view executes successfully
        detail_url = f'/kundali/{kundali.pk}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

        # Test loading a KundaliRecord that has null latitude and longitude
        null_kundali = KundaliRecord.objects.create(
            user=self.user,
            name='Test Null Coords',
            gender='Female',
            date_of_birth='2026-06-05',
            time_of_birth='12:00:00',
            place_of_birth='Nagpur',
            country='India',
            state='Maharashtra',
            latitude=None,
            longitude=None,
            timezone='Asia/Kolkata'
        )
        response = self.client.get(f'/kundali/{null_kundali.pk}/')
        self.assertEqual(response.status_code, 200)


