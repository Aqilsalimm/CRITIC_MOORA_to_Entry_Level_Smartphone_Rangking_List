<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('smartphones', function (Blueprint $table) {
            $table->id();
            $table->string('Nama_HP');
            $table->string('Brand');
            $table->double('C1'); // Harga
            $table->double('C2'); // RAM
            $table->double('C3'); // Storage
            $table->double('C4'); // AnTuTu
            $table->double('C5'); // Kamera
            $table->double('C6'); // Baterai
            $table->integer('C7'); // Tipe Storage (1:eMMC, 2:UFS)
            $table->integer('C8'); // Tipe Layar (1:IPS, 2:AMOLED)
            $table->integer('C9'); // Resolusi (1-4)
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('smartphones');
    }
};
