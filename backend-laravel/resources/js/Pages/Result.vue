<script setup>
import { ref, computed, onMounted } from 'vue';
import { Head, Link, router } from '@inertiajs/vue3';
import { Bar, Line, Radar } from 'vue-chartjs'; // Tambahkan Radar
import { 
    Chart as ChartJS, Title, Tooltip, Legend, BarElement, 
    CategoryScale, LinearScale, PointElement, LineElement,
    RadialLinearScale, Filler // Tambahkan RadialLinearScale & Filler untuk Radar
} from 'chart.js';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

ChartJS.register(
    Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, 
    PointElement, LineElement, RadialLinearScale, Filler
);

const props = defineProps({
    recommendations: {
        type: Array,
        required: true
    },
    analysis: {
        type: Object,
        default: () => ({})
    },
    calculationData: {
        type: Object,
        default: () => ({})
    }
});

const criteriaLabels = {
    'C1': 'affordablePrice',
    'C2': 'largeRam',
    'C3': 'largeRom',
    'C4': 'strongChipset',
    'C5': 'camera',
    'C6': 'largeBattery',
    'C7': 'fastRom',
    'C8': 'goodLcd',
    'C9': 'highResolution'
};

const bobotChartData = computed(() => {
    if (!props.analysis || !props.analysis.selected_weights) return { labels: [], datasets: [] };
    
    const labels = props.analysis.selected_weights.map(w => criteriaLabels[w.id] || w.id);
    const data = props.analysis.selected_weights.map(w => w.weight);
    
    return {
        labels: labels,
        datasets: [{
            label: 'Bobot (%)',
            backgroundColor: '#8b5cf6', // Purple-500 matching the image
            data: data,
            borderRadius: 4,
        }]
    };
});

const bobotChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y', // Makes it horizontal
    plugins: {
        legend: { position: 'bottom' }
    },
    scales: {
        x: { beginAtZero: true, grid: { borderDash: [5, 5] } },
        y: { grid: { display: false } }
    }
};

const skorChartData = computed(() => ({
    labels: props.recommendations.map(hp => hp.Nama_HP),
    datasets: [{
        label: 'Skor',
        borderColor: '#6366f1', // Indigo-500
        backgroundColor: '#6366f1',
        data: props.recommendations.map(hp => hp.Nilai_Optimasi_Yi),
        fill: false,
        tension: 0.1
    }]
}));

const skorChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { position: 'bottom' }
    },
    scales: {
        y: { beginAtZero: true, grid: { borderDash: [5, 5] } },
        x: { grid: { display: false } }
    }
};

// Tab Management
const activeTab = ref('Rekomendasi');
const tabs = ['Rekomendasi', 'Analisis', 'Perhitungan', 'Perbandingan'];

// State untuk fitur Compare (Maks 3 HP)
const selectedToCompare = ref([]);

const toggleCompare = (id) => {
    const index = selectedToCompare.value.indexOf(id);
    if (index > -1) {
        selectedToCompare.value.splice(index, 1);
    } else {
        if (selectedToCompare.value.length < 3) selectedToCompare.value.push(id);
        else alert('Maksimal membandingkan 3 Smartphone!');
    }
};

// ==========================================
// LOGIKA TAB PERBANDINGAN
// ==========================================

// 1. Mengambil data utuh dari HP yang dicentang
const comparedPhones = computed(() => {
    return props.recommendations.filter(hp => selectedToCompare.value.includes(hp.Nama_HP));
});

// 2. Data untuk Radar Chart (Visualisasi)
const radarChartData = computed(() => {
    const phones = comparedPhones.value;
    if (phones.length === 0) return { labels: [], datasets: [] };

    // Label radar chart
    const labels = ['Harga (Murah)', 'RAM', 'Storage', 'AnTuTu', 'Kamera', 'Baterai'];
    
    // Palet warna sesuai gambar (Indigo, Merah, Hijau)
    const colors = [
        { border: '#4f46e5', bg: 'rgba(79, 70, 229, 0.2)' }, // Galaxy S24
        { border: '#ef4444', bg: 'rgba(239, 68, 68, 0.2)' }, // Redmi
        { border: '#10b981', bg: 'rgba(16, 185, 129, 0.2)' }  // ROG
    ];

    // Mencari nilai Maksimal/Minimal dari top 10 untuk skala 0-100% di Radar Chart
    const minC1 = Math.min(...props.recommendations.map(hp => hp.C1));
    const maxC2 = Math.max(...props.recommendations.map(hp => hp.C2));
    const maxC3 = Math.max(...props.recommendations.map(hp => hp.C3));
    const maxC4 = Math.max(...props.recommendations.map(hp => hp.C4));
    const maxC5 = Math.max(...props.recommendations.map(hp => hp.C5));
    const maxC6 = Math.max(...props.recommendations.map(hp => hp.C6));

    const datasets = phones.map((hp, index) => {
        const cColor = colors[index % colors.length];
        return {
            label: hp.Nama_HP,
            backgroundColor: cColor.bg,
            borderColor: cColor.border,
            pointBackgroundColor: cColor.border,
            fill: true,
            data: [
                (minC1 / hp.C1) * 100, // C1 (Cost): Semakin murah = Semakin tinggi nilainya (dibalik)
                (hp.C2 / maxC2) * 100, // C2 (Benefit): Nilai mentah / Max * 100
                (hp.C3 / maxC3) * 100,
                (hp.C4 / maxC4) * 100,
                (hp.C5 / maxC5) * 100,
                (hp.C6 / maxC6) * 100
            ]
        };
    });

    return { labels, datasets };
});

const radarChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'bottom' } },
    scales: {
        r: {
            beginAtZero: true,
            max: 100,
            ticks: { display: false } // Menyembunyikan angka 0-100 agar mirip desain asli
        }
    }
};

const goBack = () => {
    router.get('/');
};

// Konfigurasi Chart.js mengambil data MOORA Score
const chartData = computed(() => ({
    labels: props.recommendations.map(hp => hp.Nama_HP),
    datasets: [{
        label: 'Skor MOORA',
        backgroundColor: '#4f46e5', // Indigo-600 Tailwind
        data: props.recommendations.map(hp => hp.Nilai_Optimasi_Yi),
        borderRadius: 4,
    }]
}));

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { position: 'bottom' }
    },
    scales: {
        y: { beginAtZero: true, grid: { borderDash: [5, 5] } },
        x: { grid: { display: false } }
    }
};

// Helper Format Data Kualitatif (C7, C8, C9)
const formatStorageType = (val) => val === 2 ? 'UFS' : 'eMMC';
const formatLcdType = (val) => val === 2 ? 'AMOLED' : (val === 1 ? 'IPS/TFT' : 'Unknown');
const formatResolution = (val) => {
    if (val === 4) return '1.5K';
    if (val === 3) return 'FHD+';
    if (val === 2) return 'FHD';
    return 'HD+';
};

const isExporting = ref(false);

const downloadPDF = async () => {
    isExporting.value = true;
    const element = document.getElementById('report-content');
    
    try {
        const canvas = await html2canvas(element, {
            scale: 2,
            useCORS: true,
            logging: false,
        });

        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });

        const imgProps = pdf.getImageProperties(imgData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(`Laporan-Rekomendasi-${new Date().getTime()}.pdf`);
        
    } catch (error) {
        console.error("Gagal mengexport PDF:", error);
        alert("Terjadi kesalahan saat membuat PDF");
    } finally {
        isExporting.value = false;
    }
};
</script>

<template>
    <Head title="Hasil Rekomendasi" />

    <div class="min-h-screen bg-[#f4f7ff] font-sans pb-12">
        <!-- Header -->
        <header class="pt-12 pb-8 text-center px-4">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Hasil Rekomendasi Smartphone</h1>
            <p class="text-gray-500">Menggunakan metode CRITIC-MOORA Decision Support System</p>
        </header>

        <main class="max-w-6xl mx-auto px-4 mt-8">
            
            <!-- Tabs Navigation -->
            <div class="bg-gray-100/50 p-1 rounded-xl flex mb-8 overflow-x-auto">
                <button 
                    v-for="tab in tabs" :key="tab"
                    @click="activeTab = tab"
                    :class="[
                        'flex-1 py-3 px-6 text-sm font-semibold rounded-lg text-center transition-all whitespace-nowrap',
                        activeTab === tab ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    ]"
                >
                    {{ tab }}
                </button>
            </div>

            <div class="flex justify-end mb-4">
                <button 
                    @click="downloadPDF"
                    :disabled="isExporting"
                    class="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl shadow-md transition-all font-bold text-sm"
                >
                    <svg v-if="!isExporting" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    <span v-else class="animate-spin border-2 border-white border-t-transparent rounded-full w-4 h-4"></span>
                    {{ isExporting ? 'Memproses PDF...' : 'Download Laporan (PDF)' }}
                </button>
            </div>

            <!-- REPORT CONTENT WRAPPER -->
            <div id="report-content" class="bg-white p-8 rounded-2xl border border-gray-100 mb-8">
                
                <div class="border-b-2 border-indigo-600 pb-6 mb-8 text-center">
                    <h1 class="text-2xl font-bold text-gray-900 uppercase">Laporan Hasil Rekomendasi Smartphone</h1>
                    <p class="text-gray-500 text-sm italic">Metode CRITIC-MOORA Decision Support System</p>
                    <p class="text-xs text-gray-400 mt-2">Dicetak pada: {{ new Date().toLocaleString('id-ID') }}</p>
                </div>

                <div class="space-y-10">
                    
                    <!-- TAB CONTENT: REKOMENDASI -->
                    <div v-if="activeTab === 'Rekomendasi' || isExporting" class="space-y-6">
                        
                        <!-- Chart Section -->
                        <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                            <h2 class="text-lg font-bold text-gray-800 mb-6">Top 10 Rekomendasi - Grafik Skor</h2>
                            <div class="h-64">
                                <Bar :data="chartData" :options="chartOptions" />
                            </div>
                        </section>

                        <!-- List Section -->
                        <section class="space-y-4">
                            <h2 class="text-lg font-bold text-gray-800 mb-4">Daftar Peringkat Smartphone</h2>
                            
                            <!-- Card Item -->
                            <div v-for="(hp, index) in recommendations" :key="hp.Nama_HP" class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow relative overflow-hidden">
                                <!-- Rank Badge -->
                                <div class="absolute top-0 left-0 w-12 h-12 bg-indigo-600 text-white flex items-center justify-center font-bold text-lg rounded-br-2xl">
                                    #{{ hp.Peringkat }}
                                </div>

                                <div class="ml-14">
                                    <!-- Header HP -->
                                    <div class="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-2">
                                        <div>
                                            <div class="flex items-center gap-2">
                                                <h3 class="text-xl font-bold text-gray-900">{{ hp.Nama_HP }}</h3>
                                                <span class="bg-indigo-100 text-indigo-700 text-xs font-bold px-2.5 py-1 rounded-full">{{ hp.Brand }}</span>
                                            </div>
                                            <p class="text-indigo-600 font-bold text-lg mt-1">Rp {{ hp.C1.toLocaleString('id-ID') }}</p>
                                        </div>
                                        
                                        <!-- Skor & Compare -->
                                        <div class="flex flex-col items-end gap-2">
                                            <div class="text-right">
                                                <p class="text-xs text-gray-500 font-medium">Skor MOORA</p>
                                                <p class="text-2xl font-bold text-indigo-600">{{ hp.Nilai_Optimasi_Yi.toFixed(4) }}</p>
                                            </div>
                                            
                                            <!-- Checkbox Compare -->
                                            <label class="flex items-center gap-2 cursor-pointer">
                                                <input 
                                                    type="checkbox" 
                                                    :checked="selectedToCompare.includes(hp.Nama_HP)"
                                                    @change="toggleCompare(hp.Nama_HP)"
                                                    class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                                                >
                                                <span class="text-sm font-medium text-gray-600">Compare</span>
                                            </label>
                                        </div>
                                    </div>

                                    <!-- Grid Spesifikasi -->
                                    <div class="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-6 border-t border-gray-100 pt-4">
                                        <div>
                                            <p class="text-blue-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">📸</span> Kamera (C5)</p>
                                            <p class="font-bold text-gray-900 mt-0.5">{{ hp.C5 }} MP</p>
                                        </div>

                                        <div>
                                            <p class="text-violet-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">📟</span> RAM (C2)</p>
                                            <p class="font-bold text-gray-900 mt-0.5">{{ hp.C2 }} GB</p>
                                        </div>

                                        <div>
                                            <p class="text-orange-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">🗂️</span> Storage (C3)</p>
                                            <p class="font-bold text-gray-900 mt-0.5">{{ hp.C3 }} GB</p>
                                        </div>

                                        <div>
                                            <p class="text-red-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">🚀</span> AnTuTu (C4)</p>
                                            <p class="font-bold text-gray-900 mt-0.5">{{ hp.C4.toLocaleString('id-ID') }}</p>
                                        </div>

                                        <div>
                                            <p class="text-emerald-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">🔋</span> Baterai (C6)</p>
                                            <p class="font-bold text-gray-900 mt-0.5">{{ hp.C6 }} mAh</p>
                                        </div>

                                        <div>
                                            <p class="text-indigo-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">⚡</span> Tipe ROM (C7)</p>
                                            <p class="font-bold text-gray-900 mt-0.5">{{ formatStorageType(hp.C7) }}</p>
                                        </div>

                                        <div>
                                            <p class="text-cyan-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">📱</span> Panel Layar (C8)</p>
                                            <p class="font-bold text-gray-900 mt-0.5">{{ formatLcdType(hp.C8) }}</p>
                                        </div>

                                        <div>
                                            <p class="text-pink-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">📺</span> Resolusi (C9)</p>
                                            <p class="font-bold text-gray-900 mt-0.5">{{ formatResolution(hp.C9) }}</p>
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </section>
                    </div>

                    <!-- TAB CONTENT: PERBANDINGAN -->
                    <div v-if="activeTab === 'Perbandingan' || isExporting" class="space-y-6">
                        <section class="bg-white p-6 md:p-10 rounded-2xl shadow-sm border border-gray-200">
                            <h2 class="text-xl font-bold text-gray-800 mb-1">Perbandingan Smartphone (Pilih maksimal 3)</h2>
                            <p class="text-sm text-gray-500 mb-10">{{ selectedToCompare.length }} smartphone dipilih untuk perbandingan</p>

                            <div v-if="selectedToCompare.length === 0" class="flex flex-col items-center justify-center py-16 text-gray-400">
                                <svg class="w-16 h-16 mb-4 text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                                <p class="font-medium text-gray-500">Belum ada smartphone yang dipilih.</p>
                                <p class="text-sm">Silakan centang opsi "Compare" pada Tab Rekomendasi.</p>
                            </div>

                            <div v-else>
                                
                                <div class="h-[400px] mb-12">
                                    <Radar :data="radarChartData" :options="radarChartOptions" />
                                </div>

                                <div class="overflow-x-auto rounded-xl border border-gray-200">
                                    <table class="w-full text-sm text-left text-gray-600">
                                        <thead class="text-xs text-gray-800 bg-gray-50 uppercase font-bold">
                                            <tr>
                                                <th scope="col" class="px-6 py-4 border-b border-r border-gray-200 w-1/4">Spesifikasi</th>
                                                <th v-for="hp in comparedPhones" :key="'head-'+hp.Nama_HP" scope="col" class="px-6 py-4 border-b border-gray-200 text-center">{{ hp.Nama_HP }}</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr class="bg-white">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Rank</td>
                                                <td v-for="hp in comparedPhones" :key="'rank-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">#{{ hp.Peringkat }}</td>
                                            </tr>
                                            <tr class="bg-gray-50">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">MOORA Score</td>
                                                <td v-for="hp in comparedPhones" :key="'score-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center text-indigo-600 font-bold">{{ hp.Nilai_Optimasi_Yi.toFixed(4) }}</td>
                                            </tr>
                                            <tr class="bg-white">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Harga (C1)</td>
                                                <td v-for="hp in comparedPhones" :key="'c1-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">Rp {{ hp.C1.toLocaleString('id-ID') }}</td>
                                            </tr>
                                            <tr class="bg-gray-50">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Kamera (C5)</td>
                                                <td v-for="hp in comparedPhones" :key="'c5-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">{{ hp.C5 }} MP</td>
                                            </tr>
                                            <tr class="bg-white">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">RAM (C2)</td>
                                                <td v-for="hp in comparedPhones" :key="'c2-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">{{ hp.C2 }} GB</td>
                                            </tr>
                                            <tr class="bg-gray-50">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Storage (C3)</td>
                                                <td v-for="hp in comparedPhones" :key="'c3-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">{{ hp.C3 }} GB</td>
                                            </tr>
                                            <tr class="bg-white">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Chipset / AnTuTu (C4)</td>
                                                <td v-for="hp in comparedPhones" :key="'c4-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">{{ hp.C4.toLocaleString('id-ID') }}</td>
                                            </tr>
                                            <tr class="bg-gray-50">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Baterai (C6)</td>
                                                <td v-for="hp in comparedPhones" :key="'c6-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">{{ hp.C6 }} mAh</td>
                                            </tr>
                                            <tr class="bg-white">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Tipe Storage (C7)</td>
                                                <td v-for="hp in comparedPhones" :key="'c7-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">{{ formatStorageType(hp.C7) }}</td>
                                            </tr>
                                            <tr class="bg-gray-50">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Display Panel (C8)</td>
                                                <td v-for="hp in comparedPhones" :key="'c8-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">{{ formatLcdType(hp.C8) }}</td>
                                            </tr>
                                            <tr class="bg-white">
                                                <td class="px-6 py-4 border-b border-r border-gray-200 font-bold text-gray-900">Resolusi (C9)</td>
                                                <td v-for="hp in comparedPhones" :key="'c9-'+hp.Nama_HP" class="px-6 py-4 border-b border-gray-200 text-center">{{ formatResolution(hp.C9) }}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>

                            </div>
                        </section>
                        
                    </div>
                </div>

                <div class="mt-12 pt-6 border-t border-gray-100 text-center">
                    <p class="text-xs text-gray-400">Hasil ini bersifat rekomendasi berdasarkan algoritma DSS objektif.</p>
                </div>
            </div>

            <!-- Cari Rekomendasi Baru Button (Move outside report if needed or keep it) -->
            <div class="flex justify-center mt-8 mb-8">
                <button 
                    @click="goBack"
                    class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-xl shadow-lg transition-colors flex items-center gap-2"
                >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    Cari Rekomendasi Baru
                </button>
            </div>

            <!-- OTHER TABS (OUTSIDE REPORT) -->
            
            <!-- TAB CONTENT: ANALISIS -->
            <div v-show="activeTab === 'Analisis'" class="space-y-6">
                
                <!-- Bobot Kriteria Card -->
                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <h2 class="text-lg font-bold text-gray-800 mb-6">Bobot Kriteria (CRITIC Method)</h2>
                    <div class="h-72">
                        <Bar :data="bobotChartData" :options="bobotChartOptions" />
                    </div>
                </section>

                <!-- Distribusi Skor MOORA -->
                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <h2 class="text-lg font-bold text-gray-800 mb-6">Distribusi Skor MOORA</h2>
                    <div class="h-72">
                        <Line :data="skorChartData" :options="skorChartOptions" />
                    </div>
                </section>

                <!-- Bottom Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Kriteria yang Dipilih -->
                    <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                        <h2 class="text-lg font-bold text-gray-800 mb-6">Kriteria yang Dipilih</h2>
                        <div class="space-y-4">
                            <div v-for="w in (analysis.selected_weights || [])" :key="w.id" class="flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <div class="bg-green-100 p-1 rounded-full text-green-600">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                                    </div>
                                    <span class="text-sm font-medium text-gray-700">{{ criteriaLabels[w.id] || w.id }}</span>
                                </div>
                                <span class="bg-gray-100 text-gray-600 text-xs font-bold px-2.5 py-1 rounded-full">{{ w.weight }}%</span>
                            </div>
                        </div>
                    </section>

                    <!-- Statistik Data -->
                    <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                        <h2 class="text-lg font-bold text-gray-800 mb-6">Statistik Data</h2>
                        <div class="space-y-4 text-sm text-gray-600">
                            <div>
                                <p class="text-gray-500">Total Smartphone Dianalisis</p>
                                <p class="text-2xl font-bold text-gray-900">{{ analysis.stats ? analysis.stats.total_analyzed : 0 }}</p>
                            </div>
                            <div>
                                <p class="text-gray-500">Range Harga</p>
                                <p class="text-xl font-bold text-gray-900">
                                    Rp {{ (analysis.stats && analysis.stats.min_price) ? analysis.stats.min_price.toLocaleString('id-ID') : 0 }} - 
                                    Rp {{ (analysis.stats && analysis.stats.max_price) ? analysis.stats.max_price.toLocaleString('id-ID') : 0 }}
                                </p>
                            </div>
                            <div>
                                <p class="text-gray-500">Skor Tertinggi</p>
                                <p class="text-xl font-bold text-indigo-600">{{ analysis.stats ? analysis.stats.highest_score.toFixed(4) : '0.0000' }}</p>
                            </div>
                        </div>
                    </section>
                </div>
            </div>

            <!-- TAB CONTENT: PERHITUNGAN -->
            <div v-show="activeTab === 'Perhitungan'" class="space-y-6">
                
                <div class="bg-blue-50 border border-blue-200 p-5 rounded-xl text-sm">
                    <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-blue-600 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <div>
                            <h4 class="font-bold text-blue-900 mb-2">Tentang Metode CRITIC-MOORA</h4>
                            <p class="text-blue-800 mb-1"><b>CRITIC (CRiteria Importance Through Intercriteria Correlation):</b> Metode objektif untuk menghitung bobot kriteria berdasarkan standar deviasi dan korelasi antar kriteria.</p>
                            <p class="text-blue-800"><b>MOORA (Multi-Objective Optimization on the basis of Ratio Analysis):</b> Metode multi-kriteria untuk ranking alternatif berdasarkan benefit dan cost criteria.</p>
                        </div>
                    </div>
                </div>

                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">1</div>
                        <h3 class="text-lg font-bold text-gray-800">Filter Data</h3>
                    </div>
                    <p class="text-gray-500 text-sm mb-4 ml-11">Memfilter smartphone berdasarkan rentang harga dan brand yang dipilih.</p>
                    <pre class="bg-gray-50 p-4 rounded-xl text-sm text-gray-700 font-mono overflow-x-auto border border-gray-100">{{ JSON.stringify(calculationData?.step_1, null, 4) }}</pre>
                </section>

                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">2</div>
                        <h3 class="text-lg font-bold text-gray-800">Matriks Keputusan</h3>
                    </div>
                    <p class="text-gray-500 text-sm mb-4 ml-11">Membuat matriks keputusan awal dengan kriteria C1 - C9 (Mentah).</p>
                    <pre class="bg-gray-50 p-4 rounded-xl text-sm text-gray-700 font-mono overflow-x-auto border border-gray-100">{{ JSON.stringify(calculationData?.step_2, null, 4) }}</pre>
                </section>

                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">3</div>
                        <h3 class="text-lg font-bold text-gray-800">Normalisasi Matriks</h3>
                    </div>
                    <p class="text-gray-500 text-sm mb-4 ml-11">Normalisasi menggunakan metode Vector Normalization.</p>
                    <pre class="bg-gray-50 p-4 rounded-xl text-sm text-gray-700 font-mono overflow-x-auto border border-gray-100">{{ JSON.stringify(calculationData?.step_3, null, 4) }}</pre>
                </section>

                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">4</div>
                        <h3 class="text-lg font-bold text-gray-800">Perhitungan Bobot CRITIC</h3>
                    </div>
                    <p class="text-gray-500 text-sm mb-4 ml-11">Menghitung bobot kriteria menggunakan metode CRITIC (standard deviation × conflict measure).</p>
                    <pre class="bg-gray-50 p-4 rounded-xl text-sm text-gray-700 font-mono overflow-x-auto border border-gray-100">{{ JSON.stringify(calculationData?.step_4, null, 4) }}</pre>
                </section>

                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">5</div>
                        <h3 class="text-lg font-bold text-gray-800">Perhitungan MOORA</h3>
                    </div>
                    <p class="text-gray-500 text-sm mb-4 ml-11">Menghitung skor optimasi MOORA (Yi) berdasarkan Benefit dan Cost kriteria.</p>
                    <pre class="bg-gray-50 p-4 rounded-xl text-sm text-gray-700 font-mono overflow-x-auto border border-gray-100">{{ JSON.stringify(calculationData?.step_5, null, 4) }}</pre>
                </section>

                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">6</div>
                        <h3 class="text-lg font-bold text-gray-800">Ranking Final</h3>
                    </div>
                    <p class="text-gray-500 text-sm mb-4 ml-11">Mengurutkan smartphone berdasarkan skor MOORA (tertinggi ke terendah).</p>
                    <pre class="bg-gray-50 p-4 rounded-xl text-sm text-gray-700 font-mono overflow-x-auto border border-gray-100">{{ JSON.stringify(calculationData?.step_6, null, 4) }}</pre>
                </section>
                
            </div>

        </main>
    </div>
</template>
