# Swamini Vaidik Panchang (स्वामिनी वैदिक पंचांग)

A complete, premium Django web application designed for Vedic astrology calculations, daily Panchang analysis, festival tracking, auspicious timings, and marriage compatibility checks.

## Design Details
- **Primary Gold**: `#D4A017`
- **Dark Maroon**: `#5B0F0F`
- **Saffron Orange**: `#E67E22`
- **Cream Background**: `#FFF8E7`
- Theme aligns exactly with "Swamini Banner.jpg" used on every page.

---

## Installation & Setup Instructions

### Prerequisites
- Python 3.10 or higher
- pip (Python Package Installer)

### 1. Install Dependencies
Run the following command to install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Apply Database Migrations
Create and configure the SQLite database schema:
```bash
python manage.py makemigrations panchang_app
python manage.py migrate
```

### 3. Seed Sample/Demo Data
Populate the database with sample Panchang entries, festivals, Shubha Muhurts, and a default superuser account:
```bash
python manage.py seed_data
```

### 4. Run the Development Server
Start the local server:
```bash
python manage.py run_server
```
*Note: You can access the website at `http://127.0.0.1:8000/`*

---

## Demo Credentials
Use these credentials to log in to the application or access the Django admin panel (`http://127.0.0.1:8000/admin/`):
- **Email ID / Username**: `admin@swaminipanchang.com`
- **Password**: `adminpassword123`

---

## Running Unit Tests
To verify the application features and calculation utilities:
```bash
python manage.py test panchang_app
```

---

## Key Features

1. **Dashboard**: Beautiful responsive grid of 8 spiritual card features with micro-animations.
2. **Masik (Monthly Calendar)**: Navigation grid indicating Pournima, Amavasya, Ekadashi, and local festivals.
3. **Panchang (Daily View)**: Interactive calendar page displaying Vaar, Tithi, Nakshatra, Yoga, Karan, and sun/moon rises.
4. **Sanwar (Festivals)**: Category filters with a dynamic modal to upload new religious events and images.
5. **Shubha Muhurt (Auspicious Timings)**: Table of auspicious timings for marriage, housewarming, etc.
6. **Kundali**: Forms to save birth details and generate a traditional diamond horoscope chart in vector SVG.
7. **Kundali Milan**: Detailed Ashtakoot matching score evaluator (out of 36 points) with Guna feedback.
8. **Choughadiya**: Calculating Day and Night divisions based on local sunrise and sunset timings.
9. **Settings**: Theme switches, profile adjustments, and database backup simulators.
