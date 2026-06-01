#!/usr/bin/env python3
"""
Login Portal - TCP Forward Panel 前置认证网关
用户在登录页面认证后，反向代理到后端管理面板
"""
from flask import Flask, request, redirect, render_template_string, Response
import sqlite3, hashlib, secrets, os, urllib.request

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DB_FILE = "/root/login_portal.db"
DEFAULT_PORT = "8081"
DEFAULT_USER = "admin"
DEFAULT_PASS = "admin123"
TARGET_URL = "http://127.0.0.1:8080"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
    defaults = [
        ("port", DEFAULT_PORT),
        ("username", DEFAULT_USER),
        ("password", hashlib.sha256(DEFAULT_PASS.encode()).hexdigest()),
        ("target", TARGET_URL),
    ]
    for k, v in defaults:
        c.execute("INSERT OR IGNORE INTO config VALUES (?,?)", (k, v))
    conn.commit()
    conn.close()
init_db()

def get_config():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT key, value FROM config")
    rows = c.fetchall()
    conn.close()
    return dict(rows)

def check_auth(user, pwd):
    cfg = get_config()
    return user == cfg.get("username") and hashlib.sha256(pwd.encode()).hexdigest() == cfg.get("password")

from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login?next=" + request.path)
        return f(*args, **kwargs)
    return decorated

LOGIN_HTML = """
<!DOCTYPE html>
<html><head><meta charset=utf-8><title>\u767b\u5f55</title>
<style>
body{background:#0f172a;color:#f1f5f9;font-family:system-ui;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{background:#1e293b;border-radius:16px;padding:32px;width:360px;border:1px solid rgba(255,255,255,.1)}
h2{color:#d0daf0;font-weight:400;text-align:center;margin-bottom:24px}
input{width:100%;padding:10px 14px;margin:8px 0;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.3);color:#f1f5f9;font-size:14px;box-sizing:border-box}
button{width:100%;padding:10px;border-radius:8px;border:none;background:#667eea;color:white;font-size:14px;cursor:pointer;margin-top:12px}
.error{color:#f87171;font-size:13px;text-align:center;margin-top:8px}
</style></head><body>
<div class=card>
<h2>\u767b\u5f55</h2>
<form method=post>
<input name=username placeholder="\u8d26\u53f7" required>
<input name=password type=password placeholder="\u5bc6\u7801" required>
<button type=submit>\u767b\u5f55</button>
</form>
{% if error %}<div class=error>{{ error }}</div>{% endif %}
</div></body></html>
"""

SETTINGS_HTML = """
<!DOCTYPE html>
<html><head><meta charset=utf-8><title>\u8bbe\u7f6e</title>
<style>
body{background:#0f172a;color:#f1f5f9;font-family:system-ui;padding:20px;max-width:500px;margin:0 auto}
h2{color:#d0daf0;font-weight:400}
.card{background:#1e293b;border-radius:16px;padding:24px;border:1px solid rgba(255,255,255,.1);margin-bottom:16px}
label{font-size:13px;color:#94a3b8;display:block;margin-top:12px;margin-bottom:4px}
input{width:100%;padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.3);color:#f1f5f9;font-size:14px;box-sizing:border-box}
.btn{padding:8px 20px;border-radius:8px;border:none;background:#667eea;color:white;cursor:pointer;margin-top:12px}
.msg{color:#6ee7b7;font-size:13px;margin-top:8px}
a{color:#60a5fa;text-decoration:none;font-size:13px}
</style></head><body>
<a href="/">&larr; \u8fd4\u56de</a>
<h2>\u8bbe\u7f6e</h2>
<form method=post>
<div class=card>
<h3>\u767b\u5f55\u8bbe\u7f6e</h3>
<label>\u767b\u5f55\u7aef\u53e3</label>
<input name=port value="{{ port }}">
<label>\u8d26\u53f7</label>
<input name=username value="{{ username }}">
<label>\u5bc6\u7801</label>
<input name=password type=password placeholder="\u4e0d\u4fee\u6539\u5219\u7559\u7a7a">
<label>\u786e\u8ba4\u5bc6\u7801</label>
<input name=password2 type=password placeholder="\u518d\u6b21\u8f93\u5165">
<label>\u540e\u7aef\u9762\u677f\u5730\u5740</label>
<input name=target value="{{ target }}" placeholder="http://127.0.0.1:8080">
</div>
<button class=btn type=submit>\u4fdd\u5b58</button>
{% if msg %}<div class=msg>{{ msg }}</div>{% endif %}
</form></body></html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username", "")
        pwd = request.form.get("password", "")
        if check_auth(user, pwd):
            session["user"] = user
            next_url = request.args.get("next", "/")
            return redirect(next_url)
        return render_template_string(LOGIN_HTML, error="\u8d26\u53f7\u6216\u5bc6\u7801\u9519\u8bef")
    return render_template_string(LOGIN_HTML, error="")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    cfg = get_config()
    if request.method == "POST":
        new_port = request.form.get("port", "").strip()
        new_user = request.form.get("username", "").strip()
        new_pwd = request.form.get("password", "")
        new_pwd2 = request.form.get("password2", "")
        new_target = request.form.get("target", "").strip()
        msg = "\u5df2\u4fdd\u5b58"
        restart = False
        conn = sqlite3.connect(DB_FILE)
        
        if new_port and new_port.isdigit():
            conn.execute("INSERT OR REPLACE INTO config VALUES (?,?)", ("port", new_port))
            restart = True
        if new_user:
            conn.execute("INSERT OR REPLACE INTO config VALUES (?,?)", ("username", new_user))
            session["user"] = new_user
        if new_pwd and new_pwd == new_pwd2:
            conn.execute("INSERT OR REPLACE INTO config VALUES (?,?)", ("password", hashlib.sha256(new_pwd.encode()).hexdigest()))
        elif new_pwd:
            msg = "\u4e24\u6b21\u5bc6\u7801\u4e0d\u4e00\u81f4"
        if new_target:
            conn.execute("INSERT OR REPLACE INTO config VALUES (?,?)", ("target", new_target))
        
        conn.commit()
        conn.close()
        
        if restart:
            import subprocess as _sp
            _sp.Popen("(sleep 1; kill -9 " + str(os.getpid()) + ") &", shell=True)
            _sp.Popen("nohup python3 /root/login_portal.py >/dev/null 2>&1 ", shell=True)
            msg = "\u7aef\u53e3\u5df2\u4fee\u6539\uff0c\u8bf7\u5237\u65b0\u9875\u9762\u91cd\u65b0\u767b\u5f55"
        
        cfg = get_config()
        return render_template_string(SETTINGS_HTML, port=cfg.get("port", DEFAULT_PORT), username=cfg.get("username", ""), target=cfg.get("target", TARGET_URL), msg=msg)
    
    return render_template_string(SETTINGS_HTML, port=cfg.get("port", DEFAULT_PORT), username=cfg.get("username", ""), target=cfg.get("target", TARGET_URL), msg="")

@app.route("/")
@login_required
def index():
    cfg = get_config()
    target = cfg.get("target", TARGET_URL)
    return redirect(target)

@app.route("/proxy/<path:subpath>")
@login_required
def proxy(subpath):
    """\u53cd\u5411\u4ee3\u7406\u5230\u540e\u7aef\u9762\u677f"""
    cfg = get_config()
    target = cfg.get("target", TARGET_URL)
    try:
        url = target + "/" + subpath
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=10)
        content = resp.read()
        return Response(content, content_type=resp.headers.get("Content-Type", "text/html"))
    except Exception as e:
        target_url = target
        return f'<html><body><h2>\u540e\u7aef\u9762\u677f\u65e0\u6cd5\u8bbf\u95ee</h2><p>{e}</p><a href=/{target_url}>\u8df3\u8f6c\u5230\u540e\u7aef</a></body></html>'

if __name__ == "__main__":
    cfg = get_config()
    port = int(cfg.get("port", DEFAULT_PORT))
    app.run(host="0.0.0.0", port=port)
