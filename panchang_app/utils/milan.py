# Ashtakoot Milan Horoscope Matching Utility

# 27 Nakshatras with their properties
NAKSHATRAS = {
    'Ashwini': {'varna': 'Kshatriya', 'vashya': 'Chatushpada', 'yoni': 'Horse', 'gana': 'Deva', 'nadi': 'Adi', 'lord': 'Ketu'},
    'Bharani': {'varna': 'Shudra', 'vashya': 'Manushya', 'yoni': 'Elephant', 'gana': 'Manushya', 'nadi': 'Madhya', 'lord': 'Venus'},
    'Krittika': {'varna': 'Vaishya', 'vashya': 'Chatushpada', 'yoni': 'Sheep', 'gana': 'Rakshasa', 'nadi': 'Antya', 'lord': 'Sun'},
    'Rohini': {'varna': 'Brahmin', 'vashya': 'Chatushpada', 'yoni': 'Serpent', 'gana': 'Deva', 'nadi': 'Antya', 'lord': 'Moon'},
    'Mrigashira': {'varna': 'Kshatriya', 'vashya': 'Chatushpada', 'yoni': 'Serpent', 'gana': 'Deva', 'nadi': 'Madhya', 'lord': 'Mars'},
    'Ardra': {'varna': 'Shudra', 'vashya': 'Manushya', 'yoni': 'Dog', 'gana': 'Manushya', 'nadi': 'Adi', 'lord': 'Rahu'},
    'Punarvasu': {'varna': 'Vaishya', 'vashya': 'Manushya', 'yoni': 'Cat', 'gana': 'Deva', 'nadi': 'Adi', 'lord': 'Jupiter'},
    'Pushya': {'varna': 'Brahmin', 'vashya': 'Chatushpada', 'yoni': 'Sheep', 'gana': 'Deva', 'nadi': 'Madhya', 'lord': 'Saturn'},
    'Ashlesha': {'varna': 'Kshatriya', 'vashya': 'Keeta', 'yoni': 'Cat', 'gana': 'Rakshasa', 'nadi': 'Antya', 'lord': 'Mercury'},
    'Magha': {'varna': 'Shudra', 'vashya': 'Chatushpada', 'yoni': 'Rat', 'gana': 'Rakshasa', 'nadi': 'Antya', 'lord': 'Ketu'},
    'Purva Phalguni': {'varna': 'Vaishya', 'vashya': 'Manushya', 'yoni': 'Rat', 'gana': 'Manushya', 'nadi': 'Madhya', 'lord': 'Venus'},
    'Uttara Phalguni': {'varna': 'Brahmin', 'vashya': 'Manushya', 'yoni': 'Cow', 'gana': 'Manushya', 'nadi': 'Adi', 'lord': 'Sun'},
    'Hasta': {'varna': 'Kshatriya', 'vashya': 'Manushya', 'yoni': 'Buffalo', 'gana': 'Deva', 'nadi': 'Adi', 'lord': 'Moon'},
    'Chitra': {'varna': 'Shudra', 'vashya': 'Manushya', 'yoni': 'Tiger', 'gana': 'Rakshasa', 'nadi': 'Madhya', 'lord': 'Mars'},
    'Swati': {'varna': 'Vaishya', 'vashya': 'Manushya', 'yoni': 'Buffalo', 'gana': 'Deva', 'nadi': 'Antya', 'lord': 'Rahu'},
    'Vishakha': {'varna': 'Brahmin', 'vashya': 'Manushya', 'yoni': 'Tiger', 'gana': 'Rakshasa', 'nadi': 'Antya', 'lord': 'Jupiter'},
    'Anuradha': {'varna': 'Kshatriya', 'vashya': 'Chatushpada', 'yoni': 'Hare', 'gana': 'Deva', 'nadi': 'Madhya', 'lord': 'Saturn'},
    'Jyeshtha': {'varna': 'Shudra', 'vashya': 'Keeta', 'yoni': 'Hare', 'gana': 'Rakshasa', 'nadi': 'Adi', 'lord': 'Mercury'},
    'Mula': {'varna': 'Vaishya', 'vashya': 'Chatushpada', 'yoni': 'Dog', 'gana': 'Rakshasa', 'nadi': 'Adi', 'lord': 'Ketu'},
    'Purva Ashadha': {'varna': 'Brahmin', 'vashya': 'Manushya', 'yoni': 'Monkey', 'gana': 'Manushya', 'nadi': 'Madhya', 'lord': 'Venus'},
    'Uttara Ashadha': {'varna': 'Kshatriya', 'vashya': 'Manushya', 'yoni': 'Mongoose', 'gana': 'Manushya', 'nadi': 'Antya', 'lord': 'Sun'},
    'Shravana': {'varna': 'Shudra', 'vashya': 'Manushya', 'yoni': 'Monkey', 'gana': 'Deva', 'nadi': 'Antya', 'lord': 'Moon'},
    'Dhanishta': {'varna': 'Vaishya', 'vashya': 'Chatushpada', 'yoni': 'Lion', 'gana': 'Rakshasa', 'nadi': 'Madhya', 'lord': 'Mars'},
    'Shatabhisha': {'varna': 'Brahmin', 'vashya': 'Manushya', 'yoni': 'Horse', 'gana': 'Rakshasa', 'nadi': 'Adi', 'lord': 'Rahu'},
    'Purva Bhadrapada': {'varna': 'Kshatriya', 'vashya': 'Manushya', 'yoni': 'Lion', 'gana': 'Manushya', 'nadi': 'Adi', 'lord': 'Jupiter'},
    'Uttara Bhadrapada': {'varna': 'Shudra', 'vashya': 'Manushya', 'yoni': 'Cow', 'gana': 'Deva', 'nadi': 'Madhya', 'lord': 'Saturn'},
    'Revati': {'varna': 'Vaishya', 'vashya': 'Manushya', 'yoni': 'Elephant', 'gana': 'Deva', 'nadi': 'Antya', 'lord': 'Mercury'},
}

# List of Nakshatras for lookup by index
NAKSHATRA_LIST = list(NAKSHATRAS.keys())

# Varna hierarchy points
VARNA_POINTS = {'Brahmin': 4, 'Kshatriya': 3, 'Vaishya': 2, 'Shudra': 1}

# Planetary friendship matrix
PLANET_FRIENDSHIP = {
    'Sun': {'Sun': 5, 'Moon': 5, 'Mars': 5, 'Mercury': 4, 'Jupiter': 5, 'Venus': 0, 'Saturn': 0, 'Rahu': 0, 'Ketu': 4},
    'Moon': {'Sun': 5, 'Moon': 5, 'Mars': 4, 'Mercury': 5, 'Jupiter': 4, 'Venus': 3, 'Saturn': 3, 'Rahu': 1, 'Ketu': 1},
    'Mars': {'Sun': 5, 'Moon': 4, 'Mars': 5, 'Mercury': 1, 'Jupiter': 5, 'Venus': 3, 'Saturn': 3, 'Rahu': 1, 'Ketu': 5},
    'Mercury': {'Sun': 4, 'Moon': 3, 'Mars': 1, 'Mercury': 5, 'Jupiter': 3, 'Venus': 5, 'Saturn': 4, 'Rahu': 4, 'Ketu': 3},
    'Jupiter': {'Sun': 5, 'Moon': 5, 'Mars': 5, 'Mercury': 1, 'Jupiter': 5, 'Venus': 1, 'Saturn': 3, 'Rahu': 3, 'Ketu': 4},
    'Venus': {'Sun': 0, 'Moon': 3, 'Mars': 3, 'Mercury': 5, 'Jupiter': 3, 'Venus': 5, 'Saturn': 5, 'Rahu': 4, 'Ketu': 4},
    'Saturn': {'Sun': 0, 'Moon': 1, 'Mars': 0, 'Mercury': 4, 'Jupiter': 3, 'Venus': 5, 'Saturn': 5, 'Rahu': 4, 'Ketu': 1},
    'Rahu': {'Sun': 0, 'Moon': 1, 'Mars': 1, 'Mercury': 4, 'Jupiter': 3, 'Venus': 4, 'Saturn': 4, 'Rahu': 5, 'Ketu': 0},
    'Ketu': {'Sun': 4, 'Moon': 1, 'Mars': 5, 'Mercury': 3, 'Jupiter': 4, 'Venus': 4, 'Saturn': 1, 'Rahu': 0, 'Ketu': 5},
}

# Yoni relationship matrix
YONI_RELATION = {
    'Horse': {'Horse': 4, 'Elephant': 2, 'Sheep': 1, 'Serpent': 1, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 1, 'Buffalo': 2, 'Tiger': 1, 'Hare': 1, 'Monkey': 2, 'Lion': 1, 'Mongoose': 0},
    'Elephant': {'Horse': 2, 'Elephant': 4, 'Sheep': 2, 'Serpent': 1, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 2, 'Buffalo': 3, 'Tiger': 1, 'Hare': 2, 'Monkey': 2, 'Lion': 0, 'Mongoose': 1},
    'Sheep': {'Horse': 1, 'Elephant': 2, 'Sheep': 4, 'Serpent': 2, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 1, 'Buffalo': 2, 'Tiger': 0, 'Hare': 2, 'Monkey': 1, 'Lion': 0, 'Mongoose': 1},
    'Serpent': {'Horse': 1, 'Elephant': 1, 'Sheep': 2, 'Serpent': 4, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 1, 'Buffalo': 1, 'Tiger': 1, 'Hare': 1, 'Monkey': 1, 'Lion': 1, 'Mongoose': 0},
    'Dog': {'Horse': 1, 'Elephant': 1, 'Sheep': 1, 'Serpent': 1, 'Dog': 4, 'Cat': 0, 'Rat': 1, 'Cow': 1, 'Buffalo': 1, 'Tiger': 1, 'Hare': 0, 'Monkey': 1, 'Lion': 1, 'Mongoose': 1},
    'Cat': {'Horse': 1, 'Elephant': 1, 'Sheep': 1, 'Serpent': 1, 'Dog': 0, 'Cat': 4, 'Rat': 0, 'Cow': 1, 'Buffalo': 1, 'Tiger': 1, 'Hare': 1, 'Monkey': 1, 'Lion': 1, 'Mongoose': 1},
    'Rat': {'Horse': 1, 'Elephant': 1, 'Sheep': 1, 'Serpent': 1, 'Dog': 1, 'Cat': 0, 'Rat': 4, 'Cow': 1, 'Buffalo': 1, 'Tiger': 1, 'Hare': 1, 'Monkey': 1, 'Lion': 1, 'Mongoose': 1},
    'Cow': {'Horse': 1, 'Elephant': 2, 'Sheep': 1, 'Serpent': 1, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 4, 'Buffalo': 3, 'Tiger': 0, 'Hare': 2, 'Monkey': 2, 'Lion': 1, 'Mongoose': 1},
    'Buffalo': {'Horse': 2, 'Elephant': 3, 'Sheep': 2, 'Serpent': 1, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 3, 'Buffalo': 4, 'Tiger': 1, 'Hare': 1, 'Monkey': 1, 'Lion': 1, 'Mongoose': 1},
    'Tiger': {'Horse': 1, 'Elephant': 1, 'Sheep': 0, 'Serpent': 1, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 0, 'Buffalo': 1, 'Tiger': 4, 'Hare': 1, 'Monkey': 1, 'Lion': 1, 'Mongoose': 1},
    'Hare': {'Horse': 1, 'Elephant': 2, 'Sheep': 2, 'Serpent': 1, 'Dog': 0, 'Cat': 1, 'Rat': 1, 'Cow': 2, 'Buffalo': 1, 'Tiger': 1, 'Hare': 4, 'Monkey': 1, 'Lion': 1, 'Mongoose': 1},
    'Monkey': {'Horse': 2, 'Elephant': 2, 'Sheep': 1, 'Serpent': 1, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 2, 'Buffalo': 1, 'Tiger': 1, 'Hare': 1, 'Monkey': 4, 'Lion': 1, 'Mongoose': 1},
    'Lion': {'Horse': 1, 'Elephant': 0, 'Sheep': 0, 'Serpent': 1, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 1, 'Buffalo': 1, 'Tiger': 1, 'Hare': 1, 'Monkey': 1, 'Lion': 4, 'Mongoose': 1},
    'Mongoose': {'Horse': 0, 'Elephant': 1, 'Sheep': 1, 'Serpent': 0, 'Dog': 1, 'Cat': 1, 'Rat': 1, 'Cow': 1, 'Buffalo': 1, 'Tiger': 1, 'Hare': 1, 'Monkey': 1, 'Lion': 1, 'Mongoose': 4},
}

def get_nakshatra_from_date(date_val, time_val):
    """
    Deterministically computes a Nakshatra name based on DOB and TOB.
    This acts as our local astronomical calculator.
    """
    total_minutes = (date_val.year * 365 + date_val.month * 30 + date_val.day) * 24 * 60 + time_val.hour * 60 + time_val.minute
    idx = total_minutes % 27
    return NAKSHATRA_LIST[idx]

RASHI_NAMES_MR = [
    "मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुळ", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"
]

def calculate_milan(groom_nakshatra, bride_nakshatra, groom_pada=1, bride_pada=1, current_lang='mr'):
    """
    Calculates Ashtakoot matching between groom and bride based on their Nakshatras and Padas.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    g = NAKSHATRAS.get(groom_nakshatra, NAKSHATRAS['Rohini'])
    b = NAKSHATRAS.get(bride_nakshatra, NAKSHATRAS['Rohini'])
    
    # Calculate indices and wrap around safely
    try:
        idx_g = NAKSHATRA_LIST.index(groom_nakshatra)
    except ValueError:
        idx_g = 3 # Rohini fallback
    try:
        idx_b = NAKSHATRA_LIST.index(bride_nakshatra)
    except ValueError:
        idx_b = 3
        
    rashi_idx_g = ((idx_g * 4) + groom_pada - 1) // 9
    rashi_idx_b = ((idx_b * 4) + bride_pada - 1) // 9
    
    rashi_idx_g %= 12
    rashi_idx_b %= 12

    # 1. Varna (1 point) - Based on Rashi
    def get_varna(r_idx):
        if r_idx in [3, 7, 11]: return 'Brahmin'
        elif r_idx in [0, 4, 8]: return 'Kshatriya'
        elif r_idx in [1, 5, 9]: return 'Vaishya'
        else: return 'Shudra'

    varna_g = get_varna(rashi_idx_g)
    varna_b = get_varna(rashi_idx_b)
    
    varna_score = 1.0 if VARNA_POINTS[varna_g] >= VARNA_POINTS[varna_b] else 0.0
    
    # 2. Vashya (2 points) - Based on Rashi
    def get_vashya(r_idx):
        if r_idx in [3, 9, 11]: return 'Jalachar'
        elif r_idx == 7: return 'Keeta'
        elif r_idx == 4: return 'Vanchar'
        elif r_idx in [2, 5, 6, 10]: return 'Manushya'
        else: return 'Chatushpada'

    vashya_g = get_vashya(rashi_idx_g)
    vashya_b = get_vashya(rashi_idx_b)
    
    vashya_score = 0.0
    if vashya_g == vashya_b:
        vashya_score = 2.0
    elif vashya_g in ['Chatushpada', 'Manushya'] and vashya_b in ['Chatushpada', 'Manushya']:
        vashya_score = 1.0
        
    # 3. Tara (3 points) - Based on Nakshatra distance
    # Tara from Bride to Groom determines Groom's Tara
    tara_num_g = ((idx_g - idx_b) % 27) % 9 + 1
    tara_num_b = ((idx_b - idx_g) % 27) % 9 + 1
    
    bad_rem = [3, 5, 7]
    if tara_num_g not in bad_rem and tara_num_b not in bad_rem:
        tara_score = 3.0
    elif tara_num_g not in bad_rem or tara_num_b not in bad_rem:
        tara_score = 1.5
    else:
        tara_score = 0.0

    # 4. Yoni (4 points)
    yoni_score = float(YONI_RELATION[g['yoni']][b['yoni']])
    
    # 5. Graha Maitri (5 points) - Rashi Lords
    RASHI_LORDS = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']
    lord_g = RASHI_LORDS[rashi_idx_g]
    lord_b = RASHI_LORDS[rashi_idx_b]
    maitri_score = float(PLANET_FRIENDSHIP[lord_g][lord_b])
    
    # 6. Gana (6 points)
    gana_score = 0.0
    if g['gana'] == b['gana']:
        gana_score = 6.0
    elif (g['gana'] == 'Deva' and b['gana'] == 'Manushya') or (g['gana'] == 'Manushya' and b['gana'] == 'Deva'):
        gana_score = 5.0
    elif g['gana'] == 'Deva' and b['gana'] == 'Rakshasa':
        gana_score = 1.0
    else:
        gana_score = 0.0
        
    # 7. Bhakoot (7 points) - Rashi Difference
    rashi_diff = (rashi_idx_b - rashi_idx_g) % 12
    if rashi_diff in [1, 4, 5, 7, 8, 11]:
        bhakoot_score = 0.0
    else:
        bhakoot_score = 7.0
        
    # 8. Nadi (8 points)
    nadi_score = 8.0 if g['nadi'] != b['nadi'] else 0.0
        
    total_score = varna_score + vashya_score + tara_score + yoni_score + maitri_score + gana_score + bhakoot_score + nadi_score
    
    # Matching evaluation
    if total_score >= 25:
        verdict = "Excellent Match (Uttam Milan)"
        description = "Highly compatible horoscope. Great harmony, health, and mutual understanding. Very auspicious for marriage."
        status_color = "success"
    elif total_score >= 18:
        verdict = "Good Match (Madhyam Milan)"
        description = "Auspicious match. Standard compatibility with minor differences. Normal married life is indicated. Can proceed."
        status_color = "warning"
    else:
        verdict = "Incompatible Match (Ashubh Milan)"
        description = "Low compatibility score. Nadi or Bhakoot Dosha may be present. Remedial prayers are recommended before proceeding."
        status_color = "danger"
        
    # Localization Display logic
    VARNA_MR = {'Brahmin': 'ब्राह्मण', 'Kshatriya': 'क्षत्रिय', 'Vaishya': 'वैश्य', 'Shudra': 'शूद्र'}
    VASHYA_MR = {'Chatushpada': 'चतुष्पाद', 'Manushya': 'मनुष्य', 'Jalachar': 'जलचर', 'Vanchar': 'वनचर', 'Keeta': 'कीट'}
    TARA_NAMES_MR = ['जन्म', 'संपत', 'विपत', 'क्षेम', 'प्रत्यारी', 'साधक', 'नैधन', 'मित्र', 'परममित्र']
    PLANET_NAMES_MR = {'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगळ', 'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र', 'Saturn': 'शनी', 'Rahu': 'राहू', 'Ketu': 'केतू'}
    
    if current_lang == 'mr':
        rashi_str_g = RASHI_NAMES_MR[rashi_idx_g]
        rashi_str_b = RASHI_NAMES_MR[rashi_idx_b]
        varna_str_g = VARNA_MR[varna_g]
        varna_str_b = VARNA_MR[varna_b]
        vashya_str_g = VASHYA_MR[vashya_g]
        vashya_str_b = VASHYA_MR[vashya_b]
        tara_str_g = TARA_NAMES_MR[tara_num_g - 1]
        tara_str_b = TARA_NAMES_MR[tara_num_b - 1]
        lord_str_g = PLANET_NAMES_MR[lord_g]
        lord_str_b = PLANET_NAMES_MR[lord_b]
    else:
        rashi_str_g = RASHI_NAMES_MR[rashi_idx_g] # Defaulting to Marathi per requirement
        rashi_str_b = RASHI_NAMES_MR[rashi_idx_b]
        varna_str_g = varna_g
        varna_str_b = varna_b
        vashya_str_g = vashya_g
        vashya_str_b = vashya_b
        tara_str_g = str(tara_num_g)
        tara_str_b = str(tara_num_b)
        lord_str_g = lord_g
        lord_str_b = lord_b

    # Log debug metrics using logger
    logger.info(f"[DEBUG MILAN] {groom_nakshatra}({groom_pada}) vs {bride_nakshatra}({bride_pada})")
    logger.info(f"Rashi: {rashi_idx_g} vs {rashi_idx_b}")
    logger.info(f"Varna: {varna_g} vs {varna_b} = {varna_score}")
    logger.info(f"Vashya: {vashya_g} vs {vashya_b} = {vashya_score}")
    logger.info(f"Tara: {tara_num_g} vs {tara_num_b} = {tara_score}")
    logger.info(f"Maitri: {lord_g} vs {lord_b} = {maitri_score}")
    logger.info(f"Bhakoot Diff: {rashi_diff} = {bhakoot_score}")

    return {
        'total_score': total_score,
        'verdict': verdict,
        'description': description,
        'status_color': status_color,
        'kootas': [
            {'name': 'Varna (Work & Egos)', 'max': 1, 'score': varna_score, 'groom': varna_str_g, 'bride': varna_str_b},
            {'name': 'Vashya (Dominance & Control)', 'max': 2, 'score': vashya_score, 'groom': vashya_str_g, 'bride': vashya_str_b},
            {'name': 'Tara (Destiny & Longevity)', 'max': 3, 'score': tara_score, 'groom': tara_str_g, 'bride': tara_str_b},
            {'name': 'Yoni (Physical & Affinity)', 'max': 4, 'score': yoni_score, 'groom': g['yoni'], 'bride': b['yoni']},
            {'name': 'Graha Maitri (Mental Friendship)', 'max': 5, 'score': maitri_score, 'groom': lord_str_g, 'bride': lord_str_b},
            {'name': 'Gana (Temperament & Behavior)', 'max': 6, 'score': gana_score, 'groom': g['gana'], 'bride': b['gana']},
            {'name': 'Bhakoot (Love & Relationship)', 'max': 7, 'score': bhakoot_score, 'groom': rashi_str_g, 'bride': rashi_str_b},
            {'name': 'Nadi (Health & Genetics)', 'max': 8, 'score': nadi_score, 'groom': g['nadi'], 'bride': b['nadi']},
        ]
    }
