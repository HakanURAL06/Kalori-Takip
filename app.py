from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.jinja_env.add_extension('jinja2.ext.do')

# --- KLASÖR VE DOSYA AYARLARI ---
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def baglan():
    conn = sqlite3.connect('kalori_takip.db')
    conn.row_factory = sqlite3.Row 
    return conn

def veritabani_kur():
    conn = baglan()
    # 1. Ayarlar (Hedef Kalori)
    conn.execute('CREATE TABLE IF NOT EXISTS ayarlar (id INTEGER PRIMARY KEY, hedef_kalori REAL)')
    if conn.execute('SELECT count(*) FROM ayarlar').fetchone()[0] == 0:
        conn.execute('INSERT INTO ayarlar (hedef_kalori) VALUES (2000)')
    
    # 2. Türler (Kategoriler) 
    conn.execute('CREATE TABLE IF NOT EXISTS turler (id INTEGER PRIMARY KEY AUTOINCREMENT, tur_adi TEXT, pixel_ikon_yolu TEXT)')
    
    # 3. Ürünler 
    conn.execute('''CREATE TABLE IF NOT EXISTS urunler (
        id INTEGER PRIMARY KEY AUTOINCREMENT, marka_isim TEXT,
        kalori REAL, protein REAL, yag REAL, karbonhidrat REAL, seker REAL, lif REAL, tuz REAL,
        foto_yolu TEXT)''')
    
    # 4. Bağlantı ve Kayıt Tabloları
    conn.execute('CREATE TABLE IF NOT EXISTS urun_tur_baglanti (urun_id INTEGER, tur_id INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS gunluk_kayitlar (id INTEGER PRIMARY KEY AUTOINCREMENT, urun_id INTEGER, gramaj REAL, ogun TEXT, tarih TEXT)')
    conn.commit()
    conn.close()

# --- ANA SAYFA ---
@app.route('/')
def ana_sayfa():
    bugun = datetime.now().strftime('%Y-%m-%d')
    conn = baglan()
    toplam_veri = conn.execute('''
        SELECT SUM((u.kalori / 100) * g.gramaj) as toplam
        FROM gunluk_kayitlar g
        JOIN urunler u ON g.urun_id = u.id
        WHERE g.tarih = ?
    ''', (bugun,)).fetchone()
    toplam = toplam_veri['toplam'] if toplam_veri['toplam'] else 0
    hedef = conn.execute('SELECT hedef_kalori FROM ayarlar WHERE id = 1').fetchone()['hedef_kalori']
    yuzde = round((toplam / hedef) * 100) if hedef > 0 else 0
    conn.close()
    return render_template('index.html', toplam=round(toplam), hedef=int(hedef), yuzde=yuzde)

@app.route('/hedef-guncelle', methods=['POST'])
def hedef_guncelle():
    conn = baglan()
    conn.execute('UPDATE ayarlar SET hedef_kalori = ? WHERE id = 1', (request.form.get('yeni_hedef'),))
    conn.commit()
    conn.close()
    return redirect(url_for('ana_sayfa'))

# --- ÜRÜN YÖNETİMİ ---
@app.route('/tur-ekle', methods=['GET', 'POST'])
def tur_ekle():
    if request.method == 'POST':
        f = request.files.get('ikon')
        if f:
            fname = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            conn = baglan()
            conn.execute('INSERT INTO turler (tur_adi, pixel_ikon_yolu) VALUES (?,?)', (request.form['tur_adi'], f'uploads/{fname}'))
            conn.commit()
            conn.close()
        return redirect(url_for('ana_sayfa'))
    return render_template('tur_ekle.html')

@app.route('/urun-ekle', methods=['GET', 'POST'])
def urun_ekle():
    conn = baglan()
    if request.method == 'POST':
        f = request.files.get('foto')
        foto = f'uploads/{secure_filename(f.filename)}' if f else 'assets/placeholder.png'
        if f: f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO urunler (marka_isim, kalori, protein, yag, karbonhidrat, seker, lif, tuz, foto_yolu) 
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', (request.form['marka'], request.form['kalori'], request.form['protein'], request.form['yag'], 
              request.form['karbonhidrat'], request.form['seker'], request.form['lif'], request.form['tuz'], foto))
        u_id = cursor.lastrowid
        for t_id in request.form.getlist('turler'):
            conn.execute('INSERT INTO urun_tur_baglanti (urun_id, tur_id) VALUES (?,?)', (u_id, t_id))
        conn.commit()
        conn.close()
        return redirect(url_for('ana_sayfa'))
    turler = conn.execute('SELECT * FROM turler').fetchall()
    conn.close()
    return render_template('urun_ekle.html', turler=turler)


@app.route('/urunler')
@app.route('/urunler/<int:tur_id>')
def urunler_listesi(tur_id=None):
   
    show_all = request.args.get('all', False)
    conn = baglan()
    turler = conn.execute('SELECT * FROM turler').fetchall()
    
    urunler = []
    secilen_tur = None
    
    if tur_id:
        urunler = conn.execute('''
            SELECT u.* FROM urunler u 
            JOIN urun_tur_baglanti utb ON u.id = utb.urun_id 
            WHERE utb.tur_id = ?
        ''', (tur_id,)).fetchall()
        secilen_tur = conn.execute('SELECT * FROM turler WHERE id = ?', (tur_id,)).fetchone()
    elif show_all:
        urunler = conn.execute('SELECT * FROM urunler').fetchall()
    
    conn.close()
    return render_template('urunler_listesi.html', 
                           urunler=urunler, 
                           turler=turler, 
                           secilen_tur=secilen_tur, 
                           show_all=show_all)
# --- ÖĞÜN KAYIT VE GEÇMİŞ ---
@app.route('/ogunlerim')
def ogunlerim():
    bugun = datetime.now().strftime('%Y-%m-%d')
    conn = baglan()
    
    kayitlar = conn.execute('''
        SELECT g.*, u.marka_isim, u.kalori, u.foto_yolu FROM gunluk_kayitlar g 
        JOIN urunler u ON g.urun_id = u.id WHERE g.tarih = ?
    ''', (bugun,)).fetchall()
    
    turler = conn.execute('SELECT * FROM turler').fetchall()

 
    urunler_hepsi = conn.execute('''
        SELECT u.id, u.marka_isim, 
        (SELECT IFNULL(GROUP_CONCAT(tur_id), '') FROM urun_tur_baglanti WHERE urun_id = u.id) as tur_ids 
        FROM urunler u
    ''').fetchall()
    
    conn.close()
    return render_template('ogunlerim.html', kayitlar=kayitlar, urunler_hepsi=urunler_hepsi, turler=turler, tarih=bugun)
@app.route('/kaydet', methods=['POST'])
def kaydet():
    conn = baglan()
    conn.execute('INSERT INTO gunluk_kayitlar (urun_id, gramaj, ogun, tarih) VALUES (?,?,?,?)', 
                 (request.form['urun_id'], request.form['gramaj'], request.form['ogun_ismi'], datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    return redirect(url_for('ogunlerim'))

@app.route('/gecmis')
def gecmis():
    conn = baglan()
    tarihler = conn.execute('SELECT DISTINCT tarih FROM gunluk_kayitlar ORDER BY tarih DESC').fetchall()
    conn.close()
    return render_template('gecmis.html', tarihler=tarihler)

@app.route('/gecmis/<tarih>')
def gecmis_detay(tarih):
    conn = baglan()
    kayitlar = conn.execute('''
        SELECT g.*, u.* FROM gunluk_kayitlar g 
        JOIN urunler u ON g.urun_id = u.id 
        WHERE g.tarih = ?
    ''', (tarih,)).fetchall()
    conn.close()
    return render_template('gun_detay.html', kayitlar=kayitlar, tarih=tarih)

@app.route('/urun-sil/<int:urun_id>')
def urun_sil(urun_id):
    conn = baglan()
    conn.execute('DELETE FROM urunler WHERE id = ?', (urun_id,))
    conn.execute('DELETE FROM urun_tur_baglanti WHERE urun_id = ?', (urun_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('urunler_listesi'))

@app.route('/kayit-sil/<int:kayit_id>')
def kayit_sil(kayit_id):
    conn = baglan()
    conn.execute('DELETE FROM gunluk_kayitlar WHERE id = ?', (kayit_id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer)

if __name__ == '__main__':
    veritabani_kur() 
    app.run(host='0.0.0.0', port=0)