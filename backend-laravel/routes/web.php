<?php

use App\Http\Controllers\RecommendationController;
use Illuminate\Support\Facades\Route;

Route::get('/', [RecommendationController::class, 'index'])->name('home');
Route::post('/rekomendasi', [RecommendationController::class, 'calculate'])->name('rekomendasi');
Route::get('/rekomendasi', [RecommendationController::class, 'showResult'])->name('rekomendasi.show');

