#!/bin/sh

# 1. Setup .env if missing
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# 2. Install composer dependencies if vendor folder is missing
if [ ! -d vendor ]; then
    echo "Installing Composer dependencies..."
    composer install --no-interaction --optimize-autoloader
fi

# 3. Install NPM dependencies if node_modules is missing
if [ ! -d node_modules ]; then
    echo "Installing NPM dependencies..."
    npm install
fi

# 4. Generate Key if missing from .env
if ! grep -q "APP_KEY=base64:" .env || [ -z "$(grep APP_KEY .env | cut -d '=' -f2)" ]; then
    echo "Generating Application Key..."
    php artisan key:generate
fi

# 5. Build assets
echo "Building Vite assets..."
npm run build

# 6. Wait for database connection
DB_HOST_VAL=$(grep DB_HOST .env | cut -d '=' -f2 | tr -d '\r')
DB_PORT_VAL=$(grep DB_PORT .env | cut -d '=' -f2 | tr -d '\r')
DB_USER_VAL=$(grep DB_USERNAME .env | cut -d '=' -f2 | tr -d '\r')
DB_PASS_VAL=$(grep DB_PASSWORD .env | cut -d '=' -f2 | tr -d '\r')

DB_HOST_VAL=${DB_HOST_VAL:-db}
DB_PORT_VAL=${DB_PORT_VAL:-3306}
DB_USER_VAL=${DB_USER_VAL:-root}
DB_PASS_VAL=${DB_PASS_VAL:-root}

echo "Waiting for database connection to $DB_HOST_VAL:$DB_PORT_VAL..."
until php -r "
try {
    \$conn = new PDO('mysql:host=$DB_HOST_VAL;port=$DB_PORT_VAL', '$DB_USER_VAL', '$DB_PASS_VAL');
    exit(0);
} catch (PDOException \$e) {
    exit(1);
}
"; do
    echo "Database not ready yet, retrying in 2 seconds..."
    sleep 2
done
echo "Database is ready!"

# 7. Run Migrations
echo "Running migrations..."
php artisan migrate --force

# 8. Start Laravel Serve
echo "Starting Laravel server..."
exec php artisan serve --host=0.0.0.0 --port=8000
