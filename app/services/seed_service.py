"""
Seed Service - Inserts sample pickle products into local database if the products
table is empty. Called automatically from the products list route on first load.
"""
from app.models.db import db
from app.models.product import Product, ProductStatus
from app.models.category import Category
from app.models.user import User, UserRole
import logging
import uuid

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Placeholder image URLs (public Unsplash/Picsum – no auth needed)
# ---------------------------------------------------------------------------
_PICKLE_IMAGE = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&q=80"

SAMPLE_PRODUCTS = [
    {
        "name": "Mango Pickle",
        "description": "Classic South Indian raw mango pickle made with mustard seeds, red chilli and sesame oil. A staple condiment in every Indian household.",
        "price": 149.00,
        "original_price": 199.00,
        "discount_percentage": 25.13,
        "stock": 50,
        "images": ["/uploads/products/mango_pickle.jpg"],
        "status": "active",
        "ingredients": "Raw mango, mustard seeds, red chilli, sesame oil, salt, turmeric",
        "spice_level": "high",
        "shelf_life": "12 months",
        "weight": "500g",
        "is_featured": True,
        "rating": 4.7,
        "review_count": 128,
    },
    {
        "name": "Lemon Pickle",
        "description": "Tangy and spicy whole lemon pickle in mustard oil. Sun-cured for 15 days for an authentic flavour.",
        "price": 129.00,
        "original_price": 159.00,
        "discount_percentage": 18.87,
        "stock": 40,
        "images": ["/uploads/products/lemon_pickle.jpg"],
        "status": "active",
        "ingredients": "Lemon, mustard oil, salt, red chilli, fenugreek",
        "spice_level": "medium",
        "shelf_life": "18 months",
        "weight": "400g",
        "is_featured": True,
        "rating": 4.5,
        "review_count": 95,
    },
    {
        "name": "Garlic Pickle",
        "description": "Bold, aromatic garlic pickle slow-cooked in sesame oil with select spices. Pairs perfectly with dal and roti.",
        "price": 179.00,
        "original_price": None,
        "discount_percentage": None,
        "stock": 35,
        "images": ["/uploads/products/garlic_pickle.jpg"],
        "status": "active",
        "ingredients": "Garlic, sesame oil, red chilli, mustard seeds, vinegar, salt",
        "spice_level": "medium",
        "shelf_life": "9 months",
        "weight": "250g",
        "is_featured": False,
        "rating": 4.6,
        "review_count": 72,
    },
    {
        "name": "Tomato Pickle",
        "description": "Sweet and spicy tomato pickle from Andhra Pradesh, prepared with fresh tomatoes and traditional spices.",
        "price": 119.00,
        "original_price": 149.00,
        "discount_percentage": 20.13,
        "stock": 60,
        "images": ["/uploads/products/tomato_pickle.jpg"],
        "status": "active",
        "ingredients": "Tomatoes, red chilli, mustard, tamarind, oil, salt, jaggery",
        "spice_level": "medium",
        "shelf_life": "6 months",
        "weight": "300g",
        "is_featured": False,
        "rating": 4.3,
        "review_count": 61,
    },
    {
        "name": "Mixed Vegetable Pickle",
        "description": "A delightful medley of carrot, cauliflower, turnip and green chilli pickled in mustard oil with aromatic spices.",
        "price": 139.00,
        "original_price": None,
        "discount_percentage": None,
        "stock": 45,
        "images": ["/uploads/products/mixed_veg_pickle.jpg"],
        "status": "active",
        "ingredients": "Carrot, cauliflower, turnip, green chilli, mustard oil, salt, spices",
        "spice_level": "low",
        "shelf_life": "12 months",
        "weight": "500g",
        "is_featured": True,
        "rating": 4.4,
        "review_count": 83,
    },
    {
        "name": "Andhra Avakaya",
        "description": "Legendary Andhra-style raw mango pickle with generous amounts of chilli powder, mustard and gingelly oil.",
        "price": 199.00,
        "original_price": 249.00,
        "discount_percentage": 20.08,
        "stock": 30,
        "images": ["/uploads/products/andhra_avakaya.jpg"],
        "status": "active",
        "ingredients": "Raw mango, red chilli powder, mustard seeds, gingelly oil, salt, fenugreek",
        "spice_level": "high",
        "shelf_life": "12 months",
        "weight": "500g",
        "is_featured": True,
        "rating": 4.9,
        "review_count": 210,
    },
    {
        "name": "Amla Pickle",
        "description": "Nutrient-rich Indian gooseberry pickle with a perfect balance of sour, spicy and salty flavours.",
        "price": 159.00,
        "original_price": None,
        "discount_percentage": None,
        "stock": 25,
        "images": ["/uploads/products/amla_pickle.jpg"],
        "status": "active",
        "ingredients": "Amla (gooseberry), mustard oil, red chilli, turmeric, salt",
        "spice_level": "low",
        "shelf_life": "8 months",
        "weight": "250g",
        "is_featured": False,
        "rating": 4.2,
        "review_count": 44,
    },
    {
        "name": "Ginger Pickle",
        "description": "Zesty ginger pickle made with fresh ginger root, green chillies and lime juice. Great digestive aid.",
        "price": 139.00,
        "original_price": 169.00,
        "discount_percentage": 17.75,
        "stock": 20,
        "images": ["/uploads/products/ginger_pickle.jpg"],
        "status": "active",
        "ingredients": "Fresh ginger, green chilli, lemon juice, salt, mustard seeds",
        "spice_level": "medium",
        "shelf_life": "6 months",
        "weight": "200g",
        "is_featured": False,
        "rating": 4.1,
        "review_count": 37,
    },
    {
        "name": "Onion Pickle",
        "description": "Crispy small pearl onions pickled in vinegar and spices – a classic British-Indian fusion condiment.",
        "price": 109.00,
        "original_price": None,
        "discount_percentage": None,
        "stock": 55,
        "images": ["/uploads/products/onion_pickle.jpg"],
        "status": "active",
        "ingredients": "Pearl onions, malt vinegar, mustard seeds, black pepper, bay leaf, salt",
        "spice_level": "low",
        "shelf_life": "12 months",
        "weight": "400g",
        "is_featured": False,
        "rating": 4.0,
        "review_count": 29,
    },
    {
        "name": "Coconut Pickle",
        "description": "Fresh coconut pickle from Kerala made with coconut shreds, curry leaves and dried red chillies in coconut oil.",
        "price": 169.00,
        "original_price": 199.00,
        "discount_percentage": 15.08,
        "stock": 15,
        "images": ["/uploads/products/coconut_pickle.jpg"],
        "status": "active",
        "ingredients": "Fresh coconut, coconut oil, red chilli, curry leaves, mustard seeds, salt",
        "spice_level": "low",
        "shelf_life": "3 months",
        "weight": "200g",
        "is_featured": False,
        "rating": 4.3,
        "review_count": 51,
    },
    {
        "name": "Chicken Pickle",
        "description": "Boneless chicken pickle slow-cooked with aromatic spices and preserved in oil. A non-veg delicacy.",
        "price": 299.00,
        "original_price": 349.00,
        "discount_percentage": 14.33,
        "stock": 20,
        "images": ["/uploads/products/chicken_pickle.jpg"],
        "status": "active",
        "ingredients": "Chicken, red chilli, ginger, garlic, spices, oil, vinegar",
        "spice_level": "high",
        "shelf_life": "6 months",
        "weight": "300g",
        "is_featured": True,
        "rating": 4.8,
        "review_count": 156,
    },
    {
        "name": "Fish Pickle",
        "description": "Traditional Goan fish pickle with mackerel, kokum and an intense blend of coastal spices.",
        "price": 279.00,
        "original_price": None,
        "discount_percentage": None,
        "stock": 18,
        "images": ["/uploads/products/fish_pickle.jpg"],
        "status": "active",
        "ingredients": "Mackerel, kokum, red chilli, ginger, garlic, vinegar, oil, spices",
        "spice_level": "high",
        "shelf_life": "4 months",
        "weight": "300g",
        "is_featured": False,
        "rating": 4.6,
        "review_count": 89,
    },
    {
        "name": "Prawn Pickle",
        "description": "Succulent prawn pickle from coastal Karnataka with fresh prawns in tangy tamarind and spice base.",
        "price": 319.00,
        "original_price": 379.00,
        "discount_percentage": 15.83,
        "stock": 12,
        "images": ["/uploads/products/prawn_pickle.jpg"],
        "status": "active",
        "ingredients": "Prawns, tamarind, red chilli, mustard, oil, garlic, ginger, spices",
        "spice_level": "high",
        "shelf_life": "3 months",
        "weight": "250g",
        "is_featured": True,
        "rating": 4.7,
        "review_count": 103,
    },
    {
        "name": "Rajasthani Lal Mirch Ka Achaar",
        "description": "Authentic Marwari jumbo thick red chillies stuffed with tangy amchur, roasted fennel, mustard and steeped in pure mustard oil.",
        "price": 199.00,
        "original_price": 249.00,
        "discount_percentage": 20.08,
        "stock": 35,
        "images": ["/uploads/products/rajasthani_lal_mirch.jpg"],
        "status": "active",
        "ingredients": "Whole red chillies, mustard seeds, dry mango powder (amchur), saunf, fenugreek, mustard oil, salt",
        "spice_level": "high",
        "shelf_life": "12 months",
        "weight": "350g",
        "is_featured": True,
        "rating": 4.9,
        "review_count": 164,
    },
    {
        "name": "Andhra Gongura Pachadi",
        "description": "The quintessential culinary pride of Andhra Pradesh – tangy sorrel (gongura) leaves slow-cooked with fiery red chillies and crushed garlic.",
        "price": 159.00,
        "original_price": 189.00,
        "discount_percentage": 15.87,
        "stock": 40,
        "images": ["/uploads/products/andhra_gongura.jpg"],
        "status": "active",
        "ingredients": "Gongura leaves, red chillies, garlic, sesame oil, fenugreek, mustard, cumin, salt",
        "spice_level": "high",
        "shelf_life": "6 months",
        "weight": "300g",
        "is_featured": True,
        "rating": 4.8,
        "review_count": 142,
    },
    {
        "name": "Rajasthani Ker Sangri Achaar",
        "description": "Royal desert delicacy prepared with wild Ker berries and Sangri beans harvested from Thar Desert, preserved in cold-pressed mustard oil.",
        "price": 249.00,
        "original_price": 299.00,
        "discount_percentage": 16.72,
        "stock": 25,
        "images": ["/uploads/products/ker_sangri.jpg"],
        "status": "active",
        "ingredients": "Wild ker berries, sangri beans, cold-pressed mustard oil, dry mango slices, red chilli, hing, spices",
        "spice_level": "medium",
        "shelf_life": "12 months",
        "weight": "400g",
        "is_featured": True,
        "rating": 4.9,
        "review_count": 118,
    },
    {
        "name": "Punjabi Gobhi Gajar Shalgam",
        "description": "Traditional North Indian sweet and sour winter achar with crisp cauliflower, tender carrots and turnips in gur (jaggery) and spiced vinegar.",
        "price": 149.00,
        "original_price": 179.00,
        "discount_percentage": 16.76,
        "stock": 50,
        "images": ["/uploads/products/gobhi_gajar_shalgam.jpg"],
        "status": "active",
        "ingredients": "Cauliflower florets, winter carrots, turnips, jaggery (gur), malt vinegar, mustard oil, ginger, garlic, garam masala",
        "spice_level": "low",
        "shelf_life": "9 months",
        "weight": "500g",
        "is_featured": False,
        "rating": 4.6,
        "review_count": 87,
    },
    {
        "name": "Maharashtrian Khatta Meetha Nimbu",
        "description": "Aged oil-free whole lemon pickle prepared with organic jaggery, rock salt and roasted cumin. Delicious digestive accompaniment.",
        "price": 139.00,
        "original_price": None,
        "discount_percentage": None,
        "stock": 45,
        "images": ["/uploads/products/khatta_meetha_nimbu.jpg"],
        "status": "active",
        "ingredients": "Fresh thin-skinned lemons, organic jaggery, rock salt, roasted cumin seeds, black pepper, red chilli (Oil-Free)",
        "spice_level": "low",
        "shelf_life": "18 months",
        "weight": "400g",
        "is_featured": False,
        "rating": 4.5,
        "review_count": 76,
    },
    {
        "name": "Hari Mirch Ka Achaar",
        "description": "Crisp slit fresh green chillies fermented with coarse yellow mustard seeds (rai kuria), lemon juice and virgin mustard oil.",
        "price": 129.00,
        "original_price": 149.00,
        "discount_percentage": 13.42,
        "stock": 60,
        "images": ["/uploads/products/hari_mirch_pickle.jpg"],
        "status": "active",
        "ingredients": "Fresh green chillies, yellow mustard seeds (rai kuria), lemon juice, turmeric, cold-pressed mustard oil, salt",
        "spice_level": "high",
        "shelf_life": "6 months",
        "weight": "250g",
        "is_featured": False,
        "rating": 4.4,
        "review_count": 92,
    },
    {
        "name": "Gujarati Mango Chunda",
        "description": "Sun-cured shredded green mango sweet relish delicately spiced with roasted cumin seeds and red chilli powder. Perfect with thepla.",
        "price": 169.00,
        "original_price": 199.00,
        "discount_percentage": 15.08,
        "stock": 40,
        "images": ["/uploads/products/mango_chunda.jpg"],
        "status": "active",
        "ingredients": "Grated green raw mango, sugar, roasted cumin powder, Kashmiri red chilli powder, rock salt",
        "spice_level": "low",
        "shelf_life": "12 months",
        "weight": "450g",
        "is_featured": True,
        "rating": 4.8,
        "review_count": 135,
    },
    {
        "name": "Bengali Kasundi Mustard Relish",
        "description": "Fiery and pungent stone-ground mustard relish handcrafted with green mangoes, yellow and black mustard seeds and aromatic Bengali spices.",
        "price": 179.00,
        "original_price": 209.00,
        "discount_percentage": 14.35,
        "stock": 30,
        "images": ["/uploads/products/bengali_kasundi.jpg"],
        "status": "active",
        "ingredients": "Stone-ground yellow and black mustard seeds, green mango pulp, green chillies, mustard oil, spices",
        "spice_level": "high",
        "shelf_life": "8 months",
        "weight": "300g",
        "is_featured": True,
        "rating": 4.7,
        "review_count": 110,
    },
    {
        "name": "Assam Bhoot Jolokia Achaar",
        "description": "Fiery northeastern smoked ghost pepper (Bhut Jolokia) and tender mountain bamboo shoots preserved in pure virgin mustard oil.",
        "price": 269.00,
        "original_price": 319.00,
        "discount_percentage": 15.67,
        "stock": 20,
        "images": ["/uploads/products/bhoot_jolokia.jpg"],
        "status": "active",
        "ingredients": "Smoked ghost peppers (Bhut Jolokia), bamboo shoots, virgin mustard oil, garlic, ginger, vinegar, salt",
        "spice_level": "high",
        "shelf_life": "12 months",
        "weight": "200g",
        "is_featured": True,
        "rating": 4.9,
        "review_count": 158,
    },
    {
        "name": "Hyderabadi Mutton Pickle",
        "description": "Royal Nizami delicacy featuring tender boneless fried mutton chunks simmered in aromatic ginger-garlic paste and roasted sesame oil spices.",
        "price": 349.00,
        "original_price": 399.00,
        "discount_percentage": 12.53,
        "stock": 18,
        "images": ["/uploads/products/mutton_pickle.jpg"],
        "status": "active",
        "ingredients": "Tender boneless mutton, ginger-garlic paste, red chilli powder, ground coriander, cloves, cardamom, sesame oil, lemon juice",
        "spice_level": "high",
        "shelf_life": "4 months",
        "weight": "300g",
        "is_featured": True,
        "rating": 4.9,
        "review_count": 189,
    },
    {
        "name": "Kerala Kadumanga (Tender Mango)",
        "description": "Crispy baby raw mango cut pickle tempered with crushed mustard seeds, red chilli, asafoetida (hing) and fresh curry leaves in gingelly oil.",
        "price": 149.00,
        "original_price": 179.00,
        "discount_percentage": 16.76,
        "stock": 35,
        "images": ["/uploads/products/kadumanga_pickle.jpg"],
        "status": "active",
        "ingredients": "Baby tender raw mangoes, Kashmiri chilli powder, asafoetida (hing), mustard seeds, curry leaves, gingelly oil",
        "spice_level": "medium",
        "shelf_life": "6 months",
        "weight": "350g",
        "is_featured": False,
        "rating": 4.6,
        "review_count": 94,
    },
    {
        "name": "Karonda Mirchi Ka Achaar",
        "description": "Wild tart pink Karonda berries cooked with crisp green chillies, aromatic fennel seeds (saunf) and kalonji in golden mustard oil.",
        "price": 139.00,
        "original_price": None,
        "discount_percentage": None,
        "stock": 30,
        "images": ["/uploads/products/karonda_pickle.jpg"],
        "status": "active",
        "ingredients": "Wild karonda berries, slit green chillies, fennel seeds, kalonji, turmeric, mustard oil, salt",
        "spice_level": "medium",
        "shelf_life": "6 months",
        "weight": "300g",
        "is_featured": False,
        "rating": 4.3,
        "review_count": 62,
    },
]


def _get_or_create_category(name: str, description: str, sort_order: int) -> str:
    """Return existing category id or insert a new one and return its id."""
    try:
        category = Category.query.filter_by(name=name).first()
        if category:
            return str(category.id)
        
        category = Category(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            is_active=True,
            sort_order=sort_order
        )
        db.session.add(category)
        db.session.commit()
        return str(category.id)
    except Exception as e:
        db.session.rollback()
        logger.error(f"get_or_create_category error for '{name}': {e}")
        return None


def _get_or_create_seed_seller() -> str:
    """
    Return the id of a seed seller profile.
    We look for an existing user with role='seller'; if none exists we
    create one.
    """
    try:
        seller = User.query.filter_by(role=UserRole.SELLER).first()
        if seller:
            return str(seller.id)
        
        # Create a seed seller
        seller = User(
            id=str(uuid.uuid4()),
            email='seller@picklehub.com',
            full_name='PickleHub Seller',
            role=UserRole.SELLER,
            is_active=True,
            is_verified=True
        )
        seller.set_password('seller123')
        db.session.add(seller)
        db.session.commit()
        return str(seller.id)
    except Exception as e:
        db.session.rollback()
        logger.error(f"get_or_create_seed_seller error: {e}")
        # Last resort – a nil UUID
        return '00000000-0000-0000-0000-000000000000'


# ---------------------------------------------------------------------------
# Category → spice-level mapping helpers
# ---------------------------------------------------------------------------
_VEGIE_CATEGORIES = {
    'Mango Pickle': ('Mango Pickle', 'Traditional mango pickles from across India', 1),
    'Lemon Pickle': ('Lemon Pickle', 'Tangy and spicy lemon pickles', 2),
    'Garlic Pickle': ('Garlic Pickle', 'Flavorful garlic-based pickles', 3),
    'Tomato Pickle': ('Mixed Vegetable', 'Assorted vegetable pickles', 4),
    'Mixed Vegetable Pickle': ('Mixed Vegetable', 'Assorted vegetable pickles', 4),
    'Andhra Avakaya': ('Mango Pickle', 'Traditional mango pickles from across India', 1),
    'Amla Pickle': ('Specialty', 'Regional and specialty pickles', 7),
    'Ginger Pickle': ('Specialty', 'Regional and specialty pickles', 7),
    'Onion Pickle': ('Mixed Vegetable', 'Assorted vegetable pickles', 4),
    'Coconut Pickle': ('Specialty', 'Regional and specialty pickles', 7),
    'Chicken Pickle': ('Non-Veg Pickles', 'Authentic meat and seafood pickles', 6),
    'Fish Pickle': ('Non-Veg Pickles', 'Authentic meat and seafood pickles', 6),
    'Prawn Pickle': ('Non-Veg Pickles', 'Authentic meat and seafood pickles', 6),
    'Rajasthani Lal Mirch Ka Achaar': ('Chilli Pickle', 'Stuffed and spiced red and green chilli pickles', 5),
    'Andhra Gongura Pachadi': ('Specialty', 'Regional and specialty pickles', 7),
    'Rajasthani Ker Sangri Achaar': ('Specialty', 'Regional and specialty pickles', 7),
    'Punjabi Gobhi Gajar Shalgam': ('Mixed Vegetable', 'Assorted vegetable pickles', 4),
    'Maharashtrian Khatta Meetha Nimbu': ('Lemon Pickle', 'Tangy and spicy lemon pickles', 2),
    'Hari Mirch Ka Achaar': ('Chilli Pickle', 'Stuffed and spiced red and green chilli pickles', 5),
    'Gujarati Mango Chunda': ('Mango Pickle', 'Traditional mango pickles from across India', 1),
    'Bengali Kasundi Mustard Relish': ('Specialty', 'Regional and specialty pickles', 7),
    'Assam Bhoot Jolokia Achaar': ('Chilli Pickle', 'Stuffed and spiced red and green chilli pickles', 5),
    'Hyderabadi Mutton Pickle': ('Non-Veg Pickles', 'Authentic meat and seafood pickles', 6),
    'Kerala Kadumanga (Tender Mango)': ('Mango Pickle', 'Traditional mango pickles from across India', 1),
    'Karonda Mirchi Ka Achaar': ('Specialty', 'Regional and specialty pickles', 7),
}


def seed_products_if_empty() -> bool:
    """
    Check if products table is empty; if so, insert all sample products.
    Returns True when seeding was performed, False when products already exist
    or seeding failed.
    """
    try:
        count = Product.query.count()
        if count > 0:
            logger.info("Products table already has data – skipping seed.")
            return False

        logger.info("Products table is empty – seeding sample products …")
        seller_id = _get_or_create_seed_seller()

        for product in SAMPLE_PRODUCTS:
            cat_info = _VEGIE_CATEGORIES.get(product['name'], ('Specialty', 'Regional and specialty pickles', 7))
            category_id = _get_or_create_category(cat_info[0], cat_info[1], cat_info[2])

            new_product = Product(
                id=str(uuid.uuid4()),
                seller_id=seller_id,
                category_id=category_id,
                name=product['name'],
                description=product['description'],
                price=product['price'],
                original_price=product.get('original_price'),
                discount_percentage=product.get('discount_percentage'),
                stock=product['stock'],
                images=product['images'],
                status=ProductStatus(product.get('status', 'active')),
                ingredients=product['ingredients'],
                spice_level=product['spice_level'],
                shelf_life=product['shelf_life'],
                weight=product['weight'],
                is_featured=product['is_featured'],
                rating=product['rating'],
                review_count=product['review_count']
            )
            
            try:
                db.session.add(new_product)
                db.session.commit()
                logger.info(f"  Seeded: {product['name']}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"  Failed to seed '{product['name']}': {e}")

        logger.info("Seeding complete.")
        return True

    except Exception as e:
        db.session.rollback()
        logger.error(f"seed_products_if_empty error: {e}")
        return False
