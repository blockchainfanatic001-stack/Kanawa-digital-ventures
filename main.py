from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import uvicorn
import os
import json
from datetime import datetime

# --- DATABASE ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./kanawa_vip.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    category = Column(String)
    vendor_name = Column(String)
    vendor_phone = Column(String)
    image_base64 = Column(Text)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    customer_phone = Column(String)
    customer_email = Column(String)
    customer_address = Column(String)
    items = Column(Text) # JSON string of cart items
    total_amount = Column(Float)
    payment_method = Column(String)
    date_created = Column(String)

Base.metadata.create_all(bind=engine)

# --- BACKEND ---
app = FastAPI(title="Kanawa Digital Ventures")

class ProductCreate(BaseModel):
    name: str
    price: float
    description: str
    category: str
    vendor_name: str
    vendor_phone: str
    image_base64: str

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: str
    customer_address: str
    items: str
    total_amount: float
    payment_method: str

@app.post("/saka-kaya/")
def create_product(product: ProductCreate):
    db = SessionLocal()
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.close()
    return {"sako": "Success"}

@app.get("/duba-kaya/")
def read_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

@app.delete("/goge-kaya/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    db.close()
    return {"sako": "An goge"}

@app.post("/yi-order/")
def create_order(order: OrderCreate):
    db = SessionLocal()
    new_order = Order(**order.dict(), date_created=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(new_order)
    db.commit()
    db.close()
    return {"sako": "Order Saved"}

@app.get("/duba-orders/")
def read_orders():
    db = SessionLocal()
    orders = db.query(Order).order_by(Order.id.desc()).all()
    db.close()
    return orders

# --- FRONTEND (MASTER UI: UI + SIDE MENU + PRODUCT DETAILS + CHECKOUT FORM + ORDERS PANEL + PAYSTACK) ---
@app.get("/kasuwa", response_class=HTMLResponse)
def vip_market():
    html_content = """
    <!DOCTYPE html>
    <html lang="ha">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Kanawa Digital Ventures</title>
        <script src="https://js.paystack.co/v1/inline.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
            body { font-family: 'Roboto', sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; padding-bottom: 70px; color: #333; overflow-x: hidden; }
            
            .top-header { background: #fff; padding: 10px 15px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 10px;}
            .menu-icon { font-size: 24px; cursor: pointer; color: #333; padding-right: 5px; font-weight: bold;}
            .logo-text { font-size: 18px; font-weight: 900; color: #e62e04; margin: 0; letter-spacing: -0.5px; white-space: nowrap;}
            .search-box { flex: 1; background: #f0f2f5; border-radius: 20px; padding: 8px 15px; display: flex; align-items: center; border: 1px solid #e0e0e0;}
            .search-box input { border: none; background: transparent; outline: none; width: 100%; font-size: 14px; }
            
            .sidenav { height: 100%; width: 260px; position: fixed; z-index: 300; top: 0; left: -260px; background-color: #fff; overflow-x: hidden; transition: 0.3s; box-shadow: 2px 0 10px rgba(0,0,0,0.2); display: flex; flex-direction: column;}
            .sidenav-header { background: #e62e04; color: white; padding: 25px 20px; font-size: 20px; font-weight: 900; position: relative;}
            .sidenav-close { position: absolute; top: 15px; right: 15px; font-size: 24px; color: white; cursor: pointer; background: none; border: none; font-weight: bold;}
            .sidenav a { padding: 15px 20px; text-decoration: none; font-size: 15px; color: #333; display: block; border-bottom: 1px solid #eee; transition: 0.2s; display: flex; align-items: center; gap: 15px; font-weight: bold;}
            .sidenav a:hover { background-color: #f9f9f9; color: #e62e04; }
            .sidenav-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 250; }

            .top-actions { display: flex; padding: 10px 15px; background: #fff; gap: 10px; overflow-x: auto; scrollbar-width: none; align-items: center;}
            .action-btn { background: #ffebee; color: #e62e04; border: none; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 13px; white-space: nowrap; cursor: pointer; }
            .action-btn.post { background: #e62e04; color: white; }
            .lang-toggle { background: #333; color: white; border: none; padding: 8px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; cursor: pointer;}

            .banner-section { margin: 10px 15px; background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); border-radius: 12px; padding: 20px; color: #d81b60; font-weight: bold; font-size: 18px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}

            .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; padding: 10px 15px; }
            .card { background: #fff; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; cursor: pointer; border: 1px solid #f0f0f0; transition: transform 0.2s;}
            .card-img { width: 100%; aspect-ratio: 1; object-fit: cover; background: #f9f9f9; }
            .card-details { padding: 10px; }
            .card-title { font-size: 13px; color: #333; margin: 0 0 5px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.3;}
            .card-price { color: #111; font-size: 18px; font-weight: 900; margin-bottom: 2px; }
            .card-price small { font-size: 12px; color: #666; font-weight: normal; text-decoration: line-through; }
            .card-shipping { font-size: 11px; color: #008800; font-weight: bold; background: #e8f5e9; display: inline-block; padding: 2px 5px; border-radius: 3px; margin-bottom: 8px;}
            
            .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #fff; display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #eee; z-index: 100;}
            .nav-item { display: flex; flex-direction: column; align-items: center; color: #666; text-decoration: none; font-size: 11px; cursor: pointer; width: 25%;}
            .nav-item.active { color: #e62e04; font-weight: bold; }
            .nav-icon { font-size: 22px; margin-bottom: 3px; }
            .cart-badge { background: #e62e04; color: white; border-radius: 50%; padding: 2px 6px; font-size: 10px; position: absolute; margin-left: 15px; margin-top: -5px;}

            .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 400; justify-content: center; align-items: flex-end;}
            .modal-content { background: #fff; width: 100%; border-radius: 20px 20px 0 0; padding: 20px; box-sizing: border-box; max-height: 90vh; overflow-y: auto;}
            .close-modal { float: right; font-size: 24px; font-weight: bold; color: #333; cursor: pointer; border: none; background: none;}
            
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; font-weight: bold;}
            .form-control { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; box-sizing: border-box; background: #f9f9f9; outline: none;}
            
            .submit-btn { background: #e62e04; color: #fff; width: 100%; padding: 15px; border: none; border-radius: 25px; font-size: 14px; font-weight: bold; margin-top: 10px; cursor: pointer;}
            .crypto-btn { background: #14F195; color: #111; width: 100%; padding: 15px; border: none; border-radius: 25px; font-size: 14px; font-weight: bold; margin-top: 10px; cursor: pointer;}
            
            .cart-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #eee;}
            .cart-item-info { display: flex; flex-direction: column; }
            
            .whatsapp-float { position: fixed; bottom: 80px; right: 20px; background-color: #25d366; color: white; border-radius: 50%; width: 50px; height: 50px; display: flex; justify-content: center; align-items: center; font-size: 24px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); z-index: 100; text-decoration: none;}
            
            .prod-modal-img { width: 100%; border-radius: 10px; max-height: 300px; object-fit: contain; background: #f0f0f0; margin-bottom: 15px;}
            
            .admin-tabs { display: flex; border-bottom: 2px solid #eee; margin-bottom: 15px; }
            .admin-tab { flex: 1; text-align: center; padding: 10px; font-weight: bold; cursor: pointer; color: #666; }
            .admin-tab.active { color: #e62e04; border-bottom: 2px solid #e62e04; }
            .order-card { background: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 10px; font-size: 13px;}
        </style>
    </head>
    <body>

        <div id="sidenavOverlay" class="sidenav-overlay" onclick="closeNav()"></div>

        <div id="sideNav" class="sidenav">
            <div class="sidenav-header">Kanawa Digital<button class="sidenav-close" onclick="closeNav()">&times;</button></div>
            <a href="#" onclick="closeNav(); openModal('contactModal')"><span>📞</span> <span id="nContact">Tuntube Mu</span></a>
            <a href="#" onclick="closeNav(); openModal('helpModal')"><span>❓</span> <span id="nHelp">Taimako</span></a>
            <a href="#" onclick="closeNav(); openModal('termsModal')"><span>📜</span> <span id="nTerms">Ka'idojin Aiki</span></a>
            <a href="#" onclick="closeNav(); openModal('uploadModal')"><span>➕</span> <span id="nSell">Sayar da Kaya</span></a>
            <a href="#" onclick="closeNav(); openModal('adminModal')"><span>👤</span> <span id="nAdmin">Dakin Gudanarwa (Admin)</span></a>
        </div>

        <div class="top-header">
            <span class="menu-icon" onclick="openNav()">☰</span>
            <span class="logo-text">Kanawa Digital</span>
            <div class="search-box"><span>🔍</span><input type="text" id="searchInput" placeholder="Bincika waya..." onkeyup="filterProducts()"></div>
        </div>

        <div class="top-actions">
            <button class="lang-toggle" onclick="changeLanguage('ha')">HA</button>
            <button class="lang-toggle" onclick="changeLanguage('en')">EN</button>
            <button class="action-btn post" id="btnPostAd" onclick="openModal('uploadModal')">➕ Sayar da Kaya</button>
            <select class="action-btn" id="categoryFilter" onchange="filterProducts()" style="outline:none;">
                <option value="Duka" id="catAll">Dukkan Rukunoni</option>
                <option value="Wayoyi" id="catPhones">📱 Wayoyi</option>
                <option value="Takalma" id="catShoes">👞 Takalma</option>
                <option value="Kayan Sawa" id="catClothes">👕 Kayan Sawa</option>
                <option value="Wasu" id="catOthers">📦 Wasu</option>
            </select>
        </div>

        <div class="banner-section"><span id="bannerTitle">🔥 Zafafan Kayayyaki</span><br><span style="font-size: 12px; font-weight: normal; color: #333;" id="bannerSub">Kudin Aikawa ₦500 kacal!</span></div>

        <div class="product-grid" id="kayayyaki"><div style="text-align:center; width:100%; color:gray; padding:20px;" id="loadingTxt">Ana lodo kayayyaki...</div></div>

        <a href="https://wa.me/2349166614894" class="whatsapp-float" target="_blank">📱</a>

        <div class="bottom-nav">
            <div class="nav-item active" onclick="window.scrollTo(0,0)"><span class="nav-icon">🏠</span><span id="navHome">Gida</span></div>
            <div class="nav-item" onclick="document.getElementById('categoryFilter').focus()"><span class="nav-icon">📋</span><span id="navCat">Rukunoni</span></div>
            <div class="nav-item" onclick="openModal('cartModal')"><span class="nav-icon">🛒<span class="cart-badge" id="cartCount">0</span></span><span id="navCart">Kwando</span></div>
            <div class="nav-item" onclick="openNav()"><span class="nav-icon">☰</span><span id="navMenu">Menu</span></div>
        </div>

        <div id="productModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('productModal')">&times;</button>
                <img id="pdImg" class="prod-modal-img" src="">
                <h3 id="pdName" style="margin:5px 0;"></h3>
                <h2 id="pdPrice" style="color:#e62e04; margin:5px 0;"></h2>
                <div style="background:#f0fdf4; color:#008800; padding:5px 10px; border-radius:5px; font-size:12px; display:inline-block; margin-bottom:15px;" id="pdShipping">Shipping: ₦500</div>
                <p id="pdDesc" style="color:#555; font-size:14px; line-height:1.5;"></p>
                <hr style="border:0; border-top:1px solid #eee; margin:15px 0;">
                <p style="font-size:12px; color:#888; margin:0;" id="pdVendorText">Shago / Vendor:</p>
                <strong id="pdVendor" style="font-size:14px;"></strong>
                <button class="submit-btn" id="pdAddToCart" onclick="">Saka a Kwando</button>
            </div>
        </div>

        <div id="checkoutModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('checkoutModal')">&times;</button>
                <h3 style="margin-top:0;" id="chkTitle">Bayanan Isar Da Kaya</h3>
                <form id="checkoutForm">
                    <div class="form-group"><label id="clName">Cikakken Suna</label><input type="text" id="cName" class="form-control" required></div>
                    <div class="form-group"><label id="clPhone">Lambar Waya</label><input type="number" id="cPhone" class="form-control" required></div>
                    <div class="form-group"><label id="clEmail">Imel (Don samun rasiti)</label><input type="email" id="cEmail" class="form-control" required></div>
                    <div class="form-group"><label id="clAddress">Cikakken Adireshi (Gida/Unguwa)</label><textarea id="cAddress" class="form-control" rows="3" required></textarea></div>
                    <input type="hidden" id="paymentChoice">
                    <button type="submit" class="submit-btn" id="btnProceedPay">Ci Gaba Zuwa Biyan Kudi</button>
                </form>
            </div>
        </div>

        <div id="uploadModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('uploadModal')">&times;</button>
                <h3 style="margin-top:0;" id="mPostTitle">Dora Kayanka A Saukake</h3>
                <form id="uploadForm">
                    <div class="form-group"><label id="lName">Sunan Kaya</label><input type="text" id="name" class="form-control" required></div>
                    <div class="form-group"><label id="lPrice">Farashi (₦)</label><input type="number" id="price" class="form-control" required></div>
                    <div class="form-group"><label id="lCat">Zabi Rukuni</label><select id="category" class="form-control" required><option value="Wayoyi">Wayoyi / Phones</option><option value="Takalma">Takalma / Shoes</option><option value="Kayan Sawa">Kayan Sawa / Clothes</option><option value="Wasu">Wasu / Others</option></select></div>
                    <div class="form-group"><label>Bayanin Kaya (Description)</label><textarea id="desc" class="form-control" rows="2" required></textarea></div>
                    <div class="form-group"><label id="lVendor">Sunan Shagonka</label><input type="text" id="vendor" class="form-control" required></div>
                    <div class="form-group"><label id="lPhone">Lambar Waya</label><input type="number" id="phone" class="form-control" required></div>
                    <div class="form-group"><label id="lImg">Dauki Hoto (Max 2MB)</label><input type="file" id="image_file" class="form-control" accept="image/*" required><input type="hidden" id="base64String"></div>
                    <button type="submit" class="submit-btn" id="btnSubmitPost">POST AD YANZU</button>
                </form>
            </div>
        </div>

        <div id="cartModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('cartModal')">&times;</button>
                <h3 style="margin-top:0;" id="mCartTitle">Kwandon Siyayyarka</h3>
                <div id="cartItems" style="min-height: 100px;">Babu kaya a kwandonka.</div>
                <div style="border-top: 2px solid #333; margin-top: 15px; padding-top: 15px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 5px;"><span id="cSubText">Kudin Kaya:</span> <strong id="cartSubtotal">₦0</strong></div>
                    <div style="display:flex; justify-content:space-between; margin-bottom: 15px; color:#008800;"><span id="cShipText">Kudin Aikawa:</span> <strong>₦500</strong></div>
                    <div style="display:flex; justify-content:space-between; font-size:20px; font-weight:900;"><span id="cTotalText">Jimilla:</span> <span style="color:#e62e04;">₦<span id="cartTotal">0</span></span></div>
                    <button class="submit-btn" id="btnCheckoutNaira" onclick="initCheckout('naira')">💳 BIYA DA NAIRA</button>
                    <button class="crypto-btn" id="btnCheckoutCrypto" onclick="initCheckout('crypto')">🪙 BIYA DA CRYPTO</button>
                </div>
            </div>
        </div>

        <div id="cryptoModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('cryptoModal')">&times;</button>
                <h3 style="margin-top:0;" id="crTitle">Tsarin Biyan Kudi na Crypto</h3>
                <div class="crypto-box">
                    <h2 style="margin:0; color:#111;">$<span id="cryptoUsdTotal">0.00</span></h2>
                    <div class="wallet-addr" id="walletAddr">GDcKRBja7tDKqDftF2WGj3zcwUUBUoUV2xCqaMxfKwzR</div>
                    <button class="submit-btn" style="background:#333; padding:10px;" onclick="copyWallet()">📋 Kwafi Asusun (Copy)</button>
                </div>
                <button class="crypto-btn" style="margin-top:20px;" onclick="confirmCryptoPaid()">✅ NA TURA KUDIN</button>
            </div>
        </div>

        <div id="contactModal" class="modal"><div class="modal-content"><button class="close-modal" onclick="closeModal('contactModal')">&times;</button><h3 style="margin-top:0;">Tuntube Mu</h3><p>Waya/WhatsApp: 09166614894</p></div></div>
        <div id="helpModal" class="modal"><div class="modal-content"><button class="close-modal" onclick="closeModal('helpModal')">&times;</button><h3 style="margin-top:0;">Taimako</h3><p>Zabi kaya, saka a kwando, cike adireshinka, sannan ka biya. Zamu kawo maka kofar gida.</p></div></div>
        <div id="termsModal" class="modal"><div class="modal-content"><button class="close-modal" onclick="closeModal('termsModal')">&times;</button><h3 style="margin-top:0;">Ka'idojin Aiki</h3><p>Kudinka yana cikin aminci. Muna cajin N500 kudin aikawa a Gombe.</p></div></div>

        <div id="adminModal" class="modal">
            <div class="modal-content" style="height: 90vh;">
                <button class="close-modal" onclick="closeModal('adminModal')">&times;</button>
                <h3 style="margin-top:0;">Dakin Gudanarwa (Admin)</h3>
                <div id="adminAuth">
                    <input type="password" id="adminPass" class="form-control" placeholder="Password: kanawa123">
                    <button class="submit-btn" onclick="loginAdmin()">Shiga</button>
                </div>
                <div id="adminPanel" style="display:none;">
                    <div class="admin-tabs">
                        <div class="admin-tab active" id="tabProducts" onclick="switchAdminTab('products')">Kayayyaki</div>
                        <div class="admin-tab" id="tabOrders" onclick="switchAdminTab('orders')">Siyayya (Orders)</div>
                    </div>
                    <div id="adminItems"></div>
                    <div id="adminOrders" style="display:none;"></div>
                </div>
            </div>
        </div>

        <script>
            const EXCHANGE_RATE = 1500;
            const dict = {
                'ha': { search: "Bincika...", addToCart: "Saka a Kwando", empty: "Babu kaya.", ship: "Aikawa: ₦500" },
                'en': { search: "Search...", addToCart: "Add to Cart", empty: "No items.", ship: "Shipping: ₦500" }
            };
            let currentLang = 'ha'; let allProducts = []; let cart = []; const SHIPPING_FEE = 500; let currentCartTotal = 0;

            function openNav() { document.getElementById("sideNav").style.left = "0"; document.getElementById("sidenavOverlay").style.display = "block"; }
            function closeNav() { document.getElementById("sideNav").style.left = "-260px"; document.getElementById("sidenavOverlay").style.display = "none"; }
            function changeLanguage(lang) { currentLang = lang; document.getElementById('searchInput').placeholder = dict[lang].search; filterProducts(); }
            function openModal(id) { document.getElementById(id).style.display = 'flex'; }
            function closeModal(id) { document.getElementById(id).style.display = 'none'; }

            document.getElementById("image_file").addEventListener("change", function() {
                const file = this.files[0];
                if (file) {
                    if(file.size > 2000000){ alert("Hoto yayi nauyi (Max 2MB)"); this.value = ""; return; }
                    const reader = new FileReader(); reader.onload = function(e) { document.getElementById("base64String").value = e.target.result; }; reader.readAsDataURL(file);
                }
            });

            document.getElementById('uploadForm').onsubmit = function(e) {
                e.preventDefault(); document.getElementById('btnSubmitPost').disabled = true;
                const data = { name: document.getElementById('name').value, price: parseFloat(document.getElementById('price').value), description: document.getElementById('desc').value, category: document.getElementById('category').value, vendor_name: document.getElementById('vendor').value, vendor_phone: document.getElementById('phone').value, image_base64: document.getElementById('base64String').value };
                fetch('/saka-kaya/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }).then(res => res.json()).then(res => {
                    alert("An dora kayanka!"); document.getElementById('uploadForm').reset(); closeModal('uploadModal'); loadProducts(); document.getElementById('btnSubmitPost').disabled = false;
                });
            };

            function filterProducts() {
                const query = document.getElementById('searchInput').value.toLowerCase(); const cat = document.getElementById('categoryFilter').value;
                const filtered = allProducts.filter(p => p.name.toLowerCase().includes(query) && (cat === "Duka" || p.category === cat));
                renderProducts(filtered);
            }

            function renderProducts(products) {
                const container = document.getElementById('kayayyaki'); container.innerHTML = '';
                if(products.length === 0){ container.innerHTML = `<div style="text-align:center; padding:20px; width:100%; color:#999;">${dict[currentLang].empty}</div>`; return; }
                products.forEach(kaya => {
                    const card = document.createElement('div'); card.className = 'card';
                    card.onclick = () => viewProduct(kaya);
                    card.innerHTML = `<img src="${kaya.image_base64}" class="card-img"><div class="card-details"><h4 class="card-title">${kaya.name}</h4><div class="card-price">₦${kaya.price}</div></div>`;
                    container.appendChild(card);
                });
            }

            function loadProducts() { fetch('/duba-kaya/').then(res => res.json()).then(data => { allProducts = data; renderProducts(allProducts); renderAdminProducts(allProducts); }); }

            function viewProduct(p) {
                document.getElementById('pdImg').src = p.image_base64; document.getElementById('pdName').innerText = p.name; document.getElementById('pdPrice').innerText = '₦' + p.price; document.getElementById('pdDesc').innerText = p.description; document.getElementById('pdVendor').innerText = p.vendor_name + " (" + p.vendor_phone + ")";
                document.getElementById('pdAddToCart').onclick = function() { addToCart(p.id, p.name, p.price); closeModal('productModal'); };
                openModal('productModal');
            }

            function addToCart(id, name, price) { cart.push({id, name, price}); updateCart(); alert("An saka a kwando!"); }

            function updateCart() {
                document.getElementById('cartCount').innerText = cart.length; const div = document.getElementById('cartItems');
                if(cart.length === 0) { div.innerHTML = dict[currentLang].empty; document.getElementById('cartTotal').innerText = '0'; currentCartTotal = 0; return; }
                div.innerHTML = ''; let sub = 0;
                cart.forEach((item, i) => { sub += item.price; div.innerHTML += `<div class="cart-item"><div><b>${item.name}</b><br><span style="color:red">₦${item.price}</span></div><button class="remove-btn" onclick="cart.splice(${i},1); updateCart();">X</button></div>`; });
                document.getElementById('cartSubtotal').innerText = '₦' + sub; currentCartTotal = sub + SHIPPING_FEE; document.getElementById('cartTotal').innerText = currentCartTotal;
            }

            function initCheckout(method) {
                if(cart.length === 0) return alert("Kwando fanko ne!");
                document.getElementById('paymentChoice').value = method;
                closeModal('cartModal'); openModal('checkoutModal');
            }

            document.getElementById('checkoutForm').onsubmit = function(e) {
                e.preventDefault(); const method = document.getElementById('paymentChoice').value;
                if(method === 'naira') { doPaystack(); } else { doCrypto(); }
            };

            function saveOrder(method) {
                const orderData = { customer_name: document.getElementById('cName').value, customer_phone: document.getElementById('cPhone').value, customer_email: document.getElementById('cEmail').value, customer_address: document.getElementById('cAddress').value, items: JSON.stringify(cart), total_amount: currentCartTotal, payment_method: method };
                fetch('/yi-order/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(orderData) }).then(() => {
                    alert("Mun samu Order dinka! Zamu kawo maka kaya nan bada dadewa ba.");
                    cart = []; updateCart(); closeModal('checkoutModal'); closeModal('cryptoModal'); document.getElementById('checkoutForm').reset();
                });
            }

            function doPaystack() {
                let handler = PaystackPop.setup({
                    key: 'pk_test_4d6a3f906c1a1fa859539e7b6086d6be3e3b5b1f', 
                    email: document.getElementById('cEmail').value, amount: currentCartTotal * 100, currency: 'NGN', channels: ['card', 'bank_transfer', 'ussd'], 
                    ref: 'KDV_' + Math.floor((Math.random() * 1000000000) + 1), 
                    callback: function(res) { saveOrder('Paystack'); },
                    onClose: function() { alert("An fasa biya."); }
                }); handler.openIframe();
            }

            function doCrypto() {
                document.getElementById('cryptoUsdTotal').innerText = (currentCartTotal / EXCHANGE_RATE).toFixed(2);
                closeModal('checkoutModal'); openModal('cryptoModal');
            }

            function copyWallet() { navigator.clipboard.writeText("GDcKRBja7tDKqDftF2WGj3zcwUUBUoUV2xCqaMxfKwzR"); alert("An kwafi asusun!"); }
            function confirmCryptoPaid() { saveOrder('Crypto'); }

            function loginAdmin() { if(document.getElementById('adminPass').value === "kanawa123") { document.getElementById('adminAuth').style.display = 'none'; document.getElementById('adminPanel').style.display = 'block'; loadOrders(); } else { alert("Kuskure!"); } }
            
            function switchAdminTab(tab) {
                document.getElementById('tabProducts').className = tab === 'products' ? 'admin-tab active' : 'admin-tab';
                document.getElementById('tabOrders').className = tab === 'orders' ? 'admin-tab active' : 'admin-tab';
                document.getElementById('adminItems').style.display = tab === 'products' ? 'block' : 'none';
                document.getElementById('adminOrders').style.display = tab === 'orders' ? 'block' : 'none';
            }

            function renderAdminProducts(products) {
                const div = document.getElementById('adminItems'); div.innerHTML = '';
                products.forEach(p => { div.innerHTML += `<div style="display:flex; justify-content:space-between; border-bottom:1px solid #ccc; padding:10px 0;"><span>${p.name} (₦${p.price})</span><button onclick="if(confirm('Goge?')) fetch('/goge-kaya/${p.id}', {method:'DELETE'}).then(()=>loadProducts())" style="background:red; color:white; border:none; padding:5px; border-radius:5px;">Goge</button></div>`; });
            }

            function loadOrders() {
                fetch('/duba-orders/').then(res => res.json()).then(data => {
                    const div = document.getElementById('adminOrders'); div.innerHTML = '';
                    if(data.length===0) div.innerHTML = "Babu Siyayya tukunna.";
                    data.forEach(o => {
                        let items = JSON.parse(o.items).map(i => i.name).join(", ");
                        div.innerHTML += `<div class="order-card"><b>Suna:</b> ${o.customer_name} <br><b>Waya:</b> ${o.customer_phone} <br><b>Adireshi:</b> ${o.customer_address} <br><b>Kaya:</b> ${items} <br><b>Kudi:</b> ₦${o.total_amount} (${o.payment_method}) <br><small style="color:gray">${o.date_created}</small></div>`;
                    });
                });
            }

            window.onload = function() { loadProducts(); };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
