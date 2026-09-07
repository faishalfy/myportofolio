Nama : Faishal Falih

NPM : 2506612064

Kelas : PBP B

Hobi : GYM

### Tugas 1

1. Saya menggunakan beberapa elemen semantik HTML5 seperti `<header>`, `<main>`, `<section>`, `<nav>`, `<footer>`, `<form>`, `<label>`, dan `<time>`. Bagian profile, experience, dan kontak masing-masing dibuat menggunakan `<section>`, sehingga struktur halaman lebih mudah dipahami oleh browser, screen reader, dan developer lain. Saya juga menggunakan `<details>` dan `<summary>` untuk menu navigasi mobile serta detail experience. Elemen tersebut menyediakan perilaku buka-tutup secara native tanpa JavaScript tambahan. Penggunaan elemen semantik membantu saya membuat static web yang tetap terstruktur, mudah dinavigasi, dan lebih aksesibel.

2. Tantangan utama adalah menyesuaikan hero section, navigasi, experience entry, dan form kontak pada mobile. Pada desktop, hero menggunakan CSS Grid dengan dua kolom, sedangkan pada mobile diubah menjadi satu kolom dengan urutan identitas, foto, lalu detail profile. Experience entry menggunakan tiga kolom untuk logo, informasi pekerjaan, dan tombol buka-tutup pada desktop. Pada mobile, layout diubah menjadi dua kolom, ukuran logo diperkecil, dan ikon toggle disembunyikan agar ruang lebih banyak digunakan untuk informasi utama. Pada form kontak, field nama dan email dibuat dua kolom pada desktop, lalu menjadi satu kolom pada mobile. Saya menentukan prioritas berdasarkan urutan informasi yang paling penting untuk dibaca.

3. Batasan utama static web ini adalah seluruh konten masih ditulis langsung di template HTML. Jika section experience, kontak, atau profil berubah, saya harus mengedit kode secara manual. Section kontak saat ini menggunakan `mailto:`, sehingga pengiriman bergantung pada email client milik user. Website tidak dapat menyimpan pesan, memberikan status pengiriman yang konsisten, atau melakukan validasi server-side. Pada implementasi berikutnya, fungsionalitas yang paling ingin saya tambahkan adalah backend contact form menggunakan Django. Fitur tersebut dapat menyimpan pesan, melakukan validasi server-side, mengirim email melalui layanan email, dan menampilkan pesan berhasil atau gagal. Setelah itu, data section experience juga dapat dipindahkan ke model Django agar bisa dikelola melalui admin tanpa mengubah template secara manual.

### AI Disclosure

- Saya menggunakan OpenAI Codex (gpt-5.6/luna) untuk membantu proses pengerjaan. AI digunakan untuk membuat draft struktur HTML semantik, menyusun CSS responsive, merancang menu mobile berbasis `<details>`, melakukan audit selector CSS, dan menyusun dokumentasi awal.
- Saya memberikan konteks repository, batasan teknis, dan kebutuhan fitur terlebih dahulu.
- Section profile, experience, tanggal, kontak, gambar, urutan visual, dan keputusan untuk tetap menggunakan static web ditentukan dan diverifikasi secara manual. Saya memastikan bahwa implementasi tidak menambahkankan fitur di luar scope yang ditentukan.
- AI memiliki keterbatasan dalam memahami konteks proyek secara keseluruhan. Saya perlu mengevaluasi hasilnya dan memastikan interface yang ada sudah sesuai.
- Link chat untuk Tugas 1 : https://chatgpt.com/s/cx_6a9edb41d63c8191836bd7813e0bcc78