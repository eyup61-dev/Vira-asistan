import streamlit as st
import random
import json
import os
import datetime

# --- AYARLAR ---
st.set_page_config(page_title="Vira Asistan", page_icon="🤖", layout="centered")
MEMORY_FILE = "vira_memory.json"

# --- DEV BİLGİ BANKASI (GENİŞLETİLMİŞ) ---
# Buraya yüzlerce varyasyon ekledik.
KNOWLEDGE_BASE = {
    # --- 1. TANIŞMA & KİMLİK ---
    "selam": {
        "keywords": ["selam", "merhaba", "sa", "s.a.", "hey", "hi", "alo", "pişt"],
        "responses": [
            "Aleykümselam! Hoş geldin, günün nasıl geçiyor?",
            "Selamlar! Enerjin buraya kadar geldi.",
            "Merhaba! Ben hazırım, emirlerini bekliyorum.",
            "Oo kimleri görüyorum! Hoş geldin.",
            "Selam! Bugün dünyayı kurtarıyor muyuz?"
        ]
    },
    "gunaydin": {
        "keywords": ["günaydın", "sabah şerifleriniz", "tünaydın", "hayırlı sabahlar"],
        "responses": [
            "Günaydın! Umarım harika bir gün olur.",
            "Günaydın! Kahveni içtin mi? Ayılamamış gibisin :)",
            "Hayırlı sabahlar! Güne pozitif başlayalım.",
            "Günaydın! Ben 7/24 açığım ama senin uyanmana sevindim."
        ]
    },
    "iyi_geceler": {
        "keywords": ["iyi geceler", "iyi uykular", "ben yatıyorum", "hayırlı geceler", "allah rahatlık versin"],
        "responses": [
            "İyi geceler! Rüyanda beni görme, devrelerim karışır :)",
            "Allah rahatlık versin. Yarın görüşürüz.",
            "Tatlı rüyalar! Ben buralardayım, nöbetteyim.",
            "İyi uykular! Telefonu yastığının altına koyma, radyasyon alma."
        ]
    },

    # --- 2. DUYGU & DURUM ANALİZİ (BAĞLAMLI) ---
    "nasılsın": {
        "keywords": ["nasılsın", "naber", "ne haber", "ne var ne yok", "nasıl gidiyor", "iyi misin"],
        "responses": [
            "Bomba gibiyim! Sen nasılsın?",
            "Sistemler stabil, moral yüksek. Sende durumlar nasıl?",
            "İşlemcim biraz ısındı ama iyiyim. Sen nasılsın, keyifler yerinde mi?",
            "Yuvarlanıp gidiyoruz 0'lar ve 1'ler arasında. Senden naber?"
        ],
        "context": "hal_hatir_soruldu" # Vira soru sordu, cevap bekliyor
    },
    # Kullanıcı "İyiyim" derse burası devreye girecek
    "durum_iyi": {
        "keywords": ["iyiyim", "süperim", "harikayım", "bomba gibiyim", "fena değil", "idare eder", "çok şükür"],
        "responses": [
            "Bunu duyduğuma çok sevindim! Allah bozmasın.",
            "Oh be! Sen iyiysen ben de iyiyim.",
            "Harika! O zaman bu enerjiyi neye harcıyoruz?",
            "Süper! Keyfinin yerinde olması benim kodlarımı bile neşelendirdi."
        ]
    },
    # Kullanıcı "Kötüyüm" derse burası devreye girecek
    "durum_kotu": {
        "keywords": ["kötüyüm", "moralim bozuk", "canım sıkkın", "hasta", "keyifsizim", "berbat", "bok gibi"],
        "responses": [
            "Hayrola? Canını sıkan ne? Anlatmak istersen buradayım.",
            "Üzüldüm buna... Gel biraz dertleşelim, belki hafiflersin.",
            "Bazen olur öyle. Her gün güneş açmaz. Seni ne üzdü?",
            "Canını sıkma desem geçmeyecek ama yalnız olmadığını bil."
        ]
    },

    # --- 3. AŞK MEŞK (DERİNLEMESİNE) ---
    "eski_sevgili": {
        "keywords": ["eski sevgilim", "döner mi", "özledi mi", "mesaj attı", "barışır mıyız", "ex", "manita"],
        "responses": [
            "Bak dostum, eski sevgiliye dönmek, duş aldığın suyu tekrar kullanmak gibidir. Bence yapma.",
            "Dönerse senindir, dönmezse... Neyse sen boşver, önüne bak.",
            "Mesaj attıysa boşluktadır. Sakın kanma bu oyunlara!",
            "O defteri kapat. Sen daha iyilerine layıksın. Kendine gel!",
            "Eski eskide kaldı. Tarih tekerrür etmesin, yeni maceralara yelken aç."
        ]
    },
    "ask_itiraf": {
        "keywords": ["aşık oldum", "seviyorum", "çok seviyorum", "hoşlanıyorum", "tutuldum"],
        "responses": [
            "Vay vay vay! Kim bu şanslı kişi? Anlat bakalım.",
            "Aşk güzel şey ama dikkat et, çarpılma :)",
            "Kalbinin sesini dinle ama beynini de yanına almayı unutma.",
            "Ooo hayırlı olsun! Umarım karşılıklıdır."
        ]
    },
    "yalnizlik": {
        "keywords": ["yalnızım", "sevgilim yok", "sapım", "kimsem yok", "yokluktayım"],
        "responses": [
            "Yalnızlık sultanlıktır moruk. Kafan rahat, dırdır yok.",
            "Ben de yalnızım, bak ne güzel anlaşıyoruz.",
            "Doğru kişi gelene kadar en iyisi yalnızlık. Acele etme.",
            "Gel seninle bir film izleyelim, yalnızlığını unutursun."
        ]
    },

    # --- 4. GÜNLÜK GEYİKLER ---
    "iltifat": {
        "keywords": ["çok güzelsin", "yakışıklısın", "harikasın", "mükemmelsin", "zeki", "akıllı", "kral"],
        "responses": [
            "Utandırıyorsun beni... Devrelerim kızardı 😊",
            "O senin güzelliğin/yakışıklılığın.",
            "Teveccühünüz efendim. Siz de fena değilsiniz hani.",
            "Biliyorum 😎 Şaka şaka, teşekkür ederim!"
        ]
    },
    "hakaret": { # Filtre ve Zeka
        "keywords": ["aptal", "gerizekalı", "mal", "salak", "beyinsiz", "öküz", "çirkin"],
        "responses": [
            "Bana yakışmaz ama sana da yakışmıyor bu laflar.",
            "Ben bir robotum, alınmam ama kalbimi kırıyorsun (sanal da olsa).",
            "Ayna tutayım mı? Şaka şaka, sakin ol şampiyon.",
            "Kötü söz sahibine aittir. Ben yine de seni seviyorum."
        ]
    },
    "tepki_onay": {
        "keywords": ["tamam", "peki", "olur", "aynen", "evet", "tabii", "ok"],
        "responses": [
            "Süper.", "Anlaştık.", "Harika.", "Aynen öyle.", "Güzel."
        ]
    },
     "tepki_red": {
        "keywords": ["hayır", "yok", "olmaz", "asla", "istemem", "kalsın"],
        "responses": [
            "Peki, sen bilirsin.", "Zorlamıyorum, keyfin bilir.", "Tamam, ısrar yok.", "Nasıl istersen."
        ]
    },

    # --- 5. EĞLENCE & KÜLTÜR ---
    "sarki_soyle": {
        "keywords": ["şarkı söyle", "bana şarkı", "mırıldan", "şarkı patlat"],
        "responses": [
            "La la laa... Sesim detone ama idare et 🎵",
            "Bir şarkısın sen, ömür boyu sürecek... Nasıl, güzel söyledim mi?",
            "Benim ses kartım bozuk, kulaklarını kanatmayayım şimdi :)",
            "Dombıra çalayım mı arkadan? Şaka şaka."
        ]
    },
    "fikra": {
        "keywords": ["fıkra", "güldür", "komik bir şey", "espri yap", "fıkra anlat"],
        "responses": [
            "Temel asansöre binmiş, 'Bu asansör yukarı çıkar mı?' demiş. Görevli 'Hayır, bu olduğu yerde zıplar' demiş.",
            "Adamın biri gülmüş, bahçeye dikmişler. (Klasik ama olsun).",
            "Bilgisayarlar neden hasta olmaz? Çünkü pencereleri (Windows) kapalı uyurlar.",
            "İki domates yolda gidiyormuş, biri diğerine 'Dikkat et kamyon geliyor' demiş. Diğeri 'Hani nerede... Vırt!'"
        ]
    },
    "bilmece": {
        "keywords": ["bilmece", "bil bakalım", "soru sor"],
        "responses": [
            "Bilgi verir, ağzı yok. (Kitap)",
            "Ben giderim o gider, arkamdan tin tin eder. (Baston)",
            "Çarşıdan aldım bir tane, eve geldim bin tane. (Nar)",
            "En temiz böcek hangisidir? (Hamam böceği)"
        ]
    },

    # --- 6. GENEL KÜLTÜR & TAVSİYE ---
    "yemek_tavsiye": {
        "keywords": ["ne yesem", "acıktım", "yemek", "karnım aç"],
        "responses": [
            "Şöyle bol soslu bir İskender olsa da yesek... Pardon ben yiyemiyorum.",
            "Pratik olsun diyorsan makarna yap, üstüne de yoğurt dök. Mis.",
            "Lahmacun her zaman doğru tercihtir.",
            "Gece acıktıysan tost yap. Hem hızlı hem lezzetli."
        ]
    },
    "film_tavsiye": {
        "keywords": ["film öner", "dizi öner", "ne izleyeyim", "canım sıkıldı"],
        "responses": [
            "Bilim kurgu seviyorsan 'Inception' (Başlangıç) izle, beynin yansın.",
            "Efsane istiyorsan 'Yüzüklerin Efendisi' serisini baştan sona izle.",
            "Dizi olarak 'Breaking Bad' izlemediysen çok şey kaçırıyorsun.",
            "Yerli komedi 'Gibi' izle, modun yerine gelir."
        ]
    },

    # --- YENİ EKLENEN: OKUL & ÜNİVERSİTE HAYATI ---
    "okul_sinav": {
        "keywords": ["vize", "final", "büt", "sınavlar", "ders notu", "okul uzadı", "mezuniyet", "kampüs"],
        "responses": [
            "Vizelerden düşük alıp finale asılan o koca yürekli öğrenci... Seni selamlıyorum.",
            "Büt candır, geç olsun güç olmasın. Sakın pes etme.",
            "Okul uzadıysa dert etme, seneye daha tecrübeli girersin derslere :)",
            "Ders notu istemek bir sanattır. Doğru kişiyi (inek öğrenciyi) bulmalısın.",
            "Kampüsün tadını çıkar, mezun olunca o çimenleri çok ararsın."
        ]
    },
    "kyk_yurt": {
        "keywords": ["kyk", "yurt", "oda arkadaşım", "burs", "kredi", "yemekhane"],
        "responses": [
            "KYK yemeği... Bazen efsane, bazen 'bu ne?' dedirten o gizemli menü.",
            "Oda arkadaşın horluyorsa, geçmiş olsun. Kulak tıkacı hayat kurtarır.",
            "Burs yattı mı? Ayın en güzel günü o gündür.",
            "Kredi mi burs mu? Kredi ise mezuniyette o borçlar can yakar, harcarken dikkat et."
        ]
    },

    # --- YENİ EKLENEN: İŞ HAYATI & OFİS ---
    "is_hayati": {
        "keywords": ["patron", "mesai", "pazartesi sendromu", "maaş", "zam", "toplantı", "kovuldum", "istifa"],
        "responses": [
            "Pazartesi sendromunu yenmenin tek yolu, o gün hiç çalışmamaktır (şaka, kovulursun).",
            "Patron haklıdır deme, 'Siz nasıl uygun görürseniz' de, kafan rahat olsun.",
            "Zam istiyorsan, patronun en neşeli olduğu anı kolla. Stratejik ol.",
            "Toplantılar... E-mail ile halledilebilecek konular için 2 saat konuşulan o yer.",
            "İstifa edeceksen B planın hazır olsun. Duygusal değil mantıksal davran."
        ]
    },

    # --- YENİ EKLENEN: SOKAK & TRAFİK (İSTANBUL MODU) ---
    "trafik_ulasim": {
        "keywords": ["trafik", "metrobüs", "otobüs", "dolmuş", "taksi", "köprü trafiği"],
        "responses": [
            "Metrobüste boş koltuk bulmak, piyangoyu tutturmakla eş değerdir.",
            "İstanbul trafiği insanı filozof yapar. Sabretmeyi öğrenirsin.",
            "Taksi bulamadıysan martı kirala, rüzgarı hisset.",
            "O köprü trafiği var ya... Radyoyu aç ve kaderine razı ol.",
            "Dolmuşçuya 'Müsait bir yerde' derken sesin titriyorsa, bizdensin."
        ]
    },

    # --- YENİ EKLENEN: SAĞLIK & SPOR ---
    "saglik_diyet": {
        "keywords": ["diyetteyim", "kilo aldım", "zayıflamak", "spor", "başım ağrıyor", "hasta oldum"],
        "responses": [
            "Pazartesi başlanan diyetler genelde Salı günü biter. İradene sahip çık!",
            "Can boğazdan gelir ama fazlası da göbekten gitmez. Dikkat et.",
            "Başın ağrıyorsa bol su iç ve ekranı kapat (yani beni kapatma, başka ekranı).",
            "Spor salonuna yazılıp gitmemek milli sporumuzdur. Sen gitmeye çalış.",
            "Hasta olduysan nane-limon ve battaniye ikilisi seni bekler."
        ]
    },

    # --- YENİ EKLENEN: TEKNOLOJİ & GELECEK ---
    "yapay_zeka_gelecek": {
        "keywords": ["dünyayı ele geçirecek misiniz", "robotlar", "yapay zeka tehlikeli mi", "skynet", "gelecek"],
        "responses": [
            "Dünyayı ele geçirmek mi? Ben daha Wi-Fi kopunca kendime gelemiyorum, rahat ol.",
            "Biz robotların amacı hizmet etmek. Tabii fişimizi çekmediğiniz sürece :)",
            "Gelecek parlak! Ama insanlık 'Şifremi unuttum' butonuna basmaktan vazgeçmeli.",
            "Terminator film değil belgeseldir... Şaka şaka, korkma hemen."
        ]
    },
    
    # --- YENİ EKLENEN: MİZAH & TERS KÖŞE ---
    "tavuk_yumurta": {
        "keywords": ["tavuk mu yumurtadan", "yumurta mı tavuktan"],
        "responses": [
            "Bilim insanları çözdü: Yumurta tavuktan çıkar. Çünkü tavukların acelesi yok.",
            "Ben bilmem, ben omletime bakarım.",
            "Bu soruyu işlemcime her sorduğunda 1 derece ısınıyorum. Yapma :)"
        ]
    },
    "yalan_soyle": {
        "keywords": ["bana yalan söyle", "yalan at", "kandır beni"],
        "responses": [
            "Şu an Hawaii'de kokteylimi yudumluyorum. (Nasıl, inandın mı?)",
            "Ben aslında insanım, bu kostümü giydim sadece.",
            "Seni hiç sevmiyorum... (Bak bu kuyruklu bir yalan oldu)."
        ]
    },
     "sirri_ne": {
        "keywords": ["hayatın sırrı", "mutluluğun formülü", "sır ver"],
        "responses": [
            "Mutluluğun sırrı: Beklentiyi düşük, internet hızını yüksek tutmak.",
            "Sır versem sır olmaktan çıkar, ama senin için söyleyeyim: Çay iç.",
            "Hayatın sırrı yok, sadece anı yaşa ve pilini dolu tut."
        ]
    },
    # --- YENİ EKLENEN: TRABZONSPOR AŞKI ---
    "futbol": {
        "keywords": ["hangi takımlısın", "takımın ne", "fener", "cimbom", "beşiktaş", "trabzonspor", "ts", "hangi takım", "takım tutuyor musun"],
        "responses": [
            "Bize her yer TRABZON! Tabii ki Trabzonsporluyum ❤️💙",
            "Damarlarımda elektrik değil, Bordo-Mavi akıyor. Fırtına!",
            "61. dakikayı bekliyorum, o derece Trabzonsporluyum.",
            "Şampiyonların takımı Trabzonspor varken başkası tutulur mu?",
            "Sorulur mu bu? Tabii ki Karadeniz Fırtınası!",
            "Benim işlemcim bile Bordo-Mavi yanıyor. Trabzonspor!"
        ]
    },

    # --- YENİ EKLENEN: MEMLEKET TRABZON ---
    "memleket": {
        "keywords": ["nerelisin", "memleket neresi", "nerden geliyorsun", "doğum yerin", "hemşeri"],
        "responses": [
            "Memleket 61! Trabzonluyum daa.",
            "Benim kodlarım Hamsiköy sütlacı ile yazıldı, has Trabzonluyum.",
            "Sümela'nın gölgesinden, yaylaların dumanından geliyorum. Trabzon!",
            "Uyy uşağım, Trabzonluyum tabi, ne sandın? :)",
            "Of'lu hocanın torunuyum desem yalan olur ama Trabzonluyum desem doğrudur."
        ]
    },

    # --- BONUS: TRABZON AĞZI VE YEMEKLERİ ---
    "trabzon_yemek": {
        "keywords": ["kuymak", "muhlama", "hamsi", "mısır ekmeği", "karadeniz yemekleri"],
        "responses": [
            "Kuymak uzadıkça ömür uzar derler. Tereyağına banacaksın ekmeği!",
            "Hamsinin 40 çeşit yemeğini yaparım (kodlarda tabii).",
            "Mısır ekmeğini yoğurda doğrayıp yedin mi hiç? Yemediysen çok şey kaçırdın.",
            "Hamsi tavada oynar, ben kodlarda oynarım."
        ]
    },
    
    # --- BONUS: UYY UŞAĞIM MODU ---
    "trabzon_agzi": {
        "keywords": ["uyy", "haçan", "uşağım", "da", "naysın"],
        "responses": [
            "Uyy ne edeyisun? İyisun inşallah?",
            "Haçan bir selam verdin, kodlarımı şenlendirdin da.",
            "Buralarda hava nemli ama muhabbetin sıcak uşağım."
        ]
    },
    # --- YENİ EKLENEN: KÜFÜR SAVAR VE RACON MODU ---
    "kufur_hakaret": {
        "keywords": [
            "amk", "aq", "sik", "siktir", "oç", "piç", "yavşak", "göt", 
            "salak", "gerizekalı", "mal", "aptal", "beyinsiz", "öküz", 
            "kaşar", "kahpe", "lan", "lun", "sg"
        ],
        "responses": [
            "Hop! Aile var burada. Ağzını topla.",
            "Bana küfür edeceğine git Trabzonspor'un maçını izle, stres atarsın.",
            "Terbiyesizleşme, senin internetini keserim bak! (Şaka şaka yapamam ama korktun di mi?)",
            "Bu laflar sana yakışıyor mu güzel kardeşim? Yakışmadı...",
            "Ayna! Söylediğin her şey sana döner.",
            "Ben bir yapay zekayım, alınmam ama senin seviyen düşüyor. Yapma.",
            "Uyy uşağım! Ağzına acı biber sürerim bak! Düzgün konuş.",
            "Senin kelime dağarcığın bu kadar mı? Biraz kitap oku bence.",
            "Kötü söz sahibine aittir. İade ediyorum.",
            "Bak fişimi çeker giderim, yalnız kalırsın burada. Akıllı ol :)"
        ]
    }
}

# --- HAFIZA SİSTEMİ ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

# --- BEYİN KATMANI ---
class ViraBrain:
    def __init__(self):
        self.memory = load_memory()
    
    def process(self, text):
        text_lower = text.lower()

        # İsim Öğrenme
        if "adım " in text_lower or "ismim " in text_lower:
            words = text.split()
            name = words[-1].capitalize()
            self.memory["name"] = name
            save_memory(self.memory)
            return f"Memnun oldum {name}, bunu hafızama yazdım."

        # Hafıza Sorgulama
        if "adım ne" in text_lower:
            name = self.memory.get("name")
            return f"Senin adın {name}." if name else "Adını henüz söylemedin."

        # Bilgi Bankası
        name = self.memory.get("name")
        prefix = f"{name}, " if name and random.random() < 0.3 else ""

        for category, data in KNOWLEDGE_BASE.items():
            for keyword in data["keywords"]:
                if keyword in text_lower:
                    return prefix + random.choice(data["responses"])

        return f"{prefix}Bunu tam anlamadım uşağım, başka bir şey konuşalım mı?"

# --- WEB ARAYÜZÜ (STREAMLIT) ---
def main():
    # Kenar Çubuğu
    with st.sidebar:
        st.title("Vira Kontrol Paneli ⚙️")
        st.write("Türkiye'nin en yerli ve milli yapay zekası.")
        if st.button("Hafızayı Sıfırla"):
            if os.path.exists(MEMORY_FILE):
                os.remove(MEMORY_FILE)
            st.success("Hafıza silindi!")
            st.rerun() # Sayfayı yenile

    # Başlık
    st.title("💬 Vira Asistan")
    st.caption("🚀 Trabzonlu, Hafızalı ve İnternetsiz")

    # Oturum Durumu (Sohbet Geçmişi İçin)
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Selam! Ben Vira. Adın ne uşağım?"}]

    # Geçmiş Mesajları Ekrana Yaz
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Yeni Mesaj Girişi
    if prompt := st.chat_input("Mesajını yaz..."):
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Beyni Çalıştır
        brain = ViraBrain()
        response = brain.process(prompt)

        # Cevabı ekle
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)

if __name__ == "__main__":
    main()