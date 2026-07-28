import streamlit as st
import json
import os
import requests

# --- إعدادات النظام ---
DATA_FILE = "store_data.json"
BOT_TOKEN = "8640762406:AAF540rnfipL54HSUIRZqODSsBcQjM2uybo"
CHAT_ID = "7055252264"

if not os.path.exists("saved_images"): os.makedirs("saved_images")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    # الهيكل المحدث لجميع المواد
    return {"products": {
        "علوم 1": {"price": 00, "old_price": 00, "available": True, "img": "https://via.placeholder.com/150"},
        "علوم 2": {"price": 00, "old_price": 0, "available": True, "img": "https://via.placeholder.com/150"},
        "علوم 3": {"price": 0, "old_price": 0, "available": True, "img": "https://via.placeholder.com/150"},
        "رياضيات": {"price": 00, "old_price": 0, "available": True, "img": "https://via.placeholder.com/150"},
        "فيزياء": {"price": 0, "old_price": 0, "available": True, "img": "https://via.placeholder.com/150"},
        "إسلامية": {"price": 00, "old_price": 0, "available": True, "img": "https://via.placeholder.com/150"}
    }}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = "shop"

# --- لوحة التحكم ---
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    if st.text_input("كلمة السر", type="password") == "admin77":
        for p, info in st.session_state.data['products'].items():
            st.subheader(p)
            info['price'] = st.number_input(f"السعر الحالي {p}", value=info['price'], key=f"p_{p}")
            info['old_price'] = st.number_input(f"السعر القديم (0 للإلغاء)", value=info.get('old_price', 0), key=f"o_{p}")
            info['available'] = st.checkbox(f"متوفر", value=info.get('available', True), key=f"a_{p}")
            
            uploaded_file = st.file_uploader(f"تغيير صورة {p}", type=["jpg", "png"], key=f"file_{p}")
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
    
    products = list(st.session_state.data['products'].items())
    for i in range(0, len(products), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(products):
                p, info = products[i+j]
                with cols[j]:
                    st.image(info['img'], use_column_width=True)
                    
                    price_display = f"**{info['price']} دج**"
                    if info.get('old_price', 0) > 0:
                        price_display = f"~~{info['old_price']} دج~~ <span style='color:red;'>{info['price']} دج</span>"
                    
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <h3>{p}</h3>
                        <p style="font-size: 18px;">{price_display}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if info.get('available', True):
                        if st.button(f"🛒 اشتري الآن", key=f"add_{p}", use_container_width=True):
                            st.session_state.cart[p] = st.session_state.cart.get(p, 0) + 1
                            st.toast(f"تمت إضافة {p}")
                    else:
                        st.warning("غير متوفر حالياً")
    
    if st.session_state.cart:
        if st.button("🛒 إتمام الطلب", use_container_width=True):
            st.session_state.page = "checkout"
            st.rerun()

# --- واجهة تأكيد الطلب ---
elif st.session_state.page == "checkout":
    st.title("📄 تأكيد الطلب")
    total = sum(st.session_state.data['products'][p]['price'] * q for p, q in st.session_state.cart.items())
    with st.form("order_form"):
        name = st.text_input("الاسم ")
        phone = st.text_input("رقم الهاتف")
        wilaya = st.selectbox("الولاية", ["أفلّو" ])
        delivery = st.radio("طريقة الاستلام", ["استلام فردي (0 دج)", "توصيل إلى باب المنزل (100 دج)"])
        address = ""
        if "توصيل" in delivery:
            address = st.text_input(" عنوان المنزل بالتفصيل في حال توصيل للمنزل *")
            total += 100 
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

    if st.button("العودة للمتجر"):
        st.session_state.page = "shop"
        st.rerun()
