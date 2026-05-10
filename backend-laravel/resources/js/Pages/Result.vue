<script setup>
import { ref, computed, onMounted } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import { Bar, Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

const props = defineProps({
    recommendations: {
        type: Array,
        required: true
    },
    analysis: {
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
</script>

<template>
    <Head title="Hasil Rekomendasi" />

    <div class="min-h-screen bg-[#f4f7ff] font-sans pb-12">
        <!-- Header -->
        <header class="pt-12 pb-8 text-center px-4">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Hasil Rekomendasi Smartphone</h1>
            <p class="text-gray-500">Menggunakan metode CRITIC-MOORA Decision Support System</p>
        </header>

        <main class="max-w-6xl mx-auto px-4">
            
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

            <!-- TAB CONTEN: REKOMENDASI -->
            <div v-show="activeTab === 'Rekomendasi'" class="space-y-6">
                
                <!-- Chart Section -->
                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <h2 class="text-lg font-bold text-gray-800 mb-6">Top 10 Rekomendasi - Grafik Skor</h2>
                    <div class="h-72">
                        <Bar :data="chartData" :options="chartOptions" />
                    </div>
                </section>

                <!-- Cards List Section -->
                <section class="space-y-4">
                    <div 
                        v-for="(hp, index) in recommendations" :key="hp.Nama_HP"
                        class="bg-white p-5 rounded-2xl shadow-sm border border-indigo-200 flex flex-col md:flex-row gap-6 transition-hover hover:shadow-md"
                    >
                        <!-- Left: Rank & Compare -->
                        <div class="flex flex-col items-center justify-center min-w-[80px] border-b md:border-b-0 md:border-r border-gray-100 pb-4 md:pb-0 md:pr-4">
                            <!-- Trophy Icon Color based on rank -->
                            <svg :class="['w-8 h-8 mb-1', index === 0 ? 'text-yellow-400' : (index === 1 ? 'text-gray-400' : (index === 2 ? 'text-amber-600' : 'text-indigo-300'))]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
                            <span class="text-sm text-gray-500 font-semibold mb-3">Rank {{ index + 1 }}</span>
                            
                            <label class="flex flex-col items-center cursor-pointer">
                                <input type="checkbox" :value="hp.Nama_HP" @change="toggleCompare(hp.Nama_HP)" class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
                                <span class="text-xs text-gray-400 mt-1">Compare</span>
                            </label>
                        </div>

                        <!-- Right: HP Details -->
                        <div class="flex-1">
                            <div class="flex flex-wrap items-center gap-3 mb-1">
                                <div class="bg-indigo-600 p-2 rounded-lg text-white">📱</div>
                                <h3 class="text-xl font-bold text-gray-900">{{ hp.Nama_HP }}</h3>
                                <span class="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">{{ hp.Brand }}</span>
                            </div>
                            <p class="text-sm text-gray-500 mb-4">MOORA Score: <span class="font-bold text-gray-700">{{ hp.Nilai_Optimasi_Yi.toFixed(4) }}</span></p>

                            <!-- Spesifikasi Grid (C1 - C9) -->
                            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-y-4 gap-x-2 text-sm">
                                
                                <div>
                                    <p class="text-green-600 flex items-center gap-1 font-semibold text-xs"><span class="text-base">$</span> Harga (C1)</p>
                                    <p class="font-bold text-gray-900 mt-0.5">Rp {{ hp.C1.toLocaleString('id-ID') }}</p>
                                </div>

                                <div>
                                    <p class="text-purple-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">📸</span> Kamera (C5)</p>
                                    <p class="font-bold text-gray-900 mt-0.5">{{ hp.C5 }} MP</p>
                                </div>

                                <div>
                                    <p class="text-blue-500 flex items-center gap-1 font-semibold text-xs"><span class="text-base">💾</span> RAM (C2)</p>
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

            <!-- TAB CONTENT: ANALISIS -->
            <div v-show="activeTab === 'Analisis'" class="space-y-6">
                
                <!-- Bobot Kriteria Card -->
                <section class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <h2 class="text-lg font-bold text-gray-800 mb-6">Bobot Kriteria (CRITIC Method)</h2>
                    <div class="h-72">
                        <Bar :data="bobotChartData" :options="bobotChartOptions" />
                    </div>
                </section>

                <!-- Distribusi Skor Card -->
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

                <!-- Cari Rekomendasi Baru Button -->
                <div class="flex justify-center mt-6">
                    <Link href="/" class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-8 rounded-xl transition-colors flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                        Cari Rekomendasi Baru
                    </Link>
                </div>
            </div>

            <!-- Tab Perhitungan, Perbandingan akan diisi pada iterasi berikutnya -->
            <div v-show="activeTab !== 'Rekomendasi' && activeTab !== 'Analisis'" class="bg-white p-12 text-center rounded-2xl shadow-sm border border-gray-200">
                <p class="text-gray-500">Konten untuk tab {{ activeTab }} sedang dalam pengembangan.</p>
            </div>

        </main>
    </div>
</template>
