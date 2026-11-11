from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sqlalchemy import create_engine, text
import pymysql

app = Flask(__name__)
CORS(app)

# MySQL Config - Tumcha password 1234
DB_URL = "mysql+mysqlconnector://root:1234@127.0.0.1:3306/crop_price_db"
engine = create_engine(DB_URL)

# Marathi-English Mix Registration Form HTML
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>🌾 शेतकरी नोंदणी | Farmer Registration</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #F1F8E9; margin:0; padding:20px; }
        .container { max-width:600px; margin:auto; background:white; padding:25px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1); border-top:5px solid #1B5E20; }
        h2 { color:#1B5E20; text-align:center; }
        label { font-weight:600; color:#2E7D32; display:block; margin-top:15px; }
        input, select { width:100%; padding:10px; margin-top:5px; border:1px solid #C8E6C9; border-radius:8px; }
        .checks { display:flex; flex-wrap:wrap; gap:10px; margin-top:5px; }
        .checks label { font-weight:400; color:#212121; background:#E8F5E9; padding:5px 10px; border-radius:6px; }
        button { width:100%; margin-top:20px; background:#1B5E20; color:white; padding:12px; border:none; border-radius:8px; font-size:16px; cursor:pointer; }
        button:hover { background:#2E7D32; }
        .msg { margin-top:15px; padding:10px; border-radius:8px; text-align:center; display:none; }
        .success { background:#C8E6C9; color:#1B5E20; }
        .error { background:#FFCDD2; color:#C62828; }
    </style>
</head>
<body>
<div class="container">
    <h2>🌾 शेतकरी नोंदणी करा</h2>
    <p style="text-align:center; color:#666;">Register for Daily Crop Price SMS/Email Alerts</p>
    <form id="regForm">
        <label>नाव / Name *</label>
        <input type="text" id="farmer_name" required placeholder="Amar Prajapati">
        
        <label>मोबाईल / Mobile (10 digit) *</label>
        <input type="text" id="mobile_number" required pattern="[0-9]{10}" placeholder="8551003989">
        
        <label>Email (optional)</label>
        <input type="email" id="email_id" placeholder="amar@gmail.com">
        
        <label>जिल्हा / District *</label>
        <select id="district" required>
            <option value="">-- निवडा --</option>
            <option>Nashik</option><option>Latur</option><option>Jalgaon</option><option>Aurangabad</option><option>Solapur</option><option>Amravati</option><option>Dhule</option><option>Kolhapur</option><option>Nanded</option><option>Pune</option>
        </select>
        
        <label>आवडीची पिके / Preferred Crops *</label>
        <div class="checks">
            <label><input type="checkbox" value="Onion"> Onion</label>
            <label><input type="checkbox" value="Tomato"> Tomato</label>
            <label><input type="checkbox" value="Soybean"> Soybean</label>
            <label><input type="checkbox" value="Cotton"> Cotton</label>
            <label><input type="checkbox" value="Gram"> Gram</label>
        </div>
        
        <label>आवडीची बाजारपेठ / Preferred Market</label>
        <select id="preferred_market">
            <option value="">-- निवडा --</option>
            <option>Lasalgaon</option><option>Pimpalgaon</option><option>Nanded</option><option>Latur</option><option>Jalgaon</option><option>Aurangabad</option><option>Solapur</option><option>Amravati</option><option>Dhule</option><option>Kolhapur</option>
        </select>
        
        <label>Alert कसा हवा? *</label>
        <select id="alert_type" required>
            <option value="BOTH">SMS + Email (BEST)</option>
            <option value="SMS">SMS Only</option>
            <option value="EMAIL">Email Only</option>
        </select>
        
        <button type="submit">✅ नोंदणी करा / Register</button>
    </form>
    <div id="msg" class="msg"></div>
    <p style="text-align:center; margin-top:15px; font-size:12px; color:#888;">Maharashtra Crop Price Prediction | Daily 8 AM Alerts | ML 97.5% Accuracy</p>
</div>
<script>
document.getElementById('regForm').onsubmit = async (e) => {
    e.preventDefault();
    const crops = Array.from(document.querySelectorAll('.checks input:checked')).map(c=>c.value).join(',');
    if(!crops){ alert('Ek tari pik nivda!'); return; }
    const data = {
        farmer_name: document.getElementById('farmer_name').value,
        mobile_number: document.getElementById('mobile_number').value,
        email_id: document.getElementById('email_id').value || null,
        district: document.getElementById('district').value,
        preferred_crops: crops,
        preferred_market: document.getElementById('preferred_market').value || null,
        alert_type: document.getElementById('alert_type').value
    };
    const res = await fetch('/api/register', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
    const j = await res.json();
    const msg = document.getElementById('msg');
    msg.style.display='block';
    if(j.status=='success'){ msg.className='msg success'; msg.innerText='✅ नोंदणी यशस्वी! Registration Successful!'; e.target.reset(); }
    else { msg.className='msg error'; msg.innerText='❌ Error: '+(j.message||'Failed'); }
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_FORM)

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        # Validation
        if not data.get('farmer_name') or not data.get('mobile_number'):
            return jsonify({"status":"error","message":"Name and Mobile required"}),400
        if len(data['mobile_number'])!=10 or not data['mobile_number'].isdigit():
            return jsonify({"status":"error","message":"Mobile must be 10 digits"}),400
        
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO farmer_contacts (farmer_name, mobile_number, email_id, district, preferred_crops, preferred_market, alert_type)
                VALUES (:farmer_name, :mobile_number, :email_id, :district, :preferred_crops, :preferred_market, :alert_type)
                ON DUPLICATE KEY UPDATE farmer_name=:farmer_name, email_id=:email_id, district=:district, preferred_crops=:preferred_crops, preferred_market=:preferred_market, alert_type=:alert_type, is_active=1
            """), data)
            conn.commit()
        return jsonify({"status":"success","message":"Registered"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500

@app.route('/api/farmers', methods=['GET'])
def list_farmers():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT farmer_name, mobile_number, district, preferred_crops, preferred_market, alert_type, registered_date FROM farmer_contacts WHERE is_active=1 ORDER BY registered_date DESC")).fetchall()
        data = [dict(r._mapping) for r in rows]
        return jsonify(data)

if __name__ == '__main__':
    print("🌾 Farmer Registration Portal Running at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
