Nama : Faishal Falih

NPM : 2506612064

Kelas : PBP B

Hobi : GYM

### Tugas 1

1. Saya menggunakan beberapa elemen semantik HTML5 seperti <header>, <main>, <section>, <nav>, <footer>, <form>, <label>, dan <time>. Bagian profil, pengalaman, dan kontak masing-masing dibuat menggunakan <section>, sehingga struktur halaman lebih mudah dipahami oleh browser, screen reader, dan developer lain. Saya juga menggunakan <details> dan <summary> untuk menu navigasi mobile serta detail section experience. Elemen tersebut menyediakan perilaku buka tutup secara native tanpa JavaScript tambahan. Penggunaan elemen semantik membantu saya membuat static web yang tetap terstruktur, mudah dinavigasi, dan lebih aksesibel.
2. Tantangan utama adalah menyesuaikan hero section, navigasi, experience entry, dan form kontak pada layar kecil. Pada desktop, hero menggunakan CSS Grid dengan dua kolom, sedangkan pada mobile diubah menjadi satu kolom dengan urutan identitas, foto, lalu detail profil.
Experience entry menggunakan tiga kolom untuk logo, informasi pekerjaan, dan tombol buka tutup pada desktop. Pada mobile, layout diubah menjadi dua kolom, ukuran logo diperkecil, dan ikon toggle disembunyikan agar ruang lebih banyak digunakan untuk informasi utama.
Pada form kontak, field nama dan email dibuat dua kolom pada desktop, lalu menjadi satu kolom pada mobile. Saya menentukan prioritas berdasarkan urutan informasi yang paling penting untuk dibaca.
3. Batasan utama static web ini adalah seluruh konten masih ditulis langsung di template HTML. Jika section experience, kontak, atau profil berubah, saya harus mengedit kode secara manual. Section kontak saat ini menggunakan mailto:, sehingga pengiriman bergantung pada email client milik pengunjung. Website tidak dapat menyimpan pesan, memberikan status pengiriman yang konsisten, atau melakukan validasi server-side. Pada implementasi berikutnya, fungsionalitas yang paling ingin saya tambahkan adalah backend contact form menggunakan Django. Fitur tersebut dapat menyimpan pesan, melakukan validasi server-side, mengirim email melalui layanan email, dan menampilkan pesan berhasil atau gagal. Setelah itu, data section experience juga dapat dipindahkan ke model Django agar bisa dikelola melalui admin tanpa mengubah template secara manual.

### AI Disclosure
Saya menggunakan OpenAI Codex (gpt-5.6/luna) untuk membantu proses pengerjaan. AI digunakan untuk membuat draft struktur HTML semantik, menyusun CSS responsive, merancang menu mobile berbasis <details>, melakukan audit selector CSS, dan menyusun dokumentasi awal.

Strategi prompting yang digunakan adalah memberikan konteks repository, batasan teknis, dan kebutuhan fitur terlebih dahulu. Saya kemudian meminta AI mengusulkan implementasi, memeriksa kemungkinan over-engineering, serta meninjau kembali penggunaan selector dan struktur responsive. Saya lalu mengoreksi hasilnya secara manual.

Section profil, experience, tanggal, kontak, gambar, urutan visual, dan keputusan untuk tetap menggunakan static web ditentukan dan diverifikasi secara manual. Saya juga memeriksa bahwa implementasi tidak menambahkan di luar scope yang ditentukan.

AI memiliki keterbatasan terkait konteks dan memori yang dibutuhkan. AI juga tidak memiliki kemampuan untuk "melihat" hasilnya secara langsung, jadi saya berperan untuk mengorkestrasi, mengevaluasi dan mengarahkan AI supaya hasilnya lebih nyaman dilihat secara visual oleh user.
