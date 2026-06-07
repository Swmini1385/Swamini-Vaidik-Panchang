import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse

from .models import CustomUser, Panchang, Festival, ShubhaMuhurt, KundaliRecord, LocationMaster
from .forms import (
    CustomUserCreationForm, CustomLoginForm, ForgotPasswordForm, 
    ProfileUpdateForm, KundaliForm, KundaliMilanForm
)
from django.contrib.auth.forms import PasswordChangeForm

# Import our utilities
from .utils.choughadiya import calculate_choughadiya
from .utils.milan import calculate_milan
from .utils.panchang_calc import (
    generate_kundali_svg, calculate_real_panchang, 
    get_real_birth_chart, decimal_hours_to_time, PLANET_MAPPING
)
import jyotishganit
from jyotishganit.core.astronomical import get_sunrise_sunset
from zoneinfo import ZoneInfo

import urllib.request
import urllib.parse
import json

def get_tz_offset(tz_name, dt):
    try:
        tz = ZoneInfo(tz_name)
        return dt.replace(tzinfo=tz).utcoffset().total_seconds() / 3600.0
    except Exception:
        return 5.5

def get_active_location(request):
    """
    Returns (place_name, latitude, longitude, timezone, timezone_offset) from session,
    defaulting to user preferred location, then to database Nagpur, then fallback.
    """
    if 'location' not in request.session:
        loc_data = None
        
        # 1. Check user profile
        if request.user.is_authenticated and request.user.preferred_location:
            pref = request.user.preferred_location
            dt = datetime.datetime.now()
            offset = get_tz_offset(pref.timezone, dt)
            loc_data = {
                'id': pref.id,
                'place_name': pref.location_name,
                'latitude': float(pref.latitude),
                'longitude': float(pref.longitude),
                'timezone': pref.timezone,
                'timezone_offset': offset
            }
        
        # 2. Check database for Nagpur
        if not loc_data:
            nagpur = LocationMaster.objects.filter(location_name__iexact='Nagpur', is_active=True).first()
            if nagpur:
                dt = datetime.datetime.now()
                offset = get_tz_offset(nagpur.timezone, dt)
                loc_data = {
                    'id': nagpur.id,
                    'place_name': nagpur.location_name,
                    'latitude': float(nagpur.latitude),
                    'longitude': float(nagpur.longitude),
                    'timezone': nagpur.timezone,
                    'timezone_offset': offset
                }
                
        # 3. Fallback
        if not loc_data:
            loc_data = {
                'place_name': 'Nagpur',
                'latitude': 21.145800,
                'longitude': 79.088200,
                'timezone': 'Asia/Kolkata',
                'timezone_offset': 5.5
            }
        request.session['location'] = loc_data
        
    return request.session['location']

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Swami Samarth Quotes
    quotes = [
        "भिऊ नकोस, मी तुझ्या पाठीशी आहे। (Fear not, I am behind you.)",
        "अशक्य ही शक्य करतील स्वामी। (Swami will make even the impossible possible.)",
        "विश्वास ठेव, सर्व काही ठीक होईल। (Have faith, everything will be alright.)",
        "कर्म करत राहा, फळाची चिंता करू नका। (Keep performing duties without worrying about fruits.)"
    ]
    # Select quote based on day
    quote = quotes[datetime.date.today().day % len(quotes)]
    
    return render(request, 'home.html', {'quote': quote})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        print(f"[DEBUG LOGIN] POST data: {request.POST}")
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            
            print(f"[DEBUG LOGIN] Email entered: '{email}'")
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                print(f"[DEBUG LOGIN] Authentication Success. Logging in user '{user.email}'...")
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0) # Browser close deletes session
                else:
                    request.session.set_expiry(1209600) # 2 weeks
                messages.success(request, "Login Successful")
                return redirect('dashboard')
            else:
                print(f"[DEBUG LOGIN] Authentication Failed for email '{email}'. Checking if user exists...")
                try:
                    existing_user = CustomUser.objects.get(email__iexact=email)
                    if not existing_user.is_active:
                        print(f"[DEBUG LOGIN] User '{email}' is found but inactive (disabled).")
                        messages.error(request, "Account Disabled")
                    else:
                        print(f"[DEBUG LOGIN] User '{email}' found, but incorrect password.")
                        messages.error(request, "Invalid Email or Password")
                except CustomUser.DoesNotExist:
                    print(f"[DEBUG LOGIN] User '{email}' does not exist in database.")
                    messages.error(request, "Invalid Email or Password")
        else:
            print(f"[DEBUG LOGIN] Form is invalid. Errors: {form.errors}")
            messages.error(request, "Please correct the form errors.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Simulating sending password reset email
            messages.success(request, f"A password reset link has been sent to {email}. (Simulation)")
            return render(request, 'forgot_password_success.html', {'email': email})
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

@login_required
def dashboard(request):
    today = datetime.date.today()
    loc = get_active_location(request)
    
    # Calculate real panchang
    panchang_today = calculate_real_panchang(
        today, loc['latitude'], loc['longitude'], loc['timezone_offset'], loc['place_name']
    )
    
    # Festivals today
    festivals = Festival.objects.filter(date=today)
    
    # Swami Samarth Quote
    quotes = [
        "भिऊ नकोस, मी तुझ्या पाठीशी आहे।",
        "अशक्य ही शक्य करतील स्वामी।",
        "विश्वास ठेव, सर्व काही ठीक होईल।",
        "अनन्य भावाने मला शरण ये।"
    ]
    quote = quotes[today.day % len(quotes)]
    
    context = {
        'panchang': panchang_today,
        'festivals': festivals,
        'quote': quote,
        'today': today,
        'active_location': loc,
    }
    return render(request, 'dashboard.html', context)

@login_required
def panchang_view(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.date.today()
    else:
        selected_date = datetime.date.today()
        
    loc = get_active_location(request)
    panchang = calculate_real_panchang(
        selected_date, loc['latitude'], loc['longitude'], loc['timezone_offset'], loc['place_name']
    )
    
    festivals = Festival.objects.filter(date=selected_date)
    
    context = {
        'panchang': panchang,
        'festivals': festivals,
        'selected_date': selected_date,
        'active_location': loc,
    }
    return render(request, 'panchang.html', context)

@login_required
def masik_view(request):
    year_str = request.GET.get('year')
    month_str = request.GET.get('month')
    
    today = datetime.date.today()
    year = int(year_str) if year_str else today.year
    month = int(month_str) if month_str else today.month
    
    # Calculate previous and next months
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
        
    # Get first day of month and number of days
    first_day = datetime.date(year, month, 1)
    first_weekday = first_day.weekday() # Monday=0, Sunday=6
    # Map Monday=0 to Sunday=6 to grid index where Sunday is first column
    # Sunday index=0, Monday index=1, etc.
    start_grid_offset = (first_weekday + 1) % 7
    
    if month in [1, 3, 5, 7, 8, 10, 12]:
        num_days = 31
    elif month in [4, 6, 9, 11]:
        num_days = 30
    else:
        # Leap year check
        is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        num_days = 29 if is_leap else 28
        
    loc = get_active_location(request)
    db_festivals = Festival.objects.filter(date__in=[datetime.date(year, month, d) for d in range(1, num_days + 1)])
    
    calendar_days = []
    for day in range(1, num_days + 1):
        cur_date = datetime.date(year, month, day)
        p_rec = calculate_real_panchang(
            cur_date, loc['latitude'], loc['longitude'], loc['timezone_offset'], loc['place_name']
        )
        
        f_recs = list(db_festivals.filter(date=cur_date))
        
        if not f_recs:
            if p_rec['is_ekadashi']:
                f_recs.append(Festival(name="Ekadashi Vrat", category="Vrat"))
            if p_rec['is_pournima']:
                f_recs.append(Festival(name="Pournima Vrat", category="Vrat"))
            if p_rec['is_amavasya']:
                f_recs.append(Festival(name="Amavasya Tarpan", category="Vrat"))
            if p_rec['is_sankashti']:
                f_recs.append(Festival(name="Sankashti Chaturthi", category="Vrat"))
                
        calendar_days.append({
            'day': day,
            'date': cur_date,
            'panchang': p_rec,
            'festivals': f_recs,
            'is_today': (cur_date == today),
        })
        
    # Grid assembly: leading empty cells, then days, then trailing empty cells
    grid_cells = [{'day': '', 'dummy': True}] * start_grid_offset + calendar_days
    # Padding to make grid multiple of 7
    while len(grid_cells) % 7 != 0:
        grid_cells.append({'day': '', 'dummy': True})
        
    # Split into weeks (rows of 7)
    weeks = [grid_cells[i:i+7] for i in range(0, len(grid_cells), 7)]
    
    month_name = first_day.strftime('%B')
    
    context = {
        'weeks': weeks,
        'month_name': month_name,
        'year': year,
        'month': month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'masik.html', context)

@login_required
def sanwar_view(request):
    category_filter = request.GET.get('category', 'All')
    
    if category_filter == 'All':
        festivals = Festival.objects.all().order_by('date')
    else:
        festivals = Festival.objects.filter(category=category_filter).order_by('date')
        
    if request.method == 'POST':
        # Add festival via simple form
        name = request.POST.get('name')
        date_val = request.POST.get('date')
        description = request.POST.get('description')
        category = request.POST.get('category')
        image = request.FILES.get('image')
        
        if name and date_val:
            Festival.objects.create(
                name=name,
                date=date_val,
                description=description or '',
                category=category or 'Festival',
                image=image
            )
            messages.success(request, f"Festival '{name}' added successfully!")
            return redirect('sanwar')
        else:
            messages.error(request, "Name and Date are required fields.")
            
    categories = ['Festival', 'Jayanti', 'Punyatithi', 'Vrat', 'Other']
    
    context = {
        'festivals': festivals,
        'categories': categories,
        'current_filter': category_filter,
    }
    return render(request, 'sanwar.html', context)

@login_required
def shubha_muhurt_view(request):
    category_filter = request.GET.get('category', 'All')
    
    if category_filter == 'All':
        muhurts = ShubhaMuhurt.objects.all().order_by('start_time')
    else:
        muhurts = ShubhaMuhurt.objects.filter(category=category_filter).order_by('start_time')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        description = request.POST.get('description')
        category = request.POST.get('category')
        
        if name and start_time and end_time:
            ShubhaMuhurt.objects.create(
                name=name,
                start_time=start_time,
                end_time=end_time,
                description=description or '',
                category=category or 'Other'
            )
            messages.success(request, f"Shubha Muhurt '{name}' created successfully!")
            return redirect('shubha_muhurt')
        else:
            messages.error(request, "Name, Start Time, and End Time are required.")
            
    categories = [
        ('Marriage', 'Marriage (Vivah)'),
        ('Gruh Pravesh', 'Gruh Pravesh'),
        ('Naming Ceremony', 'Naming Ceremony'),
        ('Business', 'Business'),
        ('Other', 'Other')
    ]
    
    context = {
        'muhurts': muhurts,
        'categories': categories,
        'current_filter': category_filter,
    }
    return render(request, 'shubha_muhurt.html', context)

@login_required
def kundali_view(request):
    if request.method == 'POST':
        form = KundaliForm(request.POST)
        if form.is_valid():
            kundali = form.save(commit=False)
            kundali.user = request.user
            kundali.save()
            messages.success(request, f"Janma Kundali for '{kundali.name}' generated and saved successfully!")
            return redirect('kundali_detail', pk=kundali.pk)
    else:
        form = KundaliForm()
        
    saved_kundalis = KundaliRecord.objects.filter(user=request.user)
    return render(request, 'kundali.html', {'form': form, 'saved_kundalis': saved_kundalis})

@login_required
def kundali_detail_view(request, pk):
    kundali = get_object_or_404(KundaliRecord, pk=pk, user=request.user)
    
    lang = request.session.get('lang', 'mr')
    dt = datetime.datetime.combine(kundali.date_of_birth, kundali.time_of_birth)
    tz_offset = get_tz_offset(kundali.timezone, dt)
    
    # Generate D1 SVG Kundali chart
    svg_chart = generate_kundali_svg(
        kundali.date_of_birth, kundali.time_of_birth,
        kundali.latitude, kundali.longitude, tz_offset, chart_type='d1',
        lang=lang
    )
    
    # Generate D9 (Navamsha) SVG Kundali chart
    svg_chart_d9 = generate_kundali_svg(
        kundali.date_of_birth, kundali.time_of_birth,
        kundali.latitude, kundali.longitude, tz_offset, chart_type='d9',
        lang=lang
    )
    
    # Calculate detailed planetary positions and houses
    chart = get_real_birth_chart(
        kundali.date_of_birth, kundali.time_of_birth,
        kundali.latitude, kundali.longitude, tz_offset, kundali.place_of_birth
    )
    chart_dict = chart.to_dict()
    
    first_house = chart_dict['d1Chart']['houses'][0]
    lagna_sign = first_house['sign']
    lagna_deg = float(first_house['signDegrees'])
    lagna_nak = first_house['nakshatra']
    lagna_pada = first_house['pada']
    
    moon_sign = ""
    moon_nak = ""
    moon_pada = ""
    
    planets_data = []
    PLANET_NAME_MR = {
        'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगळ',
        'Mercury': 'बुध', 'Jupiter': 'गुरू', 'Venus': 'शुक्र',
        'Saturn': 'शनि', 'Rahu': 'राहू', 'Ketu': 'केतू'
    }
    
    SIGN_NAMES_MR = {
        'Aries': 'मेष (Aries)', 'Taurus': 'वृषभ (Taurus)', 'Gemini': 'मिथुन (Gemini)',
        'Cancer': 'कर्क (Cancer)', 'Leo': 'सिंह (Leo)', 'Virgo': 'कन्या (Virgo)',
        'Libra': 'तूळ (Libra)', 'Scorpio': 'वृश्चिक (Scorpio)', 'Sagittarius': 'धनु (Sagittarius)',
        'Capricorn': 'मकर (Capricorn)', 'Aquarius': 'कुंभ (Aquarius)', 'Pisces': 'मीन (Pisces)'
    }
    SIGN_NAMES_EN = {
        'Aries': 'Mesha (Aries)', 'Taurus': 'Vrishabha (Taurus)', 'Gemini': 'Mithuna (Gemini)',
        'Cancer': 'Karka (Cancer)', 'Leo': 'Simha (Leo)', 'Virgo': 'Kanya (Virgo)',
        'Libra': 'Tula (Libra)', 'Scorpio': 'Vrishchika (Scorpio)', 'Sagittarius': 'Dhanu (Sagittarius)',
        'Capricorn': 'Makara (Capricorn)', 'Aquarius': 'Kumbha (Aquarius)', 'Pisces': 'Meena (Pisces)'
    }
    sign_names = SIGN_NAMES_MR if lang == 'mr' else SIGN_NAMES_EN
    
    for h in chart_dict['d1Chart']['houses']:
        h_num = h['number']
        for occ in h.get('occupants', []):
            body = occ['celestialBody']
            if body in PLANET_MAPPING:
                deg = float(occ['signDegrees'])
                nak = occ['nakshatra']
                pada = occ['pada']
                sign = h['sign']
                motion = occ.get('motion_type', 'direct')
                
                if body == 'Moon':
                    moon_sign = sign_names.get(sign, sign)
                    moon_nak = nak
                    moon_pada = pada
                    
                planets_data.append({
                    'name': body,
                    'name_mr': PLANET_NAME_MR.get(body, body) if lang == 'mr' else body,
                    'house': h_num,
                    'sign': sign_names.get(sign, sign),
                    'degree': f"{int(deg)}° {int((deg - int(deg)) * 60)}'",
                    'nakshatra': nak,
                    'pada': pada,
                    'motion': motion
                })
                
    order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    planets_data.sort(key=lambda x: order.index(x['name']) if x['name'] in order else 99)
    
    # Get Namakshar for birth Moon Nakshatra
    namakshar = ""
    if moon_nak:
        from panchang_app.utils.panchang_calc import NAMAKSHAR_MAP, normalize_nakshatra_name
        matched_key = None
        norm_moon_nak = normalize_nakshatra_name(moon_nak)
        for k in NAMAKSHAR_MAP.keys():
            if normalize_nakshatra_name(k) == norm_moon_nak:
                matched_key = k
                break
        if matched_key:
            padas = NAMAKSHAR_MAP[matched_key]
            try:
                namakshar = padas[(int(moon_pada) - 1) % 4]
            except Exception:
                pass

    # Dasha details (Vimshottari Dasha)
    dashas_dict = chart_dict.get('dashas', {})
    
    # Build complete Vimshottari Dasha hierarchy
    all_dashas = []
    today = datetime.date.today()
    
    def format_date_str(d_str):
        if not d_str:
            return ""
        try:
            d_val = datetime.datetime.strptime(d_str, '%Y-%m-%d').date()
            return d_val.strftime('%d-%m-%Y')
        except Exception:
            return d_str
            
    mahadashas = dashas_dict.get('all', {}).get('mahadashas', {})
    for m_lord, m_val in mahadashas.items():
        m_start_str = m_val.get('start')
        m_end_str = m_val.get('end')
        
        m_start = datetime.datetime.strptime(m_start_str, '%Y-%m-%d').date() if m_start_str else None
        m_end = datetime.datetime.strptime(m_end_str, '%Y-%m-%d').date() if m_end_str else None
        
        m_status = 'normal'
        if m_start and m_end:
            if m_end < today:
                m_status = 'completed'
            elif m_start <= today <= m_end:
                m_status = 'running'
            else:
                m_status = 'upcoming'
                
        # Calculate duration in years
        m_duration = ""
        if m_start and m_end:
            years = (m_end - m_start).days / 365.25
            m_duration = f"{round(years)} Yrs"
            
        m_antardashas = []
        antardashas = m_val.get('antardashas', {})
        for a_lord, a_val in antardashas.items():
            a_start_str = a_val.get('start')
            a_end_str = a_val.get('end')
            
            a_start = datetime.datetime.strptime(a_start_str, '%Y-%m-%d').date() if a_start_str else None
            a_end = datetime.datetime.strptime(a_end_str, '%Y-%m-%d').date() if a_end_str else None
            
            a_status = 'normal'
            if a_start and a_end:
                if a_end < today:
                    a_status = 'completed'
                elif a_start <= today <= a_end:
                    a_status = 'running'
                else:
                    a_status = 'upcoming'
                    
            a_duration = ""
            if a_start and a_end:
                days = (a_end - a_start).days
                if days >= 30:
                    a_duration = f"{round(days/30.44, 1)} Mths"
                else:
                    a_duration = f"{days} Days"
                    
            a_pratyantardashas = []
            pratyantardashas = a_val.get('pratyantardashas', {})
            for p_lord, p_val in pratyantardashas.items():
                p_start_str = p_val.get('start')
                p_end_str = p_val.get('end')
                
                p_start = datetime.datetime.strptime(p_start_str, '%Y-%m-%d').date() if p_start_str else None
                p_end = datetime.datetime.strptime(p_end_str, '%Y-%m-%d').date() if p_end_str else None
                
                p_status = 'normal'
                if p_start and p_end:
                    if p_end < today:
                        p_status = 'completed'
                    elif p_start <= today <= p_end:
                        p_status = 'running'
                    else:
                        p_status = 'upcoming'
                        
                a_pratyantardashas.append({
                    'lord': p_lord,
                    'start_formatted': format_date_str(p_start_str),
                    'end_formatted': format_date_str(p_end_str),
                    'status': p_status
                })
                
            m_antardashas.append({
                'lord': a_lord,
                'start_formatted': format_date_str(a_start_str),
                'end_formatted': format_date_str(a_end_str),
                'duration': a_duration,
                'status': a_status,
                'pratyantardashas': a_pratyantardashas
            })
            
        all_dashas.append({
            'lord': m_lord,
            'start_formatted': format_date_str(m_start_str),
            'end_formatted': format_date_str(m_end_str),
            'duration': m_duration,
            'status': m_status,
            'antardashas': m_antardashas
        })
        
    context = {
        'kundali': kundali,
        'svg_chart': svg_chart,
        'svg_chart_d9': svg_chart_d9,
        'planets': planets_data,
        'nakshatra': moon_nak,
        'lagna': sign_names.get(lagna_sign, lagna_sign),
        'rashi': moon_sign,
        'pada': moon_pada,
        'namakshar': namakshar,
        'all_dashas': all_dashas,
    }
    return render(request, 'kundali_detail.html', context)

@login_required
def kundali_milan_view(request):
    if request.method == 'POST':
        form = KundaliMilanForm(request.POST)
        if form.is_valid():
            groom_name = form.cleaned_data['groom_name']
            groom_dob = form.cleaned_data['groom_dob']
            groom_tob = form.cleaned_data['groom_tob']
            groom_pob = form.cleaned_data['groom_pob']
            
            bride_name = form.cleaned_data['bride_name']
            bride_dob = form.cleaned_data['bride_dob']
            bride_tob = form.cleaned_data['bride_tob']
            bride_pob = form.cleaned_data['bride_pob']
            
            def get_coordinates_for_place(place_name):
                loc = LocationMaster.objects.filter(location_name__icontains=place_name, is_active=True).first()
                if loc:
                    return loc.latitude, loc.longitude, loc.timezone
                return 21.1458, 79.0882, 'Asia/Kolkata'
                
            g_lat, g_lon, g_tz = get_coordinates_for_place(groom_pob)
            b_lat, b_lon, b_tz = get_coordinates_for_place(bride_pob)
            
            g_dt = datetime.datetime.combine(groom_dob, groom_tob)
            g_tz_offset = get_tz_offset(g_tz, g_dt)
            g_chart = get_real_birth_chart(groom_dob, groom_tob, g_lat, g_lon, g_tz_offset, groom_pob)
            groom_nak = g_chart.to_dict()['panchanga'].get('nakshatra', 'Rohini')
            
            b_dt = datetime.datetime.combine(bride_dob, bride_tob)
            b_tz_offset = get_tz_offset(b_tz, b_dt)
            b_chart = get_real_birth_chart(bride_dob, bride_tob, b_lat, b_lon, b_tz_offset, bride_pob)
            bride_nak = b_chart.to_dict()['panchanga'].get('nakshatra', 'Rohini')
            
            result = calculate_milan(groom_nak, bride_nak)
            
            context = {
                'groom': {'name': groom_name, 'dob': groom_dob, 'tob': groom_tob, 'pob': groom_pob, 'nakshatra': groom_nak},
                'bride': {'name': bride_name, 'dob': bride_dob, 'tob': bride_tob, 'pob': bride_pob, 'nakshatra': bride_nak},
                'result': result
            }
            return render(request, 'kundali_milan_result.html', context)
    else:
        form = KundaliMilanForm()
        
    return render(request, 'kundali_milan.html', {'form': form})

@login_required
def choughadiya_view(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.date.today()
    else:
        selected_date = datetime.date.today()
        
    loc = get_active_location(request)
    noon_dt = datetime.datetime.combine(selected_date, datetime.time(12, 0, 0))
    p = jyotishganit.Person(noon_dt, float(loc['latitude']), float(loc['longitude']), float(loc['timezone_offset']))
    sunrise_dec, sunset_dec = get_sunrise_sunset(p)
    
    sunrise = decimal_hours_to_time(sunrise_dec)
    sunset = decimal_hours_to_time(sunset_dec)
        
    day_choughadiyas, night_choughadiyas = calculate_choughadiya(selected_date, sunrise, sunset)
    
    context = {
        'selected_date': selected_date,
        'sunrise': sunrise,
        'sunset': sunset,
        'day_choughadiyas': day_choughadiyas,
        'night_choughadiyas': night_choughadiyas,
        'active_location': loc,
    }
    return render(request, 'choughadiya.html', context)

@login_required
def settings_view(request):
    profile_form = ProfileUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)
    
    # Simulated Theme & Backup Settings
    current_theme = request.session.get('theme', 'golden_maroon')
    backup_status = request.session.get('backup_status', 'No backups run yet.')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'profile':
            profile_form = ProfileUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('settings')
                
        elif action == 'password':
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # keeps user logged in
                messages.success(request, "Password updated successfully!")
                return redirect('settings')
            else:
                messages.error(request, "Please correct password errors.")
                
        elif action == 'theme':
            theme_choice = request.POST.get('theme_choice', 'golden_maroon')
            request.session['theme'] = theme_choice
            messages.success(request, f"Theme settings updated to '{theme_choice}'!")
            return redirect('settings')
            
        elif action == 'backup':
            # Simulate backup
            now_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            request.session['backup_status'] = f"Vaidik Database Backup completed at {now_str} (Status: SUCCESS, Size: 18 KB)"
            messages.success(request, "Vaidik Database Backup triggered and completed successfully!")
            return redirect('settings')
            
    saved_locations = LocationMaster.objects.filter(is_active=True).order_by('-created_date')
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'current_theme': current_theme,
        'backup_status': backup_status,
        'saved_locations': saved_locations,
    }
    return render(request, 'settings.html', context)

def select_language(request):
    lang = request.GET.get('lang', 'mr')
    if lang in ['mr', 'en']:
        request.session['lang'] = lang
        if lang == 'en':
            messages.success(request, "Language switched to English successfully!")
        else:
            messages.success(request, "भाषा यशस्वीरित्या मराठीत बदलली गेली!")
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('home')

def set_active_location(request):
    """
    Sets the active location in session.
    """
    if request.method == 'POST':
        place_name = request.POST.get('place_name', 'Nagpur')
        lat = request.POST.get('latitude', '21.1458')
        lon = request.POST.get('longitude', '79.0882')
        tz = request.POST.get('timezone', 'Asia/Kolkata')
        
        # Calculate timezone offset
        try:
            tz_info = ZoneInfo(tz)
            now = datetime.datetime.now(tz_info)
            offset = now.utcoffset().total_seconds() / 3600.0
        except Exception:
            offset = 5.5
            
        loc = LocationMaster.objects.filter(location_name=place_name, latitude=float(lat), longitude=float(lon)).first()
        loc_id = loc.id if loc else None
        
        if loc and request.user.is_authenticated:
            request.user.preferred_location = loc
            request.user.save()
            
        request.session['location'] = {
            'id': loc_id,
            'place_name': place_name,
            'latitude': float(lat),
            'longitude': float(lon),
            'timezone': tz,
            'timezone_offset': offset
        }
        
        if loc:
            recent_ids = request.session.get('recent_locations', [])
            if loc.id in recent_ids:
                recent_ids.remove(loc.id)
            recent_ids.insert(0, loc.id)
            request.session['recent_locations'] = recent_ids[:5]
            request.session.modified = True
            
        messages.success(request, f"Location updated to {place_name} successfully!")
        
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('dashboard')

def api_location_search(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse([], safe=False)
        
    # 1. Search LocationMaster
    locations = LocationMaster.objects.filter(location_name__icontains=query, is_active=True)[:10]
    results = []
    for loc in locations:
        results.append({
            'id': loc.id,
            'place_name': loc.location_name,
            'location_name': loc.location_name,
            'district': loc.district,
            'state': loc.state,
            'country': loc.country,
            'city_village': loc.city_village,
            'latitude': str(loc.latitude),
            'longitude': str(loc.longitude),
            'timezone': loc.timezone,
        })
        
    # 2. If not found in LocationMaster, search Nominatim API
    if not results:
        try:
            url_query = urllib.parse.quote(query)
            # Fetch from Nominatim
            req = urllib.request.Request(
                f"https://nominatim.openstreetmap.org/search?q={url_query}&format=json&addressdetails=1&limit=5",
                headers={'User-Agent': 'SwaminiVaidikPanchang/1.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            for item in data:
                lat = float(item.get('lat', 0.0))
                lon = float(item.get('lon', 0.0))
                addr = item.get('address', {})
                city_village = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('hamlet') or addr.get('suburb') or query
                state = addr.get('state', '')
                country = addr.get('country', 'India')
                district = addr.get('county') or addr.get('district') or ''
                
                # Fetch Timezone from timeapi.io
                tz_name = 'Asia/Kolkata' # Default
                try:
                    tz_url = f"https://timeapi.io/api/timezone/coordinate?latitude={lat}&longitude={lon}"
                    tz_req = urllib.request.Request(tz_url, headers={'User-Agent': 'SwaminiVaidikPanchang/1.0'})
                    with urllib.request.urlopen(tz_req, timeout=3) as tz_response:
                        tz_data = json.loads(tz_response.read().decode())
                        tz_name = tz_data.get('timeZone', 'Asia/Kolkata')
                except Exception as e:
                    print(f"[ERROR tz lookup] {e}")
                
                # Create default location name
                location_name = f"{city_village}"
                
                # Prevent duplicate inserts
                loc, created = LocationMaster.objects.get_or_create(
                    location_name=location_name,
                    latitude=lat,
                    longitude=lon,
                    defaults={
                        'country': country,
                        'state': state,
                        'district': district,
                        'city_village': city_village,
                        'timezone': tz_name,
                        'is_active': True
                    }
                )
                
                results.append({
                    'id': loc.id,
                    'place_name': loc.location_name,
                    'location_name': loc.location_name,
                    'district': loc.district,
                    'state': loc.state,
                    'country': loc.country,
                    'city_village': loc.city_village,
                    'latitude': str(loc.latitude),
                    'longitude': str(loc.longitude),
                    'timezone': loc.timezone,
                })
        except Exception as e:
            print(f"[ERROR Nominatim Geocoding] {e}")
            
    return JsonResponse(results, safe=False)

def api_save_location(request):
    if request.method == 'POST':
        # AJAX POST request to save location details
        data = request.POST
        location_name = data.get('location_name', '').strip() or data.get('city_village', '').strip()
        if not location_name:
            return JsonResponse({'status': 'error', 'message': 'Location name is required'}, status=400)
            
        lat = float(data.get('latitude', 0.0))
        lon = float(data.get('longitude', 0.0))
        
        # Check duplicate
        existing = LocationMaster.objects.filter(location_name=location_name, latitude=lat, longitude=lon).first()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.save()
                return JsonResponse({'status': 'success', 'message': 'Location reactivated successfully', 'id': existing.id})
            return JsonResponse({'status': 'error', 'message': 'Location already exists in database', 'id': existing.id})
            
        loc = LocationMaster.objects.create(
            location_name=location_name,
            country=data.get('country', 'India'),
            state=data.get('state', ''),
            district=data.get('district', ''),
            city_village=data.get('city_village', ''),
            latitude=lat,
            longitude=lon,
            timezone=data.get('timezone', 'Asia/Kolkata'),
            is_active=True
        )
        return JsonResponse({'status': 'success', 'message': 'Location saved successfully', 'id': loc.id})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def api_recent_locations(request):
    recent_ids = request.session.get('recent_locations', [])
    locations = LocationMaster.objects.filter(id__in=recent_ids, is_active=True)
    # Sort in the order of usage
    loc_map = {loc.id: loc for loc in locations}
    sorted_locs = []
    for lid in recent_ids:
        if lid in loc_map:
            loc = loc_map[lid]
            sorted_locs.append({
                'id': loc.id,
                'place_name': loc.location_name,
                'location_name': loc.location_name,
                'district': loc.district,
                'state': loc.state,
                'country': loc.country,
                'city_village': loc.city_village,
                'latitude': str(loc.latitude),
                'longitude': str(loc.longitude),
                'timezone': loc.timezone,
            })
    return JsonResponse(sorted_locs, safe=False)

def api_delete_location(request, pk):
    if request.method == 'POST':
        location = get_object_or_404(LocationMaster, pk=pk)
        
        # 1. Default location protection check
        active_loc = request.session.get('location', {})
        if active_loc.get('id') == pk or (active_loc.get('place_name') == location.location_name and float(active_loc.get('latitude', 0)) == float(location.latitude)):
            return JsonResponse({
                'status': 'error',
                'message': 'This location is currently set as default. Please select another default location before deleting.'
            }, status=400)
            
        if request.user.is_authenticated and request.user.preferred_location_id == pk:
            return JsonResponse({
                'status': 'error',
                'message': 'This location is currently set as default. Please select another default location before deleting.'
            }, status=400)
            
        # 2. Location Usage Check in Kundalis
        kundali_count = KundaliRecord.objects.filter(place_of_birth__iexact=location.location_name).count()
        option = request.POST.get('option', '')
        
        if kundali_count > 0 and not option:
            return JsonResponse({
                'status': 'confirm_required',
                'message': f"This location is currently used in {kundali_count} Kundali records.",
                'kundali_count': kundali_count,
                'is_admin': request.user.is_superuser
            })
            
        if option == 'remove_references':
            if not request.user.is_superuser:
                return JsonResponse({'status': 'error', 'message': 'Admin privileges required to remove references.'}, status=403)
            # Remove references in Kundalis
            KundaliRecord.objects.filter(place_of_birth__iexact=location.location_name).update(
                latitude=None,
                longitude=None
            )
            
        # Soft delete
        location.is_active = False
        location.save()
        
        recent_ids = request.session.get('recent_locations', [])
        if pk in recent_ids:
            recent_ids.remove(pk)
            request.session['recent_locations'] = recent_ids
            request.session.modified = True
            
        return JsonResponse({'status': 'success', 'message': 'Location deleted successfully.'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def api_restore_location(request, pk):
    if request.method == 'POST':
        if not request.user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'Admin privileges required to restore locations.'}, status=403)
        location = get_object_or_404(LocationMaster, pk=pk)
        location.is_active = True
        location.save()
        return JsonResponse({'status': 'success', 'message': 'Location restored successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
