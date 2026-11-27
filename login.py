import streamlit as st
import mysql.connector
import menu
import hashlib
from database import koneksi

# Mengecek status login
if "login" not in st.session_state:
    st.session_state["login"] = False

# =====================
# HALAMAN LOGIN
# =====================

if not st.session_state["login"]:

    st.title("📚 Aplikasi Perpustakaan")

    pilihan = st.radio(
        "Pilih Aktivitas",
        ["Login", "Register"],
        horizontal=True
    )

    # LOGIN
    if pilihan == "Login":

        st.subheader("Login Pengguna")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Masuk"):

            if username == "" or password == "":
                st.warning("Username dan password wajib diisi!")

            else:

                db = koneksi()
                cursor = db.cursor()

                password_hash = hashlib.sha256(password.encode()).hexdigest()

                sql = "SELECT * FROM users WHERE username=%s AND password=%s"
                cursor.execute(sql, (username, password_hash))

                hasil = cursor.fetchone()

                if hasil:
                    st.session_state["login"] = True
                    st.session_state["username"] = username
                    st.session_state["nama"] = hasil[1]
                    st.session_state["user_id"] = hasil[0]

                    st.success("Login Berhasil!")
                    st.rerun()

                else:
                    st.error("Username atau password salah!")

                cursor.close()
                db.close()

    # REGISTER
    elif pilihan == "Register":

        st.subheader("Pendaftaran Pengguna Baru")

        nama = st.text_input("Nama Lengkap")
        username = st.text_input("Username Baru")
        password = st.text_input("Password Baru", type="password")

        if st.button("Daftar"):

            if nama == "" or username == "" or password == "":
                st.warning("Semua data wajib diisi!")

            else:
                db = mysql.connector.connect(
                    host="localhost",
                    port=3306,
                    user="root",
                    password="",
                    database="db_perpustakaan"
                )
                
                cursor = db.cursor()

                # Mengecek username
                cek_username = "SELECT * FROM users WHERE username=%s"
                cursor.execute(cek_username, (username,))

                hasil = cursor.fetchone()

                if hasil:
                    st.error("Username sudah digunakan!")

                else:
                    sql = """
                    INSERT INTO users (nama, username, password)
                    VALUES (%s, %s, %s)
                    """

                    password_hash = hashlib.sha256(password.encode()).hexdigest()

                    cursor.execute(
                        sql,
                        (nama, username, password_hash)
                    )

                    db.commit()

                    st.success("Register Berhasil!")

                cursor.close()
                db.close()

# =====================
# HALAMAN MENU
# =====================

else:
    menu.tampilkan_menu()
