import streamlit as st
import pandas as pd

st.title("BudgetWatch AI")
st.write("Cek penyerapan anggaran per jenis belanja dalam satu dinas.")

nama_dinas = st.text_input("Nama dinas", "Dinas Pendidikan Kab. Bengkalis")
file = st.file_uploader("Unggah file CSV", type="csv")


def nilai_risiko(s):
    if s > 100:
        return "Tinggi", "Realisasi melebihi anggaran"
    if s < 50:
        return "Tinggi", "Serapan sangat rendah (di bawah 50%)"
    if s < 80:
        return "Sedang", "Serapan rendah (di bawah 80%)"
    return "Rendah", "Tidak ada tanda"


if file:
    df = pd.read_csv(file)
    df["serapan_persen"] = df["realisasi"] / df["anggaran"] * 100
    df["sisa_miliar"] = (df["anggaran"] - df["realisasi"]) / 1e9
    df["tingkat_risiko"] = df["serapan_persen"].apply(lambda s: nilai_risiko(s)[0])
    df["alasan"] = df["serapan_persen"].apply(lambda s: nilai_risiko(s)[1])

    tahun_list = sorted(df["tahun"].unique())
    tahun = st.selectbox("Pilih tahun", tahun_list, index=len(tahun_list) - 1)
    d = df[df["tahun"] == tahun]

    total_anggaran = d["anggaran"].sum()
    total_realisasi = d["realisasi"].sum()
    st.subheader(f"{nama_dinas} TA {tahun}")
    st.write(f"Total anggaran: Rp{total_anggaran / 1e9:,.2f} miliar")
    st.write(f"Total realisasi: Rp{total_realisasi / 1e9:,.2f} miliar")
    st.write(f"Serapan keseluruhan: {total_realisasi / total_anggaran * 100:.2f}%")
    st.write(f"Sisa anggaran: Rp{(total_anggaran - total_realisasi) / 1e9:,.2f} miliar")

    st.subheader("Hasil analisis per jenis belanja")
    st.dataframe(d[["kode", "uraian", "serapan_persen", "sisa_miliar", "tingkat_risiko", "alasan"]])

    st.subheader("Jenis belanja yang perlu dicek")
    st.dataframe(d[d["tingkat_risiko"] != "Rendah"][["uraian", "serapan_persen", "sisa_miliar", "tingkat_risiko", "alasan"]])

    st.subheader("Sisa anggaran per kelompok (miliar rupiah)")
    st.bar_chart(d.groupby("kelompok")["sisa_miliar"].sum())

    if len(tahun_list) >= 2:
        awal = tahun_list[0]
        akhir = tahun_list[-1]
        st.subheader(f"Perbandingan serapan {awal} dan {akhir} (%)")
        p = df.pivot(index="uraian", columns="tahun", values="serapan_persen")
        p["perubahan_poin"] = p[akhir] - p[awal]
        p["catatan"] = p["perubahan_poin"].apply(
            lambda x: "Turun tajam, perlu dicek" if x < -10 else ("Naik" if x > 0 else "Turun ringan")
        )
        st.dataframe(p)
        st.bar_chart(p[[awal, akhir]])
