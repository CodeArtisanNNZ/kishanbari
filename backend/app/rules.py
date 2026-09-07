from .models import SoilTest

def analyze(test: SoilTest) -> tuple[dict, float, bool]:
    """Safe v1 baseline. It classifies observations; it never invents fertilizer doses."""
    findings, actions = [], []
    known = 0
    if test.ph is not None:
        known += 1
        if test.ph < 5.5:
            findings.append({"code":"ph_low","severity":"attention","bn":"মাটি অম্লীয় হওয়ার সম্ভাবনা আছে।"})
        elif test.ph > 7.8:
            findings.append({"code":"ph_high","severity":"attention","bn":"মাটি ক্ষারীয় হওয়ার সম্ভাবনা আছে।"})
        else:
            findings.append({"code":"ph_mid","severity":"ok","bn":"pH সাধারণ মধ্যবর্তী সীমায় আছে।"})
    for key, label in (("nitrogen","নাইট্রোজেন"),("phosphorus","ফসফরাস"),("potassium","পটাশিয়াম")):
        value = getattr(test, key)
        if value and value != "unknown":
            known += 1
            severity = "attention" if value == "low" else "ok"
            findings.append({"code":f"{key}_{value}","severity":severity,"bn":f"{label} পরীক্ষার ফল { {'low':'কম','medium':'মাঝারি','high':'বেশি'}[value] }।"})
    if test.moisture is not None:
        known += 1
        findings.append({"code":"moisture_recorded","severity":"info","bn":f"নমুনার আর্দ্রতা {test.moisture:g}% লেখা হয়েছে।"})
    requires_expert = known < 3 or any(x["severity"] == "attention" for x in findings)
    if known < 3: actions.append("কমপক্ষে তিনটি নির্ভরযোগ্য মান না থাকায় আবার পরীক্ষা করুন।")
    if any(x["severity"] == "attention" for x in findings): actions.append("সার বা চুনের নির্দিষ্ট মাত্রা দেওয়ার আগে কৃষি কর্মকর্তা বা ল্যাবের সঙ্গে যাচাই করুন।")
    actions.append("একই জমির কয়েক জায়গা থেকে মিশ্র নমুনা নেওয়া হয়েছিল কি না নিশ্চিত করুন।")
    confidence = round(min(0.90, 0.35 + known * 0.10), 2)
    return {"summary_bn":"প্রাথমিক পরীক্ষার ফল গুছিয়ে দেখানো হয়েছে।","findings":findings,"actions_bn":actions,"disclaimer_bn":"এটি প্রাথমিক স্ক্রিনিং; ল্যাব পরীক্ষা বা কৃষি বিশেষজ্ঞের বিকল্প নয়।"}, confidence, requires_expert
