import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from .models import CustomUser, Panchang, Festival, ShubhaMuhurt, KundaliRecord, LocationMaster, SHANTI_PUJAN_CHOICES, MANTRA_UPASANA_CHOICES
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
from panchang_app.translations import TRANSLATIONS
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
    from django.core.cache import cache
    
    today = datetime.date.today()
    loc = get_active_location(request)
    
    # Create a unique cache key based on date and location
    # Use timezone offset and place name to differentiate
    cache_key = f"dashboard_data_{today}_{loc['latitude']}_{loc['longitude']}_{loc['timezone_offset']}"
    
    context_data = cache.get(cache_key)
    
    if not context_data:
        # Calculate real panchang
        panchang_today = calculate_real_panchang(
            today, loc['latitude'], loc['longitude'], loc['timezone_offset'], loc['place_name']
        )
        
        # Festivals today
        festivals = list(Festival.objects.filter(date=today))
        
        # Swami Samarth Quote
        quotes = [
            "भिऊ नकोस, मी तुझ्या पाठीशी आहे।",
            "अशक्य ही शक्य करतील स्वामी।",
            "विश्वास ठेव, सर्व काही ठीक होईल।",
            "अनन्य भावाने मला शरण ये।"
        ]
        quote = quotes[today.day % len(quotes)]
        
        context_data = {
            'panchang': panchang_today,
            'festivals': festivals,
            'quote': quote,
            'today': today,
        }
        
        # Cache for 6 hours
        cache.set(cache_key, context_data, 60 * 60 * 6)
    
    # Add active location dynamically since it can change per request
    context_data['active_location'] = loc
    
    return render(request, 'dashboard.html', context_data)

@login_required
def panchang_view(request):
    from django.core.cache import cache
    
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.date.today()
    else:
        selected_date = datetime.date.today()
        
    loc = get_active_location(request)
    
    cache_key = f"panchang_view_{selected_date}_{loc['latitude']}_{loc['longitude']}_{loc['timezone_offset']}"
    context_data = cache.get(cache_key)
    
    if not context_data:
        panchang = calculate_real_panchang(
            selected_date, loc['latitude'], loc['longitude'], loc['timezone_offset'], loc['place_name']
        )
        
        festivals = list(Festival.objects.filter(date=selected_date))
        
        context_data = {
            'panchang': panchang,
            'festivals': festivals,
            'selected_date': selected_date,
        }
        cache.set(cache_key, context_data, 60 * 60 * 24) # Cache for 24 hours
        
    context_data['active_location'] = loc
    
    return render(request, 'panchang.html', context_data)

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
    
    from django.core.cache import cache
    cache_key = f"masik_view_{year}_{month}_{loc['latitude']}_{loc['longitude']}_{loc['timezone_offset']}"
    context = cache.get(cache_key)
    
    if not context:
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
        cache.set(cache_key, context, 60 * 60 * 24) # cache for 24 hours
        
    # Re-evaluate is_today dynamically since it's cached
    for week in context['weeks']:
        for day in week:
            if not day.get('dummy'):
                day['is_today'] = (day['date'] == today)

    return render(request, 'masik.html', context)

from django.core.paginator import Paginator

@login_required
def sanwar_view(request):
    category_filter = request.GET.get('category', 'All')
    
    if category_filter == 'All':
        festivals_list = Festival.objects.all().order_by('date')
    else:
        festivals_list = Festival.objects.filter(category=category_filter).order_by('date')
        
    paginator = Paginator(festivals_list, 20)
    page_number = request.GET.get('page')
    festivals = paginator.get_page(page_number)
        
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
        muhurts_list = ShubhaMuhurt.objects.all().order_by('start_time')
    else:
        muhurts_list = ShubhaMuhurt.objects.filter(category=category_filter).order_by('start_time')
        
    paginator = Paginator(muhurts_list, 20)
    page_number = request.GET.get('page')
    muhurts = paginator.get_page(page_number)
        
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

def get_tropical_position_helper(sidereal_sign, sidereal_degree_val, ayanamsha_val):
    SIGN_KEYS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    try:
        sign_idx = SIGN_KEYS.index(sidereal_sign)
    except ValueError:
        return sidereal_sign, f"{int(sidereal_degree_val)}° {int((sidereal_degree_val - int(sidereal_degree_val)) * 60)}'"
        
    sidereal_long = (sign_idx * 30) + float(sidereal_degree_val)
    tropical_long = (sidereal_long + float(ayanamsha_val)) % 360
    
    t_sign_idx = int(tropical_long / 30)
    t_sign_name = SIGN_KEYS[t_sign_idx]
    t_sign_deg = tropical_long % 30
    t_deg_str = f"{int(t_sign_deg)}° {int((t_sign_deg - int(t_sign_deg)) * 60)}'"
    
    return t_sign_name, t_deg_str

def calculate_custom_vimshottari(birth_date, balance_dict, current_lang='mr'):
    PLANET_NAME_MR = {
        'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगळ',
        'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र',
        'Saturn': 'शनि', 'Rahu': 'राहु', 'Ketu': 'केतु'
    }
    
    if not balance_dict:
        return []
        
    birth_lord = list(balance_dict.keys())[0]
    balance_years = float(balance_dict[birth_lord])
    
    # Durations in years
    VIMSHOTTARI_DURATIONS = {
        'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18,
        'Jupiter': 16, 'Saturn': 19, 'Mercury': 17, 'Ketu': 7, 'Venus': 20
    }
    VIMSHOTTARI_ORDER = ['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus']
    
    lord_idx = VIMSHOTTARI_ORDER.index(birth_lord)
    mahadasha_order = VIMSHOTTARI_ORDER[lord_idx:] + VIMSHOTTARI_ORDER[:lord_idx]
    
    today = datetime.date.today()
    all_dashas = []
    
    for i, m_lord in enumerate(mahadasha_order):
        m_duration = VIMSHOTTARI_DURATIONS[m_lord]
        
        # Calculate Mahadasha start and end dates
        if i == 0:
            m_start = birth_date
            # The remaining period from birth
            m_end = birth_date + datetime.timedelta(days=int(balance_years * 365.25))
            # Theoretical start (to align Antardashas)
            theoretical_start = birth_date - datetime.timedelta(days=int((m_duration - balance_years) * 365.25))
        else:
            m_start = all_dashas[-1]['end_date']
            m_end = m_start + datetime.timedelta(days=int(m_duration * 365.25))
            theoretical_start = m_start
            
        m_status = 'normal'
        if m_end < today:
            m_status = 'completed'
        elif m_start <= today <= m_end:
            m_status = 'running'
        else:
            m_status = 'upcoming'
            
        # Get Antardashas
        m_lord_idx = VIMSHOTTARI_ORDER.index(m_lord)
        antardasha_order = VIMSHOTTARI_ORDER[m_lord_idx:] + VIMSHOTTARI_ORDER[:m_lord_idx]
        
        m_antardashas = []
        ad_current_start = theoretical_start
        
        for a_lord in antardasha_order:
            a_duration = VIMSHOTTARI_DURATIONS[a_lord]
            # Antardasha duration in decimal years
            ad_years = (m_duration * a_duration) / 120.0
            ad_days = int(ad_years * 365.25)
            
            ad_start = ad_current_start
            ad_end = ad_start + datetime.timedelta(days=ad_days)
            ad_current_start = ad_end
            
            # Filter for first Mahadasha balance
            if i == 0:
                if ad_end <= birth_date:
                    continue
                if ad_start < birth_date:
                    ad_start = birth_date
            
            a_status = 'normal'
            if ad_end < today:
                a_status = 'completed'
            elif ad_start <= today <= ad_end:
                a_status = 'running'
            else:
                a_status = 'upcoming'
                
            # Get Pratyantardashas
            a_lord_idx = VIMSHOTTARI_ORDER.index(a_lord)
            pratyantardasha_order = VIMSHOTTARI_ORDER[a_lord_idx:] + VIMSHOTTARI_ORDER[:a_lord_idx]
            
            a_pratyantardashas = []
            pd_current_start = ad_start
            # Theoretical PD start for first Antardasha of first Mahadasha
            if i == 0 and ad_start == birth_date:
                # If this Antardasha started before birth, calculate theoretical PD start
                pd_theoretical_start = ad_end - datetime.timedelta(days=ad_days)
                pd_current_start = pd_theoretical_start
            
            for p_lord in pratyantardasha_order:
                p_duration = VIMSHOTTARI_DURATIONS[p_lord]
                # PD duration in decimal years
                pd_years = (m_duration * a_duration * p_duration) / 14400.0
                pd_days = int(pd_years * 365.25)
                
                pd_start = pd_current_start
                pd_end = pd_start + datetime.timedelta(days=pd_days)
                pd_current_start = pd_end
                
                if i == 0:
                    if pd_end <= birth_date:
                        continue
                    if pd_start < birth_date:
                        pd_start = birth_date
                        
                p_status = 'normal'
                if pd_end < today:
                    p_status = 'completed'
                elif pd_start <= today <= pd_end:
                    p_status = 'running'
                else:
                    p_status = 'upcoming'
                    
                a_pratyantardashas.append({
                    'lord': p_lord,
                    'lord_mr': PLANET_NAME_MR.get(p_lord, p_lord) if current_lang == 'mr' else p_lord,
                    'start_formatted': pd_start.strftime('%d/%m/%Y'),
                    'end_formatted': pd_end.strftime('%d/%m/%Y'),
                    'status': p_status
                })
                
            m_antardashas.append({
                'lord': a_lord,
                'lord_mr': PLANET_NAME_MR.get(a_lord, a_lord) if current_lang == 'mr' else a_lord,
                'start_formatted': ad_start.strftime('%d/%m/%Y'),
                'end_formatted': ad_end.strftime('%d/%m/%Y'),
                'status': a_status,
                'pratyantardashas': a_pratyantardashas
            })
            
        all_dashas.append({
            'lord': m_lord,
            'lord_mr': PLANET_NAME_MR.get(m_lord, m_lord) if current_lang == 'mr' else m_lord,
            'start_formatted': m_start.strftime('%d/%m/%Y'),
            'end_formatted': m_end.strftime('%d/%m/%Y'),
            'end_date': m_end, # helper for next iteration
            'status': m_status,
            'antardashas': m_antardashas
        })
        
    return all_dashas

from functools import lru_cache

def compute_kundali_details(date_val, time_val, latitude, longitude, timezone_name, place_name, name=None, gender=None, current_lang='mr'):
    from django.core.cache import cache
    import hashlib
    import json
    import datetime
    from zoneinfo import ZoneInfo
    from panchang_app.utils.panchang_calc import (
        get_real_birth_chart,
        generate_kundali_svg,
        calculate_extra_planets,
        get_tropical_position,
        NAMAKSHAR_MAP,
        normalize_nakshatra_name,
        calculate_real_panchang,
        PLANETS,
        PLANET_SHORTS,
        PLANET_SHORTS_MR
    )
    from panchang_app.utils.milan import NAKSHATRAS
    
    # Generate Cache Key based on input params
    key_str = f"{date_val}_{time_val}_{latitude}_{longitude}_{timezone_name}_{place_name}_{name}_{gender}_{current_lang}"
    cache_key = "kundali_details_" + hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    dt = datetime.datetime.combine(date_val, time_val)
    try:
        tz = ZoneInfo(timezone_name)
        tz_offset = dt.replace(tzinfo=tz).utcoffset().total_seconds() / 3600.0
    except Exception:
        tz_offset = 5.5
        
    svg_chart = generate_kundali_svg(
        date_val, time_val, latitude, longitude, tz_offset, chart_type='d1', lang=current_lang
    )
    svg_chart_d9 = generate_kundali_svg(
        date_val, time_val, latitude, longitude, tz_offset, chart_type='d9', lang=current_lang
    )
    
    chart = get_real_birth_chart(date_val, time_val, latitude, longitude, tz_offset, place_name)
    chart_dict = chart.to_dict()
    
    ayanamsa_val = chart.ayanamsa.value
    
    first_house = chart_dict['d1Chart']['houses'][0]
    lagna_sign = first_house['sign']
    lagna_deg = float(first_house['signDegrees'])
    lagna_nak = first_house['nakshatra']
    lagna_pada = first_house['pada']
    
    lagna_namakshar = ""
    matched_key = None
    norm_nak = normalize_nakshatra_name(lagna_nak)
    for k in NAMAKSHAR_MAP.keys():
        if normalize_nakshatra_name(k) == norm_nak:
            matched_key = k
            break
    if matched_key:
        padas = NAMAKSHAR_MAP[matched_key]
        try:
            lagna_namakshar = padas[(int(lagna_pada) - 1) % 4]
        except Exception:
            pass
            
    lagna_t_sign, lagna_t_deg_str = get_tropical_position_helper(lagna_sign, lagna_deg, ayanamsa_val)
    
    moon_sign = ""
    moon_nak = ""
    moon_pada = ""
    moon_namakshar = ""
    
    planets_data = []
    
    PLANET_NAME_MR = {
        'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगळ',
        'Mercury': 'बुध', 'Jupiter': 'गुरू', 'Venus': 'शुक्र',
        'Saturn': 'शनि', 'Rahu': 'राहू', 'Ketu': 'केतू'
    }
    
    SIGN_NAMES_MR = {
        'Aries': 'मेष', 'Taurus': 'वृषभ', 'Gemini': 'मिथुन',
        'Cancer': 'कर्क', 'Leo': 'सिंह', 'Virgo': 'कन्या',
        'Libra': 'तूळ', 'Scorpio': 'वृश्चिक', 'Sagittarius': 'धनु',
        'Capricorn': 'मकर', 'Aquarius': 'कुंभ', 'Pisces': 'मीन'
    }
    SIGN_NAMES_EN = {
        'Aries': 'Aries', 'Taurus': 'Taurus', 'Gemini': 'Gemini',
        'Cancer': 'Cancer', 'Leo': 'Leo', 'Virgo': 'Virgo',
        'Libra': 'Libra', 'Scorpio': 'Scorpio', 'Sagittarius': 'Sagittarius',
        'Capricorn': 'Capricorn', 'Aquarius': 'Aquarius', 'Pisces': 'Pisces'
    }
    sign_names = SIGN_NAMES_MR if current_lang == 'mr' else SIGN_NAMES_EN
    
    sun_deg = 0
    from panchang_app.utils.panchang_calc import SIGN_MAP, check_combust
    for h in chart_dict['d1Chart']['houses']:
        for occ in h.get('occupants', []):
            if occ['celestialBody'] == 'Sun':
                sun_deg = (SIGN_MAP.get(h['sign'], 1) - 1) * 30 + float(occ['signDegrees'])
                break

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
                
                planet_namakshar = ""
                matched_k = None
                norm_n = normalize_nakshatra_name(nak)
                for k in NAMAKSHAR_MAP.keys():
                    if normalize_nakshatra_name(k) == norm_n:
                        matched_k = k
                        break
                if matched_k:
                    padas = NAMAKSHAR_MAP[matched_k]
                    try:
                        planet_namakshar = padas[(int(pada) - 1) % 4]
                    except Exception:
                        pass
                
                t_sign, t_deg_str = get_tropical_position_helper(sign, deg, ayanamsa_val)
                
                if body == 'Moon':
                    moon_sign = sign_names.get(sign, sign)
                    moon_nak = nak
                    moon_pada = pada
                    moon_namakshar = planet_namakshar
                    
                is_retro = (motion == 'retrograde')
                p_deg_total = (SIGN_MAP.get(sign, 1) - 1) * 30 + deg
                
                # Check combust
                is_combust = check_combust(PLANET_MAPPING.get(body, body), p_deg_total, sun_deg, is_retro)
                
                suffix = ""
                if is_retro:
                    suffix += "*"
                if is_combust:
                    suffix += "^"
                    
                final_name = body + suffix
                final_name_mr = PLANET_NAME_MR.get(body, body) + suffix
                    
                planets_data.append({
                    'name': final_name,
                    'name_mr': final_name_mr,
                    'house': h_num,
                    'sidereal_sign': sign,
                    'sidereal_degree': f"{int(deg)}° {int((deg - int(deg)) * 60)}'",
                    'tropical_sign': t_sign,
                    'tropical_degree': t_deg_str,
                    'nakshatra': nak,
                    'pada': pada,
                    'namakshar': planet_namakshar,
                    'motion': motion
                })
                
    order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    planets_data.sort(key=lambda x: order.index(x['name'].replace('*', '').replace('^', '')) if x['name'].replace('*', '').replace('^', '') in order else 99)
    
    extra_planets = calculate_extra_planets(date_val, time_val, latitude, longitude, tz_offset, ayanamsa_val)
    
    full_planet_rows = []
    
    full_planet_rows.append({
        'name': 'Lagna',
        'name_mr': 'लग्न',
        'sidereal_sign': sign_names.get(lagna_sign, lagna_sign),
        'sidereal_degree': f"{int(lagna_deg)}° {int((lagna_deg - int(lagna_deg)) * 60)}'",
        'tropical_sign': sign_names.get(lagna_t_sign, lagna_t_sign),
        'tropical_degree': lagna_t_deg_str,
        'nakshatra': lagna_nak,
        'pada': lagna_pada,
        'namakshar': lagna_namakshar
    })
    
    for p in planets_data:
        full_planet_rows.append({
            'name': p['name'],
            'name_mr': p['name_mr'],
            'sidereal_sign': sign_names.get(p['sidereal_sign'], p['sidereal_sign']),
            'sidereal_degree': p['sidereal_degree'],
            'tropical_sign': sign_names.get(p['tropical_sign'], p['tropical_sign']),
            'tropical_degree': p['tropical_degree'],
            'nakshatra': p['nakshatra'],
            'pada': p['pada'],
            'namakshar': p['namakshar']
        })
        
    for ep in extra_planets:
        full_planet_rows.append({
            'name': ep['name'],
            'name_mr': ep['name_mr'],
            'sidereal_sign': sign_names.get(ep['sidereal_sign'], ep['sidereal_sign']),
            'sidereal_degree': ep['sidereal_degree'],
            'tropical_sign': sign_names.get(ep['tropical_sign'], ep['tropical_sign']),
            'tropical_degree': ep['tropical_degree'],
            'nakshatra': ep['nakshatra'],
            'pada': ep['pada'],
            'namakshar': ep['namakshar']
        })
        
    balance_dict = chart_dict.get('dashas', {}).get('balance', {})
    
    # Custom Vimshottari calculations using Dasha Bhogya balance
    all_dashas = calculate_custom_vimshottari(date_val, balance_dict, current_lang)
    
    panchang_data = calculate_real_panchang(date_val, latitude, longitude, tz_offset, place_name, dt)
    
    lagna_deg_str = f"{int(lagna_deg)}° {int((lagna_deg - int(lagna_deg)) * 60)}'"
    
    mars_house = 0
    for h in chart_dict['d1Chart']['houses']:
        for occ in h.get('occupants', []):
            if occ['celestialBody'] == 'Mars':
                mars_house = h['number']
                break
    has_mangal_dosha = mars_house in [1, 4, 7, 8, 12]
    
    # Define custom planet names map for dasha bhogya to match user requested spelling
    PLANET_NAME_BHOGYA_MR = {
        'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगळ',
        'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र',
        'Saturn': 'शनि', 'Rahu': 'राहु', 'Ketu': 'केतु'
    }
    
    dasha_bhogya = "नाही" if current_lang == 'mr' else "None"
    if balance_dict:
        b_lord = list(balance_dict.keys())[0]
        b_years_dec = float(balance_dict[b_lord])
        
        # Convert decimal years to y, m, d
        y = int(b_years_dec)
        rem = b_years_dec - y
        m = int(rem * 12)
        rem_m = (rem * 12) - m
        d = int(round(rem_m * 30.4375))
        if d >= 30:
            m += d // 30
            d = d % 30
        if m >= 12:
            y += m // 12
            m = m % 12
            
        lord_disp = PLANET_NAME_BHOGYA_MR.get(b_lord, b_lord) if current_lang == 'mr' else b_lord
        dasha_bhogya = f"{lord_disp} {y}y {m}m {d}d"

    RASHI_LORD_MAP = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    moon_sign_english = None
    for h in chart_dict['d1Chart']['houses']:
        for occ in h.get('occupants', []):
            if occ['celestialBody'] == 'Moon':
                moon_sign_english = h['sign']
                break

    lord_en = RASHI_LORD_MAP.get(moon_sign_english, '') if moon_sign_english else ''
    rashi_swami = PLANET_NAME_MR.get(lord_en, lord_en) if current_lang == 'mr' else lord_en

    
    nak_key = None
    for k in NAKSHATRAS.keys():
        if k.lower() == moon_nak.strip().lower():
            nak_key = k
            break
            
    yoni_val = "--"
    gana_val = "--"
    nadi_val = "--"
    varna_val = "--"
    nak_lord = "--"
    nak_paya = "चांदी" if current_lang == 'mr' else "Silver"
    
    if nak_key:
        props = NAKSHATRAS[nak_key]
        YONI_MR = {'Horse': 'अश्व (Horse)', 'Elephant': 'गज (Elephant)', 'Sheep': 'मेष (Sheep)', 'Serpent': 'सर्प (Serpent)', 'Dog': 'श्वान (Dog)', 'Cat': 'मार्जार (Cat)', 'Rat': 'मूषक (Rat)', 'Cow': 'गौ (Cow)', 'Buffalo': 'महिष (Buffalo)', 'Tiger': 'व्याघ्र (Tiger)', 'Hare': 'शशक (Hare)', 'Monkey': 'वानर (Monkey)', 'Lion': 'सिंह (Lion)', 'Mongoose': 'नकुल (Mongoose)'}
        GANA_MR = {'Deva': 'देव (Deva)', 'Manushya': 'मनुष्य (Manushya)', 'Rakshasa': 'राक्षस (Rakshasa)'}
        NADI_MR = {'Adi': 'आद्य (वात)', 'Madhya': 'मध्य (पित्त)', 'Antya': 'अंत्य (कफ)'}
        VARNA_MR = {'Brahmin': 'ब्राह्मण (Brahmin)', 'Kshatriya': 'क्षत्रिय (Kshatriya)', 'Vaishya': 'वैश्य (Vaishya)', 'Shudra': 'शूद्र (Shudra)'}
        
        if current_lang == 'mr':
            yoni_val = YONI_MR.get(props['yoni'], props['yoni'])
            gana_val = GANA_MR.get(props['gana'], props['gana'])
            nadi_val = NADI_MR.get(props['nadi'], props['nadi'])
            varna_val = VARNA_MR.get(props['varna'], props['varna'])
            nak_lord = PLANET_NAME_MR.get(props['lord'], props['lord'])
        else:
            yoni_val = props['yoni']
            gana_val = props['gana']
            NADI_EN = {'Adi': 'Adya (Vata)', 'Madhya': 'Madhya (Pitta)', 'Antya': 'Antya (Kapha)'}
            nadi_val = NADI_EN.get(props['nadi'], props['nadi'])
            varna_val = props['varna']
            nak_lord = props['lord']
            
        from panchang_app.utils.panchang_calc import SIGN_MAP
        m_idx = SIGN_MAP.get(moon_sign, 1)
        if m_idx in [1, 6, 11]:
            nak_paya = "सोने (Gold)" if current_lang == 'mr' else "Gold"
        elif m_idx in [2, 5, 9]:
            nak_paya = "चांदी (Silver)" if current_lang == 'mr' else "Silver"
        elif m_idx in [3, 7, 10]:
            nak_paya = "तांबे (Copper)" if current_lang == 'mr' else "Copper"
        else:
            nak_paya = "लोखंड (Iron)" if current_lang == 'mr' else "Iron"

    RATNA_MAP_MR = {
        'Aries': 'पोवळे (Red Coral)', 'Taurus': 'हिरा (Diamond)', 'Gemini': 'पाचू (Emerald)',
        'Cancer': 'मोती (Pearl)', 'Leo': 'माणिक (Ruby)', 'Virgo': 'पाचू (Emerald)',
        'Libra': 'हिरा (Diamond)', 'Scorpio': 'पोवळे (Red Coral)', 'Sagittarius': 'पुष्कराज (Yellow Sapphire)',
        'Capricorn': 'नीलम (Blue Sapphire)', 'Aquarius': 'नीलम (Blue Sapphire)', 'Pisces': 'पुष्कराज (Yellow Sapphire)'
    }
    rashi_ratna = RATNA_MAP_MR.get(moon_sign_english, 'Unknown') if moon_sign_english else 'Unknown'

    trans = TRANSLATIONS.get(current_lang, TRANSLATIONS['mr'])
    
    return {
        'name': name or (trans.get('current_chart', 'सध्याची कुंडली')),
        'gender': gender or 'Male',
        'date_of_birth': date_val,
        'time_of_birth': time_val,
        'place_of_birth': place_name,
        'latitude': latitude,
        'longitude': longitude,
        'timezone': timezone_name,
        'svg_chart': svg_chart,
        'svg_chart_d9': svg_chart_d9,
        'planets': full_planet_rows,
        'nakshatra': moon_nak,
        'pada': moon_pada,
        'namakshar': moon_namakshar,
        'lagna': sign_names.get(lagna_sign, lagna_sign),
        'lagna_deg': lagna_deg_str,
        'rashi': moon_sign,
        'all_dashas': all_dashas,
        'panchang': panchang_data,
        'mangal_dosha': has_mangal_dosha,
        'dasha_bhogya': dasha_bhogya,
        'rashi_swami': rashi_swami,
        'nak_swami': nak_lord,
        'nak_paya': nak_paya,
        'yoni': yoni_val,
        'gana': gana_val,
        'nadi': nadi_val,
        'varna': varna_val,
        'rashi_ratna': rashi_ratna,
    }
    
    cache.set(cache_key, result_dict, timeout=60 * 60 * 24 * 7) # Cache for 7 days
    return result_dict

@login_required
def kundali_view(request):
    current_lang = request.session.get('lang', 'mr')
    trans = TRANSLATIONS.get(current_lang, TRANSLATIONS['mr'])
    
    if request.method == 'POST':
        form = KundaliForm(request.POST)
        if form.is_valid():
            kundali = form.save(commit=False)
            kundali.user = request.user
            kundali.save()
            messages.success(request, f"Janma Kundali for '{kundali.name}' generated and saved successfully!")
            return redirect('kundali_detail', pk=kundali.pk)
        else:
            messages.error(request, "Failed to save Kundali. Please check the inputs.")
            return redirect('kundali')

    # GET parameters parsing
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    lat_str = request.GET.get('lat')
    lon_str = request.GET.get('lon')
    timezone_str = request.GET.get('timezone')
    place_str = request.GET.get('place_name')
    
    # Defaults
    loc = get_active_location(request)
    
    if date_str:
        try:
            date_val = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            date_val = datetime.date.today()
    else:
        date_val = datetime.date.today()
        
    if time_str:
        try:
            if len(time_str) > 5:
                time_val = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
            else:
                time_val = datetime.datetime.strptime(time_str, '%H:%M').time()
        except Exception:
            time_val = datetime.datetime.now().time()
    else:
        time_val = datetime.datetime.now().time()
        
    latitude = float(lat_str) if lat_str else float(loc['latitude'])
    longitude = float(lon_str) if lon_str else float(loc['longitude'])
    timezone_name = timezone_str if timezone_str else loc['timezone']
    place_name = place_str if place_str else loc['place_name']
    
    # Compute context data
    chart_context = compute_kundali_details(
        date_val, time_val, latitude, longitude, timezone_name, place_name, current_lang=current_lang
    )
    
    form = KundaliForm(initial={
        'date_of_birth': date_val,
        'time_of_birth': time_val,
        'place_of_birth': place_name,
        'latitude': latitude,
        'longitude': longitude,
        'timezone': timezone_name,
        'country': 'India',
        'state': 'Maharashtra'
    })
    
    saved_kundalis = KundaliRecord.objects.select_related('user').filter(user=request.user)
    
    context = {
        **chart_context,
        'form': form,
        'saved_kundalis': saved_kundalis,
        'trans': trans,
        'current_lang': current_lang,
        'is_recalculated': True,
        'selected_profile_id': None
    }
    
    return render(request, 'kundali.html', context)

@login_required
def kundali_detail_view(request, pk):
    current_lang = request.session.get('lang', 'mr')
    trans = TRANSLATIONS.get(current_lang, TRANSLATIONS['mr'])
    
    kundali = get_object_or_404(KundaliRecord, pk=pk, user=request.user)
    
    # GET parameters parsing (allow temporary recalculations)
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    lat_str = request.GET.get('lat')
    lon_str = request.GET.get('lon')
    timezone_str = request.GET.get('timezone')
    place_str = request.GET.get('place_name')
    
    date_val = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else kundali.date_of_birth
    if time_str:
        try:
            if len(time_str) > 5:
                time_val = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
            else:
                time_val = datetime.datetime.strptime(time_str, '%H:%M').time()
        except Exception:
            time_val = kundali.time_of_birth
    else:
        time_val = kundali.time_of_birth
        
    latitude = float(lat_str) if lat_str else (float(kundali.latitude) if kundali.latitude is not None else 21.1458)
    longitude = float(lon_str) if lon_str else (float(kundali.longitude) if kundali.longitude is not None else 79.0882)
    timezone_name = timezone_str if timezone_str else kundali.timezone
    place_name = place_str if place_str else kundali.place_of_birth
    
    # Compute context data
    chart_context = compute_kundali_details(
        date_val, time_val, latitude, longitude, timezone_name, place_name,
        name=kundali.name, gender=kundali.gender, current_lang=current_lang
    )
    
    form = KundaliForm(initial={
        'name': kundali.name,
        'gender': kundali.gender,
        'date_of_birth': date_val,
        'time_of_birth': time_val,
        'place_of_birth': place_name,
        'latitude': latitude,
        'longitude': longitude,
        'timezone': timezone_name,
        'country': kundali.country,
        'state': kundali.state
    })
    
    MANTRA_DEFINITIONS = {
        'सूर्य': {'text': 'ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः', 'jap': '28,000'},
        'चन्द्र': {'text': 'ॐ श्रां श्रीं श्रौं सः चन्द्राय नमः', 'jap': '44,000'},
        'मंगळ': {'text': 'ॐ क्रां क्रीं क्रौं सः भौमाय नमः', 'jap': '40,000'},
        'बुध': {'text': 'ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः', 'jap': '36,000'},
        'गुरु': {'text': 'ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः', 'jap': '76,000'},
        'शुक्र': {'text': 'ॐ द्रां द्रीं द्रौं सः शुक्राय नमः', 'jap': '64,000'},
        'शनि': {'text': 'ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः', 'jap': '92,000'},
        'राहू': {'text': 'ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः', 'jap': '72,000'},
        'केतु': {'text': 'ॐ स्रां स्रीं स्रौं सः केतवे नमः', 'jap': '68,000'},
        'महा मृत्युंजय मंत्र': {'text': 'ॐ त्र्यंबकं यजामहे सुगन्धिं पुष्टिवर्धनम् ।<br>उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात् ॥', 'jap': '1,35,000'},
    }
    
    selected_mantras = []
    if kundali.mantra_upasana:
        for m in kundali.mantra_upasana:
            if m in MANTRA_DEFINITIONS:
                selected_mantras.append({'name': m, **MANTRA_DEFINITIONS[m]})
                
    saved_kundalis = KundaliRecord.objects.filter(user=request.user)
    
    context = {
        **chart_context,
        'form': form,
        'saved_kundalis': saved_kundalis,
        'trans': trans,
        'current_lang': current_lang,
        'is_recalculated': True,
        'selected_profile_id': pk,
        'profile_name': kundali.name,
        'shanti_pujan': kundali.shanti_pujan,
        'mantra_upasana_details': selected_mantras,
        'phalashruti': kundali.phalashruti,
        'all_shanti_choices': [choice[0] for choice in SHANTI_PUJAN_CHOICES],
        'all_mantra_choices': [choice[0] for choice in MANTRA_UPASANA_CHOICES],
    }
    
    return render(request, 'kundali.html', context)

@login_required
def delete_kundali_view(request, pk):
    kundali = get_object_or_404(KundaliRecord, pk=pk, user=request.user)
    name = kundali.name
    kundali.delete()
    messages.success(request, f"Kundali profile for '{name}' deleted successfully.")
    return redirect('kundali')

@login_required
def kundali_milan_view(request):
    saved_kundalis = KundaliRecord.objects.filter(user=request.user)
    
    if request.method == 'POST':
        groom_id = request.POST.get('groom_id')
        bride_id = request.POST.get('bride_id')
        
        if groom_id and bride_id:
            groom = get_object_or_404(KundaliRecord, id=groom_id, user=request.user)
            bride = get_object_or_404(KundaliRecord, id=bride_id, user=request.user)
            
            g_ctx = compute_kundali_details(
                groom.date_of_birth, groom.time_of_birth, 
                float(groom.latitude or 21.1458), float(groom.longitude or 79.0882), 
                groom.timezone, groom.place_of_birth, request.session.get('lang', 'mr')
            )
            groom_nak = g_ctx.get('nakshatra') or 'Rohini'
            try:
                groom_pada = int(g_ctx.get('pada') or 1)
            except ValueError:
                groom_pada = 1
            
            b_ctx = compute_kundali_details(
                bride.date_of_birth, bride.time_of_birth, 
                float(bride.latitude or 21.1458), float(bride.longitude or 79.0882), 
                bride.timezone, bride.place_of_birth, request.session.get('lang', 'mr')
            )
            bride_nak = b_ctx.get('nakshatra') or 'Rohini'
            try:
                bride_pada = int(b_ctx.get('pada') or 1)
            except ValueError:
                bride_pada = 1
            
            result = calculate_milan(groom_nak, bride_nak, groom_pada, bride_pada, request.session.get('lang', 'mr'))
            
            context = {
                'groom': {'name': groom.name, 'dob': groom.date_of_birth, 'tob': groom.time_of_birth, 'pob': groom.place_of_birth, 'nakshatra': g_ctx.get('nakshatra'), 'rashi': g_ctx.get('rashi'), 'pada': groom_pada},
                'bride': {'name': bride.name, 'dob': bride.date_of_birth, 'tob': bride.time_of_birth, 'pob': bride.place_of_birth, 'nakshatra': b_ctx.get('nakshatra'), 'rashi': b_ctx.get('rashi'), 'pada': bride_pada},
                'result': result,
                'saved_kundalis': saved_kundalis
            }
            return render(request, 'kundali_milan_result.html', context)
            
    return render(request, 'kundali_milan.html', {'saved_kundalis': saved_kundalis})

@login_required
def get_kundali_details_api(request, kundali_id):
    try:
        kundali = get_object_or_404(KundaliRecord, id=kundali_id, user=request.user)
        
        details = compute_kundali_details(
            kundali.date_of_birth,
            kundali.time_of_birth,
            float(kundali.latitude or 21.1458),
            float(kundali.longitude or 79.0882),
            kundali.timezone,
            kundali.place_of_birth,
            current_lang='en' # use english internal name for logic
        )
        
        return JsonResponse({
            'success': True,
            'name': kundali.name,
            'dob': kundali.date_of_birth.strftime('%Y-%m-%d'),
            'tob': kundali.time_of_birth.strftime('%H:%M:%S'),
            'pob': kundali.place_of_birth,
            'nakshatra': details.get('nakshatra', 'Unknown'),
            'rashi': details.get('rashi', 'Unknown'),
            'charan': details.get('pada', 'Unknown'),
            'namakshar': details.get('namakshar', 'Unknown')
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["POST"])
def api_save_kundali_profile(request):
    try:
        data = json.loads(request.body)
        
        name = data.get('name')
        gender = data.get('gender')
        date_str = data.get('date_of_birth')
        time_str = data.get('time_of_birth')
        place = data.get('place_of_birth')
        lat = data.get('latitude')
        lon = data.get('longitude')
        tz = data.get('timezone', 'Asia/Kolkata')
        country = data.get('country', 'India')
        state = data.get('state', 'Maharashtra')
        
        if not all([name, gender, date_str, time_str, place]):
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if len(time_str) > 5:
            time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
        else:
            time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
            
        kundali = KundaliRecord.objects.create(
            user=request.user,
            name=name,
            gender=gender,
            date_of_birth=date_obj,
            time_of_birth=time_obj,
            place_of_birth=place,
            latitude=float(lat) if lat else None,
            longitude=float(lon) if lon else None,
            timezone=tz,
            country=country,
            state=state
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Kundali Saved Successfully',
            'kundali': {
                'id': kundali.id,
                'name': kundali.name,
                'date_of_birth': kundali.date_of_birth.strftime('%d/%m/%Y')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

from django.template.loader import render_to_string

@login_required
@require_http_methods(["GET"])
def api_calculate_kundali(request):
    try:
        current_lang = request.session.get('lang', 'mr')
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')
        lat_str = request.GET.get('lat')
        lon_str = request.GET.get('lon')
        timezone_str = request.GET.get('timezone')
        place_str = request.GET.get('place_name')
        
        date_val = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        if len(time_str) > 5:
            time_val = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
        else:
            time_val = datetime.datetime.strptime(time_str, '%H:%M').time()
            
        latitude = float(lat_str)
        longitude = float(lon_str)
        
        # We can implement caching here by hashing the inputs!
        cache_key = f"kundali_{date_str}_{time_str}_{latitude}_{longitude}_{timezone_str}_{current_lang}"
        from django.core.cache import cache
        cached_html = cache.get(cache_key)
        
        if cached_html:
            return JsonResponse({'success': True, 'html': cached_html})
            
        chart_context = compute_kundali_details(
            date_val, time_val, latitude, longitude, timezone_str, place_str, current_lang=current_lang
        )
        
        context = {
            **chart_context,
            'current_lang': current_lang,
            'trans': TRANSLATIONS.get(current_lang, TRANSLATIONS['mr'])
        }
        
        html = render_to_string('kundali_content.html', context, request=request)
        cache.set(cache_key, html, timeout=60 * 60) # Cache for 1 hour
        
        return JsonResponse({'success': True, 'html': html})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["GET"])
def export_kundali_pdf(request):
    try:
        from weasyprint import HTML
    except ImportError:
        return JsonResponse({'success': False, 'error': 'WeasyPrint not properly installed.'}, status=500)
    except OSError as e:
        return JsonResponse({'success': False, 'error': f'WeasyPrint OS Error: {str(e)}'}, status=500)

    try:
        current_lang = request.session.get('lang', 'mr')
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')
        lat_str = request.GET.get('lat')
        lon_str = request.GET.get('lon')
        timezone_str = request.GET.get('timezone')
        place_str = request.GET.get('place_name')
        
        date_val = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        if len(time_str) > 5:
            time_val = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
        else:
            time_val = datetime.datetime.strptime(time_str, '%H:%M').time()
            
        latitude = float(lat_str)
        longitude = float(lon_str)
        
        chart_context = compute_kundali_details(
            date_val, time_val, latitude, longitude, timezone_str, place_str, current_lang=current_lang
        )
        
        context = {
            **chart_context,
            'current_lang': current_lang,
            'is_pdf': True,
            'trans': TRANSLATIONS.get(current_lang, TRANSLATIONS['mr'])
        }
        
        from django.template.loader import render_to_string
        html_string = render_to_string('kundali_pdf.html', context, request=request)
        
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        from django.http import HttpResponse
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Kundali_{date_str}.pdf"'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

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
            
    # Fetch locations for settings page
    recent_ids = request.session.get('recent_locations', [])
    from django.db.models import Q
    q_objects = Q(id__in=recent_ids)
    if request.user.is_authenticated:
        q_objects |= Q(user=request.user)
    saved_locations = LocationMaster.objects.filter(q_objects, is_active=True).distinct().order_by('-created_date')[:50]
    
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
        loc_id = data.get('id')
        location_name = data.get('location_name', '').strip() or data.get('city_village', '').strip()
        if not location_name:
            return JsonResponse({'status': 'error', 'message': 'Location name is required'}, status=400)
            
        try:
            lat = float(data.get('latitude', 0.0) or 0.0)
            lon = float(data.get('longitude', 0.0) or 0.0)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid latitude or longitude format'}, status=400)
        
        user = request.user if request.user.is_authenticated else None
        
        if loc_id:
            try:
                # Prioritize user's own location or global location
                loc = LocationMaster.objects.filter(id=loc_id).first()
                if not loc:
                    return JsonResponse({'status': 'error', 'message': 'Location not found'}, status=404)
                
                # If location belongs to someone else, don't overwrite it. Create a new one.
                if loc.user and loc.user != user:
                    loc = LocationMaster(user=user)
                    
                loc.location_name = location_name
                loc.country = data.get('country', 'India')
                loc.state = data.get('state', '')
                loc.district = data.get('district', '')
                loc.city_village = data.get('city_village', '')
                loc.latitude = lat
                loc.longitude = lon
                loc.timezone = data.get('timezone', 'Asia/Kolkata')
                loc.is_active = True
                if user and not loc.user:
                    loc.user = user
                loc.save()
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            # Check duplicate only when creating new
            existing = LocationMaster.objects.filter(
                location_name=location_name, latitude=lat, longitude=lon, user=user
            ).first()
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    existing.save()
                loc = existing
            else:
                loc = LocationMaster.objects.create(
                    user=user,
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
                
        # If user is authenticated, update their preferred location
        if user and hasattr(user, 'preferred_location'):
            user.preferred_location = loc
            user.save(update_fields=['preferred_location'])
        
        # Add to recent locations in session so it appears in dropdowns immediately
        recent_ids = request.session.get('recent_locations', [])
        if loc.id not in recent_ids:
            recent_ids.insert(0, loc.id)
            request.session['recent_locations'] = recent_ids[:10]
            request.session.modified = True
            
        return JsonResponse({'status': 'success', 'message': 'Location saved successfully', 'id': loc.id})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def api_recent_locations(request):
    recent_ids = request.session.get('recent_locations', [])
    
    from django.db.models import Q
    
    # Base query for session locations
    q_objects = Q(id__in=recent_ids)
    
    # If authenticated, also fetch user's saved locations
    if request.user.is_authenticated:
        q_objects |= Q(user=request.user)
        
    locations = LocationMaster.objects.filter(q_objects, is_active=True).distinct().order_by('-created_date')[:10]
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

def rashibhavishya_index(request):
    from panchang_app.utils.horoscope_calc import RASHIS
    context = {
        'rashis': RASHIS
    }
    return render(request, 'rashibhavishya_index.html', context)

def rashibhavishya_detail(request, rashi_name):
    from panchang_app.utils.horoscope_calc import RASHIS, get_all_horoscopes
    if rashi_name not in RASHIS:
        messages.error(request, "अवैध राशी (Invalid Rashi)")
        return redirect('rashibhavishya_index')
        
    horoscopes = get_all_horoscopes(rashi_name)
    
    context = {
        'rashi_name': rashi_name,
        'daily': horoscopes['daily'],
        'tomorrow': horoscopes['tomorrow'],
        'monthly': horoscopes['monthly']
    }
    return render(request, 'rashibhavishya_detail.html', context)

@login_required
def update_shanti_pujan(request, pk):
    if request.method == 'POST':
        kundali = get_object_or_404(KundaliRecord, pk=pk, user=request.user)
        shanti_list = request.POST.getlist('shanti_pujan')
        mantra_list = request.POST.getlist('mantra_upasana')
        
        kundali.shanti_pujan = shanti_list
        kundali.mantra_upasana = mantra_list
        kundali.save()
        
        messages.success(request, "शांती पूजन व मंत्र उपासना जतन करण्यात आले (Saved successfully).")
        return redirect('kundali_detail', pk=pk)
    return redirect('kundali')
