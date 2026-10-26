# Synthetic ecommerce practice data

This project contains deterministic, fictional commerce data for practicing
data cleaning, SQL joins, exploratory analysis, and visualization. It covers
three full years (2023–2025) and includes seasonal demand, repeat customers,
discounts, cancellations, and product returns. No real people or transactions
are represented.

## Files

All CSVs are in [`data/`](./data/).

| File | Grain | Rows (approximately) | Join key |
|---|---|---:|---|
| `customers.csv` | One row per customer | 1,500 | `customer_id` |
| `products.csv` | One row per product | 80 | `product_id` |
| `orders.csv` | One row per order | 8,000 | `order_id` |
| `order_items.csv` | One row per item in a non-cancelled order | 14,000 | `order_id`, `product_id` |

The exact order and line counts are printed by the generator.

## Key fields and metrics

- `orders.status`: `delivered`, `shipped`, or `cancelled`. Cancelled orders
  have no item rows and an `order_total` of zero.
- `orders.order_total`: item net sales plus shipping, with tax applied.
- `order_items.gross_sales`: `quantity * unit_price`, before discount.
- `order_items.net_sales`: gross sales after discount, before returns.
- `order_items.net_sales_after_returns`: net sales adjusted for the returned
  share of the line quantity; a convenient merchandise-sales measure.
- `order_items.unit_cost`: product cost per unit. Estimate line profit as
  `net_sales_after_returns - unit_cost * (quantity - returned_quantity)`.
- `discount_pct` is a decimal fraction (for example, `0.15` means 15%).
- Dates use ISO `YYYY-MM-DD`; monetary values are in unspecified demo currency
  units and rounded to two decimal places.

Join `orders` to `order_items` on `order_id`, and then to `customers` on
`customer_id` or `products` on `product_id`. Filter cancelled orders out of
sales analyses; they are included in `orders` for cancellation-rate analysis.

## Ideas to explore

- Monthly sales and order trends, including holiday-season peaks
- Revenue, average order value, and cancellations by country or channel
- Category and product performance, margins, discount impact, and returns
- New versus repeat customer behavior and signup cohorts
- Payment and shipping method mix

## Regenerate

From this folder, run:

```bash
python3 generate_commerce_data.py
```

The generator uses only the Python standard library and a fixed random seed,
so it recreates the same CSV contents each time.
