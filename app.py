from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import os
import random

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER DEFAULT 10,
            sizes TEXT NOT NULL,
            colors TEXT NOT NULL,
            image TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            size TEXT NOT NULL,
            color TEXT NOT NULL,
            price INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            address TEXT NOT NULL,
            payment TEXT NOT NULL,
            status TEXT NOT NULL,
            otp TEXT NOT NULL,
            return_reason TEXT DEFAULT 'None'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            insta TEXT,
            facebook TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

FINAL_STORE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Little Star Readymade Kids Wear | Beed</title>
    <style>
        :root {
            --primary: #ff4757;
            --primary-dark: #ff6b81;
            --accent: #2ed573;
            --dark: #2f3542;
            --light: #f4f6f9;
            --white: #ffffff;
            --border: #e1e8ed;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: var(--light); color: var(--dark); }

        .top-bar { background: #1e272e; color: var(--white); padding: 10px 30px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; flex-wrap: wrap; gap: 10px; }
        
        header { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: var(--white); padding: 20px 30px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .logo h1 { font-size: 26px; }
        .logo p { font-size: 13px; opacity: 0.95; margin-top: 4px; }

        .header-actions { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
        .lang-select { background: #fff; color: var(--dark); padding: 8px 12px; border-radius: 6px; font-weight: bold; border: none; cursor: pointer; }
        .user-reg-btn { background: var(--white); color: var(--primary); border: none; padding: 10px 18px; border-radius: 25px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: 0.3s; }
        .user-reg-btn:hover { background: #ffa502; color: var(--white); }

        .search-box { display: flex; flex: 1; max-width: 350px; min-width: 220px; }
        .search-box input { width: 100%; padding: 10px 15px; border: none; border-radius: 6px 0 0 6px; font-size: 14px; outline: none; }
        .search-box button { background: #ffa502; color: var(--white); border: none; padding: 0 15px; border-radius: 0 6px 6px 0; cursor: pointer; font-weight: bold; }

        .marquee-banner { background: #ffa502; color: var(--white); text-align: center; padding: 10px; font-weight: bold; font-size: 14px; }

        .layout-container { max-width: 1350px; margin: 30px auto; padding: 0 15px; display: grid; grid-template-columns: 280px 1fr; gap: 25px; }

        @media (max-width: 900px) {
            .layout-container { grid-template-columns: 1fr; }
        }

        .sidebar { background: var(--white); padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); height: fit-content; border: 1px solid var(--border); }
        .sidebar h3 { font-size: 18px; color: var(--dark); margin-bottom: 15px; border-bottom: 2px solid var(--primary); padding-bottom: 8px; }
        .menu-category { font-weight: bold; color: var(--primary); margin: 15px 0 8px 0; font-size: 15px; }
        .menu-items { list-style: none; padding-left: 10px; }
        .menu-items li { margin: 6px 0; }
        .menu-link { background: none; border: none; color: #555; font-size: 14px; cursor: pointer; text-align: left; transition: 0.2s; width: 100%; padding: 4px 8px; border-radius: 4px; }
        .menu-link:hover, .menu-link.active { background: #ffeaa7; color: var(--dark); font-weight: bold; }

        .content-area { display: flex; flex-direction: column; gap: 20px; }

        .utility-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; }
        .utility-box { background: var(--white); padding: 15px 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid var(--primary); }
        .utility-box input { padding: 8px 12px; width: 60%; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; margin-top: 8px; }
        .utility-box button { background: #ffa502; color: var(--white); border: none; padding: 8px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px; }

        .admin-toggle-btn { background: var(--dark); color: var(--white); border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; width: 100%; justify-content: center; }
        
        .admin-panel { background: var(--white); padding: 25px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); display: none; border-top: 5px solid var(--primary); margin-bottom: 20px; }
        .admin-panel h3 { margin-bottom: 15px; color: var(--dark); font-size: 18px; }
        
        .analytics-card { background: linear-gradient(135deg, #2ed573, #2f9e44); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .analytics-card h2 { font-size: 26px; }

        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 15px; }
        .admin-panel input, .admin-panel select { width: 100%; padding: 10px; border: 1px solid #ced6e0; border-radius: 6px; font-size: 13px; outline: none; }
        
        .size-builder-box { grid-column: 1 / -1; background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; }
        .size-btn-group { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
        .size-chip { background: #fff; border: 1px solid var(--primary); color: var(--primary); padding: 6px 12px; border-radius: 20px; cursor: pointer; font-weight: bold; font-size: 12px; transition: 0.2s; }
        .size-chip:hover { background: var(--primary); color: white; }

        .color-toolbox-box { grid-column: 1 / -1; background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; display: flex; align-items: center; gap: 15px; }
        .color-toolbox-box input[type="color"] { width: 60px; height: 40px; border: none; cursor: pointer; background: none; }

        .image-upload-box { grid-column: 1 / -1; background: #fff; padding: 12px; border: 2px dashed #cbd5e1; border-radius: 8px; text-align: center; }

        .admin-panel button.publish-btn { background: var(--accent); color: var(--white); border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; font-size: 15px; }

        .orders-table-container { overflow-x: auto; margin-top: 15px; }
        .orders-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; }
        .orders-table th, .orders-table td { padding: 8px; border: 1px solid #ddd; }
        .orders-table th { background: var(--primary); color: var(--white); }
        .action-link { padding: 4px 8px; border-radius: 4px; color: white; text-decoration: none; font-weight: bold; font-size: 11px; margin-right: 3px; display: inline-block; margin-bottom: 2px; }
        .btn-edit { background: #3498db; }
        .btn-status { background: #9b59b6; }
        .btn-verify { background: #2ed573; }

        .section-title { color: var(--primary); font-size: 24px; margin-bottom: 15px; border-bottom: 2px solid #ddd; padding-bottom: 5px; }

        .products-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; }
        .product-card { background: var(--white); border-radius: 12px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid var(--border); position: relative; transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-4px); }
        .product-tag { position: absolute; top: 12px; left: 12px; background: var(--primary); color: var(--white); font-size: 10px; padding: 3px 8px; border-radius: 4px; font-weight: bold; text-transform: uppercase; z-index: 10; }
        
        .stock-badge { position: absolute; top: 12px; right: 12px; background: #2ed573; color: white; font-size: 10px; padding: 3px 6px; border-radius: 4px; font-weight: bold; z-index: 10; }
        .stock-badge.low { background: #ffa502; }
        .stock-badge.out { background: #ff4757; }

        .product-img-box { width: 100%; height: 160px; background: #f8f9fa; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; margin: 12px 0; border: 1px solid #eee; cursor: pointer; }
        .product-img-box img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
        .product-img-box img:hover { transform: scale(1.08); }

        .price { color: var(--primary); font-weight: bold; font-size: 20px; margin: 8px 0; }
        
        .tags-container { display: flex; justify-content: center; gap: 5px; flex-wrap: wrap; margin: 6px 0; }
        .size-badge { background: #f1f2f6; border: 1px solid #ced6e0; padding: 3px 8px; font-size: 11px; border-radius: 4px; font-weight: bold; color: var(--dark); }
        .color-dot { width: 18px; height: 18px; border-radius: 50%; display: inline-block; border: 1px solid #bbb; box-shadow: 0 2px 3px rgba(0,0,0,0.1); }

        .btn-group { display: flex; gap: 6px; margin-top: 12px; }
        .cart-btn { background: #ffa502; color: var(--white); border: none; padding: 8px; border-radius: 6px; cursor: pointer; font-weight: bold; flex: 1; font-size: 12px; }
        .wish-btn { background: #f1f2f6; color: #ff4757; border: 1px solid #ff4757; padding: 8px 10px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px; }
        .buy-btn { background: var(--accent); color: var(--white); border: none; padding: 8px; border-radius: 6px; cursor: pointer; font-weight: bold; flex: 1; font-size: 12px; }

        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); justify-content: center; align-items: center; z-index: 2000; padding: 15px; }
        .modal-content { background: var(--white); padding: 30px; border-radius: 14px; width: 450px; max-width: 100%; position: relative; box-shadow: 0 15px 35px rgba(0,0,0,0.2); }
        .close-btn { position: absolute; top: 12px; right: 18px; font-size: 24px; cursor: pointer; color: #777; }
        .modal-content input, .modal-content select { width: 100%; padding: 10px; margin: 6px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; outline: none; }
        .modal-content button.confirm-btn { background: var(--primary); color: var(--white); border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 12px; font-size: 15px; }

        .upi-box { background: #e8f8f5; border: 1px solid #2ed573; padding: 12px; border-radius: 8px; margin: 10px 0; display: block; text-align: center; }
        .upi-box p { font-size: 13px; color: var(--dark); font-weight: bold; }

        .footer-about-btn { background: #ffa502; color: white; border: none; padding: 10px 25px; border-radius: 20px; font-weight: bold; cursor: pointer; font-size: 14px; margin-bottom: 12px; transition: 0.3s; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .footer-about-btn:hover { background: #ff4757; }

        .whatsapp-float { position: fixed; bottom: 25px; right: 25px; background-color: #25d366; color: var(--white); padding: 12px 20px; border-radius: 50px; text-decoration: none; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 1000; display: flex; align-items: center; gap: 8px; font-size: 14px; }
        
        footer { background: var(--dark); color: var(--white); text-align: center; padding: 30px; margin-top: 50px; font-size: 13px; }
    </style>
</head>
<body>

    <div class="top-bar">
        <div>📍 Near City Hotel, Karanja Road, Beed - 431122</div>
        <div>📞 9405691878 / 9921911615</div>
    </div>

    <header>
        <div class="logo">
            <h1>⭐ Little Star Readymade Kids Wear ⭐</h1>
            <p>0 Size te 15 Varsh | Ladies & Gents Special Collection</p>
        </div>
        <div class="header-actions">
            <button class="user-reg-btn" onclick="openRegModal()">👤 Register / VIP Club</button>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search collection..." onkeyup="searchProducts()">
                <button onclick="searchProducts()">🔍</button>
            </div>
        </div>
    </header>

    <div class="marquee-banner">
        🔥 Ultimate Store Live! Automated WhatsApp & Live Tracking Active 🔥
    </div>

    <div class="layout-container">
        
        <aside class="sidebar">
            <h3>🛍️ Categories & Filters</h3>
            
            <div class="menu-category">🌟 All Collections</div>
            <ul class="menu-items">
                <li><button class="menu-link active" onclick="filterMenu('All', 'All')">Show All Products</button></li>
            </ul>

            <div class="menu-category">👦 Boys Wear Collection</div>
            <ul class="menu-items">
                <li><button class="menu-link" onclick="filterMenu('Boys', 'Shirt')">🔹 Shirts</button></li>
                <li><button class="menu-link" onclick="filterMenu('Boys', 'Pant')">🔹 Pants</button></li>
                <li><button class="menu-link" onclick="filterMenu('Boys', 'T-Shirt')">🔹 T-Shirts</button></li>
                <li><button class="menu-link" onclick="filterMenu('Boys', 'Half Pant')">🔹 Half Pants</button></li>
                <li><button class="menu-link" onclick="filterMenu('Boys', 'Baba Suit')">🔹 Baba Suits</button></li>
                <li><button class="menu-link" onclick="filterMenu('Boys', 'Jacket')">🔹 Jackets & Blazers</button></li>
            </ul>

            <div class="menu-category">👧 Girls Wear Collection</div>
            <ul class="menu-items">
                <li><button class="menu-link" onclick="filterMenu('Girls', 'Frock')">🔸 Frocks & Dresses</button></li>
                <li><button class="menu-link" onclick="filterMenu('Girls', 'Lehenga')">🔸 Lehenga Choli</button></li>
                <li><button class="menu-link" onclick="filterMenu('Girls', 'Gown')">🔸 Party Gowns</button></li>
                <li><button class="menu-link" onclick="filterMenu('Girls', 'Top-Skirt')">🔸 Top & Skirt Sets</button></li>
                <li><button class="menu-link" onclick="filterMenu('Girls', 'Kurti')">🔸 Kurti & Leggings</button></li>
            </ul>

            <div class="menu-category">👗 Ladies & Gents</div>
            <ul class="menu-items">
                <li><button class="menu-link" onclick="filterMenu('Ladies', 'All')">👗 Ladies Special</button></li>
                <li><button class="menu-link" onclick="filterMenu('Gents', 'All')">👔 Gents Wear</button></li>
            </ul>
        </aside>

        <main class="content-area">
            
            <div class="utility-grid">
                <div class="utility-box">
                    <h3 style="color:var(--dark); font-size:15px;">📦 Live Order Tracking & Location</h3>
                    <div style="display:flex; gap:6px;">
                        <input type="text" id="trackInput" placeholder="Order ID (e.g. LS1023)">
                        <button onclick="trackOrder()">Track Live</button>
                    </div>
                </div>
                <div class="utility-box" style="border-left-color: #2ed573; display:flex; flex-direction:column; justify-content:center;">
                    <button class="admin-toggle-btn" onclick="toggleAdminPanel()">🔒 Shop Owner Dashboard & Analytics</button>
                </div>
            </div>

            <div class="admin-panel" id="adminPanel">
                <h3>📊 Shop Owner Management Dashboard & Revenue</h3>
                
                <div class="analytics-card">
                    <div>
                        <h4 style="font-size:14px; opacity:0.9;">Total Revenue Generated (एकूण कमाई)</h4>
                        <h2>₹ {{ total_revenue }}</h2>
                    </div>
                    <div style="text-align:right;">
                        <h4 style="font-size:14px; opacity:0.9;">Total Orders Received</h4>
                        <h2>{{ orders|length }} Orders</h2>
                    </div>
                </div>

                <div style="background:#f1f2f6; padding:15px; border-radius:8px; margin-bottom:20px;">
                    <h4 style="color:var(--primary); margin-bottom:10px;">➕ Add Product with Size Builder & Photo</h4>
                    <form action="/add_product" method="POST" enctype="multipart/form-data">
                        <div class="form-grid">
                            <input type="text" name="name" placeholder="Product Name (e.g. Designer Kids Shirt)" required>
                            <select name="category" required>
                                <option value="Boys">Boys Wear</option>
                                <option value="Girls">Girls Wear</option>
                                <option value="Ladies">Ladies Special</option>
                                <option value="Gents">Gents Wear</option>
                            </select>
                            <select name="subcategory" required>
                                <option value="Shirt">Shirt</option>
                                <option value="Pant">Pant</option>
                                <option value="T-Shirt">T-Shirt</option>
                                <option value="Half Pant">Half Pant</option>
                                <option value="Baba Suit">Baba Suit</option>
                                <option value="Jacket">Jacket</option>
                                <option value="Frock">Frock</option>
                                <option value="Lehenga">Lehenga</option>
                                <option value="Gown">Gown</option>
                                <option value="Top-Skirt">Top-Skirt</option>
                                <option value="Kurti">Kurti</option>
                                <option value="All">General / Other</option>
                            </select>
                            <input type="number" name="price" placeholder="Price in ₹ (e.g. 699)" required>
                            <input type="number" name="stock" placeholder="Initial Stock Quantity" required>
                            
                            <div class="size-builder-box">
                                <label style="font-weight:bold; font-size:13px; color:var(--dark);">📏 Select Sizes:</label>
                                <div class="size-btn-group">
                                    <button type="button" class="size-chip" onclick="addSize('0 Size')">+ 0 Size</button>
                                    <button type="button" class="size-chip" onclick="addSize('1 Year')">+ 1 Year</button>
                                    <button type="button" class="size-chip" onclick="addSize('2 Years')">+ 2 Years</button>
                                    <button type="button" class="size-chip" onclick="addSize('5 Years')">+ 5 Years</button>
                                    <button type="button" class="size-chip" onclick="addSize('10 Years')">+ 10 Years</button>
                                    <button type="button" class="size-chip" onclick="addSize('15 Years')">+ 15 Years</button>
                                    <button type="button" class="size-chip" onclick="addSize('Free Size')">+ Free Size</button>
                                    <button type="button" class="size-chip" onclick="clearSizes()" style="background:#ff4757; color:white;">Clear</button>
                                </div>
                                <input type="text" name="sizes" id="finalSizesInput" placeholder="Selected sizes will appear here..." required style="margin-top:10px; background:#fff;">
                            </div>

                            <div class="image-upload-box">
                                <label style="font-weight:bold; font-size:12px; display:block; margin-bottom:4px; color:var(--dark);">📸 Upload Product Photo:</label>
                                <input type="file" name="product_image" accept="image/*" required style="border:none; background:transparent;">
                            </div>

                            <div class="color-toolbox-box">
                                <label style="font-weight:bold; font-size:13px; color:var(--dark);">🎨 Select Color:</label>
                                <input type="color" name="colors" value="#ff4757" required>
                                <span style="font-size:12px; color:#666;">(Click box to pick any color)</span>
                            </div>
                        </div>
                        <button type="submit" class="publish-btn">🚀 Publish Product & Inventory</button>
                    </form>
                </div>

                <h4 style="color:var(--dark); margin-bottom:10px;">📋 Live Customer Orders</h4>
                <div class="orders-table-container">
                    <table class="orders-table">
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Customer & Location</th>
                                <th>Product Details</th>
                                <th>Payment & OTP</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for o in orders %}
                            <tr>
                                <td><b>{{ o[1] }}</b></td>
                                <td><b>{{ o[6] }}</b><br>{{ o[7] }}<br><small style="color:#d35400;">📍 {{ o[8] }}</small></td>
                                <td>{{ o[2] }}<br><b>Size:</b> {{ o[3] }} | <b>Color:</b> <span style="display:inline-block; width:10px; height:10px; background:{{ o[4] }}; border-radius:50%; vertical-align:middle;"></span><br><b>₹{{ o[5] }}</b></td>
                                <td><b>{{ o[9] }}</b><br><span style="background:#3498db; color:white; padding:2px 6px; border-radius:4px; font-size:11px;">OTP: {{ o[11] }}</span></td>
                                <td><span style="background:#e67e22; color:white; padding:3px 6px; border-radius:4px; font-size:11px;"><b>{{ o[10] }}</b></span></td>
                                <td>
                                    <a href="#" class="action-link btn-status" onclick="updateOrderStatus('{{ o[1] }}')">Update</a>
                                    <a href="#" class="action-link btn-verify" onclick="verifyOTP('{{ o[1] }}', '{{ o[11] }}')">Verify</a>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="6" style="text-align:center; color:#777;">No orders received yet.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <h4 style="color:var(--dark); margin:20px 0 10px 0;">📦 Manage Store Products</h4>
                <div class="orders-table-container">
                    <table class="orders-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Photo</th>
                                <th>Name</th>
                                <th>Stock</th>
                                <th>Price</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for p in products %}
                            <tr>
                                <td>{{ p[0] }}</td>
                                <td>
                                    {% if p[8] %}
                                        <img src="{{ url_for('static', filename='uploads/' + p[8]) }}" style="width:40px; height:40px; object-fit:cover; border-radius:4px;">
                                    {% else %}
                                        No Image
                                    {% endif %}
                                </td>
                                <td>{{ p[1] }}</td>
                                <td><b>{{ p[5] }} left</b></td>
                                <td>₹{{ p[4] }}</td>
                                <td>
                                    <a href="/delete_product/{{ p[0] }}" class="action-link" style="background:#ff4757;" onclick="return confirm('Delete?')">Delete</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

            </div>

            <h2 class="section-title">Live Store Collection</h2>

            <div class="products-grid" id="productGrid">
                {% for p in products %}
                <div class="product-card" data-category="{{ p[2] }}" data-subcategory="{{ p[3] }}" data-name="{{ p[1].lower() }}" data-sizes="{{ p[6].lower() }}" data-colors="{{ p[7].lower() }}">
                    <span class="product-tag">{{ p[2] }} - {{ p[3] }}</span>
                    
                    {% if p[5] > 5 %}
                        <span class="stock-badge">Stock: {{ p[5] }}</span>
                    {% elif p[5] > 0 %}
                        <span class="stock-badge low">Low: {{ p[5] }}</span>
                    {% else %}
                        <span class="stock-badge out">Sold Out</span>
                    {% endif %}

                    <div class="product-img-box" onclick="zoomImage('{% if p[8] %}{{ url_for('static', filename='uploads/' + p[8]) }}{% endif %}')">
                        {% if p[8] %}
                            <img src="{{ url_for('static', filename='uploads/' + p[8]) }}" alt="{{ p[1] }}">
                        {% else %}
                            <span style="font-size:35px;">✨</span>
                        {% endif %}
                    </div>

                    <h4>{{ p[1] }}</h4>
                    <div class="price">₹ {{ p[4] }}</div>
                    
                    <div style="font-size:12px; color:#666; margin-top:4px;">Available Sizes:</div>
                    <div class="tags-container">
                        {% for size in p[6].split(',') %}
                            <span class="size-badge">{{ size.strip() }}</span>
                        {% endfor %}
                    </div>

                    {% if p[7] and p[7].strip() != '' %}
                    <div style="font-size:12px; color:#666; margin-top:6px;">Selected Color:</div>
                    <div class="tags-container">
                        <span class="color-dot" style="background:{{ p[7] }};" title="{{ p[7] }}"></span>
                    </div>
                    {% endif %}

                    <div class="btn-group">
                        <button class="cart-btn" onclick="addToCart('{{ p[1] }}', '{{ p[4] }}')">🛒 Cart</button>
                        <button class="wish-btn" onclick="addToWishlist('{{ p[1] }}', '{{ p[4] }}')">❤️</button>
                        {% if p[5] > 0 %}
                            <button class="buy-btn" onclick="openCheckout('{{ p[1] }}', '{{ p[4] }}', '{{ p[6] }}', '{{ p[7] }}')">⚡ Buy Now</button>
                        {% else %}
                            <button class="buy-btn" style="background:#ccc; cursor:not-allowed;" disabled>Sold Out</button>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>

        </main>
    </div>

    <a href="https://wa.me/919405691878?text=Hi,%20Mala%20Little%20Star%20madhun%20help%20havi%20aahe." class="whatsapp-float" target="_blank">
        💬 Live WhatsApp Support
    </a>

    <div class="modal" id="zoomModal" onclick="closeModal('zoomModal')">
        <div style="background:transparent; text-align:center; position:relative; max-width:90%;">
            <img id="zoomedImg" src="" style="max-width:100%; max-height:80vh; border-radius:8px; box-shadow:0 0 25px rgba(0,0,0,0.5);">
            <p style="color:white; margin-top:10px; font-weight:bold;">Click anywhere to close</p>
        </div>
    </div>

    <div class="modal" id="regModal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal('regModal')">&times;</span>
            <h3 style="color:var(--primary); margin-bottom:5px;">✨ Customer Registration & VIP Club</h3>
            <p style="font-size:12px; color:#666; margin-bottom:12px;">Register with Mobile, Email & Social IDs.</p>
            
            <form action="/register_user" method="POST">
                <input type="text" name="full_name" placeholder="Full Name / पूर्ण नाव" required>
                <input type="text" name="mobile" placeholder="Mobile Number / मोबाईल नंबर" required>
                <input type="email" name="email" placeholder="Email ID / ईमेल आयडी" required>
                <input type="text" name="insta" placeholder="Instagram ID (e.g. @username)">
                <input type="text" name="facebook" placeholder="Facebook Profile Link / Name">
                <button type="submit" class="confirm-btn" style="background:#2ed573;">Complete Registration</button>
            </form>
        </div>
    </div>

    <div class="modal" id="checkoutModal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal('checkoutModal')">&times;</span>
            <h3 style="color:var(--primary); margin-bottom:8px;">⚡ Instant Order Slip & Invoice</h3>
            <p id="chkSummary" style="font-weight:bold; margin-bottom:12px; color:var(--dark);"></p>
            
            <label style="font-size:12px; font-weight:bold;">Select Exact Size:</label>
            <select id="sizeDropdown"></select>

            <div id="colorSelectionArea">
                <label style="font-size:12px; font-weight:bold;">Product Color:</label>
                <input type="text" id="colorDisplay" readonly style="background:#eee;">
            </div>

            <input type="text" id="buyerName" placeholder="Full Name / ग्राहकाचे नाव" required>
            <input type="text" id="buyerMobile" placeholder="Mobile Number / मोबाईल नंबर" required>
            <input type="text" id="buyerAddress" placeholder="Delivery Address / पत्ता (Beed)" required>
            
            <label style="font-size:12px; font-weight:bold; display:block; margin-top:4px;">Select Payment Option:</label>
            <select id="paymentMode" onchange="checkPaymentMethod(this.value)">
                <option value="PhonePe / GPay / UPI">PhonePe / Google Pay / UPI (9405691878)</option>
                <option value="Cash on Delivery (COD)">Cash on Delivery (COD - OTP Verified)</option>
                <option value="Net Banking">Net Banking</option>
            </select>

            <div class="upi-box" id="upiNoticeBox" style="display:block;">
                <p>⚡ Pay via PhonePe / GPay / UPI to: <b>9405691878</b></p>
                <small style="color:#555;">(Scan your app or transfer directly before confirming)</small>
            </div>

            <button onclick="confirmOrder()" class="confirm-btn">Generate Invoice & Send to WhatsApp</button>
        </div>
    </div>

    <footer>
        <button class="footer-about-btn" onclick="openAboutModal()">ℹ️ About Our Store & Services</button>
        <p>&copy; 2026 Little Star Readymade Kids Wear, Beed. All Rights Reserved.</p>
    </footer>

    <div class="modal" id="aboutModal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal('aboutModal')">&times;</span>
            <h3 style="color:var(--primary); margin-bottom:12px;">⭐ About Little Star Readymade Kids Wear</h3>
            <p style="font-size:13px; color:#555; line-height:1.6; margin-bottom:10px;">
                <strong>Little Star Readymade Kids Wear (Beed)</strong> brings you the finest and most trending festive and daily wear collection for newborns, kids (0 size to 15 years), along with exclusive Ladies and Gents readymade garments.
            </p>
            <p style="font-size:13px; color:#555; line-height:1.6; margin-bottom:10px;">
                <strong>Our Digital Services:</strong> Seamless online shopping with instant WhatsApp order slips, real-time live location & stage tracking, secure digital payments via PhonePe/UPI (9405691878), and Cash on Delivery (COD) with OTP verification!
            </p>
            <button onclick="closeModal('aboutModal')" class="confirm-btn" style="background:#2f3542;">Close</button>
        </div>
    </div>

    <script>
        let currentProduct = {};
        let selectedProductColor = "";

        function addSize(sizeText) {
            let sizeInput = document.getElementById('finalSizesInput');
            if(sizeInput.value === "") {
                sizeInput.value = sizeText;
            } else {
                sizeInput.value += ", " + sizeText;
            }
        }

        function clearSizes() {
            document.getElementById('finalSizesInput').value = "";
        }

        function openRegModal() { document.getElementById('regModal').style.display = 'flex'; }
        function openAboutModal() { document.getElementById('aboutModal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }

        function toggleAdminPanel() {
            let pass = prompt("Enter Shop Owner Password:");
            if(pass === "1234" || pass === "admin") {
                let panel = document.getElementById('adminPanel');
                panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
            } else if(pass !== null) { alert("Incorrect Password!"); }
        }

        function zoomImage(imgSrc) {
            if(imgSrc) {
                document.getElementById('zoomedImg').src = imgSrc;
                document.getElementById('zoomModal').style.display = 'flex';
            }
        }

        function addToWishlist(name, price) {
            alert("❤️ " + name + " (₹" + price + ") has been added to your Wishlist!");
        }

        function filterMenu(category, subcategory) {
            let links = document.querySelectorAll('.menu-link');
            links.forEach(l => l.classList.remove('active'));
            event.target.classList.add('active');

            let cards = document.querySelectorAll('.product-card');
            cards.forEach(card => {
                let cat = card.getAttribute('data-category');
                let sub = card.getAttribute('data-subcategory');
                
                if(category === 'All' || (cat === category && (subcategory === 'All' || sub === subcategory))) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function searchProducts() {
            let query = document.getElementById('searchInput').value.toLowerCase();
            let cards = document.querySelectorAll('.product-card');
            cards.forEach(card => {
                let name = card.getAttribute('data-name');
                let sizes = card.getAttribute('data-sizes');
                let colors = card.getAttribute('data-colors');
                if(name.includes(query) || sizes.includes(query) || colors.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function addToCart(name, price) {
            alert("🛍️ " + name + " (₹" + price + ") added to Cart successfully!");
        }

        function openCheckout(name, price, sizes, colorHex) {
            currentProduct = { name, price };
            selectedProductColor = colorHex;
            document.getElementById('chkSummary').innerText = name + " - ₹" + price;

            let sizeSelect = document.getElementById('sizeDropdown');
            sizeSelect.innerHTML = sizes.split(',').map(s => `<option value="${s.trim()}">${s.trim()}</option>`).join('');

            document.getElementById('colorDisplay').value = colorHex;
            document.getElementById('checkoutModal').style.display = 'flex';
        }

        function checkPaymentMethod(val) {
            let box = document.getElementById('upiNoticeBox');
            if(val.includes('UPI') || val.includes('PhonePe')) {
                box.style.display = 'block';
            } else {
                box.style.display = 'none';
            }
        }

        function confirmOrder() {
            let size = document.getElementById('sizeDropdown').value;
            let color = selectedProductColor;
            let name = document.getElementById('buyerName').value;
            let mobile = document.getElementById('buyerMobile').value;
            let address = document.getElementById('buyerAddress').value;
            let payment = document.getElementById('paymentMode').value;

            if(name && mobile && address) {
                let orderId = "LS" + Math.floor(1000 + Math.random() * 9000);
                let generatedOtp = Math.floor(1000 + Math.random() * 9000);
                
                fetch('/save_order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `order_id=${orderId}&product_name=${currentProduct.name}&size=${size}&color=${color}&price=${currentProduct.price}&customer_name=${name}&mobile=${mobile}&address=${address}&payment=${payment}&status=1. Order Placed & Packed (Beed Store)&otp=${generatedOtp}`
                }).then(() => {
                    // 👉 ऑटोमॅटिक WhatsApp नोटिफिकेशन टेम्पलेट (दुकानदाराच्या 9405691878 वर डायरेक्ट इनव्हॉइस आणि OTP पाठवण्यासाठी)
                    let invoiceSlip = `⭐ *LITTLE STAR READYMADE KIDS WEAR* ⭐%0A-----------------------------------%0A✅ *New Order Placed!*%0AOrder ID: *${orderId}*%0AProduct: ${currentProduct.name}%0ASize: ${size}%0APrice: ₹${currentProduct.price}%0APayment: ${payment}%0A-----------------------------------%0A🔒 *Delivery OTP: ${generatedOtp}*%0A-----------------------------------%0ACustomer: ${name}%0AMobile: ${mobile}%0AAddress: ${address}%0A-----------------------------------%0A📍 *Store:* Near City Hotel, Karanja Road, Beed`;
                    
                    window.open(`https://wa.me/919405691878?text=${invoiceSlip}`, '_blank');
                    alert("Order Placed Successfully! Delivery OTP is: " + generatedOtp);
                    closeModal('checkoutModal');
                    location.reload();
                });
            } else {
                alert("कृपया ग्राहकाचे नाव, मोबाईल आणि पत्ता पूर्ण भरा.");
            }
        }

        function verifyOTP(orderId) {
            let enteredOtp = prompt("Enter 4-Digit Delivery OTP received by Customer:");
            if(enteredOtp) {
                window.location.href = `/verify_order_otp/${orderId}/${enteredOtp}`;
            }
        }

        function updateOrderStatus(orderId) {
            let newStage = prompt("Update Order Stage (e.g. 2. Out for Delivery in Beed / 3. Delivered & Completed):", "2. Out for Delivery in Beed");
            let newLocation = prompt("Update Current Location (e.g. Karanja Road, Beed):", "Karanja Road, Beed");
            if(newStage && newLocation) {
                window.location.href = `/update_order_stage/${orderId}/${encodeURIComponent(newStage)}/${encodeURIComponent(newLocation)}`;
            }
        }

        function trackOrder() {
            let oid = document.getElementById('trackInput').value.trim();
            if(oid) {
                fetch('/track/' + oid)
                .then(res => res.json())
                .then(data => {
                    if(data.success) {
                        alert("📦 Live Order Tracking Report:\\n\\nOrder ID: " + data.order_id + "\\nProduct: " + data.product + "\\n📍 Current Location: " + data.location + "\\n🚀 Current Stage: " + data.status + "\\n🔒 Delivery OTP: " + data.otp);
                    } else {
                        alert("❌ Order ID not found!");
                    }
                });
            } else {
                alert("Please enter a valid Order ID.");
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY id DESC')
    products = cursor.fetchall()
    cursor.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = cursor.fetchall()
    
    total_revenue = sum(o[5] for o in orders if 'Delivered' in o[10])
    
    conn.close()
    return render_template_string(FINAL_STORE_TEMPLATE, products=products, orders=orders, total_revenue=total_revenue)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    category = request.form['category']
    subcategory = request.form['subcategory']
    price = request.form['price']
    stock = request.form['stock']
    sizes = request.form['sizes']
    colors = request.form.get('colors', '#ff4757')
    
    image_filename = ""
    if 'product_image' in request.files:
        file = request.files['product_image']
        if file.filename != '':
            image_filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, category, subcategory, price, stock, sizes, colors, image) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, category, subcategory, price, stock, sizes, colors, image_filename))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_product/<int:prod_id>')
def delete_product(prod_id):
    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (prod_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/register_user', methods=['POST'])
def register_user():
    full_name = request.form['full_name']
    mobile = request.form['mobile']
    email = request.form['email']
    insta = request.form['insta']
    facebook = request.form['facebook']

    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (full_name, mobile, email, insta, facebook) VALUES (?, ?, ?, ?, ?)',
                   (full_name, mobile, email, insta, facebook))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/save_order', methods=['POST'])
def save_order():
    order_id = request.form['order_id']
    product_name = request.form['product_name']
    size = request.form['size']
    color = request.form['color']
    price = request.form['price']
    customer_name = request.form['customer_name']
    mobile = request.form['mobile']
    address = request.form['address']
    payment = request.form['payment']
    status = request.form['status']
    otp = request.form['otp']

    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (order_id, product_name, size, color, price, customer_name, mobile, address, payment, status, otp, return_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order_id, product_name, size, color, price, customer_name, mobile, address, payment, status, otp, address))
    
    cursor.execute('UPDATE products SET stock = stock - 1 WHERE name = ? AND stock > 0', (product_name,))
    
    conn.commit()
    conn.close()
    return "OK"

@app.route('/verify_order_otp/<order_id>/<entered_otp>')
def verify_order_otp(order_id, entered_otp):
    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT otp FROM orders WHERE order_id = ?', (order_id,))
    row = cursor.fetchone()
    
    if row and row[0] == entered_otp:
        cursor.execute('UPDATE orders SET status = "3. Delivered & Completed" WHERE order_id = ?', (order_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        conn.close()
        return "<script>alert('❌ Incorrect OTP! Delivery could not be verified.'); window.location.href='/';</script>"

@app.route('/update_order_stage/<order_id>/<stage>/<location>')
def update_order_stage(order_id, stage, location):
    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ?, return_reason = ? WHERE order_id = ?', (stage, location, order_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/track/<order_id>')
def track(order_id):
    conn = sqlite3.connect('littlestar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT order_id, product_name, status, customer_name, payment, size, color, otp, return_reason FROM orders WHERE order_id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()
    if order:
        return {"success": True, "order_id": order[0], "product": order[1], "status": order[2], "name": order[3], "payment": order[4], "size": order[5], "color": order[6], "otp": order[7], "location": order[8]}
    else:
        return {"success": False}

if __name__ == '__main__':
    app.run()