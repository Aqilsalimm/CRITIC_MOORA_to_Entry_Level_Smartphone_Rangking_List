<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Smartphone extends Model
{
    use HasFactory;

    protected $fillable = [
        'Nama_HP', 'Brand', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'
    ];
}
