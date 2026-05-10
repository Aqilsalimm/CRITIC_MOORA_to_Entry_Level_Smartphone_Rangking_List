<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Inertia\Inertia;

class RecommendationController extends Controller
{
    public function index()
    {
        return Inertia::render('Home', [
            'recommendations' => session('recommendations', []),
            'error' => session('error', null)
        ]);
    }

    public function calculate(Request $request)
    {
        // Validasi input array
        $request->validate([
            'min_price' => 'required|numeric',
            'max_price' => 'required|numeric',
            'selected_brands' => 'array',
            'selected_criteria' => 'required|array|max:3', // Memastikan max 3 dari backend
        ]);

        try {
            // Melempar payload ke API Python
            $response = Http::timeout(15)->post('http://flask_engine:5000/api/rekomendasi', [
                'min_price' => $request->min_price,
                'max_price' => $request->max_price,
                'brands' => $request->selected_brands,
                'fokus_kriteria' => $request->selected_criteria, 
            ]);

            if ($response->successful()) {
                $hasilDss = $response->json();
                
                session(['recommendations' => $hasilDss]);
                
                return redirect()->route('rekomendasi.show');
            }

            return redirect()->back()->with('error', 'Gagal memproses matriks DSS.');

        } catch (\Exception $e) {
            return redirect()->back()->with('error', 'Koneksi ke Engine Python terputus.');
        }
    }

    public function showResult()
    {
        $recommendations = session('recommendations', []);
        
        if (empty($recommendations)) {
            return redirect()->route('home');
        }
        
        \Log::info('Session recommendations: ' . json_encode($recommendations));
        
        return Inertia::render('Result', [
            'recommendations' => array_values($recommendations['recommendations'] ?? []),
            'analysis' => $recommendations['analysis'] ?? null
        ]);
    }
}
