import os
import json
import datetime
import requests
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from blood_detect import check_for_blood
import sqlite3
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder="../onboarding", static_url_path="/onboarding")
app.secret_key = os.getenv("ADMIN_SECRET_KEY", "sovereign_fallback_key_123")
CORS(app)

# --- CONFIGURATION ---
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "gaelf@example.com") 


# Knowledge path discovery
APPDATA_PATH = os.environ.get('APPDATA', '')
KI_PATH = os.path.join(APPDATA_PATH, 'antigravity', 'knowledge')
# Fallback search if above fails
if not os.path.exists(KI_PATH):
    potential_brain = os.path.join(APPDATA_PATH, 'antigravity', 'brain')
    if os.path.exists(potential_brain):
        KI_PATH = potential_brain

# --- DATA PATHS (Vault vs Public) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.join(BASE_DIR, 'vault')
DATA_ROOT = os.path.join(BASE_DIR, 'data')

# Intelligent toggle
IS_PRIVATE = os.path.exists(VAULT_DIR)
ACTIVE_ROOT = VAULT_DIR if IS_PRIVATE else DATA_ROOT

# Strict Absolute Path Construction (as recommended in frc79280)
DATA_DIR = os.path.abspath(os.path.join(ACTIVE_ROOT, "onboarding_submissions"))
UPLOAD_FOLDER = os.path.abspath(os.path.join(DATA_DIR, "media"))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# --- ACCESS TOKENS ---
def load_access_tokens():
    registry_path = os.path.join(ACTIVE_ROOT, 'access_tokens.json')
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

ACCESS_TOKENS = load_access_tokens()

# --- IDENTITY & ROLES ---
# Cloudflare Access transmits identity via 'Cf-Access-Authenticated-User-Email'
def get_user_identity():
    """Extracts user identity from Cloudflare headers, session, or token."""
    # 1. Cloudflare Identity
    cf_email = request.headers.get("Cf-Access-Authenticated-User-Email")
    if cf_email:
        return cf_email
    
    # 2. Token-based Identity (Magic Link)
    token = request.args.get("token") or session.get("auth_token")
    if token and token in ACCESS_TOKENS:
        token_data = ACCESS_TOKENS[token]
        session["user_email"] = token_data["email"]
        session["user_role"] = token_data["role"]
        session["auth_token"] = token
        return token_data["email"]

    # 3. Session-based Identity
    return session.get("user_email")

def get_user_role():
    """Determines user role based on email or token data."""
    identity = get_user_identity()
    if not identity:
        return "GUEST"
    
    # Check session/token role cache first
    if session.get("user_role"):
        return session.get("user_role")

    # Admin check for the master email
    if identity == ADMIN_EMAIL:
        return "ADMIN"
    
    # Everyone else with an identity is at least a READER
    return "READER"

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = get_user_role()
        if role == "GUEST":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_user_role() != "ADMIN":
            return jsonify({"error": "Forbidden", "message": "Admin privileges required."}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- SCOPE VALIDATION ---
def load_valid_scopes():
    valid = set()
    try:
        # Priority 1: Main Registry (vault-first)
        registry_p = os.path.join(ACTIVE_ROOT, 'campaign_registry.json')
        if os.path.exists(registry_p):
            with open(registry_p, 'r', encoding='utf-8') as f:
                reg = json.load(f)
                mappings = reg.get("mappings", {})
                for bid in mappings.keys():
                    clean_id = "".join([c for c in bid if c.isdigit()])
                    if clean_id: valid.add(clean_id)
        
        # Priority 2: Large Scanned List (data/ only - not sensitive)
        wa_list_p = os.path.join(DATA_ROOT, 'new_whatsapp_onboarding_list_v2.json')
        if os.path.exists(wa_list_p):
            with open(wa_list_p, 'r', encoding='utf-8') as f:
                large_list = json.load(f)
                for p in large_list:
                    name = p.get('name', '')
                    clean_id = "".join([c for c in name if c.isdigit()])
                    if clean_id: valid.add(clean_id)

        # Priority 3: Potential list (legacy, data/ only)
        pot_p = os.path.join(DATA_ROOT, 'potential_beneficiaries.json')
        if os.path.exists(pot_p):
            with open(pot_p, 'r', encoding='utf-8') as f:
                potential_data = json.load(f)
                for p in potential_data:
                    pid = p.get('name', p.get('id', ''))
                    clean_id = "".join([c for c in pid if c.isdigit()])
                    if clean_id: valid.add(clean_id)

        # Priority 4: Existing submissions (vault-first)
        submissions_dir = os.path.join(ACTIVE_ROOT, 'onboarding_submissions')
        if os.path.exists(submissions_dir):
            for fname in os.listdir(submissions_dir):
                if fname.endswith('_submission.json'):
                    bid = fname.replace('_submission.json', '')
                    clean_id = "".join([c for c in bid if c.isdigit()])
                    if clean_id: valid.add(clean_id)

    except Exception as e:
        print(f"Error loading scopes: {e}")
    return valid

VALID_SCOPES = load_valid_scopes()

def is_in_scope(identifier):
    if not identifier: return False
    clean_id = "".join([c for c in str(identifier) if c.isdigit()])
    
    # Check if pre-registered
    if clean_id in VALID_SCOPES:
        return True
        
    # RELAXED CHECK: If it's a Palestinian/Gaza number (+970 or +972 5...) allow viral onboarding
    if clean_id.startswith('970') or clean_id.startswith('972'):
        if len(clean_id) >= 10: # Basic length check
            return True
            
    return False

@app.route('/api/growth-list-save', methods=['POST'])
def save_growth_list_v2():
    try:
        data = request.json
        if not isinstance(data, list):
            return jsonify({"error": "Data must be a list"}), 400

        # --- NORMALIZE IDs before writing ---
        # Strip viral_+ from all IDs, set norm_whatsapp to clean phone digits
        import re as _re
        for camp in data:
            # Clean the whatsapp field (should be digits only)
            raw = str(camp.get('whatsapp') or '')
            clean_digits = _re.sub(r'\D', '', raw)
            if clean_digits:
                camp['whatsapp'] = clean_digits

            # Derive norm_whatsapp: prefix + clean digits (strip leading 0 for trunk numbers)
            prefix = (camp.get('whatsapp_prefix') or '').strip()
            prefix_digits = _re.sub(r'\D', '', prefix)
            # Strip leading 0 from trunk-format numbers (e.g. 0599... → 599...)
            base_digits = clean_digits.lstrip('0') if clean_digits.startswith('0') else clean_digits
            if base_digits and prefix_digits:
                if base_digits.startswith(prefix_digits):
                    # Already has country code embedded
                    camp['norm_whatsapp'] = '+' + base_digits
                else:
                    camp['norm_whatsapp'] = '+' + prefix_digits + base_digits
            elif base_digits:
                camp['norm_whatsapp'] = base_digits

            # Strip viral_+ from bids array
            if 'bids' in camp and isinstance(camp['bids'], list):
                camp['bids'] = [
                    b.replace('viral_+', '').replace('viral_', '') for b in camp['bids']
                ]

            # Strip viral_+ from bid field
            if 'bid' in camp and isinstance(camp['bid'], str):
                camp['bid'] = camp['bid'].replace('viral_+', '').replace('viral_', '')

        # Vault-first: save to active root (vault/ in private mode, data/ in demo mode)
        save_path = os.path.join(ACTIVE_ROOT, 'UNIFIED_REGISTRY.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Regenerate onboarding_messages.txt with the corrected live data
        try:
            _regenerate_onboarding_messages(data)
        except Exception as regen_err:
            print(f"[WARN] Message regeneration failed: {regen_err}")

        return jsonify({"status": "success", "saved_to": "vault" if IS_PRIVATE else "demo"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _regenerate_onboarding_messages(campaigns):
    import re as _re
    import json
    
    # Default fallbacks
    PORTAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/onboarding/"
    VIRAL_URL  = "https://dours-d.github.io/local-ai-campaign-assistant/"
    NOOR_URL   = "https://dours-d.github.io/local-ai-campaign-assistant/brain.html"

    # Dynamic resolve from status.json (Priority)
    try:
        status_path = os.path.join(BASE_DIR, 'data', 'status.json')
        if os.path.exists(status_path):
            with open(status_path, 'r') as f:
                status_data = json.load(f)
                server_url = status_data.get('services', {}).get('onboarding_server', {}).get('public_url')
                if server_url:
                    server_url = server_url.rstrip('/')
                    PORTAL_URL = f"{server_url}"
                    VIRAL_URL  = f"{server_url}/"
                    NOOR_URL   = f"{server_url}/brain"
                    print(f"[AUTO] Using dynamic tunnel URL for messages: {server_url}")
    except Exception as e:
        print(f"[WARN] Failed to resolve dynamic tunnel URL: {e}")

    # Load USDT addresses from vault
    vault_addresses = {}
    try:
        from sovereign_vault import SovereignVault
        vault = SovereignVault()
        for key, val in vault.mapping.items():
            addr = val.get('address')
            if addr:
                clean = _re.sub(r'\D', '', str(key))
                if clean:
                    vault_addresses[clean] = addr
                    vault_addresses[clean[-9:]] = addr
    except Exception:
        pass

    messages_path = os.path.join(BASE_DIR, 'onboarding_messages.txt')

    # Always build from scratch — no stale blocks preserved.
    # The prefix token selection on the portal must drive ALL links.
    existing_blocks = {}

    for camp in campaigns:
        # --- FIELD RESOLUTION ---
        raw_phone = str(camp.get('whatsapp') or camp.get('norm_whatsapp') or
                        camp.get('bid') or (camp.get('bids') or [None])[0] or '')
        if not raw_phone:
            continue

        # Prefix chosen on the page
        prefix = (camp.get('whatsapp_prefix') or '').strip()
        # Strip leading 0 from trunk numbers before applying prefix
        digits_only = _re.sub(r'\D', '', raw_phone)
        base_digits = digits_only.lstrip('0') if digits_only.startswith('0') else digits_only

        if prefix and base_digits:
            prefix_digits = _re.sub(r'\D', '', prefix)
            if base_digits.startswith(prefix_digits):
                full_phone = '+' + base_digits
            else:
                full_phone = '+' + prefix_digits + base_digits
        else:
            full_phone = base_digits or digits_only

        # Universal match key (last 9 digits)
        l9_key = base_digits[-9:] if len(base_digits) >= 9 else base_digits

        # Block header ID (clean)
        block_id = full_phone if prefix else base_digits

        # Tracking ID (digits only, no prefix)
        tracking_id = base_digits

        # Sovereign Portal link
        portal_link = f"{PORTAL_URL}/onboard/{full_phone}"

        # Identity name stamped from client
        identity_name = (
            camp.get('identity_name') or
            camp.get('registry_name') or
            base_digits or
            'Resilient Family'
        )

        # Sovereign Portal link uses the full phone (with prefix)
        portal_link = f"{PORTAL_URL}/onboard/{full_phone}"

        # USDT wallet
        address = (
            camp.get('usdt_address') or
            vault_addresses.get(digits_only) or
            vault_addresses.get(digits_only[-9:]) or
            '[WALLET_PENDING]'
        )

        personal_wd = (camp.get('whydonate_url') or '').strip() or None

        # --- MESSAGE BODY ---
        if personal_wd:
            ar  = f"{full_phone}\n"
            ar += f"السلام عليكم ورحمة الله وبركاته، {identity_name}.\n\n"
            ar += f"حملتكم الآن أمانة (Amanah) مفعلة! إليك أدواتكم:\n\n"
            ar += f"1️⃣ **رابط النافذة المباشرة (Direct Window)**:\n{personal_wd}\n"
            ar += f"استخدموا هذا الرابط لمشاركة قصتكم مع العالم وبدء جمع التبرعات مباشرة.\n\n"
            ar += f"2️⃣ **رابط الدرع الجماعي (Collective Shield)**:\n{VIRAL_URL}\n"
            ar += f"اطلبو من المتبرعين كتابة الـ ID الخاص بكم: **{tracking_id}** في الملاحظات.\n\n"
            ar += f"💰 **محفظتكم السيادية (USDT)**:\n{address}\n\n"
            ar += f"🌍 **بوابة 'نور' المعرفية**: {NOOR_URL}\n"

            en  = f"Salam Alaykum, {identity_name}.\n\n"
            en += f"Your campaign is now a live Amanah! Use these links:\n\n"
            en += f"1. **Your Direct Window**:\n{personal_wd}\n\n"
            en += f"2. **Collective Shield**:\n{VIRAL_URL}\n"
            en += f"Ask donors to include ID: **{tracking_id}** for transparent tracking.\n\n"
            en += f"💰 **Your Sovereign Wallet**:\n{address}\n\n"
            en += f"🌍 **Noor Knowledge Portal**: {NOOR_URL}\n"
        else:
            ar  = f"{full_phone}\n"
            ar += f"السلام عليكم ورحمة الله وبركاته، {identity_name}.\n\n"
            ar += f"نحن هنا لنكون شهوداً (Shahada) على صمودكم، ولتفعيل أمانتكم (Amanah).\n\n"
            ar += f"🛠 **بوابة التعديل السيادي**:\n{portal_link}\n\n"
            ar += f"💰 **محفظتكم السيادية (USDT)**:\n{address}\n\n"
            ar += f"🔗 **رابط الصندوق الموحد**: {VIRAL_URL}\n"
            ar += f"اذكروا الـ ID الخاص بكم: {tracking_id} في رسالة المتبرع.\n\n"
            ar += f"🌍 **بوابة 'نور' المعرفية**: {NOOR_URL}\n"

            en  = f"Salam Alaykum.\n\n"
            en += f"We are establishing your sacred Trust (Amanah). Step 1: verify your data.\n\n"
            en += f"🛠 **Sovereign Portal**:\n{portal_link}\n\n"
            en += f"💰 **Digital Wallet (USDT)**:\n{address}\n\n"
            en += f"🔗 **Umbrella Fund**:\n{VIRAL_URL}\n"
            en += f"Donors: include ID: {tracking_id}\n\n"
            en += f"🌍 **Noor Knowledge Portal**: {NOOR_URL}\n"

        full_msg = ar + "\n" + "-"*30 + "\n\n" + en
        # Store with l9_key so it overwrites any old dirty entry, using clean block_id as header
        existing_blocks[l9_key] = (block_id, full_msg + "\n")

    # Write all blocks: each value is (header_id, body)
    output = ""
    for _key, val in existing_blocks.items():
        if isinstance(val, tuple):
            hdr, body = val
        else:
            hdr, body = _key, val  # fallback for any legacy entry
        output += f"--- MESSAGE FOR {hdr} ---\n{body}\n"
    with open(messages_path, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"[OK] onboarding_messages.txt regenerated ({len(existing_blocks)} entries)")


@app.route('/api/growth-list', methods=['GET'])
def handle_growth_list():
    """Gets or updates the verified unified growth list."""
    try:
        registry_path = os.path.join(ACTIVE_ROOT, 'UNIFIED_REGISTRY.json')
        if os.path.exists(registry_path):
            with open(registry_path, 'r', encoding='utf-8') as f:
                campaigns = json.load(f)
            return jsonify(campaigns)
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Lightweight endpoint for watchdog pings."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "tunnel_url": request.host_url
    })

# --- SUBMISSION LOOKUP ---
# --- SUBMISSION LOOKUP (Formal Database) ---
DB_PATH = os.path.join(ACTIVE_ROOT, 'submissions.db')

@app.route('/api/submissions/<path:phone_id>')
def get_submissions(phone_id):
    """Return all submission data for a campaign from the local formal database."""
    import re as _re
    if not phone_id or phone_id.strip() == "":
        return jsonify([])

    lookup_digits = _re.sub(r'\D', '', phone_id)
    if not lookup_digits:
        return jsonify([])
        
    l9 = lookup_digits[-9:] if len(lookup_digits) >= 9 else lookup_digits

    results = []
    if not os.path.exists(DB_PATH):
        return jsonify([])

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Match by last 9 digits or full bid
        query = "SELECT * FROM submissions WHERE bid LIKE ? OR bid = ? OR whatsapp LIKE ?"
        cursor.execute(query, (f"%{l9}", lookup_digits, f"%{l9}"))
        rows = cursor.fetchall()
        
        for row in rows:
            results.append({
                'bid':           row['bid'],
                'title':         row['title'],
                'story':         row['story'],
                'images':        json.loads(row['media_json']),
                'local_paths':   json.loads(row['media_paths_json']) if 'media_paths_json' in row.keys() else [],
                'image_urls':    [f"/media/{row['bid']}/{os.path.basename(p)}" for p in json.loads(row['media_paths_json'])] if 'media_paths_json' in row.keys() else [],
                'source':        'formal_db',
                'timestamp':     ''
            })
        conn.close()
    except Exception as e:
        print(f"[ERR] DB Query failed: {e}")

    return jsonify(results)

# Local media serving route RESTORED for Confidential Base64 Database mode + Local Destination support.
@app.route('/media/<path:filepath>')
def serve_media(filepath):
    """Serve a local image from the secure vault/media directory."""
    # Ensure filepath is just the filename or relative to MEDIA_DIR
    fname = os.path.basename(filepath)
    # Search for the file in the vault media subdirectories
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        if fname in files:
            return send_from_directory(root, fname)
    return "Media not found", 404

# --- DOLÉANCES (TRUST COMPLAINTS) ---
@app.route('/api/dolances', methods=['POST'])
def submit_dolance():
    """Receive a complaint/grievance about the Trust. Identifier is optional."""
    try:
        data = request.json or {}
        text = (data.get('text') or '').strip()
        if not text:
            return jsonify({"error": "Complaint text is required"}), 400

        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "text": text,
            "identifier": (data.get('identifier') or '').strip() or None,
            "ip": request.remote_addr
        }

        dolances_path = os.path.join(ACTIVE_ROOT, 'dolances.json')
        records = []
        if os.path.exists(dolances_path):
            try:
                with open(dolances_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except Exception:
                records = []
        records.append(entry)
        with open(dolances_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        print(f"[DOLANCE] {entry['timestamp']} | id={entry['identifier']} | {text[:60]}")
        return jsonify({"status": "recorded", "anonymous": entry['identifier'] is None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dolances', methods=['GET'])
def get_dolances():
    """Admin: retrieve all recorded complaints."""
    dolances_path = os.path.join(ACTIVE_ROOT, 'dolances.json')
    if not os.path.exists(dolances_path):
        return jsonify([])
    with open(dolances_path, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

# --- AUTH ROUTES ---
@app.route('/login', methods=['POST'])
def login():
    """Manual login for local testing or non-Cloudflare access."""
    data = request.json
    password = data.get("password")
    
    if password == ADMIN_PASSWORD:
        session["user_email"] = ADMIN_EMAIL
        session["logged_in"] = True
        print(f"Login Successful for {ADMIN_EMAIL}")
        # Return status and role for the injection script to verify
        return jsonify({"status": "success", "role": "ADMIN", "user": ADMIN_EMAIL}), 200
    
    print(f"Login Failed. Received: {password}")
    return jsonify({"error": "Invalid Credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success"}), 200

@app.route('/api/whoami')
def whoami():
    return jsonify({
        "email": get_user_identity(),
        "role": get_user_role()
    })

# --- KNOWLEDGE (SHARED BRAIN) ROUTES ---
@app.route('/api/knowledge', methods=['GET'])
# @login_required - Public Access Enabled for Transparency
def list_knowledge():
    """Lists available Knowledge Items (Distilled Intelligence)."""
    if not os.path.exists(KI_PATH):
        return jsonify({"error": "Knowledge path not found", "path": KI_PATH}), 404
    
    ki_list = []
    # Walk through folders in knowledge/brain
    for ki_dir in os.listdir(KI_PATH):
        ki_full_path = os.path.join(KI_PATH, ki_dir)
        if not os.path.isdir(ki_full_path): continue
        
        metadata_path = os.path.join(ki_full_path, 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                try:
                    meta = json.load(f)
                    ki_list.append({
                        "id": ki_dir,
                        "title": meta.get("title", ki_dir),
                        "summary": meta.get("summary", ""),
                        "created": meta.get("created_at")
                    })
                except:
                    continue
    return jsonify(ki_list)

@app.route('/api/knowledge/<ki_id>', methods=['GET'])
# @login_required - Public Access Enabled
def get_knowledge_item(ki_id):
    """Reads a specific Knowledge Item's distilled artifacts."""
    ki_base = os.path.join(KI_PATH, secure_filename(ki_id))
    artifacts_path = os.path.join(ki_base, 'artifacts')
    
    if not os.path.exists(artifacts_path):
        # Check if requested ID is actually in the base folder
        artifacts_path = ki_base 
        if not os.path.exists(artifacts_path):
            return jsonify({"error": "Knowledge Item not found"}), 404
    
    content = []
    # Only allow reading markdown and text files for the collective
    for file in os.listdir(artifacts_path):
        if file.endswith('.md') or file.endswith('.txt'):
            file_path = os.path.join(artifacts_path, file)
            if os.path.isdir(file_path): continue
            with open(file_path, 'r', encoding='utf-8') as f:
                content.append({
                    "name": file,
                    "content": f.read()
                })
    return jsonify(content)

# --- THE VOICE: AI CHAT ---
@app.route('/api/chat', methods=['POST'])
# @login_required - Public Access Enabled
def chat_with_brain():
    """AI Chat specialized in project knowledge with Hybrid Relay & Awareness."""
    data = request.json
    user_query = data.get("query", "")
    mode = data.get("mode", "local") # "local" or "relay"
    
    if not user_query:
        return jsonify({"error": "Empty Query"}), 400

    # 1. Build Context from Knowledge Items
    context = ""
    try:
        active_ki_path = KI_PATH if os.path.exists(KI_PATH) else 'docs/ki_archive'
        for ki_folder in os.listdir(active_ki_path):
            ki_base = os.path.join(active_ki_path, ki_folder)
            if not os.path.isdir(ki_base): continue
            
            arts_path = os.path.join(ki_base, 'artifacts') if os.path.exists(os.path.join(ki_base, 'artifacts')) else ki_base
            for file in os.listdir(arts_path):
                if file.endswith('.md'):
                    with open(os.path.join(arts_path, file), 'r', encoding='utf-8') as f:
                        context += f"\n--- DOCUMENT: {file} ---\n{f.read()}\n"
    except Exception as e:
        print(f"Chat Context Error: {e}")

    # 2. Add Hybrid Awareness (Make Gemma aware of Groq history)
    relay_history = ""
    try:
        sync_file = 'data/relay_conversations.json'
        if os.path.exists(sync_file):
            with open(sync_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                relay_history = "\n--- PAST HYBRID RELAY CONVERSATIONS (Amanah Context) ---\n"
                for entry in history[-5:]: # Last 5 for context
                    relay_history += f"[{entry.get('timestamp')}] {entry.get('content')}\n"
    except: pass

    full_context = context + relay_history
    prompt = f"SYSTEM: You are 'Noor', the sovereign intelligence of the Gaza Resilience project. Answer based ONLY on context below.\n\nCONTEXT:\n{full_context[:12000]}\n\nUSER: {user_query}"

    # 3. Local Execution (Gemma 3)
    if mode == "local":
        try:
            res = requests.post('http://127.0.0.1:11434/api/generate', 
                json={"model": "gemma3:latest", "prompt": prompt, "stream": False}, timeout=30)
            if res.ok:
                return jsonify({"response": res.json().get("response"), "source": "local_gemma"})
        except Exception as e:
            print(f"Local AI Failure: {e}")
            return jsonify({"error": "Local Model heartbeat flatlined. Switch to Relay mode."}), 503

    # 4. Relay Execution (Groq - Llama 3 70B)
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            res = requests.post('https://api.groq.com/openai/v1/chat/completions', 
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are 'Noor', the sovereign intelligence of the Gaza Resilience project. Use the provided context to answer precisely."}, 
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                }, timeout=15)
            if res.ok:
                ai_text = res.json()['choices'][0]['message']['content']
                
                # Log for Gemma's future awareness
                try:
                    sync_file = 'data/relay_conversations.json'
                    convos = []
                    if os.path.exists(sync_file):
                        with open(sync_file, 'r', encoding='utf-8') as f:
                            try: convos = json.load(f)
                            except: pass
                    
                    convos.append({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "content": f"USER: {user_query}\nNOOR [Relay]: {ai_text}"
                    })
                    
                    os.makedirs('data', exist_ok=True)
                    with open(sync_file, 'w', encoding='utf-8') as f:
                        json.dump(convos, f, indent=2)
                except: pass

                return jsonify({"response": ai_text, "source": "hybrid_relay_groq"})
        except Exception as e:
            return jsonify({"error": "Hybrid Relay connection lost.", "details": str(e)}), 503

    return jsonify({"error": "No relay available. Authenticate the local brain or provide a Relay Key."}), 503

# --- INTAKE ROUTES ---
@app.route('/')
@app.route('/index.html')
@app.route('/onboard')
@app.route('/onboard/<beneficiary_id>')
def serve_portal(beneficiary_id=None):
    return app.send_static_file('index.html')

@app.route('/brain')
def serve_brain():
    return app.send_static_file('brain.html')

@app.route('/mgmt')
def mgmt_root():
    from flask import redirect, url_for
    return redirect('/mgmt/content_list.html')

@app.route('/mgmt/<path:path>')
def serve_mgmt(path):
    from flask import send_from_directory
    return send_from_directory('../frontend', path)

@app.route('/api/check_scope/<beneficiary_id>')
def check_scope(beneficiary_id):
    return jsonify({"in_scope": is_in_scope(beneficiary_id)})

@app.route('/api/onboarding-template')
def get_onboarding_template():
    template_path = os.path.join(DATA_ROOT, 'standard_beneficiary_onboarding.txt')
    if not os.path.exists(template_path):
        template_path = os.path.join(ACTIVE_ROOT, 'standard_beneficiary_onboarding.txt')
        
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    return "Template not found", 404

@app.route('/api/onboarding-message/<beneficiary_id>')
def get_onboarding_message(beneficiary_id):
    """Look up the pre-generated full message for a beneficiary from onboarding_messages.txt."""
    msg_file = os.path.join(BASE_DIR, 'onboarding_messages.txt')
    if not os.path.exists(msg_file):
        msg_file = os.path.join(ACTIVE_ROOT, 'onboarding_messages.txt')

    if not os.path.exists(msg_file):
        return "Message file not found", 404

    with open(msg_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize the lookup ID (strip +, viral_ prefixes for matching)
    lookup_id = beneficiary_id.replace('viral_', '').replace('+', '').strip()
    
    # Split on message separators
    import re
    blocks = re.split(r'--- MESSAGE FOR (.+?) ---', content)
    
    # blocks[0] = text before first message, then alternating [id, message_body, id, message_body...]
    for i in range(1, len(blocks), 2):
        block_id = blocks[i].strip()
        block_body = blocks[i+1] if i+1 < len(blocks) else ''
        
        # Normalize block_id the same way for comparison
        normalized_block_id = block_id.replace('viral_', '').replace('+', '').strip()
        
        if normalized_block_id == lookup_id:
            # Return the whole block including the header line
            full_msg = f"--- MESSAGE FOR {block_id} ---\n{block_body.rstrip()}"
            return full_msg, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    return f"No message found for ID: {beneficiary_id}", 404


@app.route('/submission/<beneficiary_id>', methods=['GET'])
@admin_required # Strict PII protection
def get_submission(beneficiary_id):
    json_path = os.path.join(DATA_DIR, f"{beneficiary_id}_submission.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f)), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    beneficiary_id = request.form.get('beneficiary_id', 'unknown')
    whatsapp_number = request.form.get('whatsapp_number', '').strip()
    
    clean_id = "".join([c for c in beneficiary_id if c.isdigit()])
    clean_wa = "".join([c for c in whatsapp_number if c.isdigit()])
    
    is_id_known = is_in_scope(clean_id) if clean_id else (not beneficiary_id.isdigit() and beneficiary_id not in ['unknown', 'onboard', 'index.html', ''])
    is_wa_known = is_in_scope(clean_wa) if clean_wa else False

    if not is_id_known and not is_wa_known:
        return jsonify({"error": "Out of Scope"}), 403

    if beneficiary_id in ['unknown', 'onboard', 'index.html', '']:
        if clean_wa:
            beneficiary_id = f"viral_{clean_wa}"
        else:
            return jsonify({"error": "Missing WhatsApp"}), 400

    submission_data = {
        "beneficiary_id": beneficiary_id,
        "whatsapp_number": whatsapp_number,
        "title": request.form.get('title', ''),
        "story": request.form.get('story', ''),
        "display_name": request.form.get('display_name', ''),
        "personal_wallet": request.form.get('personal_wallet', ''),
        "files": [],
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    files = request.files.getlist('files')
    beneficiary_folder = os.path.join(app.config['UPLOAD_FOLDER'], beneficiary_id)
    os.makedirs(beneficiary_folder, exist_ok=True)
    
    for file in files:
        if file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(beneficiary_folder, filename)
            file.save(file_path)
            
            is_flagged, blood_density = check_for_blood(file_path)
            submission_data["files"].append({
                "path": file_path,
                "is_flagged": bool(is_flagged),
                "blood_density": float(blood_density)
            })
    
    os.makedirs(DATA_DIR, exist_ok=True)
    json_path = os.path.join(DATA_DIR, f"{beneficiary_id}_submission.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(submission_data, f, indent=2)
    
    return jsonify({"status": "success", "beneficiary_id": beneficiary_id}), 201

@app.route('/api/publish-pulse', methods=['POST'])
def publish_pulse():
    """Admin Only: Inject a synthesized vertical pulse video into the portal assets."""
    # Ensure admin role via identity/session
    if get_user_role() != "ADMIN":
        return jsonify({"error": "Unauthorized", "message": "Requires Admin protocol access."}), 403

    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400
        
    file = request.files['file']
    if not file or not file.filename.endswith('.mp4'):
        return jsonify({"error": "Invalid file type. Only .mp4 allowed."}), 400

    # Public assets directory (serving from frontend/assets/pulses)
    public_pulse_dir = os.path.join(BASE_DIR, 'frontend', 'assets', 'pulses')
    os.makedirs(public_pulse_dir, exist_ok=True)
    
    filename = secure_filename(file.filename)
    save_path = os.path.join(public_pulse_dir, filename)
    file.save(save_path)
    
    # Track the pulse in a manifest for the UI to consumption
    manifest_path = os.path.join(public_pulse_dir, 'manifest.json')
    manifest = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except: manifest = []
        
    manifest.append({
        "filename": filename,
        "timestamp": datetime.datetime.now().isoformat(),
        "url": f"/assets/pulses/{filename}"
    })
    
    # Keep only the last 20 pulses to preserve bandwidth/storage
    manifest = manifest[-20:]
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        
    return jsonify({"status": "published", "url": f"/assets/pulses/{filename}"}), 201

@app.route('/api/translate', methods=['POST'])
def translate_arabic():
    data = request.json or {}
    text = (data.get('text') or '').strip()
    mode = data.get('mode', 'title')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # If title looks like a URL, resolve slug first
    is_url = False
    lower_text = text.lower()
    if mode == 'title' and ('http' in lower_text or 'chuffed.org' in lower_text or '.com' in lower_text):
        if '|' not in text: # Only extract if not already bilingual
            is_url = True
            slug = text.split('/')[-1].split('?')[0].replace('-', ' ').replace('_', ' ')
            if not slug.isdigit():
                text = slug.title()

    groq_key = os.getenv('GROQ_API_KEY', '')
    
    # Strict language detection
    has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
    
    # Check for existing bilingual format and normalize Ar | En -> En | Ar
    # Handle potentially incomplete splits (e.g. "Title | ")
    parts = [p.strip() for p in text.split('|') if p.strip()]
    if len(parts) >= 2:
        p1_ar = any('\u0600' <= char <= '\u06FF' for char in parts[0])
        p2_ar = any('\u0600' <= char <= '\u06FF' for char in parts[1])
        # If it's already bilingual and correctly ordered, return as is
        if not p1_ar and p2_ar:
            return jsonify({'translation': parts[0], 'bilingual': text, 'detected': 'mixed'})
        # Re-order if needed
        english = parts[1] if p1_ar and not p2_ar else parts[0]
        arabic = parts[0] if p1_ar and not p2_ar else parts[1]
        return jsonify({'translation': english, 'bilingual': f"{english} | {arabic}", 'detected': 'mixed'})

    if not groq_key or groq_key.startswith('your_'):
        # Best effort for URL titles if no API key
        if is_url:
            return jsonify({'translation': text, 'bilingual': f"{text} | [ترجمة معلقة]", 'detected': 'en'})
        return jsonify({'error': 'No valid Groq API key configured'}), 500

    system_prompt = (
        "You are a precise Arabic-English translator for Palestinian humanitarian campaigns. "
        "Keep it natural, compassionate, and concise. "
        "Return ONLY the translated text — no explanations, no notes."
    )
    
    target_lang = "English" if has_arabic else "Arabic"
    user_prompt = f"Translate this campaign {mode} to {target_lang}:\n{text}"

    try:
        resp = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'},
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'max_tokens': 400,
                'temperature': 0.3
            },
            timeout=20
        )
        resp.raise_for_status()
        translation = resp.json()['choices'][0]['message']['content'].strip()
        
        if mode == 'title':
            english = text if not has_arabic else translation
            arabic = translation if not has_arabic else text
            combined = f"{english} | {arabic}"
            if len(combined) > 160:
                combined = combined[:157] + "..."
            return jsonify({'translation': translation, 'bilingual': combined, 'detected': 'ar' if has_arabic else 'en'})
        else:
            arabic = text if has_arabic else translation
            english = translation if has_arabic else text
            combined = f"{english}\n\n---\n\n{arabic}"
            return jsonify({'translation': translation, 'bilingual': combined, 'detected': 'ar' if has_arabic else 'en'})
            
    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code
        err_msg = f"Groq API Error ({status_code}): {http_err.response.text}"
        print(f"[ERR] {err_msg}")
        return jsonify({'error': err_msg}), status_code
    except Exception as e:
        print(f"[ERR] Translation unexpected error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    msg = "DUNYA دنيا Sovereign Intelligence starting on http://0.0.0.0:5010"
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'ignore').decode('ascii'))
    app.run(host='0.0.0.0', port=5010)
