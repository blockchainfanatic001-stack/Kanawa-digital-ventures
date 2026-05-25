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
app = FastAPI(title="Kanawa Digital Market")

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

# --- FRONTEND ---
@app.get("/kasuwa", response_class=HTMLResponse)
def vip_market():
    html_content = """
    <!DOCTYPE html>
    <html lang="ha">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Kanawa Digital Market</title>
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
            .sidenav-header { background: #e62e04; color: white; padding: 25px 20px; font-size: 18px; font-weight: 900; position: relative;}
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
            
            .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #fff; display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #eee; z-index: 100;}
            .nav-item { display: flex; flex-direction: column; align-items: center; color: #666; text-decoration: none; font-size: 11px; cursor: pointer; width: 33.33%;}
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
            .remove-btn { background: #ffebee; border: none; padding: 5px 15px; border-radius: 5px; color: #e62e04; font-weight: bold; cursor: pointer; font-size: 14px;}
            
            .whatsapp-float { position: fixed; bottom: 80px; right: 20px; background-color: #25d366; border-radius: 50%; width: 55px; height: 55px; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 100; text-decoration: none;}
            .whatsapp-float svg { width: 32px; height: 32px; fill: white; }
            
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
            <div class="sidenav-header">Kanawa Digital Market<button class="sidenav-close" onclick="closeNav()">&times;</button></div>
            <a href="#" onclick="closeNav(); openModal('contactModal')"><span>📞</span> <span id="nContact">Tuntube Mu</span></a>
            <a href="#" onclick="closeNav(); openModal('helpModal')"><span>❓</span> <span id="nHelp">Taimako</span></a>
            <a href="#" onclick="closeNav(); openModal('termsModal')"><span>📜</span> <span id="nTerms">Ka'idojin Aiki</span></a>
            <a href="#" onclick="closeNav(); openModal('uploadModal')"><span>➕</span> <span id="nSell">Sayar da Kaya</span></a>
            <a href="#" onclick="closeNav(); openModal('adminModal')"><span>👤</span> <span id="nAdmin">Dakin Gudanarwa (Admin)</span></a>
        </div>

        <div class="top-header">
            <span class="menu-icon" onclick="openNav()">☰</span>
            <span class="logo-text">Kanawa Digital Market</span>
            <div class="search-box"><span>🔍</span><input type="text" id="searchInput" placeholder="Bincika nan..." onkeyup="filterProducts()"></div>
        </div>

        <div class="top-actions">
            <button class="lang-toggle" onclick="changeLanguage('ha')">HA</button>
            <button class="lang-toggle" onclick="changeLanguage('en')">EN</button>
            <button class="action-btn post" id="btnPostAd" onclick="openModal('uploadModal')">➕ Sayar da Kaya</button>
            <input type="hidden" id="categoryFilter" value="Duka">
        </div>

        <div class="banner-section"><span id="bannerTitle">🔥 Zafafan Kayayyaki</span><br><span style="font-size: 12px; font-weight: normal; color: #333;" id="bannerSub">Kudin Aikawa ₦500 kacal!</span></div>

        <div class="product-grid" id="kayayyaki"><div style="text-align:center; width:100%; color:gray; padding:20px;" id="loadingTxt">Ana lodo kayayyaki...</div></div>

        <a href="https://wa.me/2349166614894" class="whatsapp-float" target="_blank">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
                <path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.898 7.898 0 0 0 13.6 2.326zM7.994 14.521a6.573 6.573 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.557 6.557 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.729.729 0 0 0-.529.247c-.182.198-.691.677-.691 1.654 0 .977.71 1.916.81 2.049.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232z"/>
            </svg>
        </a>

        <div class="bottom-nav">
            <div class="nav-item active" onclick="window.scrollTo(0,0)"><span class="nav-icon">🏠</span><span id="navHome">Gida</span></div>
            <div class="nav-item" onclick="openModal('categoryModal')"><span class="nav-icon">📋</span><span id="navCat">Rukunoni</span></div>
            <div class="nav-item" onclick="openModal('cartModal')"><span class="nav-icon">🛒<span class="cart-badge" id="cartCount">0</span></span><span id="navCart">Kwando</span></div>
        </div>

        <div id="categoryModal" class="modal">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('categoryModal')">&times;</button>
                <h3 style="margin-top:0;" id="mCatTitleModal">Zabi Rukuni</h3>
                <div style="display:flex; flex-direction:column; gap:10px;">
                    <button class="submit-btn" style="background:#333;" onclick="selectCategory('Duka')" id="btnCatAll">Dukkan Rukunoni</button>
                    <button class="submit-btn" style="background:#f0f2f5; color:#333; border: 1px solid #ccc;" onclick="selectCategory('Phones')" id="btnCatPhones">📱 Wayoyi & Kwamfutoci</button>
                    <button class="submit-btn" style="background:#f0f2f5; color:#333; border: 1px solid #ccc;" onclick="selectCategory('Fashion')" id="btnCatFashion">👗 Kayan Sawa</button>
                    <button class="submit-btn" style="background:#f0f2f5; color:#333; border: 1px solid #ccc;" onclick="selectCategory('Vehicles')" id="btnCatVehicles">🚗 Ababen Hawa</button>
                    <button class="submit-btn" style="background:#f0f2f5; color:#333; border: 1px solid #ccc;" onclick="selectCategory('Food')" id="btnCatFood">🍅 Kayan Abinci</button>
                    <button class="submit-btn" style="background:#f0f2f5; color:#333; border: 1px solid #ccc;" onclick="selectCategory('Electronics')" id="btnCatElectronics">📺 Kayan Lantarki</button>
                    <button class="submit-btn" style="background:#f0f2f5; color:#333; border: 1px solid #ccc;" onclick="selectCategory('Home')" id="btnCatHome">🪑 Kayan Gida</button>
                    <button class="submit-btn" style="background:#f0f2f5; color:#333; border: 1px solid #ccc;" onclick="selectCategory('Beauty')" id="btnCatBeauty">💄 Kayan Kwalliya</button>
                    <button class="submit-btn" style="background:#f0f2f5; color:#333; border: 1px solid #ccc;" onclick="selectCategory('Others')" id="btnCatOthers">📦 Wasu</button>
                </div>
            </div>
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
                    <div class="form-group"><label id="lCat">Zabi Rukuni</label>
                        <select id="category" class="form-control" required>
                            <option value="Phones" id="optPhones">Wayoyi & Kwamfutoci</option>
                            <option value="Fashion" id="optFashion">Kayan Sawa</option>
                            <option value="Vehicles" id="optVehicles">Ababen Hawa (Motoci/Babura)</option>
                            <option value="Food" id="optFood">Kayan Abinci / Daddawa</option>
                            <option value="Electronics" id="optElectronics">Kayan Lantarki</option>
                            <option value="Home" id="optHome">Kayan Gida</option>
                            <option value="Beauty" id="optBeauty">Kayan Kwalliya</option>
                            <option value="Others" id="optOthers">Wasu / Others</option>
                        </select>
                    </div>
                    <div class="form-group"><label id="lDesc">Bayanin Kaya (Description)</label><textarea id="desc" class="form-control" rows="2" required></textarea></div>
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
                    <button class="submit-btn" style="background:#333; padding:10px;" id="btnCopyWallet" onclick="copyWallet()">📋 Kwafi Asusun (Copy)</button>
                </div>
                <button class="crypto-btn" style="margin-top:20px;" id="btnPaidCrypto" onclick="confirmCryptoPaid()">✅ NA TURA KUDIN</button>
            </div>
        </div>

        <div id="contactModal" class="modal"><div class="modal-content"><button class="close-modal" onclick="closeModal('contactModal')">&times;</button><h3 style="margin-top:0;" id="mContactTitle">Tuntube Mu</h3><p id="mContactBody">Waya/WhatsApp: 09166614894</p></div></div>
        <div id="helpModal" class="modal"><div class="modal-content"><button class="close-modal" onclick="closeModal('helpModal')">&times;</button><h3 style="margin-top:0;" id="mHelpTitle">Taimako</h3><p id="mHelpBody">Zabi kaya, saka a kwando, cike adireshinka, sannan ka biya. Zamu kawo maka kofar gida.</p></div></div>
        <div id="termsModal" class="modal"><div class="modal-content"><button class="close-modal" onclick="closeModal('termsModal')">&times;</button><h3 style="margin-top:0;" id="mTermsTitle">Ka'idojin Aiki</h3><p id="mTermsBody">Kudinka yana cikin aminci. Muna cajin N500 kudin aikawa a Gombe.</p></div></div>

        <div id="adminModal" class="modal">
            <div class="modal-content" style="height: 90vh;">
                <button class="close-modal" onclick="closeModal('adminModal')">&times;</button>
                <h3 style="margin-top:0;" id="mAdminTitle">Dakin Gudanarwa (Admin)</h3>
                <div id="adminAuth">
                    <input type="password" id="adminPass" class="form-control" placeholder="Password: kanawa123">
                    <button class="submit-btn" id="btnAdminLogin" onclick="loginAdmin()">Shiga</button>
                </div>
                <div id="adminPanel" style="display:none;">
                    <div class="admin-tabs">
                        <div class="admin-tab active" id="tabProducts" onclick="switchAdminTab('products')">Kayayyaki</div>
                        <div class="admin-tab" id="tabOrders" onclick="switchAdminTab('orders')">Siyayya</div>
                    </div>
                    <div id="adminItems"></div>
                    <div id="adminOrders" style="display:none;"></div>
                </div>
            </div>
        </div>

        <script>
            const EXCHANGE_RATE = 1500;
            const dict = {
                'ha': { 
                    search: "Bincika nan...", postAd: "➕ Sayar da Kaya", empty: "Babu kayan da ya dace.", ship: "Shipping: ₦500",
                    bannerTitle: "🔥 Zafafan Kayayyaki", bannerSub: "Kudin Aikawa ₦500 kacal!", loading: "Ana lodo kayayyaki...",
                    navHome: "Gida", navCat: "Rukunoni", navCart: "Kwando",
                    nContact: "Tuntube Mu", nHelp: "Taimako", nTerms: "Ka'idojin Aiki", nSell: "Sayar da Kaya", nAdmin: "Dakin Gudanarwa",
                    mPostTitle: "Dora Kayanka A Saukake", lName: "Sunan Kaya", lPrice: "Farashi (₦)", lCat: "Zabi Rukuni", lDesc: "Bayanin Kaya", lVendor: "Sunan Shagonka", lPhone: "Lambar Waya", lImg: "Dauki Hoto (Max 2MB)", btnSubmitPost: "POST AD YANZU",
                    mCartTitle: "Kwandon Siyayyarka", cSubText: "Kudin Kaya:", cShipText: "Kudin Aikawa:", cTotalText: "Jimilla:", btnNaira: "💳 BIYA DA NAIRA", btnCrypto: "🪙 BIYA DA CRYPTO",
                    chkTitle: "Bayanan Isar Da Kaya", clName: "Cikakken Suna", clPhone: "Lambar Waya", clEmail: "Imel (Don samun rasiti)", clAddress: "Cikakken Adireshi (Gida/Unguwa)", btnProceedPay: "Ci Gaba Zuwa Biyan Kudi",
                    crTitle: "Tsarin Biyan Kudi na Crypto", btnCopy: "📋 Kwafi Asusun (Copy)", btnPaid: "✅ NA TURA KUDIN",
                    pdVendorText: "Shago / Vendor:", pdAddToCart: "Saka a Kwando",
                    mContactTitle: "Tuntube Mu", mContactBody: "Kira ko WhatsApp: 09166614894", mHelpTitle: "Taimako", mHelpBody: "Zabi kaya, saka a kwando, cike adireshinka, sannan ka biya. Zamu kawo maka kofar gida.", mTermsTitle: "Ka'idojin Aiki", mTermsBody: "Kudinka yana cikin aminci. Muna cajin N500 kudin aikawa a Gombe.",
                    mAdminTitle: "Dakin Gudanarwa (Admin)", btnAdminLogin: "Shiga", tabProducts: "Kayayyaki", tabOrders: "Siyayya",
                    mCatTitleModal: "Zabi Rukuni", btnCatAll: "Dukkan Rukunoni", btnCatPhones: "📱 Wayoyi & Kwamfutoci", btnCatFashion: "👗 Kayan Sawa", btnCatVehicles: "🚗 Ababen Hawa", btnCatFood: "🍅 Kayan Abinci", btnCatElectronics: "📺 Kayan Lantarki", btnCatHome: "🪑 Kayan Gida", btnCatBeauty: "💄 Kayan Kwalliya", btnCatOthers: "📦 Wasu",
                    // ALERTS
                    alertImgSize: "Hoto yayi nauyi (Max 2MB)", alertAdPosted: "An dora kayanka!", alertCartAdd: "An saka a kwando!", alertCartEmpty: "Kwando fanko ne!", alertOrderSuccess: "Mun samu Order dinka! Zamu kawo maka kaya nan bada dadewa ba.", alertPayCancel: "An fasa biya.", alertCopied: "An kwafi asusun!", alertError: "Kuskure! Password ba daidai ba.", alertDelConfirm: "Goge wannan kayan?", noOrders: "Babu Siyayya tukunna."
                },
                'en': { 
                    search: "Search items...", postAd: "➕ Post Ad", empty: "No products found.", ship: "Shipping: ₦500",
                    bannerTitle: "🔥 Hot Local Products", bannerSub: "Delivery Fee just ₦500!", loading: "Loading products...",
                    navHome: "Home", navCat: "Categories", navCart: "Cart",
                    nContact: "Contact Us", nHelp: "Help & FAQ", nTerms: "Terms & Conditions", nSell: "Sell on KDV", nAdmin: "Admin Login",
                    mPostTitle: "Post Your Ad Easily", lName: "Product Name", lPrice: "Price (₦)", lCat: "Select Category", lDesc: "Description", lVendor: "Shop Name", lPhone: "Phone Number", lImg: "Take Photo (Max 2MB)", btnSubmitPost: "POST AD NOW",
                    mCartTitle: "Your Shopping Cart", cSubText: "Subtotal:", cShipText: "Delivery Fee:", cTotalText: "Total:", btnNaira: "💳 PAY WITH NAIRA", btnCrypto: "🪙 PAY WITH CRYPTO",
                    chkTitle: "Delivery Details", clName: "Full Name", clPhone: "Phone Number", clEmail: "Email (For receipt)", clAddress: "Full Delivery Address", btnProceedPay: "Proceed to Payment",
                    crTitle: "Crypto Payment Gateway", btnCopy: "📋 Copy Address", btnPaid: "✅ I HAVE PAID",
                    pdVendorText: "Vendor:", pdAddToCart: "Add to Cart",
                    mContactTitle: "Contact Us", mContactBody: "Call or WhatsApp: 09166614894", mHelpTitle: "Help Center", mHelpBody: "Select an item, add to cart, fill your address, and pay securely. We deliver to your door.", mTermsTitle: "Terms & Conditions", mTermsBody: "Your payment is secure. We charge a flat N500 delivery fee within Gombe.",
                    mAdminTitle: "Admin Panel", btnAdminLogin: "Login", tabProducts: "Products", tabOrders: "Orders",
                    mCatTitleModal: "Select Category", btnCatAll: "All Categories", btnCatPhones: "📱 Phones & Computers", btnCatFashion: "👗 Fashion", btnCatVehicles: "🚗 Vehicles", btnCatFood: "🍅 Food & Groceries", btnCatElectronics: "📺 Electronics", btnCatHome: "🪑 Home & Furniture", btnCatBeauty: "💄 Health & Beauty", btnCatOthers: "📦 Others",
                    // ALERTS
                    alertImgSize: "Image too large (Max 2MB)", alertAdPosted: "Ad posted successfully!", alertCartAdd: "Added to cart!", alertCartEmpty: "Cart is empty!", alertOrderSuccess: "Order received! We will deliver your items soon.", alertPayCancel: "Payment cancelled.", alertCopied: "Wallet address copied!", alertError: "Error! Incorrect password.", alertDelConfirm: "Delete this item?", noOrders: "No orders yet."
                }
            };
            let currentLang = 'ha'; let allProducts = []; let cart = []; const SHIPPING_FEE = 500; let currentCartTotal = 0;

            function openNav() { document.getElementById("sideNav").style.left = "0"; document.getElementById("sidenavOverlay").style.display = "block"; }
            function closeNav() { document.getElementById("sideNav").style.left = "-260px"; document.getElementById("sidenavOverlay").style.display = "none"; }
            
            function changeLanguage(lang) { 
                currentLang = lang; 
                document.getElementById('searchInput').placeholder = dict[lang].search;
                document.getElementById('btnPostAd').innerText = dict[lang].postAd;
                
                // Sabbin Abubuwa (Banner & Loading)
                document.getElementById('bannerTitle').innerText = dict[lang].bannerTitle;
                document.getElementById('bannerSub').innerText = dict[lang].bannerSub;
                if(document.getElementById('loadingTxt')) document.getElementById('loadingTxt').innerText = dict[lang].loading;
                
                document.getElementById('navHome').innerText = dict[lang].navHome; document.getElementById('navCat').innerText = dict[lang].navCat; document.getElementById('navCart').innerText = dict[lang].navCart;
                
                document.getElementById('nContact').innerText = dict[lang].nContact; document.getElementById('nHelp').innerText = dict[lang].nHelp; document.getElementById('nTerms').innerText = dict[lang].nTerms; document.getElementById('nSell').innerText = dict[lang].nSell; document.getElementById('nAdmin').innerText = dict[lang].nAdmin;
                
                document.getElementById('mPostTitle').innerText = dict[lang].mPostTitle; document.getElementById('lName').innerText = dict[lang].lName; document.getElementById('lPrice').innerText = dict[lang].lPrice; document.getElementById('lCat').innerText = dict[lang].lCat; document.getElementById('lDesc').innerText = dict[lang].lDesc; document.getElementById('lVendor').innerText = dict[lang].lVendor; document.getElementById('lPhone').innerText = dict[lang].lPhone; document.getElementById('lImg').innerText = dict[lang].lImg; document.getElementById('btnSubmitPost').innerText = dict[lang].btnSubmitPost;
                
                document.getElementById('mCartTitle').innerText = dict[lang].mCartTitle; document.getElementById('cSubText').innerText = dict[lang].cSubText; document.getElementById('cShipText').innerText = dict[lang].cShipText; document.getElementById('cTotalText').innerText = dict[lang].cTotalText; document.getElementById('btnCheckoutNaira').innerText = dict[lang].btnNaira; document.getElementById('btnCheckoutCrypto').innerText = dict[lang].btnCrypto;
                
                document.getElementById('chkTitle').innerText = dict[lang].chkTitle; document.getElementById('clName').innerText = dict[lang].clName; document.getElementById('clPhone').innerText = dict[lang].clPhone; document.getElementById('clEmail').innerText = dict[lang].clEmail; document.getElementById('clAddress').innerText = dict[lang].clAddress; document.getElementById('btnProceedPay').innerText = dict[lang].btnProceedPay;
                
                document.getElementById('crTitle').innerText = dict[lang].crTitle; document.getElementById('btnCopyWallet').innerText = dict[lang].btnCopy; document.getElementById('btnPaidCrypto').innerText = dict[lang].btnPaid;
                
                document.getElementById('pdVendorText').innerText = dict[lang].pdVendorText; document.getElementById('pdAddToCart').innerText = dict[lang].pdAddToCart;
                
                document.getElementById('mContactTitle').innerText = dict[lang].mContactTitle; document.getElementById('mContactBody').innerText = dict[lang].mContactBody;
                document.getElementById('mHelpTitle').innerText = dict[lang].mHelpTitle; document.getElementById('mHelpBody').innerText = dict[lang].mHelpBody;
                document.getElementById('mTermsTitle').innerText = dict[lang].mTermsTitle; document.getElementById('mTermsBody').innerText = dict[lang].mTermsBody;
                
                document.getElementById('mAdminTitle').innerText = dict[lang].mAdminTitle; document.getElementById('btnAdminLogin').innerText = dict[lang].btnAdminLogin; document.getElementById('tabProducts').innerText = dict[lang].tabProducts; document.getElementById('tabOrders').innerText = dict[lang].tabOrders;
                
                document.getElementById('mCatTitleModal').innerText = dict[lang].mCatTitleModal; document.getElementById('btnCatAll').innerText = dict[lang].btnCatAll; 
                document.getElementById('btnCatPhones').innerText = dict[lang].btnCatPhones; document.getElementById('btnCatFashion').innerText = dict[lang].btnCatFashion; 
                document.getElementById('btnCatVehicles').innerText = dict[lang].btnCatVehicles; document.getElementById('btnCatFood').innerText = dict[lang].btnCatFood; 
                document.getElementById('btnCatElectronics').innerText = dict[lang].btnCatElectronics; document.getElementById('btnCatHome').innerText = dict[lang].btnCatHome; 
                document.getElementById('btnCatBeauty').innerText = dict[lang].btnCatBeauty; document.getElementById('btnCatOthers').innerText = dict[lang].btnCatOthers;
                
                // Form Options Translation
                document.getElementById('optPhones').innerText = dict[lang].btnCatPhones.substring(3);
                document.getElementById('optFashion').innerText = dict[lang].btnCatFashion.substring(3);
                document.getElementById('optVehicles').innerText = dict[lang].btnCatVehicles.substring(3);
                document.getElementById('optFood').innerText = dict[lang].btnCatFood.substring(3);
                document.getElementById('optElectronics').innerText = dict[lang].btnCatElectronics.substring(3);
                document.getElementById('optHome').innerText = dict[lang].btnCatHome.substring(3);
                document.getElementById('optBeauty').innerText = dict[lang].btnCatBeauty.substring(3);
                document.getElementById('optOthers').innerText = dict[lang].btnCatOthers.substring(3);

                filterProducts(); updateCart();
            }

            function openModal(id) { document.getElementById(id).style.display = 'flex'; }
            function closeModal(id) { document.getElementById(id).style.display = 'none'; }

            document.getElementById("image_file").addEventListener("change", function() {
                const file = this.files[0];
                if (file) {
                    if(file.size > 2000000){ alert(dict[currentLang].alertImgSize); this.value = ""; return; }
                    const reader = new FileReader(); reader.onload = function(e) { document.getElementById("base64String").value = e.target.result; }; reader.readAsDataURL(file);
                }
            });

            document.getElementById('uploadForm').onsubmit = function(e) {
                e.preventDefault(); document.getElementById('btnSubmitPost').disabled = true;
                const data = { name: document.getElementById('name').value, price: parseFloat(document.getElementById('price').value), description: document.getElementById('desc').value, category: document.getElementById('category').value, vendor_name: document.getElementById('vendor').value, vendor_phone: document.getElementById('phone').value, image_base64: document.getElementById('base64String').value };
                fetch('/saka-kaya/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }).then(res => res.json()).then(res => {
                    alert(dict[currentLang].alertAdPosted); document.getElementById('uploadForm').reset(); closeModal('uploadModal'); loadProducts(); document.getElementById('btnSubmitPost').disabled = false;
                });
            };

            function selectCategory(catValue) {
                document.getElementById('categoryFilter').value = catValue;
                filterProducts();
                closeModal('categoryModal');
            }

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

            function addToCart(id, name, price) { cart.push({id, name, price}); updateCart(); alert(dict[currentLang].alertCartAdd); }

            function updateCart() {
                document.getElementById('cartCount').innerText = cart.length; 
                const div = document.getElementById('cartItems');
                if(cart.length === 0) { 
                    div.innerHTML = dict[currentLang].empty; 
                    document.getElementById('cartSubtotal').innerText = '₦0'; 
                    document.getElementById('cartTotal').innerText = '0'; 
                    currentCartTotal = 0; 
                    return; 
                }
                let sub = 0;
                let cartHtml = '';
                cart.forEach((item, i) => { 
                    sub += item.price; 
                    cartHtml += `<div class="cart-item"><div><b>${item.name}</b><br><span style="color:red">₦${item.price}</span></div><button class="remove-btn" onclick="removeFromCart(${i})">X</button></div>`; 
                });
                div.innerHTML = cartHtml;
                document.getElementById('cartSubtotal').innerText = '₦' + sub; 
                currentCartTotal = sub + SHIPPING_FEE; 
                document.getElementById('cartTotal').innerText = currentCartTotal;
            }

            function removeFromCart(index) {
                cart.splice(index, 1);
                updateCart();
            }

            function initCheckout(method) {
                if(cart.length === 0) return alert(dict[currentLang].alertCartEmpty);
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
                    alert(dict[currentLang].alertOrderSuccess);
                    cart = []; updateCart(); closeModal('checkoutModal'); closeModal('cryptoModal'); document.getElementById('checkoutForm').reset();
                });
            }

            function doPaystack() {
                let handler = PaystackPop.setup({
                    key: 'pk_test_4d6a3f906c1a1fa859539e7b6086d6be3e3b5b1f', 
                    email: document.getElementById('cEmail').value, amount: currentCartTotal * 100, currency: 'NGN', channels: ['card', 'bank_transfer', 'ussd'], 
                    ref: 'KDV_' + Math.floor((Math.random() * 1000000000) + 1), 
                    callback: function(res) { saveOrder('Paystack'); },
                    onClose: function() { alert(dict[currentLang].alertPayCancel); }
                }); handler.openIframe();
            }

            function doCrypto() {
                document.getElementById('cryptoUsdTotal').innerText = (currentCartTotal / EXCHANGE_RATE).toFixed(2);
                closeModal('checkoutModal'); openModal('cryptoModal');
            }

            function copyWallet() { navigator.clipboard.writeText("GDcKRBja7tDKqDftF2WGj3zcwUUBUoUV2xCqaMxfKwzR"); alert(dict[currentLang].alertCopied); }
            function confirmCryptoPaid() { saveOrder('Crypto'); }

            function loginAdmin() { if(document.getElementById('adminPass').value === "kanawa123") { document.getElementById('adminAuth').style.display = 'none'; document.getElementById('adminPanel').style.display = 'block'; loadOrders(); } else { alert(dict[currentLang].alertError); } }
            
            function switchAdminTab(tab) {
                document.getElementById('tabProducts').className = tab === 'products' ? 'admin-tab active' : 'admin-tab';
                document.getElementById('tabOrders').className = tab === 'orders' ? 'admin-tab active' : 'admin-tab';
                document.getElementById('adminItems').style.display = tab === 'products' ? 'block' : 'none';
                document.getElementById('adminOrders').style.display = tab === 'orders' ? 'block' : 'none';
            }

            function renderAdminProducts(products) {
                const div = document.getElementById('adminItems'); div.innerHTML = '';
                products.forEach(p => { div.innerHTML += `<div style="display:flex; justify-content:space-between; border-bottom:1px solid #ccc; padding:10px 0;"><span>${p.name} (₦${p.price})</span><button onclick="if(confirm(dict[currentLang].alertDelConfirm)) fetch('/goge-kaya/${p.id}', {method:'DELETE'}).then(()=>loadProducts())" style="background:red; color:white; border:none; padding:5px; border-radius:5px;">Goge</button></div>`; });
            }

            function loadOrders() {
                fetch('/duba-orders/').then(res => res.json()).then(data => {
                    const div = document.getElementById('adminOrders'); div.innerHTML = '';
                    if(data.length===0) div.innerHTML = dict[currentLang].noOrders;
                    data.forEach(o => {
                        let items = JSON.parse(o.items).map(i => i.name).join(", ");
                        div.innerHTML += `<div class="order-card"><b>Suna:</b> ${o.customer_name} <br><b>Waya:</b> ${o.customer_phone} <br><b>Adireshi:</b> ${o.customer_address} <br><b>Kaya:</b> ${items} <br><b>Kudi:</b> ₦${o.total_amount} (${o.payment_method}) <br><small style="color:gray">${o.date_created}</small></div>`;
                    });
                });
            }

            window.onload = function() { changeLanguage('ha'); loadProducts(); };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
