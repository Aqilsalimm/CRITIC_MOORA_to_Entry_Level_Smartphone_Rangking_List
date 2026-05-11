<script setup>
import { ref } from 'vue';
import { useForm, router } from '@inertiajs/vue3';

const props = defineProps({ smartphones: Array });

const form = useForm({
    Nama_HP: '', Brand: '', C1: '', C2: '', C3: '', C4: '', C5: '', C6: '', C7: 1, C8: 1, C9: 1
});

const csvForm = useForm({
    file: null
});

const submit = () => {
    form.post(route('admin.smartphone.store'), {
        onSuccess: () => form.reset()
    });
};

const uploadCsv = () => {
    csvForm.post(route('admin.smartphone.upload'), {
        onSuccess: () => csvForm.reset()
    });
};

const deleteHp = (id) => {
    if(confirm('Hapus data ini?')) {
        router.delete(route('admin.smartphone.destroy', id));
    }
};
</script>

<template>
    <div class="p-8 bg-gray-50 min-h-screen">
        <div class="max-w-7xl mx-auto">
            <div class="flex justify-between items-center mb-8">
                <h1 class="text-2xl font-bold text-gray-800">Manajemen Dataset Smartphone</h1>
            </div>

            <!-- Form Upload CSV -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
                <h2 class="text-lg font-bold text-gray-800 mb-4">Upload Dataset CSV</h2>
                <form @submit.prevent="uploadCsv" class="flex items-center gap-4">
                    <input type="file" @input="csvForm.file = $event.target.files[0]" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" accept=".csv" required>
                    <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-indigo-700" :disabled="csvForm.processing">
                        Upload
                    </button>
                </form>
            </div>

            <!-- Form Tambah Data -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
                <h2 class="text-lg font-bold text-gray-800 mb-4">Tambah Smartphone Baru</h2>
                <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Nama HP</label>
                        <input v-model="form.Nama_HP" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Brand</label>
                        <input v-model="form.Brand" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Harga (C1)</label>
                        <input v-model.number="form.C1" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">RAM (C2) - GB</label>
                        <input v-model.number="form.C2" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Storage (C3) - GB</label>
                        <input v-model.number="form.C3" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">AnTuTu (C4)</label>
                        <input v-model.number="form.C4" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Kamera (C5) - MP</label>
                        <input v-model.number="form.C5" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Baterai (C6) - mAh</label>
                        <input v-model.number="form.C6" type="number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Tipe Storage (C7)</label>
                        <select v-model.number="form.C7" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                            <option :value="1">eMMC</option>
                            <option :value="2">UFS</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Tipe Layar (C8)</label>
                        <select v-model.number="form.C8" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                            <option :value="1">IPS</option>
                            <option :value="2">AMOLED</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Resolusi (C9)</label>
                        <select v-model.number="form.C9" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                            <option :value="1">HD+</option>
                            <option :value="2">FHD</option>
                            <option :value="3">FHD+</option>
                            <option :value="4">1.5K</option>
                        </select>
                    </div>
                    <div class="md:col-span-3 flex justify-end">
                        <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-indigo-700" :disabled="form.processing">
                            Simpan
                        </button>
                    </div>
                </form>
            </div>

            <!-- Tabel Data -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table class="w-full text-left text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 uppercase text-xs font-bold">
                        <tr>
                            <th class="px-6 py-4">Nama HP</th>
                            <th class="px-6 py-4">Brand</th>
                            <th class="px-6 py-4">Harga (C1)</th>
                            <th class="px-6 py-4">AnTuTu (C4)</th>
                            <th class="px-6 py-4 text-center">Aksi</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="hp in smartphones" :key="hp.id" class="hover:bg-gray-50">
                            <td class="px-6 py-4 font-medium text-gray-900">{{ hp.Nama_HP }}</td>
                            <td class="px-6 py-4 text-gray-500">{{ hp.Brand }}</td>
                            <td class="px-6 py-4">Rp {{ hp.C1.toLocaleString() }}</td>
                            <td class="px-6 py-4">{{ hp.C4 }}</td>
                            <td class="px-6 py-4 text-center">
                                <button @click="deleteHp(hp.id)" class="text-red-600 hover:underline">Hapus</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
