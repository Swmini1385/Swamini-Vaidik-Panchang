import datetime
import hashlib
import random

RASHIS = [
    'मेष', 'वृषभ', 'मिथुन', 'कर्क', 
    'सिंह', 'कन्या', 'तुळ', 'वृश्चिक', 
    'धनु', 'मकर', 'कुंभ', 'मीन'
]

# Provide static banks for deterministic pseudo-random selection
LUCKY_COLORS = ['लाल', 'पांढरा', 'पिवळा', 'निळा', 'हिरवा', 'केशरी', 'गुलाबी', 'जांभळा', 'सोनेरी', 'चांदी', 'करडा', 'तपकिरी']
LUCKY_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 21, 33]
LUCKY_TIMES = ['सकाळी ०८:०० ते १०:००', 'दुपारी १२:१५ ते ०१:३०', 'संध्याकाळी ०५:०० ते ०६:३०', 'सकाळी १०:३० ते १२:००', 'दुपारी ०२:०० ते ०४:००', 'संध्याकाळी ०७:०० ते ०८:३०']

SUMMARY_BANK = [
    "आजचा दिवस तुमच्यासाठी अत्यंत लाभदायक ठरू शकतो. जुनी रखडलेली कामे पूर्ण होतील.",
    "आज काही अनपेक्षित गोष्टी घडू शकतात, त्यामुळे सावधगिरी बाळगा. शांत डोक्याने निर्णय घ्या.",
    "मित्रांच्या किंवा परिवाराच्या मदतीने तुम्हाला नवीन ऊर्जा मिळेल. प्रवासाचे योग आहेत.",
    "कामाच्या ठिकाणी तुमच्या प्रयत्नांना यश मिळेल. वरिष्ठ अधिकाऱ्यांकडून कौतुक होऊ शकते.",
    "आज आरोग्याकडे लक्ष देण्याची गरज आहे. आहारावर नियंत्रण ठेवा.",
    "आर्थिक लाभ होण्याची दाट शक्यता आहे. नवीन गुंतवणूक करण्यासाठी दिवस चांगला आहे.",
    "आजचा दिवस संमिश्र फळ देणारा राहील. काही कामांमध्ये विलंब होऊ शकतो."
]

LOVE_BANK = [
    "जोडीदारासोबत वेळ छान मजेत जाईल. नात्यामध्ये अधिक गोडवा येईल.",
    "लग्नाळू लोकांसाठी आज चांगली स्थळे चालून येतील. सकारात्मक प्रतिसाद मिळेल.",
    "आज जोडीदारासोबत काही गैरसमज होऊ शकतात, शांततेने चर्चा करून प्रश्न सोडवा.",
    "प्रेम संबंधांमध्ये एकमेकांवरील विश्वास वाढेल. जोडीदाराकडून छान सरप्राईझ मिळेल."
]

CAREER_BANK = [
    "नोकरीच्या ठिकाणी नवीन जबाबदारी मिळेल. बॉस तुमच्या कामावर खूश राहतील.",
    "नवीन नोकरीच्या शोधात असणाऱ्यांना आज चांगली बातमी मिळू शकते.",
    "कामाच्या ठिकाणी सहकाऱ्यांसोबत वाद टाळा. तुमच्या कामावर लक्ष केंद्रित करा.",
    "व्यवसायात नवीन करार किंवा डील पक्की होऊ शकते. फायदा होईल."
]

FINANCE_BANK = [
    "आज पैशांची आवक चांगली राहील. अडकलेले पैसे परत मिळतील.",
    "खर्चावर नियंत्रण ठेवणे गरजेचे आहे. अनावश्यक खर्च करणे टाळा.",
    "शेअर मार्केट किंवा म्यूचुअल फंडमध्ये गुंतवणूक करण्यासाठी दिवस अनुकूल आहे.",
    "एखाद्या मोठ्या खर्चाचा सामना करावा लागू शकतो. बजेट बनवून काम करा."
]

HEALTH_BANK = [
    "आरोग्य उत्तम राहील. आज तुम्ही खूप उत्साही असाल.",
    "पोटाचे किंवा पचनाचे त्रास उद्भवू शकतात. बाहेरचे खाणे टाळा.",
    "डोकेदुखी किंवा थकवा जाणवू शकतो. पुरेशी विश्रांती घेणे आवश्यक आहे.",
    "नियमित व्यायाम करा आणि ताणतणाव कमी करण्यासाठी योगा किंवा ध्यान करा."
]

def get_seeded_random(seed_string):
    """Generate a stable pseudo-random number generator based on a string seed."""
    seed_int = int(hashlib.md5(seed_string.encode('utf-8')).hexdigest(), 16)
    r = random.Random(seed_int)
    return r

def get_horoscope(rashi_name, date_obj, time_period='daily'):
    """
    time_period can be 'daily', 'tomorrow', or 'monthly'
    """
    if time_period == 'monthly':
        # Seed by year and month
        seed = f"{rashi_name}_monthly_{date_obj.year}_{date_obj.month}"
        title = f"{date_obj.strftime('%B %Y')} चे मासिक भविष्य"
    else:
        # Seed by exact date
        seed = f"{rashi_name}_{time_period}_{date_obj.strftime('%Y-%m-%d')}"
        if time_period == 'tomorrow':
            title = "उद्याचे भविष्य"
        else:
            title = "आजचे भविष्य"

    r = get_seeded_random(seed)
    
    return {
        'rashi': rashi_name,
        'title': title,
        'lucky_color': r.choice(LUCKY_COLORS),
        'lucky_number': r.choice(LUCKY_NUMBERS),
        'lucky_time': r.choice(LUCKY_TIMES),
        'summary': r.choice(SUMMARY_BANK),
        'love': r.choice(LOVE_BANK),
        'career': r.choice(CAREER_BANK),
        'finance': r.choice(FINANCE_BANK),
        'health': r.choice(HEALTH_BANK)
    }

def get_all_horoscopes(rashi_name):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    return {
        'daily': get_horoscope(rashi_name, today, 'daily'),
        'tomorrow': get_horoscope(rashi_name, tomorrow, 'tomorrow'),
        'monthly': get_horoscope(rashi_name, today, 'monthly'),
    }
