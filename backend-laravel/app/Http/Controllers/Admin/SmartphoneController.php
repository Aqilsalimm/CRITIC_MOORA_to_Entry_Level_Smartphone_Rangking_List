<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Smartphone;
use App\Services\CsvSyncService;
use Illuminate\Http\Request;
use Inertia\Inertia;

class SmartphoneController extends Controller
{
    public function index()
    {
        return Inertia::render('Admin/Dashboard', [
            'smartphones' => Smartphone::latest()->get()
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'Nama_HP' => 'required',
            'Brand' => 'required',
            'C1' => 'required|numeric',
            'C2' => 'required|numeric',
            'C3' => 'required|numeric',
            'C4' => 'required|numeric',
            'C5' => 'required|numeric',
            'C6' => 'required|numeric',
            'C7' => 'required|integer|in:1,2',
            'C8' => 'required|integer|in:1,2',
            'C9' => 'required|integer|between:1,4',
        ]);

        Smartphone::create($validated);
        
        // Trigger Sinkronisasi CSV
        CsvSyncService::sync();

        return redirect()->back()->with('message', 'Data berhasil ditambahkan & CSV diperbarui!');
    }

    public function destroy(Smartphone $smartphone)
    {
        $smartphone->delete();
        CsvSyncService::sync();
        return redirect()->back()->with('message', 'Data berhasil dihapus!');
    }

    public function upload(Request $request)
    {
        $request->validate([
            'file' => 'required|file|mimes:csv,txt'
        ]);

        $file = $request->file('file');
        $handle = fopen($file->getRealPath(), 'r');
        
        // Skip header
        fgetcsv($handle);
        
        // Truncate table to overwrite
        Smartphone::truncate();

        while (($data = fgetcsv($handle)) !== FALSE) {
            if (count($data) < 11) continue;

            Smartphone::create([
                'Nama_HP' => $data[0],
                'Brand' => $data[1],
                'C1' => (float)$data[2],
                'C2' => (float)$data[3],
                'C3' => (float)$data[4],
                'C4' => (float)$data[5],
                'C5' => (float)$data[6],
                'C6' => (float)$data[7],
                'C7' => (int)$data[8],
                'C8' => (int)$data[9],
                'C9' => (int)$data[10],
            ]);
        }

        fclose($handle);

        // Trigger Sinkronisasi CSV
        CsvSyncService::sync();

        return redirect()->back()->with('message', 'Dataset berhasil diperbarui dari CSV!');
    }
}
