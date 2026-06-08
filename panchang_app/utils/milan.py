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
    g = NAKSHATRAS[groom_nakshatra]
    b = NAKSHATRAS[bride_nakshatra]
    
    # 1. Varna (1 point)
    g_varna_pt = VARNA_POINTS[g['varna']]
    b_varna_pt = VARNA_POINTS[b['varna']]
    varna_score = 1.0 if g_varna_pt >= b_varna_pt else 0.0
    
    # 2. Vashya (2 points)
    vashya_score = 0.0
    if g['vashya'] == b['vashya']:
        vashya_score = 2.0
    elif (g['vashya'] in ['Chatushpada', 'Manushya'] and b['vashya'] in ['Chatushpada', 'Manushya']):
        vashya_score = 1.0
    else:
        vashya_score = 0.0
        
    # 3. Tara (3 points)
    # Count distance from bride's Nakshatra to groom's, and vice versa
    idx_g = NAKSHATRA_LIST.index(groom_nakshatra)
    idx_b = NAKSHATRA_LIST.index(bride_nakshatra)
    
    dist_g_to_b = (idx_b - idx_g) % 27
    dist_b_to_g = (idx_g - idx_b) % 27
    
    rem_g = dist_g_to_b % 9
    rem_b = dist_b_to_g % 9
    
    # Tara is auspicious if remainder is 3, 5, 7 or 0 (9) from both or even/odd check
    # Simplified standard: if both remainders are in [1, 2, 4, 6, 8] vs [3, 5, 7, 0]
    bad_rem = [1, 2, 4, 6, 8]
    if rem_g not in bad_rem and rem_b not in bad_rem:
        tara_score = 3.0
    elif rem_g not in bad_rem or rem_b not in bad_rem:
        tara_score = 1.5
    else:
        tara_score = 0.0
        
    # 4. Yoni (4 points)
    yoni_score = float(YONI_RELATION[g['yoni']][b['yoni']])
    
    # 5. Graha Maitri (5 points)
    maitri_score = float(PLANET_FRIENDSHIP[g['lord']][b['lord']])
    
    # 6. Gana (6 points)
    gana_score = 0.0
    if g['gana'] == b['gana']:
        gana_score = 6.0
    elif (g['gana'] == 'Deva' and b['gana'] == 'Manushya') or (g['gana'] == 'Manushya' and b['gana'] == 'Deva'):
        gana_score = 5.0
    elif g['gana'] == 'Deva' and b['gana'] == 'Rakshasa':
        gana_score = 1.0
    elif g['gana'] == 'Manushya' and b['gana'] == 'Rakshasa':
        gana_score = 0.0
    elif g['gana'] == 'Rakshasa' and b['gana'] == 'Deva':
        gana_score = 0.0
    elif g['gana'] == 'Rakshasa' and b['gana'] == 'Manushya':
        gana_score = 0.0
        
    # 7. Bhakoot (7 points)
    # Determined by accurate Moon sign (Rashi) distance based on Nakshatra and Pada
    rashi_idx_g = ((idx_g * 4) + groom_pada - 1) // 9
    rashi_idx_b = ((idx_b * 4) + bride_pada - 1) // 9
    
    # Ensure wrap-around just in case
    rashi_idx_g = rashi_idx_g % 12
    rashi_idx_b = rashi_idx_b % 12
    
    rashi_diff = (rashi_idx_b - rashi_idx_g) % 12
    # Bhakoot Dosha exists if difference is 2/12, 5/9, or 6/8
    if rashi_diff in [0, 3, 4, 8, 9]:
        bhakoot_score = 7.0
    else:
        bhakoot_score = 0.0
        
    # 8. Nadi (8 points)
    if g['nadi'] != b['nadi']:
        nadi_score = 8.0
    else:
        nadi_score = 0.0
        
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
        
    # Localization logic for Kootas
    if current_lang == 'mr':
        rashi_str_g = RASHI_NAMES_MR[rashi_idx_g]
        rashi_str_b = RASHI_NAMES_MR[rashi_idx_b]
    else:
        rashi_str_g = RASHI_NAMES_MR[rashi_idx_g] # Always force Marathi per requirement or use standard mapping
        rashi_str_b = RASHI_NAMES_MR[rashi_idx_b]

    return {
        'total_score': total_score,
        'verdict': verdict,
        'description': description,
        'status_color': status_color,
        'kootas': [
            {'name': 'Varna (Work & Egos)', 'max': 1, 'score': varna_score, 'groom': g['varna'], 'bride': b['varna']},
            {'name': 'Vashya (Dominance & Control)', 'max': 2, 'score': vashya_score, 'groom': g['vashya'], 'bride': b['vashya']},
            {'name': 'Tara (Destiny & Longevity)', 'max': 3, 'score': tara_score, 'groom': g['lord'], 'bride': b['lord']},
            {'name': 'Yoni (Physical & Affinity)', 'max': 4, 'score': yoni_score, 'groom': g['yoni'], 'bride': b['yoni']},
            {'name': 'Graha Maitri (Mental Friendship)', 'max': 5, 'score': maitri_score, 'groom': g['lord'], 'bride': b['lord']},
            {'name': 'Gana (Temperament & Behavior)', 'max': 6, 'score': gana_score, 'groom': g['gana'], 'bride': b['gana']},
            {'name': 'Bhakoot (Love & Relationship)', 'max': 7, 'score': bhakoot_score, 'groom': rashi_str_g, 'bride': rashi_str_b},
            {'name': 'Nadi (Health & Genetics)', 'max': 8, 'score': nadi_score, 'groom': g['nadi'], 'bride': b['nadi']},
        ]
    }
