import os, re, subprocess, tempfile, zipfile
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="AI Auto Clipper", page_icon="✂️", layout="centered")
st.title("✂️ AI AUTO CLIPPER")
st.caption("Video panjang → momen menarik → Facebook Reels 9:16")

st.info(
    "Upload file video yang kamu miliki atau punya izin untuk digunakan. "
    "Link YouTube hanya sebagai catatan sumber; aplikasi tidak mengunduh video dari YouTube."
)

@st.cache_resource(show_spinner=False)
def load_model():
    from faster_whisper import WhisperModel
    return WhisperModel("tiny", device="cpu", compute_type="int8")

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-2500:])
    return p.stdout

def probe_duration(path):
    out = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path
    ])
    return float(out.strip())

def score_segment(text):
    t = text.lower()
    score = min(len(t) / 90, 2.0)
    patterns = [
        r"\?", r"\bternyata\b", r"\brahasia\b", r"\bakhirnya\b",
        r"\bmengejutkan\b", r"\bmasalahnya\b", r"\bkenapa\b",
        r"\bbagaimana\b", r"\bkesalahan\b", r"\bpercaya\b",
        r"\bfakta\b", r"\bjarang\b", r"\bpenting\b", r"\bberhasil\b"
    ]
    score += sum(0.9 for p in patterns if re.search(p, t))
    if len(t.split()) < 7:
        score -= 1
    if len(t.split()) > 55:
        score -= 0.5
    return score

def render_clip(video, out, start, duration):
    # Crop to vertical 9:16. No subtitles or text are added to the video.
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1"
    )
    run([
        "ffmpeg", "-y", "-ss", str(start), "-i", video, "-t", str(duration),
        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out
    ])

url = st.text_input(
    "Link YouTube (opsional, sebagai referensi)",
    placeholder="https://youtube.com/watch?v=..."
)
uploaded = st.file_uploader(
    "Upload file video asli",
    type=["mp4", "mov", "mkv", "webm"]
)
clip_count = st.slider("Jumlah klip yang dicari", 1, 8, 3)
max_len = st.select_slider(
    "Durasi maksimal tiap klip",
    options=[30, 45, 60],
    value=60
)
st.caption(
    "Aplikasi memilih kandidat klip berdasarkan transkrip dan pola kalimat. "
    "Video hasil tetap perlu ditinjau sebelum diunggah."
)
st.caption("Hasil video bersih tanpa subtitle atau tulisan tambahan.")

if st.button("🔎 ANALISIS & BUAT KLIP", type="primary", use_container_width=True):
    if not uploaded:
        st.error("Upload file video terlebih dahulu.")
        st.stop()

    work = tempfile.mkdtemp(prefix="autoclipper_")
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", uploaded.name)
    src = os.path.join(work, safe_name)
    Path(src).write_bytes(uploaded.getbuffer())

    try:
        with st.spinner("Membaca durasi video..."):
            total = probe_duration(src)

        if total < 8:
            st.error("Video terlalu pendek untuk dibuat beberapa klip.")
            st.stop()

        st.write(f"Durasi video: **{total / 60:.1f} menit**")

        with st.spinner("AI sedang mendengarkan dan membuat transkrip. Video panjang bisa membutuhkan waktu."):
            model = load_model()
            segments_iter, info = model.transcribe(
                src,
                language="id",
                vad_filter=True,
                word_timestamps=False
            )
            segments = list(segments_iter)

        if not segments:
            st.error("Tidak ditemukan percakapan/audio yang bisa ditranskripsikan.")
            st.stop()

        candidates = []
        for seg in segments:
            start = max(0, seg.start - 2)
            end = min(total, start + max_len)
            if end - start < 12:
                continue

            relevant = [
                x for x in segments
                if x.end > start and x.start < end
            ]
            text = " ".join(x.text.strip() for x in relevant)
            score = score_segment(text)
            score += min(len(text.split()) / 35, 2)
            candidates.append((score, start, end, text))

        candidates.sort(reverse=True, key=lambda x: x[0])

        chosen = []
        for candidate in candidates:
            if all(
                abs(candidate[1] - old[1]) > max_len * 0.65
                for old in chosen
            ):
                chosen.append(candidate)
            if len(chosen) >= clip_count:
                break

        if not chosen:
            st.error("Belum ada bagian yang cukup jelas untuk dipotong.")
            st.stop()

        outputs = []
        progress = st.progress(0)

        for idx, (score, start, end, text) in enumerate(chosen, 1):
            out = os.path.join(work, f"facebook_reel_{idx}.mp4")
            with st.spinner(f"Membuat klip {idx}/{len(chosen)}..."):
                render_clip(src, out, start, end - start)
            outputs.append(out)
            progress.progress(idx / len(chosen))

        zip_path = os.path.join(work, "AI_Auto_Clipper_Reels.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for path in outputs:
                z.write(path, os.path.basename(path))

        st.success(f"Selesai! {len(outputs)} klip berhasil dibuat.")
        for i, path in enumerate(outputs, 1):
            st.subheader(f"Klip {i}")
            st.video(path)
            st.download_button(
                f"⬇️ Download Klip {i}",
                data=Path(path).read_bytes(),
                file_name=os.path.basename(path),
                mime="video/mp4",
                key=f"dl_{i}"
            )

        st.download_button(
            "⬇️ Download semua klip (ZIP)",
            data=Path(zip_path).read_bytes(),
            file_name="AI_Auto_Clipper_Reels.zip",
            mime="application/zip"
        )

        if url:
            st.caption("Referensi sumber: " + url)

    except Exception as e:
        st.error("Proses gagal. Pastikan file video valid dan audio terdengar jelas.")
        st.code(str(e))
