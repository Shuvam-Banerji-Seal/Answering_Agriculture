"""
Enhanced mock responses for development and testing
"""

from typing import Dict, List
import random

class MockResponseGenerator:
    """Generate realistic mock responses for development"""
    
    def __init__(self):
        self.response_templates = {
            "weather": self._weather_responses,
            "crop_disease": self._crop_disease_responses,
            "market_prices": self._market_price_responses,
            "government_schemes": self._scheme_responses,
            "general_agriculture": self._general_responses
        }
    
    def get_response(self, query: str, language: str = "hi") -> Dict:
        """Get appropriate mock response based on query content"""
        query_lower = query.lower()
        
        # Determine response type
        if any(word in query_lower for word in ['मौसम', 'weather', 'बारिश', 'तापमान']):
            return self.response_templates["weather"]()
        elif any(word in query_lower for word in ['धान', 'rice', 'पीले पत्ते', 'बीमारी', 'disease']):
            return self.response_templates["crop_disease"]()
        elif any(word in query_lower for word in ['कीमत', 'price', 'भाव', 'बाज़ार', 'market']):
            return self.response_templates["market_prices"]()
        elif any(word in query_lower for word in ['योजना', 'scheme', 'सब्सिडी', 'subsidy']):
            return self.response_templates["government_schemes"]()
        else:
            return self.response_templates["general_agriculture"]()
    
    def _weather_responses(self) -> Dict:
        """Weather-related responses"""
        responses = [
            {
                "answer": """**मौसम पूर्वानुमान और कृषि सलाह:**

🌡️ **आज का तापमान:** 24°C - 32°C
🌧️ **बारिश की संभावना:** 65% (अगले 48 घंटे में)
💨 **हवा की गति:** 12 किमी/घंटा
☁️ **आर्द्रता:** 70%

**🌾 कृषि सुझाव:**
• धान की रोपाई के लिए उत्तम समय
• सिंचाई कम करें - प्राकृतिक बारिश का फायदा उठाएं  
• खाद डालने से बचें, बारिश के बाद डालें
• सब्जियों में फफूंद रोग से बचने के लिए ड्रेनेज की व्यवस्था करें

⚠️ **चेतावनी:** तेज़ हवा और ओले की संभावना है।""",
                "sources": [
                    {"title": "IMD Weather Report", "relevance": 0.95},
                    {"title": "ICAR Weather Advisory", "relevance": 0.88}
                ],
                "confidence": 0.92
            }
        ]
        return random.choice(responses)
    
    def _crop_disease_responses(self) -> Dict:
        """Crop disease and management responses"""
        responses = [
            {
                "answer": """**धान में पीली पत्ती की समस्या का समाधान:**

🔍 **संभावित कारण:**

1️⃣ **नाइट्रोजन की कमी** (70% मामले)
   • समाधान: यूरिया 25 किलो/एकड़ + DAP 15 किलो

2️⃣ **जड़ सड़न रोग** (जलभराव से)
   • समाधान: तुरंत पानी निकालें, कार्बेन्डाजिम स्प्रे करें

3️⃣ **आयरन की कमी** (क्षारीय मिट्टी में)
   • समाधान: आयरन सल्फेट 3 ग्राम/लीटर का छिड़काव

4️⃣ **बैक्टीरियल ब्लाइट**
   • समाधान: कॉपर सल्फेट 2 ग्राम/लीटर + चिपकने वाला पदार्थ

**💊 तुरंत उपचार:**
✅ पोटाश 15 किलो/एकड़ डालें
✅ जिंक सल्फेट का छिड़काव करें
✅ बीजोपचार से बचाव करें""",
                "sources": [
                    {"title": "ICAR Rice Disease Manual", "relevance": 0.94},
                    {"title": "Plant Pathology Guide", "relevance": 0.87}
                ],
                "confidence": 0.96
            }
        ]
        return random.choice(responses)
    
    def _market_price_responses(self) -> Dict:
        """Market price responses"""
        responses = [
            {
                "answer": """**आज के मंडी भाव (₹/क्विंटल):**

📈 **अनाज की कीमतें:**
• गेहूं: ₹2,180 (↑₹30) - बढ़ती मांग
• धान: ₹2,050 (↑₹20) - सरकारी खरीद शुरू  
• मक्का: ₹1,870 (↓₹15) - अधिक आपूर्ति
• बाजरा: ₹2,400 (↑₹50) - निर्यात मांग

🌱 **दलहन-तिलहन:**
• चना: ₹5,350 (↑₹150) - त्योहारी मांग
• मूंग: ₹7,800 (↑₹300) - कम उत्पादन
• सरसों: ₹5,200 (↑₹100) - तेल की मांग

**📊 बाज़ार पूर्वानुमान:**
• अगले 2 सप्ताह में दालों की कीमत और बढ़ सकती है
• गेहूं की कीमत स्थिर रहने की संभावना
• सरकारी योजनाओं का लाभ उठाएं

💡 **सुझाव:** चना और मूंग बेचने का अच्छा समय है।""",
                "sources": [
                    {"title": "APMC Daily Rates", "relevance": 0.96},
                    {"title": "Agricultural Market Intelligence", "relevance": 0.89}
                ],
                "confidence": 0.93
            }
        ]
        return random.choice(responses)
    
    def _scheme_responses(self) -> Dict:
        """Government scheme responses"""
        responses = [
            {
                "answer": """**प्रमुख कृषि योजनाएं 2025:**

🎯 **PM-KISAN योजना:**
• ₹6,000/वर्ष (₹2,000 की 3 किस्तें)
• सभी भूमिधारक किसान पात्र
• आवेदन: pmkisan.gov.in पर ऑनलाइन

🌱 **फसल बीमा योजना:**
• खरीफ: 2% प्रीमियम, रबी: 1.5%  
• प्राकृतिक आपदा की 100% भरपाई
• 72 घंटे में नुकसान की रिपोर्ट जरूरी

💧 **सिंचाई योजना:**
• ड्रिप सिस्टम पर 55% सब्सिडी
• SC/ST किसानों के लिए 75% तक
• आवेदन कृषि विभाग में

🚜 **कृषि यंत्रीकरण:**
• ट्रैक्टर पर 25% सब्सिडी  
• थ्रेशर, हार्वेस्टर पर 40%
• कस्टम हायरिंग सेंटर अनुदान

📋 **आवेदन प्रक्रिया:**
1. आधार कार्ड + भूमि दस्तावेज़ तैयार रखें
2. नजदीकी कृषि सेवा केंद्र जाएं  
3. ऑनलाइन फॉर्म भरें और ट्रैक करें""",
                "sources": [
                    {"title": "Ministry of Agriculture", "relevance": 0.97},
                    {"title": "DBT Agriculture Portal", "relevance": 0.91}
                ],
                "confidence": 0.95
            }
        ]
        return random.choice(responses)
    
    def _general_responses(self) -> Dict:
        """General agricultural responses"""
        return {
            "answer": """**IndicAgri में आपका स्वागत है! 🌾**

आप निम्नलिखित विषयों पर प्रश्न पूछ सकते हैं:

🌱 **फसल प्रबंधन:**
• बुआई, सिंचाई, कटाई का समय
• बीज चयन और किस्म सुझाव
• खाद-उर्वरक की मात्रा और समय

🐛 **रोग-कीट नियंत्रण:**
• लक्षणों की पहचान
• जैविक और रासायनिक उपचार
• रोकथाम के उपाय

🌤️ **मौसम आधारित सलाह:**
• 7 दिन का पूर्वानुमान
• मौसम अनुकूल कृषि क्रियाएं
• प्राकृतिक आपदा से बचाव

💰 **आर्थिक जानकारी:**
• दैनिक मंडी भाव
• सरकारी योजनाएं और सब्सिडी
• फसल बीमा और लोन

कृपया अपना विशिष्ट प्रश्न पूछें। मैं आपकी सहायता के लिए यहाँ हूँ!""",
            "sources": [
                {"title": "IndicAgri Knowledge Base", "relevance": 0.78}
            ],
            "confidence": 0.80
        }
