import streamlit as st
import json
import os
import requests

# --- إعدادات النظام ---
DATA_FILE = "store_data.json"
# ضع بيانات بوت التلغرام الخاص بك هنا
BOT_TOKEN = "8640762406:AAF540rnfipL54HSUIRZqODSsBcQjM2uybo"
CHAT_ID = "7055252264"

if not os.path.exists("saved_images"): os.makedirs("saved_images")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"products": {
        "علوم 1": {"price": 500, "img": "https://via.placeholder.com/150"},
        "علوم 2": {"price": 600, "img": "https://via.placeholder.com/150"},
        "علوم 3": {"price": 550, "img": "https://via.placeholder.com/150"},
        "رياضيات": {"price": 800, "img": "https://via.placeholder.com/150"},
        "فيزياء": {"price": 750, "img": "https://via.placeholder.com/150"},
        "إسلامية": {"price": 400, "img": "https://via.placeholder.com/150"}
    }}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = "shop"

# --- لوحة التحكم (الأدمن) ---
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    if st.text_input("كلمة السر", type="password") == "admin77":
        for p, info in st.session_state.data['products'].items():
            st.subheader(p)
            info['price'] = st.number_input(f"سعر {p}", value=info['price'], key=f"price_{p}")
            uploaded_file = st.file_uploader(f"اختر صورة لـ {p}", type=["jpg", "png"], key=f"file_{p}")
            if uploaded_file:
                file_path = os.path.join("saved_images", f"{p}.jpg")
                with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                info['img'] = file_path
        if st.button("حفظ التحديثات"):
            save_data(st.session_state.data)
            st.success("تم التحديث!")
            st.rerun()

# --- واجهة المتجر ---
if st.session_state.page == "shop":
    st.markdown("<h1 style='text-align: center;'>Nexora | دليلك نحو التميز</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>معاً نحو العلامة الكاملة</h3>", unsafe_allow_html=True)
    
    for p, info in st.session_state.data['products'].items():
        col1, col2 = st.columns([1, 2])
        with col1: st.image(info['img'], width=120)
        with col2:
            st.write(f"### {p}")
            st.write(f"السعر: {info['price']} دج")
            if st.button(f"أضف للسلة", key=f"add_{p}"):
                st.session_state.cart[p] = st.session_state.cart.get(p, 0) + 1
                st.toast(f"تمت إضافة {p}")
    
    if st.session_state.cart:
        if st.button("🛒 إتمام الطلب", use_container_width=True):
            st.session_state.page = "checkout"
            st.rerun()
# --- واجهة تأكيد الطلب ---
elif st.session_state.page == "checkout":
    st.title("📄 تأكيد الطلب")
    total = sum(st.session_state.data['products'][p]['price'] * q for p, q in st.session_state.cart.items())
    
    with st.form("order_form"):
        name = st.text_input("الاسم واللقب")
        phone = st.text_input("رقم الهاتف")
        wilaya = st.selectbox("الولاية", ["أفلّو", "أخرى"])
        delivery = st.radio("طريقة الاستلام", ["استلام فردي (0 دج)", "توصيل إلى باب المنزل (10,000 دج)"])
        address = ""
        if "توصيل" in delivery:
            address = st.text_input("عنوان المنزل بالتفصيل")
            total += 10000
            
        # الزر يجب أن يكون "form_submit_button" وليس "st.button" داخل الفورم
        submitted = st.form_submit_button("تأكيد الطلب النهائي")
        
        if submitted:
            msg = f"🔔 طلب جديد:\nالاسم: {name}\nالهاتف: {phone}\nالولاية: {wilaya}\nالعنوان: {address}\nالكتب: {st.session_state.cart}\nالمجموع: {total} دج"
            try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
            except: pass
            
            st.balloons()
            st.success("تم تأكيد طلبك!")
            st.markdown("---")
            st.markdown("### 📄 فاتورة الطلب:")
            st.markdown(f"**👤 الاسم:** {name}")
            st.markdown(f"**📞 الهاتف:** {phone}")
            st.markdown(f"**📍 الولاية:** {wilaya}")
            if address: st.markdown(f"**🏠 العنوان:** {address}")
            st.markdown(f"**💰 المبلغ الإجمالي:** {total} دج")
            st.session_state.cart = {}

    # الزر هنا خارج الـ form وسيعمل بشكل طبيعي
    if st.button("العودة للمتجر"):
        st.session_state.page = "shop"
        st.rerun()
# --- واجهة المتجر (بعد التعديل) ---
    for p, info in st.session_state.data['products'].items():
        col1, col2 = st.columns([1, 2])
        with col1:
            # هنا جعلنا الصورة داخل "موسع" لتبدو صغيرة، وعند الضغط عليها تكبر
            with st.expander("🔍 اضغط للتكبير"):
                st.image(info['img'], use_column_width=True)
        with col2:
            st.write(f"### {p}")
            st.write(f"السعر: {info['price']} دج")
            if st.button(f"أضف {p} للسلة 🛒", key=f"add_{p}"):
                st.session_state.cart[p] = st.session_state.cart.get(p, 0) + 1
                st.toast(f"تمت إضافة {p}")
