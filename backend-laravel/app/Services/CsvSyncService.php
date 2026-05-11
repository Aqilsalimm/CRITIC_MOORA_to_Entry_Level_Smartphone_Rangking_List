<?php

namespace App\Services;

use App\Models\Smartphone;

class CsvSyncService
{
    public static function sync()
    {
        $data = Smartphone::all(['Nama_HP', 'Brand', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']);
        
        // Header CSV
        $csvContent = "Nama_HP,Brand,C1,C2,C3,C4,C5,C6,C7,C8,C9\n";

        foreach ($data as $row) {
            $csvContent .= "{$row->Nama_HP},{$row->Brand},{$row->C1},{$row->C2},{$row->C3},{$row->C4},{$row->C5},{$row->C6},{$row->C7},{$row->C8},{$row->C9}\n";
        }

        // Tulis ke folder dss-engine/app (Sesuai dengan struktur project)
        file_put_contents(base_path('../dss-engine/app/dataset_smartphone.csv'), $csvContent);
    }
}
