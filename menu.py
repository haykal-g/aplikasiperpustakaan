import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date
from database import koneksi

def tampilkan_menu():

    st.sidebar.title("📚 Aplikasi Perpustakaan")

    pilihan = st.sidebar.selectbox(
        "Pilih Menu",
        [
            "Beranda",
            "Lihat Data Buku",
            "Input Data Buku",
            "Peminjaman Buku",
            "Pengembalian Buku",
            "Logout"
        ]
    )

    # =====================
    # BERANDA
    # =====================

    if pilihan == "Beranda":

        st.title("Halaman Beranda")
        st.success("Selamat Datang, " + st.session_state["nama"])

    # =====================
    # LIHAT DATA BUKU
    # =====================

    elif pilihan == "Lihat Data Buku":

        st.title("Daftar Buku Perpustakaan")

        db = koneksi()
        
        query = "SELECT * FROM buku"
        data = pd.read_sql(query, db)

        st.dataframe(data)
        st.write("Jumlah Buku:", len(data))

        db.close()


    # =====================
    # INPUT DATA BUKU
    # =====================

    elif pilihan == "Input Data Buku":

        st.title("Input Data Buku")

        with st.form("form_buku"):

            kode_buku = st.text_input("Kode Buku")
            judul = st.text_input("Judul Buku")
            penulis = st.text_input("Penulis")
            kategori = st.text_input("Kategori")
            stok = st.number_input("Stok", min_value=0, step=1)

            tombol_simpan = st.form_submit_button("Simpan")

            if tombol_simpan:

                if kode_buku == "" or judul == "" or penulis == "" or kategori == "":
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

                    # Mengecek apakah kode buku sudah digunakan
                    cek = "SELECT * FROM buku WHERE kode_buku=%s"
                    cursor.execute(cek, (kode_buku,))

                    hasil = cursor.fetchone()

                    if hasil:
                        st.warning("Kode buku sudah terdaftar!")

                    else:
                        sql = """
                        INSERT INTO buku (kode_buku, judul, penulis, kategori, stok)
                        VALUES (%s, %s, %s, %s, %s)
                        """

                        cursor.execute(
                            sql,
                            (kode_buku, judul, penulis, kategori, stok)
                        )

                        db.commit()

                        st.success("Data Buku Berhasil Disimpan!")

                    cursor.close()
                    db.close()

        # =====================
        # TABEL BUKU TERBARU
        # =====================

        st.subheader("Buku Terbaru")

        db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="db_perpustakaan"
        )

        query = """
        SELECT kode_buku, judul, penulis, kategori, stok
        FROM buku
        ORDER BY kode_buku DESC
        LIMIT 5
        """

        data = pd.read_sql(query, db)

        st.dataframe(data, use_container_width=True)

        db.close()

    # =====================
    # PEMINJAMAN BUKU
    # =====================

    elif pilihan == "Peminjaman Buku":

        st.title("Peminjaman Buku")

        db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="db_perpustakaan"
        )

        cursor = db.cursor()

        cursor.execute(
            "SELECT kode_buku, judul, kategori, stok FROM buku"
        )

        daftar_buku = cursor.fetchall()

        if daftar_buku:

            pilihan_buku = st.selectbox(
                "Pilih Buku",
                daftar_buku,
                format_func=lambda x: f"{x[1]} (Stok: {x[3]})"
            )

            with st.form("form_peminjaman"):

                tanggal_peminjaman = st.date_input("Tanggal Peminjaman")
                tanggal_pengembalian = st.date_input("Batas Pengembalian")

                tombol_pinjam = st.form_submit_button("Pinjam Buku")

                if tombol_pinjam:

                    if tanggal_pengembalian < tanggal_peminjaman:
                        st.warning("Batas pengembalian tidak boleh sebelum tanggal peminjaman!")

                    else:
                        # Mengurangi stok buku
                        update_stok = """
                        UPDATE buku
                        SET stok = stok - 1
                        WHERE kode_buku=%s AND stok > 0
                        """

                        cursor.execute(update_stok, (pilihan_buku[0],))

                        if cursor.rowcount > 0:

                            sql = """
                            INSERT INTO peminjaman
                            (user_id, kode_buku, judul, kategori,
                             tanggal_peminjaman, tanggal_pengembalian, denda)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """

                            data = (
                                st.session_state["user_id"],
                                pilihan_buku[0],
                                pilihan_buku[1],
                                pilihan_buku[2],
                                tanggal_peminjaman,
                                tanggal_pengembalian,
                                0
                            )

                            cursor.execute(sql, data)
                            db.commit()

                            st.success("Peminjaman Buku Berhasil!")
                            st.rerun()

                        else:
                            db.rollback()
                            st.warning("Stok buku sudah habis!")

        else:
            st.warning("Belum ada data buku!")

        cursor.close()
        db.close()

    # =====================
    # PENGEMBALIAN BUKU
    # =====================

    elif pilihan == "Pengembalian Buku":

        st.title("Pengembalian Buku")

        db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="db_perpustakaan"
        )

        cursor = db.cursor()

        st.subheader("Proses Pengembalian Buku")

        sql = """
        SELECT id_peminjaman, kode_buku, judul, tanggal_pengembalian
        FROM peminjaman
        WHERE user_id=%s AND tanggal_dikembalikan IS NULL
        """

        cursor.execute(sql, (st.session_state["user_id"],))
        daftar_pinjam = cursor.fetchall()

        if daftar_pinjam:

            pilihan_pinjam = st.selectbox(
                "Pilih Buku yang Dikembalikan",
                daftar_pinjam,
                format_func=lambda x: x[2]
            )

            if st.button("Kembalikan Buku"):

                tanggal_kembali = date.today()
                batas_kembali = pilihan_pinjam[3]

                terlambat = (tanggal_kembali - batas_kembali).days
                denda = max(0, terlambat) * 2000

                update = """
                UPDATE peminjaman
                SET tanggal_dikembalikan=%s, denda=%s
                WHERE id_peminjaman=%s
                """

                cursor.execute(
                    update,
                    (tanggal_kembali, denda, pilihan_pinjam[0])
                )

                # Menambahkan stok buku
                update_stok = """
                UPDATE buku
                SET stok = stok + 1
                WHERE kode_buku=%s
                """

                cursor.execute(
                    update_stok,
                    (pilihan_pinjam[1],)
                )

                db.commit()

                st.success("Buku Berhasil Dikembalikan!")
                st.write("Denda: Rp", f"{denda:,}".replace(",", "."))

                cursor.close()
                db.close()

                st.rerun()

        else:
            st.info("Tidak ada buku yang perlu dikembalikan.")

        # Menampilkan riwayat peminjaman
        st.subheader("Riwayat Peminjaman Buku")

        sql_riwayat = """
        SELECT kode_buku, judul, kategori,
               tanggal_peminjaman, tanggal_pengembalian,
               tanggal_dikembalikan, denda
        FROM peminjaman
        WHERE user_id=%s
        """

        cursor.execute(sql_riwayat, (st.session_state["user_id"],))
        data_riwayat = cursor.fetchall()

        kolom = [
            "Kode Buku",
            "Judul Buku",
            "Kategori",
            "Tanggal Peminjaman",
            "Batas Pengembalian",
            "Tanggal Dikembalikan",
            "Denda"
        ]

        if data_riwayat:

            df = pd.DataFrame(data_riwayat, columns=kolom)
            st.dataframe(df, use_container_width=True)

        else:
            st.info("Belum ada riwayat peminjaman.")

        cursor.close()
        db.close()

    # =====================
    # LOGOUT
    # =====================

    elif pilihan == "Logout":

        st.session_state["login"] = False
        st.session_state["username"] = ""
        st.session_state["nama"] = ""
        st.session_state["user_id"] = None

        st.rerun()
