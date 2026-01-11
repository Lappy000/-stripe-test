# Django + Stripe Payment Integration

Тестовое задание: Django бэкенд с интеграцией Stripe API для создания платёжных форм.

## Функционал

### Основные требования
- Django модель `Item` с полями (name, description, price)
- `GET /buy/{id}` - получение Stripe Session Id для оплаты товара
- `GET /item/{id}` - HTML страница с информацией о товаре и кнопкой Buy

### Бонусные задачи
- Запуск через Docker
- Environment variables
- Django Admin панель для управления моделями
- Модель `Order` для объединения нескольких Item
- Модели `Discount` и `Tax` с интеграцией в Stripe Checkout
- Поле `Item.currency` с поддержкой разных валют (USD, EUR)
- Stripe Payment Intent (альтернативный метод оплаты)
- Современный адаптивный дизайн в стиле интернет-магазина

## Дизайн

Сайт имеет современный, профессиональный дизайн с:
- Градиентным фоном и карточками товаров
- Анимациями при наведении и загрузке
- Адаптивной вёрсткой для мобильных устройств
- Интуитивным пользовательским интерфейсом
- Информативными страницами успеха и отмены оплаты

## API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Главная страница со списком товаров и заказов |
| GET | `/item/{id}/` | HTML страница товара с кнопкой Buy |
| GET | `/buy/{id}/` | Создание Stripe Checkout Session |
| GET | `/order/{id}/` | HTML страница заказа |
| GET | `/buy-order/{id}/` | Создание Session для заказа с Discount/Tax |
| GET | `/item/{id}/intent/` | Страница с Payment Intent |
| GET | `/payment-intent/{id}/` | Создание Payment Intent |
| GET | `/success/` | Страница успешной оплаты |
| GET | `/cancel/` | Страница отмены оплаты |

## Установка и запуск

### Вариант 1: Docker (рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Lappy000/-stripe-test.git
cd -stripe-test
```

2. Создайте файл `.env` из примера:
```bash
cp .env.example .env
```

3. Заполните Stripe ключи в `.env`:
```env
STRIPE_PUBLIC_KEY_USD=pk_test_...
STRIPE_SECRET_KEY_USD=sk_test_...
STRIPE_PUBLIC_KEY_EUR=pk_test_...
STRIPE_SECRET_KEY_EUR=sk_test_...
```

4. Запустите через Docker Compose:
```bash
docker-compose up --build
```

5. Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

6. Откройте http://localhost:8000

### Вариант 2: Локальная установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте `.env` файл и заполните Stripe ключи

4. Примените миграции:
```bash
python manage.py migrate
```

5. Загрузите тестовые данные:
```bash
python manage.py load_sample_data
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер:
```bash
python manage.py runserver
```

## Получение Stripe API ключей

1. Зарегистрируйтесь на [stripe.com](https://stripe.com)
2. Перейдите в Dashboard -> Developers -> API keys
3. Используйте тестовые ключи (Test mode):
   - `pk_test_...` - Publishable key
   - `sk_test_...` - Secret key

## Модели данных

### Item
```python
- name: CharField
- description: TextField
- price: DecimalField
- currency: CharField (choices: 'usd', 'eur')
```

### Order
```python
- items: ManyToManyField(Item) через OrderItem
- discount: ForeignKey(Discount)
- tax: ForeignKey(Tax)
```

### Discount
```python
- name: CharField
- percent_off: DecimalField
- stripe_coupon_id: CharField
```

### Tax
```python
- name: CharField
- percentage: DecimalField
- inclusive: BooleanField
- stripe_tax_rate_id: CharField
```

## Тестовые карты

Для тестирования используйте тестовые карты Stripe:

| Номер карты | Описание |
|-------------|----------|
| 4242 4242 4242 4242 | Успешный платёж |
| 4000 0000 0000 0002 | Карта отклонена |
| 4000 0000 0000 9995 | Недостаточно средств |

Используйте любую будущую дату истечения срока и любой CVC (3 цифры).

## Доступ к Admin панели

URL: `/admin/`

При использовании демо-версии:
- Username: `admin`
- Password: `admin123`

## Структура проекта

```
├── stripe_payment/          # Настройки Django проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── payments/                # Приложение платежей
│   ├── models.py           # Модели Item, Order, Discount, Tax
│   ├── views.py            # Views для API endpoints
│   ├── urls.py             # URL маршруты
│   ├── admin.py            # Конфигурация Admin
│   └── management/         # Команды управления
│       └── commands/
│           └── load_sample_data.py
├── templates/               # HTML шаблоны
│   ├── base.html           # Базовый шаблон с дизайном
│   └── payments/
│       ├── home.html
│       ├── item_detail.html
│       ├── order_detail.html
│       ├── payment_intent.html
│       ├── success.html
│       └── cancel.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Environment Variables

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| SECRET_KEY | Django secret key | Dev key |
| DEBUG | Debug mode | True |
| ALLOWED_HOSTS | Allowed hosts | localhost,127.0.0.1 |
| STRIPE_PUBLIC_KEY_USD | Stripe public key for USD | - |
| STRIPE_SECRET_KEY_USD | Stripe secret key for USD | - |
| STRIPE_PUBLIC_KEY_EUR | Stripe public key for EUR | - |
| STRIPE_SECRET_KEY_EUR | Stripe secret key for EUR | - |
| DOMAIN | Base URL for redirects | http://localhost:8000 |

## Примечания

- Для поддержки двух валют создайте два отдельных Stripe аккаунта или используйте один аккаунт с разными ключами для тестирования
- Discount и Tax автоматически создаются в Stripe при первом использовании
- Payment Intent предоставляет более гибкий контроль над процессом оплаты
- Дизайн полностью адаптивен и работает на всех устройствах

## Лицензия

MIT License
