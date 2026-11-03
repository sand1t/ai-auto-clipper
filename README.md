# AI Auto Clipper — Facebook Reels (free starter)

## Fitur
- Upload file video milik sendiri / yang sudah mendapat izin.
- Transkripsi Bahasa Indonesia dengan Faster-Whisper tiny.
- Memilih kandidat momen berdasarkan isi transkrip dan pola hook sederhana.
- Membuat klip MP4 vertikal 9:16, maksimal 60 detik.
- Membakar subtitle ke video dan menyediakan unduhan MP4/ZIP.

## Catatan penting
- Ini adalah versi awal gratis, bukan model AI yang memahami emosi atau viralitas secara sempurna.
- Pemilihan momen adalah pemeringkatan heuristik berbasis transkrip; periksa hasilnya sebelum diposting.
- Link YouTube hanya disimpan sebagai referensi. Aplikasi tidak mengunduh video dari YouTube.
- Gunakan hanya video yang kamu miliki atau punya izin untuk mengedit dan mengunggahnya.
- Audio tanpa ucapan atau bahasa selain Indonesia mungkin menghasilkan subtitle/transkrip yang kurang tepat.

## Menjalankan di komputer
1. Install Python 3.10+ dan FFmpeg (pastikan `ffmpeg` dan `ffprobe` tersedia di PATH).
2. Ekstrak ZIP.
3. Jalankan:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
4. Buka alamat lokal yang ditampilkan Streamlit.

## Membuat bisa dibuka dari Android
Aplikasi perlu di-host di layanan yang menjalankan Python + FFmpeg. Setelah deploy, buka URL aplikasi dari Chrome Android. Hosting gratis memiliki batas RAM, waktu proses, dan ukuran upload; video panjang bisa gagal atau lambat. Untuk penggunaan stabil, gunakan server yang kamu kendalikan.

## Deploy Streamlit Community Cloud
1. Buat repository GitHub dan unggah `app.py`, `requirements.txt`, serta `packages.txt`.
2. Deploy repository melalui Streamlit Community Cloud.
3. Jika build gagal karena FFmpeg tidak tersedia, tambahkan file `packages.txt` berisi:
   ```
   ffmpeg
   ```
4. Buka URL hasil deploy dari Android.

## Batasan versi awal
Versi ini belum memiliki login, penyimpanan cloud permanen, pemrosesan batch besar, atau pengaturan posisi wajah otomatis. Crop 9:16 memakai potongan tengah gambar.
