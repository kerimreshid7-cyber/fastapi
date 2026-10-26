#!/usr/bin/env python3
"""Generate deterministic, synthetic ecommerce CSVs for analysis practice."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path


SEED = 20261024
START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)
OUTPUT_DIR = Path(__file__).parent / "data"


def write_csv(filename, rows, fieldnames):
    with (OUTPUT_DIR / filename).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def random_date(rng, start, end):
    return start + timedelta(days=rng.randrange((end - start).days + 1))


def make_customers(rng):
    locations = [
        ("United States", "California", "Los Angeles"),
        ("United States", "New York", "New York"),
        ("United States", "Texas", "Austin"),
        ("United States", "Illinois", "Chicago"),
        ("United States", "Washington", "Seattle"),
        ("Canada", "Ontario", "Toronto"),
        ("Canada", "Quebec", "Montreal"),
        ("United Kingdom", "England", "London"),
        ("United Kingdom", "Scotland", "Edinburgh"),
        ("Australia", "New South Wales", "Sydney"),
        ("Australia", "Victoria", "Melbourne"),
        ("Germany", "Berlin", "Berlin"),
        ("France", "Ile-de-France", "Paris"),
    ]
    channels = ["organic", "paid_search", "social", "email", "referral", "marketplace"]
    customers = []
    for number in range(1, 1501):
        country, region, city = rng.choice(locations)
        signup = random_date(rng, date(2022, 1, 1), END_DATE - timedelta(days=30))
        customers.append({
            "customer_id": f"C{number:05d}",
            "signup_date": signup.isoformat(),
            "country": country,
            "region": region,
            "city": city,
            "acquisition_channel": rng.choices(
                channels, weights=[28, 20, 17, 14, 11, 10], k=1
            )[0],
            "customer_segment": rng.choices(
                ["new", "returning", "vip"], weights=[55, 35, 10], k=1
            )[0],
        })
    return customers


def make_products(rng):
    catalog = {
        "Home & Kitchen": ["Drinkware", "Storage", "Lighting", "Cookware"],
        "Electronics": ["Audio", "Accessories", "Smart Home", "Computing"],
        "Clothing": ["Tops", "Bottoms", "Outerwear", "Activewear"],
        "Beauty": ["Skincare", "Haircare", "Makeup", "Fragrance"],
        "Sports": ["Fitness", "Outdoor", "Cycling", "Yoga"],
        "Books": ["Fiction", "Nonfiction", "Cookbooks", "Children"],
    }
    adjectives = ["Everyday", "Classic", "Essential", "Modern", "Premium", "Compact"]
    nouns = {
        "Home & Kitchen": ["Bottle", "Organizer", "Lamp", "Pan"],
        "Electronics": ["Headphones", "Charger", "Speaker", "Keyboard"],
        "Clothing": ["T-Shirt", "Trousers", "Jacket", "Leggings"],
        "Beauty": ["Serum", "Shampoo", "Palette", "Perfume"],
        "Sports": ["Dumbbell", "Backpack", "Bottle", "Mat"],
        "Books": ["Novel", "Guide", "Recipe Book", "Storybook"],
    }
    products = []
    for number in range(1, 81):
        category = list(catalog)[(number - 1) // 14] if number <= 70 else rng.choice(list(catalog))
        subcategory = rng.choice(catalog[category])
        cost = round(rng.uniform(4, 90), 2)
        price = round(cost * rng.uniform(1.55, 2.8), 2)
        launch = random_date(rng, date(2022, 1, 1), date(2025, 6, 30))
        product_id = f"P{number:04d}"
        products.append({
            "product_id": product_id,
            "product_name": f"{rng.choice(adjectives)} {rng.choice(nouns[category])} {number:02d}",
            "category": category,
            "subcategory": subcategory,
            "unit_cost": f"{cost:.2f}",
            "list_price": f"{price:.2f}",
            "launch_date": launch.isoformat(),
        })
    return products


def seasonal_weight(order_date):
    month_weights = {
        1: 0.82, 2: 0.86, 3: 0.94, 4: 0.98, 5: 1.03, 6: 1.00,
        7: 1.04, 8: 1.02, 9: 1.08, 10: 1.16, 11: 1.55, 12: 1.68,
    }
    weight = month_weights[order_date.month]
    if order_date.month == 11 and 24 <= order_date.day <= 30:
        weight *= 2.2
    if order_date.month == 12 and order_date.day <= 20:
        weight *= 1.25
    return weight


def make_orders_and_items(rng, customers, products):
    customer_by_id = {customer["customer_id"]: customer for customer in customers}
    product_by_id = {product["product_id"]: product for product in products}
    orders = []
    items = []
    order_count = 0
    customer_weights = [1.0] * len(customers)

    all_days = (END_DATE - START_DATE).days + 1
    order_dates = []
    for day_number in range(all_days):
        order_date = START_DATE + timedelta(days=day_number)
        expected = 5.8 * seasonal_weight(order_date)
        expected *= 1 + 0.00035 * day_number
        order_dates.extend([order_date] * max(0, int(expected)))
        if rng.random() < expected - int(expected):
            order_dates.append(order_date)
    rng.shuffle(order_dates)

    for order_date in order_dates:
        customer_index = rng.choices(range(len(customers)), weights=customer_weights, k=1)[0]
        customer = customers[customer_index]
        days_since_signup = (order_date - date.fromisoformat(customer["signup_date"])).days
        if days_since_signup < 0:
            eligible = [
                index for index, candidate in enumerate(customers)
                if date.fromisoformat(candidate["signup_date"]) <= order_date
            ]
            if not eligible:
                continue
            customer_index = rng.choice(eligible)
            customer = customers[customer_index]

        order_count += 1
        order_id = f"O{order_count:07d}"
        status = rng.choices(["delivered", "shipped", "cancelled"], [0.91, 0.06, 0.03], k=1)[0]
        payment_method = rng.choices(
            ["credit_card", "debit_card", "paypal", "digital_wallet", "buy_now_pay_later"],
            [42, 20, 16, 14, 8],
            k=1,
        )[0]
        shipping_method = rng.choices(
            ["standard", "express", "same_day"], [72, 24, 4], k=1
        )[0]
        shipping_cost = {"standard": 5.99, "express": 12.99, "same_day": 19.99}[shipping_method]
        tax_rate = {
            "United States": 0.0825, "Canada": 0.05, "United Kingdom": 0.20,
            "Australia": 0.10, "Germany": 0.19, "France": 0.20,
        }[customer["country"]]
        line_count = rng.choices([1, 2, 3, 4], [56, 29, 11, 4], k=1)[0]
        order_lines = []
        available_products = [
            product_id for product_id, product in product_by_id.items()
            if date.fromisoformat(product["launch_date"]) <= order_date
        ]
        chosen_products = rng.sample(available_products, line_count)
        for line_number, product_id in enumerate(chosen_products, 1):
            product = product_by_id[product_id]
            quantity = rng.choices([1, 2, 3], [78, 19, 3], k=1)[0]
            price = float(product["list_price"])
            discount = rng.choices([0, 0.05, 0.10, 0.15, 0.20, 0.30], [38, 12, 22, 14, 10, 4], k=1)[0]
            if order_date.month == 11 and 24 <= order_date.day <= 30:
                discount = min(discount + 0.05, 0.35)
            gross = round(price * quantity, 2)
            net = round(gross * (1 - discount), 2)
            returned_quantity = 0
            return_date = ""
            if status != "cancelled":
                return_probability = 0.035
                if product["category"] == "Clothing":
                    return_probability += 0.11
                elif product["category"] == "Electronics":
                    return_probability += 0.025
                if discount >= 0.20:
                    return_probability += 0.025
                if rng.random() < return_probability:
                    returned_quantity = rng.choices(
                        list(range(1, quantity + 1)),
                        [1] * quantity,
                        k=1,
                    )[0]
                    return_date = (order_date + timedelta(days=rng.randint(4, 35))).isoformat()
            order_lines.append({
                "order_id": order_id,
                "line_number": line_number,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": f"{price:.2f}",
                "discount_pct": f"{discount:.2f}",
                "gross_sales": f"{gross:.2f}",
                "net_sales": f"{net:.2f}",
                "unit_cost": product["unit_cost"],
                "returned_quantity": returned_quantity,
                "return_date": return_date,
                "net_sales_after_returns": f"{net * (quantity - returned_quantity) / quantity:.2f}",
            })

        if status == "cancelled":
            shipping_cost = 0
            order_total = 0
        else:
            subtotal = sum(float(line["net_sales"]) for line in order_lines)
            order_total = round((subtotal + shipping_cost) * (1 + tax_rate), 2)
            customer_weights[customer_index] += 2.0

        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": order_date.isoformat(),
            "status": status,
            "payment_method": payment_method,
            "shipping_method": shipping_method,
            "shipping_cost": f"{shipping_cost:.2f}",
            "tax_rate": f"{tax_rate:.4f}",
            "order_total": f"{order_total:.2f}",
        })
        if status != "cancelled":
            items.extend(order_lines)

    return orders, items


def main():
    rng = random.Random(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    customers = make_customers(rng)
    products = make_products(rng)
    orders, items = make_orders_and_items(rng, customers, products)

    write_csv("customers.csv", customers, [
        "customer_id", "signup_date", "country", "region", "city",
        "acquisition_channel", "customer_segment",
    ])
    write_csv("products.csv", products, [
        "product_id", "product_name", "category", "subcategory", "unit_cost",
        "list_price", "launch_date",
    ])
    write_csv("orders.csv", orders, [
        "order_id", "customer_id", "order_date", "status", "payment_method",
        "shipping_method", "shipping_cost", "tax_rate", "order_total",
    ])
    write_csv("order_items.csv", items, [
        "order_id", "line_number", "product_id", "quantity", "unit_price",
        "discount_pct", "gross_sales", "net_sales", "unit_cost",
        "returned_quantity", "return_date", "net_sales_after_returns",
    ])

    print(
        f"Generated {len(customers):,} customers, {len(products):,} products, "
        f"{len(orders):,} orders, and {len(items):,} order lines in {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
