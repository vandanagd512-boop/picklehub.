-- Row Level Security (RLS) Policies for PickleHub
-- Run this in your Supabase SQL Editor after schema.sql

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.carts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wishlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coupons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_tracking ENABLE ROW LEVEL SECURITY;

-- Profiles RLS Policies
CREATE POLICY "Public profiles are viewable by everyone"
    ON public.profiles FOR SELECT
    USING (true);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Admins can update any profile"
    ON public.profiles FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Categories RLS Policies (public read, admin write)
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Categories are viewable by everyone"
    ON public.categories FOR SELECT
    USING (is_active = true);

CREATE POLICY "Admins can manage categories"
    ON public.categories FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Products RLS Policies
CREATE POLICY "Active products are viewable by everyone"
    ON public.products FOR SELECT
    USING (status = 'active');

CREATE POLICY "Sellers can manage own products"
    ON public.products FOR ALL
    USING (auth.uid() = seller_id);

CREATE POLICY "Admins can manage all products"
    ON public.products FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Addresses RLS Policies
CREATE POLICY "Users can view own addresses"
    ON public.addresses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own addresses"
    ON public.addresses FOR ALL
    USING (auth.uid() = user_id);

-- Carts RLS Policies
CREATE POLICY "Users can view own cart"
    ON public.carts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own cart"
    ON public.carts FOR ALL
    USING (auth.uid() = user_id);

-- Wishlists RLS Policies
CREATE POLICY "Users can view own wishlist"
    ON public.wishlists FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own wishlist"
    ON public.wishlists FOR ALL
    USING (auth.uid() = user_id);

-- Orders RLS Policies
CREATE POLICY "Users can view own orders"
    ON public.orders FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Sellers can view orders for their products"
    ON public.orders FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM jsonb_array_elements(items) AS item
            JOIN public.products ON products.id = (item->>'product_id')::uuid
            WHERE products.seller_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own orders"
    ON public.orders FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can view all orders"
    ON public.orders FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins and sellers can update order status"
    ON public.orders FOR UPDATE
    USING (
        auth.uid() = user_id OR
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        ) OR
        EXISTS (
            SELECT 1 FROM jsonb_array_elements(items) AS item
            JOIN public.products ON products.id = (item->>'product_id')::uuid
            WHERE products.seller_id = auth.uid()
        )
    );

-- Reviews RLS Policies
CREATE POLICY "Reviews are viewable by everyone"
    ON public.reviews FOR SELECT
    USING (is_approved = true);

CREATE POLICY "Users can insert own reviews"
    ON public.reviews FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own reviews"
    ON public.reviews FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage all reviews"
    ON public.reviews FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Coupons RLS Policies
CREATE POLICY "Active coupons are viewable by everyone"
    ON public.coupons FOR SELECT
    USING (is_active = true);

CREATE POLICY "Admins can manage coupons"
    ON public.coupons FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Notifications RLS Policies
CREATE POLICY "Users can view own notifications"
    ON public.notifications FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications"
    ON public.notifications FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "System can insert notifications"
    ON public.notifications FOR INSERT
    WITH CHECK (true);

-- Order Tracking RLS Policies
CREATE POLICY "Users can view tracking for own orders"
    ON public.order_tracking FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.orders
            WHERE orders.id = order_tracking.order_id AND orders.user_id = auth.uid()
        )
    );

CREATE POLICY "Sellers can view tracking for their orders"
    ON public.order_tracking FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.orders
            JOIN jsonb_array_elements(orders.items) AS item ON true
            JOIN public.products ON products.id = (item->>'product_id')::uuid
            WHERE orders.id = order_tracking.order_id AND products.seller_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all tracking"
    ON public.order_tracking FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins and sellers can insert tracking"
    ON public.order_tracking FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        ) OR
        EXISTS (
            SELECT 1 FROM public.orders
            JOIN jsonb_array_elements(orders.items) AS item ON true
            JOIN public.products ON products.id = (item->>'product_id')::uuid
            WHERE orders.id = order_tracking.order_id AND products.seller_id = auth.uid()
        )
    );
