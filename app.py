from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, current_app 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired
from flask_bootstrap import Bootstrap
from functools import wraps
import pdfkit

app = Flask(__name__)

app.config['SECRET_KEY'] = '#$%$4939Ejjl;LIW'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/dbpuskesmas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
bootstrap =Bootstrap(app)

class Login(FlaskForm):
    username = StringField('',validators=[InputRequired()], render_kw={'autofocus':True, 'placeholder':'Username'})
    password = PasswordField('',validators=[InputRequired()], render_kw={'autofocus':True, 'placeholder':'Password'})
    level = SelectField('',validators=[InputRequired()], choices=[('Admin','Admin'), ('Dokter','Dokter')])
                           

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    password = db.Column(db.Text)
    level = db.Column(db.String(100))

    def __init__(self,username,password,level):
        self.username = username
        if password != '':
            self.password = bcrypt.generate_password_hash(password) .decode('UTF-8')
        self.level = level

class Karyawan(db.Model):
    __tablename__ = 'karyawan'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150))
    jadwal = db.Column(db.Text)
    jabatan = db.Column(db.String(150))

    def __init__(self,nama,jadwal,jabatan):
        self.nama = nama
        self.jadwal = jadwal
        self.jabatan = jabatan


class Pendaftaran(db.Model):
    __tablename__ = 'pendaftaran'
    id = db.Column(db.BigInteger, primary_key=True)
    nama = db.Column(db.String(150))
    tl = db.Column(db.String(100))
    tg_lahir = db.Column(db.String(100))
    jk = db.Column(db.String(100))
    layanan_kesehatan = db.Column(db.String(100))
    profesi = db.Column(db.String(100))
    bpjs = db.Column(db.String(100))
    no_bpjs = db.Column(db.String(100))
    alamat = db.Column(db.Text)

    def __init__(self,nama,tl,tg_lahir,jk,layanan_kesehatan,profesi,bpjs,no_bpjs,alamat):
        self.nama = nama
        self.tl = tl
        self.tg_lahir = tg_lahir
        self.jk = jk
        self.layanan_kesehatan = layanan_kesehatan
        self.profesi = profesi
        self.bpjs = bpjs
        self.no_bpjs = no_bpjs
        self.alamat = alamat

class Obat(db.Model):
    __tablename__ = 'obat'
    id = db.Column(db.Integer, primary_key=True)
    namaObat = db.Column(db.String(150))
    jenisObat = db.Column(db.String(150))
    harga_beli = db.Column(db.Integer)
    harga_jual = db.Column(db.Integer)

    def __init__(self,namaObat,jenisObat,harga_beli,harga_jual):
        self.namaObat = namaObat
        self.jenisObat = jenisObat
        self.harga_beli = harga_beli
        self.harga_jual = harga_jual

class Suplier(db.Model):
    __tablename__ = 'suplier'
    id = db.Column(db.Integer, primary_key=True)
    perusahaan = db.Column(db.String(200))
    kontak = db.Column(db.String(100))
    alamat = db.Column(db.Text)

    def __init__(self,perusahaan,kontak,alamat):
        self.perusahaan = perusahaan
        self.kontak = kontak
        self.alamat = alamat


def login_dulu(f):
    @wraps(f)
    def wrap(*arg, **kwargs):
        if 'login' in session:
            return f(*arg, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def index():
    if session.get('login') == True:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('login') == True:
        return redirect(url_for('dashboard'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data) .first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data) and user.level == form.level.data:
                session['login'] = True
                session['id'] = user.id
                session['level'] = user.level
                return redirect(url_for('dashboard'))
        pesan = "Username atau Password anda salah"
        return render_template("login.html", pesan=pesan, form=form)
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_dulu
def dashboard():
    return render_template('dashboard.html')

@app.route('/kelola_user')
@login_dulu
def kelola_user():
    data = User.query.all()
    return render_template('user.html', data=data)

@app.route('/tambahuser', methods=['GET','POST'])
@login_dulu
def tambahuser():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        level= request.form['level']
        db.session.add(User(username,password,level))
        db.session.commit()
        return redirect(url_for('kelola_user'))

@app.route('/edituser/<id>', methods=['GET','POST'])
@login_dulu
def edituser(id):
    data = User.query.filter_by(id=id) .first()
    if request.method == "POST":
        try:
            data.username = request.form['username']
            if data.password != '':
                data.password = bcrypt.generate_password_hash(request.form['password']) .decode('UTF-8')
            data.level= request.form['level']
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('kelola_user'))
        except:
            flash("Ada trouble")
            return redirect(request.referrer)

@app.route('/hapususer/<id>', methods=['GET','POST'])
@login_dulu
def hapususer(id):
    data = User.query.filter_by(id=id) .first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('kelola_user'))

@app.route('/pendaftaran')
@login_dulu
def pendaftaran():
    data = Pendaftaran.query.all()
    return render_template('pendaftaran.html', data=data)

@app.route('/tambahdaftar', methods=['GET','POST'])
@login_dulu
def tambahdaftar():
    if request.method == "POST":
        nama = request.form['nama']
        tl = request.form['tl']
        tg_lahir = request.form['tg_lahir']
        jk = request.form['jk']
        layanan_kesehatan = request.form['layanan_kesehatan']
        profesi = request.form['profesi']
        bpjs = request.form['bpjs']
        no_bpjs = request.form['no_bpjs']
        alamat = request.form['alamat']
        db.session.add(Pendaftaran(nama,tl,tg_lahir,jk,layanan_kesehatan,profesi,bpjs,no_bpjs,alamat))
        db.session.commit()
        return redirect(url_for('pendaftaran'))

@app.route('/editdaftar/<id>', methods=['GET','POST'])
@login_dulu
def editdaftar(id):
    data = Pendaftaran.query.filter_by(id=id) .first()
    if request.method == "POST":
        data.nama = request.form['nama']
        data.tl = request.form['tl']
        data.tg_lahir = request.form['tg_lahir']
        data.jk = request.form['jk']
        data.layanan_kesehatan = request.form['layanan_kesehatan']
        data.profesi = request.form['profesi']
        data.bpjs = request.form['bpjs']
        data.no_bpjs = request.form['no_bpjs']
        data.alamat = request.form['alamat']
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('pendaftaran'))

@app.route('/hapusdaftar/<id>', methods=['GET','POST'])
@login_dulu
def hapusPendaftaran(id):
    data = Pendaftaran.query.filter_by(id=id) .first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('pendaftaran'))  

@app.route('/obat')
@login_dulu
def obat():
    datao = Obat.query.all()
    return render_template('obat.html', datao=datao)

@app.route('/tambahobat', methods=['GET','POST'])
@login_dulu
def tambahobat():
    if request.method == "POST":
        namaObat = request.form['namaObat']
        jenisObat = request.form['jenisObat']
        harga_beli = request.form['harga_beli']
        harga_jual = request.form['harga_jual']
        db.session.add(Obat(namaObat,jenisObat,harga_beli,harga_jual))
        db.session.commit()
        return redirect(url_for('obat'))

@app.route('/editobat/<id>', methods=['GET','POST'])
@login_dulu
def editobat(id):
    datao = Obat.query.filter_by(id=id) .first()
    if request.method == "POST":
        datao.namaObat = request.form['namaObat']
        datao.jenisObat = request.form['jenisObat']
        datao.harga_beli = request.form['harga_beli']
        datao.harga_jual = request.form['harga_jual']
        db.session.add(datao)
        db.session.commit()
        return redirect(url_for('obat'))

@app.route('/hapusobat/<id>', methods=['GET','POST'])
@login_dulu
def hapusobat(id):
    datao = Obat.query.filter_by(id=id) .first()
    db.session.delete(datao)
    db.session.commit()
    return redirect(url_for('obat'))

@app.route('/karyawan')
@login_dulu
def karyawan():
    data = Karyawan.query.all()
    return render_template('karyawan.html', data=data)

@app.route('/tambahkaryawan', methods=['GET','POST'])
@login_dulu
def tambahkaryawan():
    if request.method == 'POST':
        nama = request.form['nama']
        jadwal = request.form['jadwal']
        jabatan = request.form['jabatan']
        db.session.add(Karyawan(nama,jadwal,jabatan))
        db.session.commit()
        return redirect(url_for('karyawan'))

@app.route('/editkaryawan/<id>', methods=['GET','POST'])
@login_dulu
def editkaryawan(id):
    data = Karyawan.query.filter_by(id=id) .first()
    if request.method == 'POST':
        data.nama = request.form['nama']
        data.jadwal = request.form['jadwal']
        data.jabatan = request.form['jabatan']
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('karyawan'))

@app.route('/hapuskaryawan/<id>', methods=['GET','POST'])
@login_dulu
def hapuskaryawan(id):
    data = Karyawan.query.filter_by(id=id) .first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('karyawan'))

@app.route('/suplier')
@login_dulu
def suplier():
    data1 = Suplier.query.all()
    return render_template('penanganan.html', data1=data1)


@app.route('/tambahsuplier', methods=['GET','POST'])
@login_dulu
def tambahsuplier():
    if request.method == "POST":
        perusahaan = request.form['perusahaan']
        kontak = request.form['kontak']
        alamat = request.form['alamat']
        db.session.add(Suplier(perusahaan,kontak,alamat))
        db.session.commit()
        return redirect(url_for('suplier'))

@app.route('/editsuplier/<id>', methods=['GET','POST'])
@login_dulu
def editsuplier(id):
    data = Suplier.query.filter_by(id=id) .first()
    if request.method == "POST":
        data.perusahaan = request.form['perusahaan']
        data.kontak = request.form['kontak']
        data.alamat = request.form['alamat']
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('suplier'))

@app.route('/hapussuplier/<id>', methods=['GET','POST'])
@login_dulu
def hapussuplier(id):
    data = Suplier.query.filter_by(id=id) .first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('suplier'))

@app.route('/laporanpasien')
@login_dulu
def laporanpasien():
    data = Pendaftaran.query.all()
    tombol = "tombol"
    return render_template('laporanpasien.html', data=data, tombol=tombol)

@app.route('/cetak_pasien_pdf', methods=['GET','POST'])
@login_dulu
def cetak_pasien_pdf():
    data = Pendaftaran.query.all()
    html = render_template('pasien_pdf.html', data=data)
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(html, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=laporan.pdf'
    return response
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
