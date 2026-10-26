#!/usr/bin/env python3
import csv
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
OUT_DIR = ROOT / 'analysis'
OUT_DIR.mkdir(exist_ok=True)


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def safe_float(value):
    return float(value or 0)


def format_money(value):
    return f'${value:,.2f}'


def make_bar_svg(path, title, labels, values, color='#1f77b4', width=700, height=280):
    if not labels:
        return
    max_val = max(values) if values else 1
    chart_h = 170
    chart_w = 560
    left = 80
    top = 40
    bar_w = chart_w / max(len(labels), 1)
    gap = 8
    inner_w = max(bar_w - gap, 10)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:Arial,sans-serif;fill:#1f2937}.label{font-size:12px}.title{font-size:18px;font-weight:bold}</style>',
        f'<text x="{width/2}" y="24" text-anchor="middle" class="title">{title}</text>',
        f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#374151" stroke-width="1"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#374151" stroke-width="1"/>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        h = (value / max_val) * (chart_h - 10)
        x = left + i * (chart_w / len(labels)) + 8
        y = top + chart_h - h
        svg.append(f'<rect x="{x}" y="{y}" width="{inner_w}" height="{h}" fill="{color}" rx="4"/>')
        txt_x = x + inner_w / 2
        svg.append(f'<text x="{txt_x}" y="{top + chart_h + 18}" text-anchor="middle" class="label">{label}</text>')
        if value > 0:
            svg.append(f'<text x="{txt_x}" y="{y - 8}" text-anchor="middle" class="label">{format_money(value)}</text>')
    svg.append('</svg>')
    path.write_text('\n'.join(svg), encoding='utf-8')


def make_line_svg(path, title, labels, values, color='#2ca02c', width=700, height=300):
    if not labels:
        return
    max_val = max(values) if values else 1
    min_val = min(values) if values else 0
    chart_h = 180
    chart_w = 560
    left = 70
    top = 40
    points = []
    for i, value in enumerate(values):
        x = left + (i / max(1, len(values)-1)) * chart_w
        y = top + chart_h - ((value - min_val) / (max_val - min_val + 1e-9)) * (chart_h - 20)
        points.append(f'{x:.1f},{y:.1f}')
    poly = ' '.join(points)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:Arial,sans-serif;fill:#1f2937}.label{font-size:12px}.title{font-size:18px;font-weight:bold}</style>',
        f'<text x="{width/2}" y="24" text-anchor="middle" class="title">{title}</text>',
        f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#374151" stroke-width="1"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#374151" stroke-width="1"/>',
        f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{poly}"/>',
    ]
    for i, label in enumerate(labels):
        x = left + (i / max(1, len(labels)-1)) * chart_w
        svg.append(f'<line x1="{x}" y1="{top + chart_h}" x2="{x}" y2="{top + chart_h + 6}" stroke="#374151" stroke-width="1"/>')
        svg.append(f'<text x="{x}" y="{top + chart_h + 20}" text-anchor="middle" class="label">{label}</text>')
    for i, value in enumerate(values):
        x = left + (i / max(1, len(values)-1)) * chart_w
        y = top + chart_h - ((value - min_val) / (max_val - min_val + 1e-9)) * (chart_h - 20)
        svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
        svg.append(f'<text x="{x}" y="{y - 8}" text-anchor="middle" class="label">{format_money(value)}</text>')
    svg.append('</svg>')
    path.write_text('\n'.join(svg), encoding='utf-8')


def main():
    customers = read_csv(DATA_DIR / 'customers.csv')
    products = read_csv(DATA_DIR / 'products.csv')
    orders = read_csv(DATA_DIR / 'orders.csv')
    items = read_csv(DATA_DIR / 'order_items.csv')

    customer_meta = {c['customer_id']: c for c in customers}
    product_meta = {p['product_id']: p for p in products}
    items_by_order = defaultdict(list)
    for row in items:
        items_by_order[row['order_id']].append(row)

    status_counts = Counter()
    revenue_by_month = defaultdict(float)
    revenue_by_country = defaultdict(float)
    revenue_by_channel = defaultdict(float)
    category_revenue = defaultdict(float)
    category_margin = defaultdict(float)
    category_return_qty = defaultdict(int)
    category_qty = defaultdict(int)
    product_revenue = defaultdict(float)
    customer_order_counts = defaultdict(int)
    total_revenue = 0.0
    total_profit = 0.0
    non_cancelled_orders = 0

    for order in orders:
        status = order['status']
        status_counts[status] += 1
        customer_id = order['customer_id']
        customer_order_counts[customer_id] += 1

        if status == 'cancelled':
            continue

        non_cancelled_orders += 1
        order_total = safe_float(order['order_total'])
        total_revenue += order_total
        month = order['order_date'][:7]
        revenue_by_month[month] += order_total
        country = customer_meta[customer_id]['country']
        revenue_by_country[country] += order_total
        channel = customer_meta[customer_id]['acquisition_channel']
        revenue_by_channel[channel] += order_total

        for item in items_by_order.get(order['order_id'], []):
            pid = item['product_id']
            product = product_meta[pid]
            category = product['category']
            qty = int(item['quantity'])
            returned = int(item['returned_quantity'])
            net_after = safe_float(item['net_sales_after_returns'])
            cost = safe_float(item['unit_cost']) * (qty - returned)
            margin = net_after - cost
            category_revenue[category] += net_after
            category_margin[category] += margin
            category_return_qty[category] += returned
            category_qty[category] += qty
            product_revenue[pid] += net_after
            total_profit += margin

    repeat_customers = sum(1 for count in customer_order_counts.values() if count > 1)
    retention_rate = repeat_customers / len(customers)
    return_rate_total = sum(category_return_qty.values()) / sum(category_qty.values()) if sum(category_qty.values()) else 0.0
    avg_order = total_revenue / non_cancelled_orders if non_cancelled_orders else 0.0
    avg_profit_margin = total_profit / total_revenue if total_revenue else 0.0

    months = sorted(revenue_by_month)
    month_labels = [m[-2:] for m in months]
    monthly_revenue = [revenue_by_month[m] for m in months]

    country_sorted = sorted(revenue_by_country.items(), key=lambda kv: kv[1], reverse=True)[:6]
    channel_sorted = sorted(revenue_by_channel.items(), key=lambda kv: kv[1], reverse=True)
    category_sorted = sorted(category_revenue.items(), key=lambda kv: kv[1], reverse=True)[:5]
    product_sorted = sorted(product_revenue.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return_rate_by_category = {
        category: (category_return_qty[category] / category_qty[category]) if category_qty[category] else 0.0
        for category in sorted(category_revenue)
    }

    make_bar_svg(OUT_DIR / 'country_revenue.svg', 'Revenue by Country', [c for c, _ in country_sorted], [v for _, v in country_sorted], color='#3b82f6')
    make_bar_svg(OUT_DIR / 'category_revenue.svg', 'Revenue by Category', [c for c, _ in category_sorted], [v for _, v in category_sorted], color='#f59e0b')
    make_bar_svg(OUT_DIR / 'channel_revenue.svg', 'Revenue by Acquisition Channel', [c for c, _ in channel_sorted], [v for _, v in channel_sorted], color='#10b981')
    make_line_svg(OUT_DIR / 'monthly_revenue.svg', 'Monthly Revenue Trend', month_labels, monthly_revenue, color='#ef4444')

    top_country = country_sorted[0][0] if country_sorted else 'N/A'
    top_country_revenue = country_sorted[0][1] if country_sorted else 0.0
    top_channel = channel_sorted[0][0] if channel_sorted else 'N/A'
    top_channel_revenue = channel_sorted[0][1] if channel_sorted else 0.0
    top_category = category_sorted[0][0] if category_sorted else 'N/A'
    top_category_revenue = category_sorted[0][1] if category_sorted else 0.0

    insight_lines = [
        '# Commerce Insights',
        '',
        '## Executive summary',
        f'- Total non-cancelled revenue: {format_money(total_revenue)}',
        f'- Average order value: {format_money(avg_order)}',
        f'- Profit contribution after unit cost: {format_money(total_profit)}',
        f'- Gross margin rate: {avg_profit_margin:.1%}',
        f'- Overall return rate: {return_rate_total:.1%}',
        f'- Repeat-customer rate: {retention_rate:.1%}',
        '',
        '## Revenue concentration',
        f'- Largest market by revenue: {top_country} ({format_money(top_country_revenue)})',
        f'- Best acquisition channel by revenue: {top_channel} ({format_money(top_channel_revenue)})',
        f'- Top revenue category: {top_category} ({format_money(top_category_revenue)})',
        '',
        '## Category performance',
    ]

    for category, revenue in category_sorted:
        margin = category_margin[category]
        rr = return_rate_by_category.get(category, 0)
        insight_lines.append(f'- {category}: revenue {format_money(revenue)}, margin {format_money(margin)}, return rate {rr:.1%}')

    insight_lines.extend([
        '',
        '## Product focus',
    ])
    for pid, revenue in product_sorted:
        name = product_meta[pid]['product_name']
        insight_lines.append(f'- {name}: {format_money(revenue)}')

    insight_lines.extend([
        '',
        '## Decision',
        '1. Prioritize growth in the highest-revenue country and acquisition channel, then expand to adjacent markets with similar customer profiles.',
        '2. Build seasonal promotions around the strongest months in the revenue trend, especially late-year holiday demand.',
        '3. Protect margin by pushing higher-margin, lower-return categories first and using bundles to reduce return exposure.',
        '4. Increase retention investment because repeat buyers are a large portion of the order base and revenue is more resilient when supported by loyalty and reactivation campaigns.',
        '',
        '## Artifacts',
        '- analysis/monthly_revenue.svg',
        '- analysis/country_revenue.svg',
        '- analysis/category_revenue.svg',
        '- analysis/channel_revenue.svg',
        '- analysis/insights.md',
    ])

    (OUT_DIR / 'insights.md').write_text('\n'.join(insight_lines), encoding='utf-8')

    print('Revenue summary:')
    print(f'  total_non_cancelled_revenue={format_money(total_revenue)}')
    print(f'  avg_order_value={format_money(avg_order)}')
    print(f'  gross_margin_rate={avg_profit_margin:.1%}')
    print(f'  overall_return_rate={return_rate_total:.1%}')
    print(f'  repeat_customer_rate={retention_rate:.1%}')
    print(f'  top_country={top_country}, {format_money(top_country_revenue)}')
    print(f'  top_channel={top_channel}, {format_money(top_channel_revenue)}')
    print(f'  top_category={top_category}, {format_money(top_category_revenue)}')
    print('Saved outputs to', OUT_DIR)


if __name__ == '__main__':
    main()
