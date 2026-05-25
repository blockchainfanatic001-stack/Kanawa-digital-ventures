from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import uvicorn
import os

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
    image_base64 = Column(String)

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

@app.post("/saka-kaya/")
def create_product(product: ProductCreate):
    db = SessionLocal()
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
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

# --- FRONTEND (ALIEXPRESS UI + BILINGUAL + CRYPTO + PAYSTACK TRANSFER) ---
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
            
            body { font-family: 'Roboto', sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; padding-bottom: 70px; color: #333; }
            
            .top-header { background: #fff; padding: 10px 15px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 10px;}
            .logo-text { font-size: 18px; font-weight: 900; color: #e62e04; margin: 0; letter-spacing: -0.5px;}
            .search-box { flex: 1; background: #f0f2f5; border-radius: 20px; padding: 8px 15px; display: flex; align-items: center; border: 1px solid #e0e0e0;}
            .search-box input { border: none; background: transparent; outline: none; width: 100%; font-size: 14px; }
            
            .top-actions { display: flex; padding: 10px 15px; background: #fff; gap: 10px; overflow-x: auto; scrollbar-width: none; align-items: center;}
            .action-btn { background: #ffebee; color: #e62e04; border: none; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 13px; white-space: nowrap; cursor: pointer; }
            .action-btn.post { background: #e62e04; color: white; }
            .lang-toggle { background: #333; color: white; border: none; padding: 8px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; cursor: pointer;}

            .banner-section { margin: 10px 15px; background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); border-radius: 12px; padding: 20px; color: #d81b60; font-weight: bold; font-size: 18px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}

            .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; padding: 10px 15px; }
            .card { background: #fff; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; cursor: pointer; border: 1px solid #f0f0f0; transition: transform 0.2s;}
            .card:active { transform: scale(0.98); }
            .card-img { width: 100%; aspect-ratio: 1; object-fit: cover; background: #f9f9f9; }
            .card-details { padding: 10px; }
            .card-title { font-size: 13px; color: #333; margin: 0 0 5px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.3;}
            .card-price { color: #111; font-size: 18px; font-weight: 900; margin-bottom: 2px; }
            .card-price small { font-size: 12px; color: #666; font-weight: normal; text-decoration: line-through; }
            .card-shipping { font-size: 11px; color: #008800; font-weight: bold; background: #e8f5e9; display: inline-block; padding: 2px 5px; border-radius: 3px; margin-bottom: 8px;}
            .card-vendor { font-size: 11px; color: #999; margin-bottom: 8px; }
            .add-cart-btn { background: #111; color: #fff; border: none; width: 100%; padding: 8px; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 13px;}

            .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #fff; display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #eee; z-index: 100; padding-bottom: max(10px, env(safe-area-inset-bottom));}
            .nav-item { display: flex; flex-direction: column; align-items: center; color: #666; text-decoration: none; font-size: 11px; cursor: pointer; width: 25%;}
            .nav-item.active { color: #e62e04; font-weight: bold; }
            .nav-icon { font-size: 22px; margin-bottom: 3px; }
            .cart-badge { background: #e62e04; color: white; border-radius: 50%; padding: 2px 6px; font-size: 10px; position: absolute; margin-left: 15px; margin-top: -5px;}

            .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 200; justify-content: center; align-items: flex-end;}
            .modal-content { background: #fff; width: 100%; border-radius: 20px 20px 0 0; padding: 20px; box-sizing: border-box; max-height: 85vh; overflow-y: auto;}
            .close-modal { float: right; font-size: 24px; font-weight: bold; color: #333; cursor: pointer; border: none; background: none;}
            
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; font-weight: bold;}
            .form-control { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; box-sizing: border-box; background: #f9f9f9; outline: none;}
            
            .submit-btn { background: #e62e04; color: #fff; width: 100%; padding: 15px; border: none; border-radius: 25px; font-size: 14px; font-weight: bold; margin-top: 10px; cursor: pointer;}
            .crypto-btn { background: #14F195; color: #111; width: 100%; padding: 15px; border: none; border-radius: 25px; font-size: 14px; font-weight: bold; margin-top: 10px; cursor: pointer;}
            
            .cart-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #eee;}
            .cart-item-info { display: flex; flex-direction: column; }
            .cart-item-title { font-size: 14px; font-weight: bold; color: #333;}
            .cart-item-price { color: #e62e04; font-weight: bold; margin-top: 5px;}
            .remove-btn { background: #f5f5f5; border: none; padding: 5px 10px; border-radius: 5px; color: #e62e04; font-weight: bold; cursor: pointer;}

            .crypto-box { background: #f0fdf4; border: 1px solid #14F195; padding: 15px; border-radius: 10px; text-align: center; margin-top: 15px;}
            .wallet-addr { font-family: monospace; font-size: 12px; word-break: break-all; background: #fff; padding: 10px; border-radius: 5px; margin: 10px 0; border: 1px dashed #ccc;}
        </style>
    </head>
    <body>

        <div class="top-header">
            <span class="logo-text">Kanawa Digital Ventures</span>
            <div class="search-box">
                <span>🔍</span>
                <input type="text" id="searchInput" placeholder="Bincika waya, takalma..." onkeyup="filterProducts()">
            </div>
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

        <div class="banner-section">
            <span id="bannerTitle">🔥 Zafafan Kayayyaki A Cikin Gida</span><br>
            <span style="font-size: 12px; font-weight: normal; color: #333;" id="bannerSub">Kudin Aikawa ₦500 kacal ko Ka Karba Kyauta!</span>
        </div>

        <div class="product-grid" id="kayayyaki">
            <div style="text-align:center; width:100%; color:gray; padding:20px;" id="loadingTxt">Ana lodo kayayyaki...</div>
        </div>

        <div class="bottom-nav">
            <div class="nav-item active" onclick="window.scrollTo(0,0)">
                <span class="nav-icon">🏠</span>
                <span id="navHome">Gida</span>
            </div>
            <div class="nav-item" onclick="document.getElementById('categoryFilter').focus()">
                <span class="nav-icon">📋</span>
                <span id="navCat">Rukunoni</span>
            </div>
            <div class="nav-item" onclick="openModal('cartModal')">
                <span class="nav-icon">🛒<span class="cart-badge" id="cartCount">0</span></span>
                <span id="navCart">Kwando</span>
            </div>
            <div class="nav-item" onclick="openModal('adminModal')">
                <span class="nav-icon">👤</span>
                <span id="navAcc">Account</span>
            </div>
        </div>

        <div id="uploadModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('uploadModal')">&times;</button>
                <h3 style="margin-top:0;" id="mPostTitle">Dora Kayanka A Saukake</h3>
                <form id="uploadForm">
                    <div class="form-group"><label id="lName">Sunan Kaya</label><input type="text" id="name" class="form-control" required></div>
                    <div class="form-group"><label id="lPrice">Farashi (₦)</label><input type="number" id="price" class="form-control" required></div>
                    <div class="form-group">
                        <label id="lCat">Zabi Rukuni</label>
                        <select id="category" class="form-control" required>
                            <option value="Wayoyi">Wayoyi / Phones</option>
                            <option value="Takalma">Takalma / Shoes</option>
                            <option value="Kayan Sawa">Kayan Sawa / Clothes</option>
                            <option value="Wasu">Wasu / Others</option>
                        </select>
                    </div>
                    <div class="form-group"><label id="lVendor">Sunan Shagonka</label><input type="text" id="vendor" class="form-control" required></div>
                    <div class="form-group"><label id="lPhone">Lambar Waya</label><input type="number" id="phone" class="form-control" required></div>
                    <div class="form-group">
                        <label id="lImg">Dauki Hoto (Max 2MB)</label>
                        <input type="file" id="image_file" class="form-control" accept="image/*" style="background:#fff; padding:8px;" required>
                        <input type="hidden" id="base64String">
                    </div>
                    <textarea id="desc" class="form-control" style="display:none;" required>Babu bayani</textarea>
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
                    <div style="display:flex; justify-content:space-between; margin-bottom: 5px;">
                        <span id="cSubText">Kudin Kaya:</span> <strong id="cartSubtotal">₦0</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom: 15px; color:#008800;">
                        <span id="cShipText">Kudin Aikawa:</span> <strong>₦500</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:20px; font-weight:900;">
                        <span id="cTotalText">Jimilla:</span> <span style="color:#e62e04;">₦<span id="cartTotal">0</span></span>
                    </div>
                    
                    <button class="submit-btn" id="btnCheckoutNaira" onclick="checkoutNaira()">💳 BIYA DA NAIRA (TRANSFER/CARD)</button>
                    <button class="crypto-btn" id="btnCheckoutCrypto" onclick="showCryptoPayment()">🪙 BIYA DA CRYPTO (SOL/USDT)</button>
                </div>
            </div>
        </div>

        <div id="cryptoModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('cryptoModal')">&times;</button>
                <h3 style="margin-top:0;" id="crTitle">Tsarin Biyan Kudi na Crypto</h3>
                <p id="crDesc">Tura daidai adadin kudin zuwa wannan asusun na Solana. Zaka iya tura SOL ko USDT (SPL).</p>
                
                <div class="crypto-box">
                    <h2 style="margin:0; color:#111;">$<span id="cryptoUsdTotal">0.00</span></h2>
                    <p style="margin:5px 0; color:#666; font-size:12px;" id="crRate">(Kiyasin Farashi: $1 = ₦1,500)</p>
                    
                    <div class="wallet-addr" id="walletAddr">GDcKRBja7tDKqDftF2WGj3zcwUUBUoUV2xCqaMxfKwzR</div>
                    
                    <button class="submit-btn" style="background:#333; padding:10px;" id="btnCopyWallet" onclick="copyWallet()">📋 Kwafi Asusun (Copy)</button>
                </div>
                
                <button class="crypto-btn" style="margin-top:20px;" id="btnPaidCrypto" onclick="confirmCryptoPaid()">✅ NA TURA KUDIN</button>
            </div>
        </div>

        <div id="adminModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('adminModal')">&times;</button>
                <h3 style="margin-top:0;">Dakin Gudanarwa (Admin)</h3>
                <div id="adminAuth">
                    <input type="password" id="adminPass" class="form-control" placeholder="Password: kanawa123">
                    <button class="submit-btn" onclick="loginAdmin()">Shiga</button>
                </div>
                <div id="adminPanel" style="display:none;">
                    <p style="color:green; font-weight:bold;">Ka shiga dakin gudanarwa.</p>
                    <div id="adminItems"></div>
                </div>
            </div>
        </div>

        <script>
            const EXCHANGE_RATE = 1500; // 1 USD = 1500 NGN (Kiyasin farashi)

            const dict = {
                'ha': {
                    search: "Bincika waya, takalma...", postAd: "➕ Sayar da Kaya",
                    catAll: "Dukkan Rukunoni", catPhones: "📱 Wayoyi", catShoes: "👞 Takalma", catClothes: "👕 Kayan Sawa", catOthers: "📦 Wasu",
                    bannerTitle: "🔥 Zafafan Kayayyaki A Cikin Gida", bannerSub: "Kudin Aikawa ₦500 kacal ko Ka Karba Kyauta!",
                    loading: "Ana lodo kayayyaki...", empty: "Babu kayan da ya dace.", shippingLabel: "Shipping: ₦500 (Local)", vendorLabel: "Shago:", addToCartBtn: "Saka a Kwando",
                    navHome: "Gida", navCat: "Rukunoni", navCart: "Kwando", navAcc: "Account",
                    mPostTitle: "Dora Kayanka A Saukake", lName: "Sunan Kaya", lPrice: "Farashi (₦)", lCat: "Zabi Rukuni", lVendor: "Sunan Shagonka", lPhone: "Lambar Waya", lImg: "Dauki Hoto (Max 2MB)", btnSubmitPost: "POST AD YANZU",
                    mCartTitle: "Kwandon Siyayyarka", cartEmpty: "Babu kaya a kwandonka.", cSubText: "Kudin Kaya:", cShipText: "Kudin Aikawa:", cTotalText: "Jimilla:", 
                    btnNaira: "💳 BIYA DA NAIRA (TRANSFER/CARD)", btnCrypto: "🪙 BIYA DA CRYPTO (SOL/USDT)",
                    crTitle: "Tsarin Biyan Kudi na Crypto", crDesc: "Tura daidai adadin kudin zuwa wannan asusun na Solana. Zaka iya tura SOL ko USDT (SPL).", crRate: "(Kiyasin Farashi: $1 = ₦1,500)", btnCopy: "📋 Kwafi Asusun (Copy)", btnPaid: "✅ NA TURA KUDIN",
                    alertAdded: "An saka a kwando!", alertSuccess: "An dora kayanka!", alertFail: "Matsala wajen dorawa", alertCopied: "An kwafi asusun!", alertCryptoDone: "Mungode! Zamu duba asusunmu mu turo maka kayanka.",
                    promptEmail: "Shigar da Imel dinka don samun rasiti:", alertPaySuccess: "Biya ya kammala! Lamba: ", alertPayCancel: "Ka fasa biyan kudin."
                },
                'en': {
                    search: "Search phones, shoes...", postAd: "➕ Post Ad",
                    catAll: "All Categories", catPhones: "📱 Phones", catShoes: "👞 Shoes", catClothes: "👕 Clothes", catOthers: "📦 Others",
                    bannerTitle: "🔥 Hot Local Products", bannerSub: "Delivery Fee just ₦500 or Free Pickup!",
                    loading: "Loading products...", empty: "No products found.", shippingLabel: "Shipping: ₦500 (Local)", vendorLabel: "Vendor:", addToCartBtn: "Add to Cart",
                    navHome: "Home", navCat: "Categories", navCart: "Cart", navAcc: "Account",
                    mPostTitle: "Post Your Ad Easily", lName: "Product Name", lPrice: "Price (₦)", lCat: "Select Category", lVendor: "Shop Name", lPhone: "Phone Number", lImg: "Take Photo (Max 2MB)", btnSubmitPost: "POST AD NOW",
                    mCartTitle: "Your Shopping Cart", cartEmpty: "Your cart is empty.", cSubText: "Subtotal:", cShipText: "Shipping Fee:", cTotalText: "Total:", 
                    btnNaira: "💳 PAY WITH NAIRA (TRANSFER/CARD)", btnCrypto: "🪙 PAY WITH CRYPTO (SOL/USDT)",
                    crTitle: "Crypto Payment Gateway", crDesc: "Send the exact amount to this Solana wallet. You can send SOL or USDT (SPL).", crRate: "(Est. Rate: $1 = ₦1,500)", btnCopy: "📋 Copy Address", btnPaid: "✅ I HAVE PAID",
                    alertAdded: "Added to cart!", alertSuccess: "Ad posted successfully!", alertFail: "Error posting ad", alertCopied: "Wallet address copied!", alertCryptoDone: "Thank you! We will verify the transaction and ship your order.",
                    promptEmail: "Enter your email for the receipt:", alertPaySuccess: "Payment complete! Ref: ", alertPayCancel: "Transaction cancelled."
                }
            };

            let currentLang = 'ha'; let allProducts = []; let cart = []; const SHIPPING_FEE = 500; let currentCartTotal = 0;

            function changeLanguage(lang) {
                currentLang = lang;
                document.getElementById('searchInput').placeholder = dict[lang].search; document.getElementById('btnPostAd').innerText = dict[lang].postAd;
                document.getElementById('catAll').innerText = dict[lang].catAll; document.getElementById('catPhones').innerText = dict[lang].catPhones; document.getElementById('catShoes').innerText = dict[lang].catShoes; document.getElementById('catClothes').innerText = dict[lang].catClothes; document.getElementById('catOthers').innerText = dict[lang].catOthers;
                document.getElementById('bannerTitle').innerText = dict[lang].bannerTitle; document.getElementById('bannerSub').innerText = dict[lang].bannerSub;
                document.getElementById('navHome').innerText = dict[lang].navHome; document.getElementById('navCat').innerText = dict[lang].navCat; document.getElementById('navCart').innerText = dict[lang].navCart; document.getElementById('navAcc').innerText = dict[lang].navAcc;
                document.getElementById('mPostTitle').innerText = dict[lang].mPostTitle; document.getElementById('lName').innerText = dict[lang].lName; document.getElementById('lPrice').innerText = dict[lang].lPrice; document.getElementById('lCat').innerText = dict[lang].lCat; document.getElementById('lVendor').innerText = dict[lang].lVendor; document.getElementById('lPhone').innerText = dict[lang].lPhone; document.getElementById('lImg').innerText = dict[lang].lImg; document.getElementById('btnSubmitPost').innerText = dict[lang].btnSubmitPost;
                document.getElementById('mCartTitle').innerText = dict[lang].mCartTitle; document.getElementById('cSubText').innerText = dict[lang].cSubText; document.getElementById('cShipText').innerText = dict[lang].cShipText; document.getElementById('cTotalText').innerText = dict[lang].cTotalText; 
                document.getElementById('btnCheckoutNaira').innerText = dict[lang].btnNaira; document.getElementById('btnCheckoutCrypto').innerText = dict[lang].btnCrypto;
                document.getElementById('crTitle').innerText = dict[lang].crTitle; document.getElementById('crDesc').innerText = dict[lang].crDesc; document.getElementById('crRate').innerText = dict[lang].crRate; document.getElementById('btnCopyWallet').innerText = dict[lang].btnCopy; document.getElementById('btnPaidCrypto').innerText = dict[lang].btnPaid;
                filterProducts(); updateCart();
            }

            function openModal(id) { document.getElementById(id).style.display = 'flex'; }
            function closeModal(id) { document.getElementById(id).style.display = 'none'; }

            document.getElementById("image_file").addEventListener("change", function() {
                const file = this.files[0];
                if (file) {
                    if(file.size > 2000000){ alert("Hoto yayi nauyi / File too large (Max 2MB)"); this.value = ""; return; }
                    const reader = new FileReader(); reader.onload = function(e) { document.getElementById("base64String").value = e.target.result; }; reader.readAsDataURL(file);
                }
            });

            document.getElementById('uploadForm').onsubmit = function(e) {
                e.preventDefault(); const btn = document.getElementById('btnSubmitPost'); btn.innerText = "..."; btn.disabled = true;
                const catSelect = document.getElementById('category'); const catValue = catSelect.options[catSelect.selectedIndex].value;
                const data = { name: document.getElementById('name').value, price: parseFloat(document.getElementById('price').value), description: document.getElementById('desc').value, category: catValue, vendor_name: document.getElementById('vendor').value, vendor_phone: document.getElementById('phone').value, image_base64: document.getElementById('base64String').value };
                
                fetch('/saka-kaya/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) })
                .then(res => res.json()).then(res => {
                    alert(dict[currentLang].alertSuccess); document.getElementById('uploadForm').reset(); document.getElementById('base64String').value = ''; closeModal('uploadModal'); loadProducts(); btn.innerText = dict[currentLang].btnSubmitPost; btn.disabled = false;
                }).catch(() => { alert(dict[currentLang].alertFail); btn.innerText = dict[currentLang].btnSubmitPost; btn.disabled = false;});
            };

            function filterProducts() {
                const query = document.getElementById('searchInput').value.toLowerCase(); const catSelect = document.getElementById('categoryFilter'); const cat = catSelect.options[catSelect.selectedIndex].value;
                const filtered = allProducts.filter(p => { return p.name.toLowerCase().includes(query) && ((cat === "Duka") || (p.category === cat)); });
                renderProducts(filtered);
            }

            function renderProducts(products) {
                const container = document.getElementById('kayayyaki'); container.innerHTML = '';
                if(products.length === 0){ container.innerHTML = `<div style="text-align:center; padding:20px; width:100%; color:#999;">${dict[currentLang].empty}</div>`; return; }
                products.forEach(kaya => {
                    const oldPrice = Math.floor(kaya.price * 1.2); 
                    const card = document.createElement('div'); card.className = 'card';
                    card.innerHTML = `<img src="${kaya.image_base64}" class="card-img" alt="${kaya.name}"><div class="card-details"><h4 class="card-title">${kaya.name}</h4><div class="card-price">₦${kaya.price} <small>₦${oldPrice}</small></div><span class="card-shipping">${dict[currentLang].shippingLabel}</span><div class="card-vendor">${dict[currentLang].vendorLabel} ${kaya.vendor_name}</div><button class="add-cart-btn" onclick="addToCart(${kaya.id}, '${kaya.name}', ${kaya.price})">${dict[currentLang].addToCartBtn}</button></div>`;
                    container.appendChild(card);
                });
            }

            function loadProducts() { fetch('/duba-kaya/').then(res => res.json()).then(data => { allProducts = data; renderProducts(allProducts); renderAdminProducts(allProducts); }).catch(()=> { document.getElementById('loadingTxt').innerText = "Network Error"; }); }

            function addToCart(id, name, price) {
                cart.push({id, name, price}); updateCart();
                const toast = document.createElement('div'); toast.innerText = dict[currentLang].alertAdded; toast.style.cssText = "position:fixed; top:20px; right:20px; background:black; color:white; padding:10px 20px; border-radius:20px; z-index:999; opacity:0.9;";
                document.body.appendChild(toast); setTimeout(() => toast.remove(), 2000);
            }

            function updateCart() {
                document.getElementById('cartCount').innerText = cart.length; const cartItemsDiv = document.getElementById('cartItems');
                if(cart.length === 0) { cartItemsDiv.innerHTML = dict[currentLang].cartEmpty; document.getElementById('cartSubtotal').innerText = '₦0'; document.getElementById('cartTotal').innerText = '0'; currentCartTotal = 0; return; }
                cartItemsDiv.innerHTML = ''; let subtotal = 0;
                cart.forEach((item, index) => { subtotal += item.price; cartItemsDiv.innerHTML += `<div class="cart-item"><div class="cart-item-info"><span class="cart-item-title">${item.name}</span><span class="cart-item-price">₦${item.price}</span></div><button class="remove-btn" onclick="removeFromCart(${index})">X</button></div>`; });
                document.getElementById('cartSubtotal').innerText = '₦' + subtotal; currentCartTotal = subtotal + SHIPPING_FEE; document.getElementById('cartTotal').innerText = currentCartTotal;
            }

            function checkoutNaira() { 
                if(cart.length === 0) { alert(dict[currentLang].cartEmpty); return; } 
                
                let userEmail = prompt(dict[currentLang].promptEmail, "kwastoma@email.com");
                if (!userEmail) return;

                let handler = PaystackPop.setup({
                    key: 'pk_test_4d6a3f906c1a1fa859539e7b6086d6be3e3b5b1f', 
                    email: userEmail,
                    amount: currentCartTotal * 100, 
                    currency: 'NGN',
                    channels: ['card', 'bank_transfer', 'ussd'], // AN KARA CHANNELS DIN NAN
                    ref: 'KDV_' + Math.floor((Math.random() * 1000000000) + 1), 
                    callback: function(response) {
                        alert(dict[currentLang].alertPaySuccess + response.reference);
                        cart = [];
                        updateCart();
                        closeModal('cartModal');
                    },
                    onClose: function() {
                        alert(dict[currentLang].alertPayCancel);
                    }
                });
                handler.openIframe();
            }

            function showCryptoPayment() {
                if(cart.length === 0) { alert(dict[currentLang].cartEmpty); return; }
                const usdTotal = (currentCartTotal / EXCHANGE_RATE).toFixed(2);
                document.getElementById('cryptoUsdTotal').innerText = usdTotal;
                closeModal('cartModal'); openModal('cryptoModal');
            }

            function copyWallet() {
                navigator.clipboard.writeText("GDcKRBja7tDKqDftF2WGj3zcwUUBUoUV2xCqaMxfKwzR");
                alert(dict[currentLang].alertCopied);
            }

            function confirmCryptoPaid() {
                alert(dict[currentLang].alertCryptoDone);
                cart = []; updateCart(); closeModal('cryptoModal');
            }

            function loginAdmin() {
                if(document.getElementById('adminPass').value === "kanawa123") { document.getElementById('adminAuth').style.display = 'none'; document.getElementById('adminPanel').style.display = 'block'; } else { alert("Kuskure!"); }
            }

            function renderAdminProducts(products) {
                const adminDiv = document.getElementById('adminItems'); adminDiv.innerHTML = '';
                products.forEach(p => { adminDiv.innerHTML += `<div style="display:flex; justify-content:space-between; border-bottom:1px solid #ccc; padding:10px 0;"><span>${p.name} (₦${p.price})</span><button onclick="deleteProduct(${p.id})" style="background:red; color:white; border:none; padding:5px 10px; border-radius:5px;">Goge</button></div>`; });
            }

            function deleteProduct(id) { if(confirm("Goge? / Delete?")) { fetch('/goge-kaya/' + id, { method: 'DELETE' }).then(() => loadProducts()); } }

            window.onload = function() { changeLanguage('ha'); loadProducts(); };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
