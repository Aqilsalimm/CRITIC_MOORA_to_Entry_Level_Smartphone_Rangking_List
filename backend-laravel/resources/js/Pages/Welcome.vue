<script setup>
import { ref } from 'vue';
import { Head, useForm } from '@inertiajs/vue3';

const props = defineProps({
    recommendations: Array,
    error: String
});

// Daftar Brand sesuai desain
const brands = ['Apple', 'Asus', 'Google', 'Honor', 'Motorola', 'Nothing', 'OnePlus', 'Oppo', 'POCO', 'Realme', 'Samsung', 'Sony', 'Vivo', 'Xiaomi', 'ZTE', 'ITEL', 'Infinix', 'Techno', 'itel', 'Tecno', 'Moto', 'Nubia ', 'Iqoo', 'Advan'];

// Mapping Kriteria ke variabel C1-C9 sesuai permintaan user
const availableCriteria = [
    { id: 'C1', title: 'Harga Terjangkau', desc: 'Harga lebih murah diprioritaskan', icon: '💲' },
    { id: 'C2', title: 'RAM Besar', desc: 'Kapasitas RAM besar', icon: '💾' },
    { id: 'C3', title: 'Penyimpanan Besar', desc: 'Kapasitas storage besar', icon: '🗂️' },
    { id: 'C4', title: 'Chipset Kuat', desc: 'Skor AnTuTu performa tinggi', icon: '🚀' },
    { id: 'C5', title: 'Kamera Megapixel', desc: 'Kamera megapixel tinggi', icon: '📸' },
    { id: 'C6', title: 'Baterai Besar', desc: 'Kapasitas baterai besar (mAh)', icon: '🔋' },
    { id: 'C7', title: 'Tipe Penyimpanan Cepat', desc: 'UFS lebih cepat dari eMMC', icon: '⚡' },
    { id: 'C8', title: 'Tipe Layar Bagus', desc: 'AMOLED > IPS > TFT', icon: '📱' },
    { id: 'C9', title: 'Resolusi Tinggi', desc: 'Resolusi layar lebih tajam', icon: '🖥️' },
];

const form = useForm({
    min_price: 0,
    max_price: 3000000, // Format Rupiah sesuai permintaan
    selected_brands: [],
    selected_criteria: []
});

// Fungsi Toggle Brand
const toggleBrand = (brand) => {
    const index = form.selected_brands.indexOf(brand);
    if (index > -1) form.selected_brands.splice(index, 1);
    else form.selected_brands.push(brand);
};

// Fungsi Mencegah pemilihan lebih dari 3 kriteria
const checkLimit = (event, id) => {
    if (form.selected_criteria.length > 3) {
        form.selected_criteria = form.selected_criteria.filter(item => item !== id);
        alert('Anda hanya dapat memilih maksimal 3 kriteria fokus!');
    }
};

const submitForm = () => {
    if (form.selected_criteria.length === 0) {
        alert('Pilih minimal 1 kriteria fokus!');
        return;
    }
    form.post('/rekomendasi', { preserveScroll: true });
};
</script>

<template>
    <Head title="Sistem Rekomendasi Smartphone" />

    <div class="min-h-screen bg-[#f8f9fc] font-sans pb-12">
        <!-- Header -->
        <header class="pt-16 pb-10 text-center px-4">
            <div class="w-16 h-20 mx-auto bg-white border-4 border-indigo-600 rounded-xl mb-6 relative">
                <div class="absolute bottom-2 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-indigo-600 rounded-full"></div>
            </div>
            <h1 class="text-3xl font-bold text-gray-900 mb-3">Sistem Rekomendasi Smartphone</h1>
            <p class="text-gray-500 max-w-3xl mx-auto">
                Pilih kriteria kebutuhan Anda untuk mendapatkan rekomendasi smartphone terbaik menggunakan metode CRITIC-MOORA Decision Support System
            </p>
        </header>

        <main class="max-w-5xl mx-auto px-4 space-y-6">
            
            <!-- Section 1: Filter & Preferensi -->
            <section class="bg-white p-6 rounded-2xl shadow-sm border border-indigo-100">
                <div class="flex items-center gap-2 mb-6">
                    <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                    <h2 class="text-lg font-bold text-gray-800">Filter & Preferensi</h2>
                </div>

                <!-- Slider Harga -->
                <div class="mb-8">
                    <div class="flex justify-between text-sm font-medium text-gray-700 mb-4">
                        <span>Maksimal Harga: Rp {{ form.max_price.toLocaleString('id-ID') }}</span>
                    </div>
                    <input 
                        type="range" 
                        min="500000" max="3000000" step="100000"
                        v-model="form.max_price"
                        class="w-full h-2 bg-indigo-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    >
                </div>

                <!-- Filter Brand -->
                <div>
                    <p class="text-sm font-medium text-gray-700 mb-3">Filter Brand (Opsional):</p>
                    <div class="flex flex-wrap gap-2">
                        <button 
                            v-for="brand in brands" :key="brand"
                            @click="toggleBrand(brand)"
                            type="button"
                            :class="[
                                'px-4 py-1.5 rounded-full text-sm border transition-all',
                                form.selected_brands.includes(brand) 
                                    ? 'bg-indigo-600 text-white border-indigo-600' 
                                    : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300'
                            ]"
                        >
                            {{ brand }}
                        </button>
                    </div>
                </div>
            </section>

            <!-- Section 2: Kriteria -->
            <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                <!-- Header Section -->
                <div class="flex items-center gap-2 mb-6">
                    <div class="bg-green-100 rounded-full p-1 text-green-600">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    <h2 class="text-lg font-bold text-gray-800">Pilih Kriteria Kebutuhan:</h2>
                </div>

                <!-- Grid Card Checkbox -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    <label 
                        v-for="item in availableCriteria" :key="item.id"
                        class="relative flex items-start gap-4 p-4 rounded-xl border transition-all cursor-pointer select-none"
                        :class="form.selected_criteria.includes(item.id) ? 'border-indigo-600 bg-indigo-50/10' : 'border-gray-200 hover:border-gray-300'"
                    >
                        <input 
                            type="checkbox" 
                            :value="item.id"
                            v-model="form.selected_criteria"
                            @change="checkLimit($event, item.id)"
                            class="absolute opacity-0 w-0 h-0"
                        >

                        <!-- Custom Checkbox UI -->
                        <div :class="[
                            'w-5 h-5 mt-0.5 rounded border flex items-center justify-center shrink-0 transition-colors',
                            form.selected_criteria.includes(item.id) ? 'bg-indigo-600 border-indigo-600' : 'border-gray-300 bg-white'
                        ]">
                            <svg v-if="form.selected_criteria.includes(item.id)" class="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                        </div>
                        
                        <!-- Text Content -->
                        <div>
                            <div class="font-bold text-gray-800 flex items-center gap-2">
                                <span>{{ item.icon }}</span> {{ item.title }}
                            </div>
                            <p class="text-sm text-gray-500 mt-1">{{ item.desc }}</p>
                        </div>
                    </label>

                </div>
            </section>

            <!-- Submit Button -->
            <button 
                @click="submitForm"
                :disabled="form.processing"
                class="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-4 rounded-xl transition-colors flex items-center justify-center gap-2"
            >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                {{ form.processing ? 'Menganalisis...' : 'Analisis & Dapatkan Rekomendasi' }}
            </button>

            <!-- Info Footer -->
            <div class="bg-blue-50/50 p-5 rounded-xl border border-blue-100 flex gap-3 text-sm text-blue-800">
                <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <div>
                    <span class="font-bold">Tentang Sistem:</span>
                    <ul class="list-disc ml-4 mt-1 space-y-1">
                        <li><b>CRITIC:</b> Menghitung bobot kriteria secara objektif berdasarkan standar deviasi dan korelasi antar kriteria</li>
                        <li><b>MOORA:</b> Menghasilkan ranking smartphone berdasarkan multi-objective optimization</li>
                    </ul>
                </div>
            </div>

            <!-- Hasil Tampil Disini -->
            <div v-if="recommendations && recommendations.length > 0" class="mt-10">
                <h3 class="text-2xl font-bold text-gray-900 mb-6">Top Rekomendasi Untuk Anda</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div v-for="hp in recommendations" :key="hp.ranking" class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between">
                        <div>
                            <div class="flex justify-between items-start mb-4">
                                <div>
                                    <span class="text-xs font-bold text-indigo-600 uppercase">{{ hp.brand }}</span>
                                    <h4 class="text-xl font-bold text-gray-900">{{ hp.type }}</h4>
                                </div>
                                <span class="bg-indigo-100 text-indigo-700 text-xs font-bold px-2.5 py-1 rounded-full">Rank #{{ hp.ranking }}</span>
                            </div>
                            <div class="space-y-2 text-sm text-gray-600">
                                <div class="flex justify-between"><span>Harga:</span><span class="font-semibold text-gray-900">Rp {{ hp.harga.toLocaleString('id-ID') }}</span></div>
                                <div class="flex justify-between"><span>RAM:</span><span class="font-semibold text-gray-900">{{ hp.ram }} GB</span></div>
                                <div class="flex justify-between"><span>Storage:</span><span class="font-semibold text-gray-900">{{ hp.storage }} GB</span></div>
                            </div>
                        </div>
                        <div class="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center text-xs">
                            <span class="text-gray-500">Skor Optimasi:</span>
                            <span class="font-bold text-indigo-600">{{ hp.skor_optimasi.toFixed(4) }}</span>
                        </div>
                    </div>
                </div>
            </div>

        </main>
    </div>
</template>
