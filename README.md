# PickleHub - Premium Homemade Pickle Marketplace

A production-ready multi-vendor marketplace for homemade pickles built with Flask, Supabase, and modern web technologies.

## Features

### Customer Features
- **Authentication**: User registration, login, logout, email verification, password reset
- **Product Browsing**: Search, filter by category/price/rating/spice level
- **Shopping Cart**: Add/remove items, quantity management
- **Checkout**: Razorpay payment integration and Cash on Delivery (COD)
- **Order Management**: Order tracking, order history, cancellation
- **Reviews & Ratings**: Product reviews with approval system
- **Wishlist**: Save favorite products
- **Address Management**: Multiple addresses, default address selection
- **AI Recommendations**: Personalized product suggestions
- **AI Recipe Suggestions**: Recipe ideas based on pickle categories

### Seller Features
- **Dashboard**: Sales overview, revenue tracking, low stock alerts
- **Product Management**: Create, edit, delete products with image uploads
- **Inventory Management**: Stock tracking, product status management
- **Order Management**: View orders, update order status
- **Analytics**: Sales data and performance metrics

### Admin Features
- **Dashboard**: Platform-wide analytics and statistics
- **User Management**: Manage users, change roles, activate/deactivate accounts
- **Product Management**: Approve/reject products, manage all products
- **Order Management**: View and manage all orders
- **Category Management**: Create and manage product categories
- **Coupon Management**: Create discount coupons with usage limits
- **Review Management**: Approve/reject user reviews

### Technical Features
- **Glassmorphism UI**: Modern, beautiful interface with glass effects
- **Dark/Light Mode**: Theme toggle with localStorage persistence
- **Responsive Design**: Mobile-friendly layout
- **Row Level Security (RLS)**: Secure database access control
- **Real-time Updates**: Supabase Realtime integration ready
- **API Endpoints**: RESTful API for frontend integration
- **Error Handling**: Comprehensive error pages and validation
- **Docker Support**: Containerized deployment ready

## Tech Stack

- **Backend**: Python 3.11, Flask
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage
- **Payment**: Razorpay
- **AI**: OpenAI API
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker, Gunicorn

## Project Structure

```
picklehub/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── extensions.py        # Supabase and Razorpay clients
│   ├── models/              # Data models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── order.py
│   │   ├── cart.py
│   │   ├── review.py
│   │   ├── coupon.py
│   │   ├── address.py
│   │   └── notification.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── category_service.py
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   ├── review_service.py
│   │   ├── coupon_service.py
│   │   ├── address_service.py
│   │   ├── notification_service.py
│   │   ├── wishlist_service.py
│   │   └── ai_service.py
│   ├── routes/              # Flask routes
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── orders.py
│   │   ├── seller.py
│   │   ├── admin.py
│   │   └── api.py
│   ├── utils/               # Utilities
│   │   ├── error_handlers.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── auth/
│       ├── main/
│       ├── products/
│       ├── cart/
│       ├── orders/
│       ├── seller/
│       ├── admin/
│       └── errors/
├── database/
│   ├── schema.sql           # Database schema
│   └── rls_policies.sql     # Row Level Security policies
├── static/
│   └── uploads/             # Uploaded files
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── .gunicorn.conf.py
└── run.py                  # Application entry point
```

## Prerequisites

- Python 3.11 or higher
- pip
- Supabase account
- Razorpay account
- OpenAI API key (for AI features)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd picklehub
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Supabase
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key

# Razorpay
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# OpenAI (for AI features)
OPENAI_API_KEY=your-openai-api-key

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@picklehub.com
```

### 5. Set Up Supabase Database

1. Create a new project in Supabase
2. Run the SQL schema from `database/schema.sql` in the Supabase SQL editor
3. Run the RLS policies from `database/rls_policies.sql`
4. Enable Realtime for required tables (orders, notifications)

### 6. Create Upload Directories

```bash
mkdir -p static/uploads/products
mkdir -p static/uploads/profiles
```

### 7. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Database Schema

The application uses the following main tables:

- **profiles**: User profiles linked to Supabase Auth
- **categories**: Product categories
- **products**: Product listings with seller information
- **addresses**: User shipping/billing addresses
- **carts**: Shopping cart items
- **wishlists**: User wishlist items
- **orders**: Order information
- **order_items**: Items in each order
- **order_tracking**: Order status tracking
- **reviews**: Product reviews
- **coupons**: Discount coupons
- **notifications**: User notifications

See `database/schema.sql` for the complete schema.

## Row Level Security (RLS)

The application implements comprehensive RLS policies to ensure data security:

- Users can only access their own profiles, addresses, carts, wishlists, and orders
- Sellers can only manage their own products
- Admins have full access to all data
- Public read access for active products and categories

See `database/rls_policies.sql` for the complete RLS configuration.

## Deployment

### Using Docker

1. Build the Docker image:

```bash
docker build -t picklehub .
```

2. Run with Docker Compose:

```bash
docker-compose up -d
```

### Manual Deployment

1. Set environment variables for production
2. Install Gunicorn:

```bash
pip install gunicorn
```

3. Run with Gunicorn:

```bash
gunicorn --config .gunicorn.conf.py run:app
```

### Environment Variables for Production

- Set `FLASK_ENV=production`
- Use a strong `SECRET_KEY`
- Configure proper database URLs
- Set up proper email configuration
- Use production Razorpay keys

## API Endpoints

### Public Endpoints
- `GET /api/products` - List all products
- `GET /api/products/<id>` - Get product details
- `GET /api/categories` - List all categories
- `GET /api/search/analyze?q=<query>` - Analyze search query

### Authenticated Endpoints
- `GET /api/cart/count` - Get cart item count
- `GET /api/recommendations` - Get AI recommendations
- `GET /api/recipes/<product_id>` - Get recipe suggestions

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project follows PEP 8 style guidelines. Use flake8 for linting:

```bash
pip install flake8
flake8 app/
```

## Troubleshooting

### Database Connection Issues
- Verify Supabase credentials in `.env`
- Check Supabase project status
- Ensure RLS policies are correctly configured

### Image Upload Issues
- Ensure upload directories have proper permissions
- Check Supabase Storage configuration
- Verify file size limits

### Payment Issues
- Verify Razorpay API keys
- Check Razorpay account status
- Ensure webhook URLs are configured

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review Supabase and Razorpay documentation

## License

This project is licensed under the MIT License.

## Acknowledgments

- Supabase for the backend infrastructure
- Razorpay for payment processing
- OpenAI for AI features
- Flask for the web framework
