from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.timezone import now as tz_now

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    preferred_location = models.ForeignKey(
        'LocationMaster',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_users'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

class Panchang(models.Model):
    date = models.DateField(unique=True)
    tithi = models.CharField(max_length=50)
    vaar = models.CharField(max_length=50)
    nakshatra = models.CharField(max_length=50)
    yoga = models.CharField(max_length=50)
    karan = models.CharField(max_length=50)
    sunrise = models.TimeField()
    sunset = models.TimeField()
    moonrise = models.TimeField()
    moonset = models.TimeField()
    
    # Masik calendar highlights
    is_ekadashi = models.BooleanField(default=False)
    is_pournima = models.BooleanField(default=False)
    is_amavasya = models.BooleanField(default=False)
    is_sankashti = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - Tithi: {self.tithi}, Vaar: {self.vaar}"

class Festival(models.Model):
    CATEGORY_CHOICES = [
        ('Festival', 'Festival'),
        ('Jayanti', 'Jayanti'),
        ('Punyatithi', 'Punyatithi'),
        ('Vrat', 'Vrat'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    date = models.DateField(db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Festival', db_index=True)
    image = models.ImageField(upload_to='festivals/', blank=True, null=True)

    class Meta:
        ordering = ['date', 'name']

    def __str__(self):
        return f"{self.name} ({self.date})"

class ShubhaMuhurt(models.Model):
    CATEGORY_CHOICES = [
        ('Marriage', 'Marriage (Vivah)'),
        ('Gruh Pravesh', 'Gruh Pravesh'),
        ('Naming Ceremony', 'Naming Ceremony (Namkaran)'),
        ('Business', 'Business (Udyog/Vyapar)'),
        ('Other', 'Other Auspicious Event'),
    ]
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Other', db_index=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time.date()})"

class LocationMaster(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, null=True, blank=True, related_name='saved_locations')
    location_name = models.CharField(max_length=150, default='', db_index=True)
    country = models.CharField(max_length=100, default='India')
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    city_village = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timezone = models.CharField(max_length=100, default='Asia/Kolkata')
    created_date = models.DateTimeField(default=tz_now)
    updated_date = models.DateTimeField(default=tz_now)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['location_name']
        verbose_name = 'Location Master'
        verbose_name_plural = 'Location Masters'

    def __str__(self):
        parts = [self.location_name]
        if self.district:
            parts.append(self.district)
        if self.state:
            parts.append(self.state)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)

    @property
    def place_name(self):
        return self.location_name

SHANTI_PUJAN_CHOICES = [
    ('नवग्रह शांती', 'नवग्रह शांती'),
    ('गुरु शांती', 'गुरु शांती'),
    ('मंगळ दोष शांती', 'मंगळ दोष शांती'),
    ('शनि शांती', 'शनि शांती'),
    ('राहु-केतु शांती', 'राहु-केतु शांती'),
    ('कालसर्प दोष', 'कालसर्प दोष'),
    ('पितृ दोष शांती', 'पितृ दोष शांती'),
    ('त्रीपिंडी श्राद्ध', 'त्रीपिंडी श्राद्ध'),
    ('चांडाळ योग शांती', 'चांडाळ योग शांती'),
    ('नक्षत्र शांती', 'नक्षत्र शांती'),
    ('लक्ष्मी शांती', 'लक्ष्मी शांती'),
    ('महामृत्युंजय जप', 'महामृत्युंजय जप'),
    ('वास्तु शांती', 'वास्तु शांती'),
    ('कुंभ विवाह', 'कुंभ विवाह'),
    ('नवचंडी विधान', 'नवचंडी विधान'),
]

MANTRA_UPASANA_CHOICES = [
    ('सूर्य', 'सूर्य'),
    ('चन्द्र', 'चन्द्र'),
    ('मंगळ', 'मंगळ'),
    ('बुध', 'बुध'),
    ('गुरु', 'गुरु'),
    ('शुक्र', 'शुक्र'),
    ('शनि', 'शनि'),
    ('राहू', 'राहू'),
    ('केतु', 'केतु'),
    ('महा मृत्युंजय मंत्र', 'महा मृत्युंजय मंत्र'),
]

class KundaliRecord(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='kundalis')
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(db_index=True)
    time_of_birth = models.TimeField()
    place_of_birth = models.CharField(max_length=100, db_index=True)
    
    # Detailed birth location fields
    country = models.CharField(max_length=100, default='India')
    state = models.CharField(max_length=100, default='Maharashtra')
    district = models.CharField(max_length=100, blank=True)
    city_village = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    
    shanti_pujan = models.JSONField(default=list, blank=True)
    mantra_upasana = models.JSONField(default=list, blank=True)
    phalashruti = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.date_of_birth} ({self.place_of_birth})"
