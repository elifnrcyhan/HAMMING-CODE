import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


# 1. HAMMING CODE MANTIKSAL MOTORU (CORE)


def get_hamming_config(mode):
    """Seçilen moda göre M (Veri), K (Parite) ve Toplam Bit sayılarını döner."""
    if mode == "8-Bit":
        return 8, 4, 12  # M=8, K=4, Toplam=12
    elif mode == "16-Bit":
        return 16, 5, 21 # M=16, K=5, Toplam=21
    elif mode == "32-Bit":
        return 32, 6, 38 # M=32, K=6, Toplam=38
    return 0, 0, 0

def is_power_of_two(n):
    """Bir sayının 2'nin kuvveti olup olmadığını kontrol eder."""
    return n > 0 and (n & (n - 1)) == 0

def calculate_hamming(data_bits, mode):
    """
    Verilen veri bitlerini alır, parite bitlerini hesaplar
     ve şemadaki 'Memory' dizilimini (1 tabanlı indeks) oluşturur.
    """
    M, K, total_bits = get_hamming_config(mode)
    
    # 1 tabanlı indeksleme için total_bits + 1 boyutunda dizi oluşturuyoruz
    hamming_code = [0] * (total_bits + 1)
    
    # 1. Adım: Veri bitlerini parite olmayan konumlara yerleştir
    data_idx = 0
    for i in range(1, total_bits + 1):
        if not is_power_of_two(i):
            hamming_code[i] = data_bits[data_idx]
            data_idx += 1
            
    # 2. Adım: Parite bitlerini hesapla (Even Parity / Çift Parite)
    # Her bir parite biti (1, 2, 4, 8, 16, 32), kendi bit pozisyonunun maskelediği yerleri XOR'lar
    for k in range(K):
        parity_pos = 1 << k  # 1, 2, 4, 8, 16, 32
        xor_sum = 0
        for i in range(1, total_bits + 1):
            # Eğer i pozisyonunun 'parity_pos' biti 1 ise, o pozisyonu hesaba kat (kendisi hariç)
            if i != parity_pos and (i & parity_pos) != 0:
                xor_sum ^= hamming_code[i]
        hamming_code[parity_pos] = xor_sum
        
    return hamming_code[1:] # Hayali 0. indeksi atıp döndür

def check_and_correct(received_code, mode):
    """
    Bellekten okunan veriyi kontrol eder (Compare & Corrector bloğu).
    Sendrom kelimesini hesaplar, hatayı bulur, düzeltir ve temiz Data Out'u verir.
    """
    M, K, total_bits = get_hamming_config(mode)
    h = [0] + list(received_code) # 1 tabanlı indeks için başına ekleme yapıyoruz
    
    syndrome = 0
    # Sendrom bitlerini hesapla
    for k in range(K):
        parity_pos = 1 << k
        xor_sum = 0
        for i in range(1, total_bits + 1):
            if (i & parity_pos) != 0:
                xor_sum ^= h[i]
        # xor_sum sonucu ilgili sendrom bitini verir
        if xor_sum != 0:
            syndrome |= parity_pos
            
    error_detected = False
    corrected_bit_index = -1
    
    # Eğer sendrom 0 değilse ve toplam bit sınırları içindeyse hata vardır
    if syndrome != 0:
        error_detected = True
        corrected_bit_index = syndrome
        if corrected_bit_index <= total_bits:
            # Şemadaki 'Corrector' bloğu: Biti ters çevirerek düzeltir
            h[corrected_bit_index] = 1 if h[corrected_bit_index] == 0 else 0
            
    # Temiz veri bitlerini (M) parite olmayan yerlerden geri topla
    clean_data = []
    for i in range(1, total_bits + 1):
        if not is_power_of_two(i):
            clean_data.append(h[i])
            
    return error_detected, corrected_bit_index, clean_data, syndrome

# ==========================================
# 2. GÖRSEL ARAYÜZ KATMANI (GUI)
# ==========================================

class HammingSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BLM230 Bilgisayar Mimarisi - Hamming Code Simülatörü")
        self.root.geometry("900x600")
        self.root.configure(bg="#F5F5F5")
        
        self.memory_bits = [] # Bellekteki mevcut bit dizisi
        
        # ÜST PANEL: Mod Seçimi ve Veri Girişi
        top_frame = tk.LabelFrame(root, text=" Giriş ve Kontrol Paneli (Data In) ", font=("Arial", 11, "bold"), bg="#F5F5F5", fg="#333333")
        top_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(top_frame, text="Veri Uzunluğu Seçin:", font=("Arial", 10), bg="#F5F5F5").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.combo_mode = ttk.Combobox(top_frame, values=["8-Bit", "16-Bit", "32-Bit"], state="readonly", width=10, font=("Arial", 10))
        self.combo_mode.set("8-Bit")
        self.combo_mode.grid(row=0, column=1, padx=5, pady=10)
        self.combo_mode.bind("<<ComboboxSelected>>", self.on_mode_change)
        
        tk.Label(top_frame, text="Veri Girişi (Binary):", font=("Arial", 10), bg="#F5F5F5").grid(row=0, column=2, padx=20, pady=10, sticky="w")
        self.entry_data = tk.Entry(top_frame, font=("Courier", 12, "bold"), width=35, justify="center")
        self.entry_data.insert(0, "10110010") # Varsayılan 8-bit veri
        self.entry_data.grid(row=0, column=3, padx=5, pady=10)
        
        btn_calc = tk.Button(top_frame, text="Belleğe Yaz (f fonksiyonu)", command=self.write_to_memory, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), relief="groove")
        btn_calc.grid(row=0, column=4, padx=15, pady=10)
        
        # ORTA PANEL: Bellek Hücreleri Matrisi
        self.mid_frame = tk.LabelFrame(root, text=" Bellek Matrisi (Yapay hata enjekte etmek için bitlere tıklayın) ", font=("Arial", 11, "bold"), bg="#F5F5F5", fg="#333333")
        self.mid_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Kaydırılabilir alan desteği (Çünkü 32-bit modunda 38 buton ekrana sığmayabilir)
        self.canvas = tk.Canvas(self.mid_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.mid_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=scrollbar.set)
        
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(fill="x", side="bottom")
        
        # ALT PANEL: Sonuçlar, Sendrom Kelimesi ve Error Signal
        bottom_frame = tk.LabelFrame(root, text=" Karşılaştırıcı ve Düzeltici Çıktıları (Compare & Corrector) ", font=("Arial", 11, "bold"), bg="#F5F5F5", fg="#333333")
        bottom_frame.pack(fill="x", padx=15, pady=10)
        
        # Grid ayarları
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        
        btn_check = tk.Button(bottom_frame, text="Bellekten Oku ve Kontrol Et", command=self.read_and_check, bg="#2196F3", fg="white", font=("Arial", 11, "bold"), height=2, relief="groove")
        btn_check.grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="nesw")
        
        self.lbl_syndrome = tk.Label(bottom_frame, text="Sendrom Kelimesi: --", font=("Courier", 12, "bold"), bg="#F5F5F5", fg="#333333")
        self.lbl_syndrome.grid(row=1, column=0, pady=10, padx=10, sticky="w")
        
        self.lbl_signal = tk.Label(bottom_frame, text="Error Signal: --", font=("Arial", 12, "bold"), bg="#F5F5F5", fg="gray")
        self.lbl_signal.grid(row=1, column=1, pady=10, padx=10, sticky="e")
        
        self.lbl_data_out = tk.Label(bottom_frame, text="Data Out: --", font=("Courier", 14, "bold"), bg="#F5F5F5", fg="#000000")
        self.lbl_data_out.grid(row=2, column=0, columnspan=2, pady=15)
        
        # Bilgilendirme Etiketi
        info_lbl = tk.Label(root, text="Mavi: Parite Bitleri (K)  |  Yeşil: Veri Bitleri (M)", font=("Arial", 9, "italic"), bg="#F5F5F5", fg="#555555")
        info_lbl.pack(pady=2)

    def on_mode_change(self, event):
        """Kullanıcı modu değiştirdiğinde giriş alanını temizler ve örnek veri atar."""
        mode = self.combo_mode.get()
        self.entry_data.delete(0, tk.END)
        if mode == "8-Bit":
            self.entry_data.insert(0, "10110010")
        elif mode == "16-Bit":
            self.entry_data.insert(0, "1101001010110001")
        elif mode == "32-Bit":
            self.entry_data.insert(0, "11010010101100011011110011000011")
        
        # Belleği ve eski sonuçları sıfırla
        self.memory_bits = []
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.clear_results()

    def clear_results(self):
        self.lbl_syndrome.config(text="Sendrom Kelimesi: --")
        self.lbl_signal.config(text="Error Signal: --", fg="gray")
        self.lbl_data_out.config(text="Data Out: --")

    def write_to_memory(self):
        mode = self.combo_mode.get()
        M, _, _ = get_hamming_config(mode)
        input_str = self.entry_data.get().strip()
        
        # Giriş doğrulama
        if len(input_str) != M or not all(c in '01' for c in input_str):
            messagebox.showerror("Giriş Hatası", f"Lütfen seçilen mod için tam olarak {M} bitlik '0' veya '1' içeren değer girin.")
            return
            
        data_bits = [int(b) for b in input_str]
        # Arka plandaki f fonksiyonu tetiklenir
        self.memory_bits = calculate_hamming(data_bits, mode)
        
        # Görsel matrisi güncelle
        self.refresh_memory_ui()
        self.clear_results()
        
    def refresh_memory_ui(self):
        # Eski buton yapılarını temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        mode = self.combo_mode.get()
        _, K, _ = get_hamming_config(mode)
        
        for i, bit_val in enumerate(self.memory_bits):
            bit_pos = i + 1 # 1 tabanlı gerçek donanım adresi
            
            # Bit parite mi yoksa veri mi renk kodlaması yap
            if is_power_of_two(bit_pos):
                color = "#BBDEFB" # Parite bitleri soft mavi
                lbl_text = f"P{bit_pos}\n[{bit_val}]"
            else:
                color = "#C8E6C9" # Veri bitleri soft yeşil
                lbl_text = f"D{bit_pos}\n[{bit_val}]"
                
            # Her bite tıklandığında o biti ters çeviren (Yapay hata enjeksiyonu) buton tasarla
            btn = tk.Button(self.scrollable_frame, text=lbl_text, bg=color, activebackground="#FFCDD2",
                            font=("Courier", 10, "bold"), width=6, height=3, relief="raised",
                            command=lambda idx=i: self.toggle_bit(idx))
            
            # 32 bit modunda butonları alt alta bölmemek için yan yana dizer, kaydırma çubuğu ile gezilir
            btn.grid(row=0, column=i, padx=3, pady=15)

    def toggle_bit(self, idx):
        """Kullanıcının tıkladığı bit hücresinde yapay hata oluşturur."""
        if not self.memory_bits:
            return
        self.memory_bits[idx] = 1 if self.memory_bits[idx] == 0 else 0
        self.refresh_memory_ui()

    def read_and_check(self):
        if not self.memory_bits:
            messagebox.showwarning("Uyarı", "Bellekte veri bulunamadı! Önce 'Belleğe Yaz' butonuna basın.")
            return
            
        mode = self.combo_mode.get()
        _, K, _ = get_hamming_config(mode)
        
        # Karşılaştırma ve Düzeltme motorunu çalıştır
        has_error, error_idx, clean_data, syndrome = check_and_correct(self.memory_bits, mode)
        
        # 1. Sendrom Kelimesini binary formatta göster (K uzunluğunda sıfır doldurarak)
        syndrome_bin = bin(syndrome)[2:].zfill(K)
        self.lbl_syndrome.config(text=f"Sendrom Kelimesi: {syndrome_bin} (Konum: {syndrome})")
        
        # 2. Şemadaki Error Signal ve durum tespiti
        if has_error:
            self.lbl_signal.config(text=f"Error Signal: ⚠ HATA TESPİT EDİLDİ (Bit {error_idx})", fg="#D32F2F")
            messagebox.showinfo("Hata Düzeltildi", f"Sendrom kelimesinden ({syndrome_bin}) yola çıkılarak {error_idx}. pozisyondaki yapay hata başarıyla teyit edildi ve otomatik düzeltildi.")
        else:
            self.lbl_signal.config(text="Error Signal: ✓ VERİ TEMİZ (Hata Yok)", fg="#388E3C")
            
        # 3. Data Out kısmında düzeltilmiş veriyi yazdır
        clean_data_str = "".join(str(b) for b in clean_data)
        self.lbl_data_out.config(text=f"Data Out (Çıktı): {clean_data_str}")
        
        # Düzeltmeden sonra arayüzdeki bellek görselini de eski orijinal haline getir
        if has_error:
            self.refresh_memory_ui()

# ==========================================
# 3. UYGULAMA BAŞLATICI
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = HammingSimulatorGUI(root)
    root.mainloop()