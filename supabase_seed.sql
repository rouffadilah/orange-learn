-- materi: 15 rows
truncate table public.materi restart identity;
insert into public.materi (id, judul, kategori, deskripsi, isi, tingkat, urutan) values
(1, 'Pengenalan Orange Data Mining', 'Dasar', 'Mengenal Orange Data Mining dan kegunaannya.', '
                <h2>Apa itu Orange Data Mining?</h2>

                <p>
                Orange Data Mining adalah platform visual untuk
                melakukan data mining, machine learning,
                analisis data, dan visualisasi.
                </p>

                <h3>Konsep utama</h3>

                <p>
                Orange menggunakan konsep widget dan workflow.
                Pengguna dapat menyusun berbagai widget pada
                Canvas kemudian menghubungkannya untuk membentuk
                proses analisis data.
                </p>

                <h3>Contoh workflow sederhana</h3>

                <pre>
File
 ↓
Data Table
 ↓
Data Visualization
                </pre>
                ', 'Pemula', 1),
(2, 'Mengenal Orange Canvas', 'Dasar', 'Memahami area kerja utama Orange.', '
                <h2>Orange Canvas</h2>

                <p>
                Canvas adalah area kerja utama di Orange Data Mining.
                Di dalam Canvas pengguna menempatkan dan menghubungkan
                berbagai widget.
                </p>

                <h3>Komponen utama</h3>

                <ul>
                    <li>Widget Toolbox</li>
                    <li>Canvas</li>
                    <li>Workflow</li>
                    <li>Connection</li>
                </ul>

                <p>
                Setiap widget memiliki fungsi tertentu dan dapat
                dihubungkan dengan widget lainnya.
                </p>
                ', 'Pemula', 2),
(3, 'Mengenal Widget', 'Dasar', 'Memahami konsep widget pada Orange.', '
                <h2>Widget Orange</h2>

                <p>
                Widget adalah komponen visual yang digunakan untuk
                melakukan suatu proses dalam analisis data.
                </p>

                <h3>Contoh widget</h3>

                <ul>
                    <li>File</li>
                    <li>Data Table</li>
                    <li>Select Columns</li>
                    <li>Scatter Plot</li>
                    <li>Test & Score</li>
                    <li>Random Forest</li>
                </ul>

                <p>
                Widget dapat dihubungkan sehingga membentuk
                workflow analisis data.
                </p>
                ', 'Pemula', 3),
(4, 'Memasukkan Dataset dengan File Widget', 'Data', 'Belajar memasukkan dataset ke dalam Orange.', '
                <h2>File Widget</h2>

                <p>
                File digunakan untuk memasukkan dataset ke dalam
                workflow Orange.
                </p>

                <h3>Format data</h3>

                <p>
                Dataset dapat berasal dari berbagai sumber dan
                format yang didukung oleh Orange.
                </p>

                <h3>Workflow</h3>

                <pre>
File
 ↓
Data Table
                </pre>

                <p>
                Setelah dataset dimasukkan, gunakan Data Table
                untuk melihat isi data.
                </p>
                ', 'Pemula', 4),
(5, 'Data Table', 'Data', 'Melihat isi dataset dalam bentuk tabel.', '
                <h2>Data Table</h2>

                <p>
                Data Table digunakan untuk melihat data dalam
                bentuk tabel.
                </p>

                <h3>Kegunaan</h3>

                <ul>
                    <li>Melihat baris data</li>
                    <li>Melihat nama atribut</li>
                    <li>Memeriksa tipe data</li>
                    <li>Memeriksa hasil proses</li>
                </ul>

                <pre>
File
 ↓
Data Table
                </pre>
                ', 'Pemula', 5),
(6, 'Select Columns', 'Preprocessing', 'Memilih variabel yang digunakan dalam analisis.', '
                <h2>Select Columns</h2>

                <p>
                Select Columns digunakan untuk menentukan variabel
                yang digunakan sebagai fitur, target, atau metadata.
                </p>

                <h3>Contoh</h3>

                <pre>
File
 ↓
Select Columns
 ↓
Random Forest
                </pre>

                <p>
                Widget ini sangat berguna sebelum melakukan
                proses machine learning.
                </p>
                ', 'Menengah', 6),
(7, 'Data Preprocessing', 'Preprocessing', 'Mempersiapkan data sebelum analisis.', '
                <h2>Data Preprocessing</h2>

                <p>
                Preprocessing merupakan tahap mempersiapkan data
                sebelum digunakan untuk analisis atau machine learning.
                </p>

                <h3>Contoh proses</h3>

                <ul>
                    <li>Impute missing values</li>
                    <li>Normalisasi</li>
                    <li>Seleksi fitur</li>
                    <li>Transformasi data</li>
                </ul>
                ', 'Menengah', 7),
(8, 'Visualisasi Data', 'Visualisasi', 'Membuat visualisasi data menggunakan Orange.', '
                <h2>Visualisasi Data</h2>

                <p>
                Orange menyediakan berbagai widget visualisasi
                untuk membantu memahami pola data.
                </p>

                <h3>Contoh widget</h3>

                <ul>
                    <li>Scatter Plot</li>
                    <li>Box Plot</li>
                    <li>Distributions</li>
                    <li>Heat Map</li>
                </ul>
                ', 'Menengah', 8),
(9, 'Classification', 'Machine Learning', 'Mengenal klasifikasi dalam machine learning.', '
                <h2>Classification</h2>

                <p>
                Classification digunakan untuk memprediksi kelas
                atau kategori dari suatu data.
                </p>

                <h3>Contoh algoritma</h3>

                <ul>
                    <li>Decision Tree</li>
                    <li>Random Forest</li>
                    <li>kNN</li>
                    <li>Naive Bayes</li>
                    <li>Logistic Regression</li>
                    <li>SVM</li>
                </ul>

                <h3>Workflow sederhana</h3>

                <pre>
File
 ↓
Select Columns
 ↓
Random Forest
 ↓
Test & Score
                </pre>
                ', 'Menengah', 9),
(10, 'Random Forest', 'Machine Learning', 'Mengenal algoritma Random Forest.', '
                <h2>Random Forest</h2>

                <p>
                Random Forest merupakan metode ensemble yang
                menggunakan banyak decision tree untuk menghasilkan
                prediksi.
                </p>

                <h3>Contoh workflow</h3>

                <pre>
File
 ↓
Select Columns
 ↓
Random Forest
 ↓
Test & Score
 ↓
Confusion Matrix
                </pre>
                ', 'Menengah', 10),
(11, 'Test & Score', 'Evaluasi', 'Mengevaluasi performa model machine learning.', '
                <h2>Test & Score</h2>

                <p>
                Test & Score digunakan untuk mengevaluasi performa
                model machine learning.
                </p>

                <h3>Contoh metrik</h3>

                <ul>
                    <li>Accuracy</li>
                    <li>Precision</li>
                    <li>Recall</li>
                    <li>F1 Score</li>
                    <li>AUC</li>
                </ul>

                <pre>
Model
 ↓
Test & Score
                </pre>
                ', 'Menengah', 11),
(12, 'Confusion Matrix', 'Evaluasi', 'Memahami hasil prediksi klasifikasi.', '
                <h2>Confusion Matrix</h2>

                <p>
                Confusion Matrix digunakan untuk melihat hasil
                prediksi model klasifikasi berdasarkan kelas aktual
                dan kelas prediksi.
                </p>

                <p>
                Confusion Matrix dapat membantu memahami kesalahan
                klasifikasi model.
                </p>
                ', 'Menengah', 12),
(13, 'Regression', 'Machine Learning', 'Mengenal regresi untuk memprediksi nilai numerik.', '
                <h2>Regression</h2>

                <p>
                Regression digunakan ketika target yang diprediksi
                berupa nilai numerik.
                </p>

                <h3>Contoh algoritma</h3>

                <ul>
                    <li>Linear Regression</li>
                    <li>Random Forest Regression</li>
                    <li>kNN Regression</li>
                </ul>
                ', 'Menengah', 13),
(14, 'K-Means Clustering', 'Clustering', 'Melakukan pengelompokan data menggunakan K-Means.', '
                <h2>K-Means Clustering</h2>

                <p>
                K-Means merupakan metode unsupervised learning
                yang digunakan untuk mengelompokkan data berdasarkan
                kemiripan karakteristik.
                </p>

                <h3>Workflow</h3>

                <pre>
File
 ↓
Preprocess
 ↓
k-Means
 ↓
Data Table
                </pre>
                ', 'Menengah', 14),
(15, 'Association Rules', 'Data Mining', 'Mengenal analisis hubungan antar item.', '
                <h2>Association Rules</h2>

                <p>
                Association Rules digunakan untuk menemukan hubungan
                atau pola keterkaitan antar item dalam data.
                </p>

                <h3>Contoh penerapan</h3>

                <p>
                Analisis keranjang belanja atau market basket analysis.
                </p>
                ', 'Lanjutan', 15);


select setval(pg_get_serial_sequence('public.materi', 'id'), coalesce((select max(id) from public.materi), 1), true);

-- widget: 15 rows
truncate table public.widget restart identity;
insert into public.widget (id, nama, kategori, deskripsi, fungsi, input_data, output_data, tingkat, contoh, urutan) values
(1, 'File', 'Data', 'Memuat dataset ke dalam Orange.', 'Digunakan untuk membaca dataset dari file.', 'Dataset', 'Data Table, Data Mining, Visualisasi', 'Pemula', '
                File
                ↓
                Data Table
                ', 1),
(2, 'Data Table', 'Data', 'Menampilkan data dalam bentuk tabel.', 'Digunakan untuk melihat dan memeriksa isi dataset.', 'Data', 'Data', 'Pemula', '
                File
                ↓
                Data Table
                ', 2),
(3, 'Select Columns', 'Transform', 'Memilih kolom yang digunakan dalam analisis.', 'Menentukan fitur, target, dan metadata.', 'Data', 'Data', 'Pemula', '
                File
                ↓
                Select Columns
                ↓
                Model
                ', 3),
(4, 'Preprocess', 'Transform', 'Melakukan preprocessing terhadap dataset.', 'Menangani missing value, scaling, encoding, dan transformasi data.', 'Data', 'Preprocessed Data', 'Menengah', '
                File
                ↓
                Preprocess
                ↓
                Model
                ', 4),
(5, 'Scatter Plot', 'Visualisasi', 'Membuat visualisasi hubungan dua variabel.', 'Melihat pola dan hubungan antar variabel.', 'Data', 'Visualisasi', 'Pemula', '
                File
                ↓
                Scatter Plot
                ', 5),
(6, 'Box Plot', 'Visualisasi', 'Menampilkan distribusi data menggunakan box plot.', 'Melihat distribusi, median, dan kemungkinan outlier.', 'Data', 'Visualisasi', 'Pemula', '
                File
                ↓
                Box Plot
                ', 6),
(7, 'Distributions', 'Visualisasi', 'Menampilkan distribusi nilai atribut.', 'Menganalisis distribusi variabel.', 'Data', 'Visualisasi', 'Pemula', '
                File
                ↓
                Distributions
                ', 7),
(8, 'Random Forest', 'Model', 'Algoritma ensemble berbasis decision tree.', 'Digunakan untuk classification dan regression.', 'Data', 'Model', 'Menengah', '
                File
                ↓
                Random Forest
                ↓
                Test & Score
                ', 8),
(9, 'Tree', 'Model', 'Membuat model decision tree.', 'Digunakan untuk classification dan regression.', 'Data', 'Model', 'Pemula', '
                File
                ↓
                Tree
                ↓
                Test & Score
                ', 9),
(10, 'kNN', 'Model', 'Algoritma k-Nearest Neighbors.', 'Membuat prediksi berdasarkan kedekatan data.', 'Data', 'Model', 'Menengah', '
                File
                ↓
                kNN
                ↓
                Test & Score
                ', 10),
(11, 'SVM', 'Model', 'Support Vector Machine.', 'Digunakan untuk classification dan regression.', 'Data', 'Model', 'Lanjutan', '
                File
                ↓
                SVM
                ↓
                Test & Score
                ', 11),
(12, 'Linear Regression', 'Model', 'Model regresi linear.', 'Memprediksi target numerik berdasarkan variabel input.', 'Data', 'Model', 'Menengah', '
                File
                ↓
                Linear Regression
                ↓
                Test & Score
                ', 12),
(13, 'k-Means', 'Clustering', 'Algoritma clustering berbasis centroid.', 'Mengelompokkan data berdasarkan kemiripan.', 'Data', 'Clusters', 'Menengah', '
                File
                ↓
                k-Means
                ↓
                Data Table
                ', 13),
(14, 'Test & Score', 'Evaluasi', 'Mengevaluasi performa model.', 'Menghasilkan metrik evaluasi model machine learning.', 'Data + Model', 'Evaluation Results', 'Menengah', '
                File
                ↓
                Model
                ↓
                Test & Score
                ', 14),
(15, 'Confusion Matrix', 'Evaluasi', 'Menampilkan hasil prediksi klasifikasi.', 'Menganalisis prediksi benar dan salah berdasarkan kelas.', 'Evaluation Results', 'Confusion Matrix', 'Menengah', '
                Test & Score
                ↓
                Confusion Matrix
                ', 15);


select setval(pg_get_serial_sequence('public.widget', 'id'), coalesce((select max(id) from public.widget), 1), true);

-- workflow: 5 rows
truncate table public.workflow restart identity;
insert into public.workflow (id, nama, kategori, tujuan, deskripsi, tingkat, urutan) values
(1, 'Klasifikasi dengan Random Forest', 'Classification', 'Membuat model untuk memprediksi kategori atau kelas.', 'Workflow untuk melakukan klasifikasi menggunakan Random Forest.', 'Menengah', 1),
(2, 'Klasifikasi dengan Decision Tree', 'Classification', 'Membuat model klasifikasi menggunakan Decision Tree.', 'Workflow sederhana untuk memahami proses klasifikasi.', 'Pemula', 2),
(3, 'Prediksi Nilai dengan Linear Regression', 'Regression', 'Memprediksi nilai numerik.', 'Workflow untuk melakukan analisis regresi.', 'Menengah', 3),
(4, 'Clustering dengan K-Means', 'Clustering', 'Mengelompokkan data berdasarkan kemiripan.', 'Workflow unsupervised learning menggunakan K-Means.', 'Menengah', 4),
(5, 'Eksplorasi dan Visualisasi Data', 'Exploratory Data Analysis', 'Memahami karakteristik dataset.', 'Workflow untuk melihat pola dan distribusi data.', 'Pemula', 5);


select setval(pg_get_serial_sequence('public.workflow', 'id'), coalesce((select max(id) from public.workflow), 1), true);
