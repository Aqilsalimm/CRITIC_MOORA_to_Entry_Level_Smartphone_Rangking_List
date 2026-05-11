<?php

use App\Http\Controllers\ProfileController;
use App\Http\Controllers\RecommendationController;
use App\Http\Controllers\Admin\SmartphoneController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

// Halaman Utama (Custom)
Route::get('/', [RecommendationController::class, 'index'])->name('home');
Route::post('/rekomendasi', [RecommendationController::class, 'calculate'])->name('rekomendasi');
Route::get('/rekomendasi', [RecommendationController::class, 'showResult'])->name('rekomendasi.show');

// Breeze Default Dashboard
Route::get('/dashboard', function () {
    return Inertia::render('Dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

// Breeze Profile Routes
Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

// Admin Routes (Custom)
Route::middleware(['auth'])->prefix('admin')->name('admin.')->group(function () {
    Route::get('/dashboard', [SmartphoneController::class, 'index'])->name('dashboard');
    Route::post('/smartphone', [SmartphoneController::class, 'store'])->name('smartphone.store');
    Route::post('/smartphone/upload', [SmartphoneController::class, 'upload'])->name('smartphone.upload');
    Route::delete('/smartphone/{smartphone}', [SmartphoneController::class, 'destroy'])->name('smartphone.destroy');
});

require __DIR__.'/auth.php';
