from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "sales_data.csv"
OUTPUT_DIR = BASE_DIR / "analysis_output"


def add_metrics(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy()
    result["Sale_Date"] = pd.to_datetime(result["Sale_Date"], errors="coerce")
    result["Revenue"] = result["Sales_Amount"]
    result["Cost"] = result["Unit_Cost"] * result["Quantity_Sold"]
    result["Profit"] = result["Revenue"] - result["Cost"]
    result["Profit_Margin"] = result["Profit"] / result["Revenue"].where(result["Revenue"] != 0)
    return result


def summarize(dataframe: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    summary = (
        dataframe.groupby(group_columns, dropna=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Quantity_Sold=("Quantity_Sold", "sum"),
            Transactions=("Product_ID", "size"),
        )
        .reset_index()
    )
    summary["Profit_Margin"] = summary["Profit"] / summary["Revenue"].where(summary["Revenue"] != 0)
    summary["Growth_Rate"] = summary["Revenue"].pct_change()
    return summary


def format_value(value: float) -> str:
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    return "N/A" if pd.isna(value) else f"{value:.2%}"


def main() -> None:
    raw = pd.read_csv(INPUT_PATH)
    input_rows = len(raw)
    missing_before = int(raw.isna().sum().sum())
    duplicates_before = int(raw.duplicated().sum())

    data = add_metrics(raw.dropna().drop_duplicates())
    data = data.dropna(subset=["Sale_Date"])
    data["Month"] = data["Sale_Date"].dt.to_period("M").astype(str)
    data["Quarter"] = data["Sale_Date"].dt.to_period("Q").astype(str)
    data["Year"] = data["Sale_Date"].dt.year.astype(str)

    monthly = summarize(data, ["Month"])
    quarterly = summarize(data, ["Quarter"])
    yearly = summarize(data, ["Year"])
    product = summarize(data, ["Product_ID"])
    category = summarize(data, ["Product_Category"])
    region = summarize(data, ["Region"])

    total_revenue = data["Revenue"].sum()
    total_profit = data["Profit"].sum()
    first_month_revenue = monthly.iloc[0]["Revenue"]
    last_month_revenue = monthly.iloc[-1]["Revenue"]
    revenue_growth = (last_month_revenue / first_month_revenue) - 1 if first_month_revenue else float("nan")
    kpis = pd.DataFrame(
        {
            "KPI": [
                "Total revenue",
                "Total profit",
                "Profit margin",
                "Total quantity sold",
                "Transactions",
                "Average transaction revenue",
                "First month to last month growth",
                "Rows after cleaning",
                "Null values removed",
                "Duplicate rows removed",
            ],
            "Value": [
                total_revenue,
                total_profit,
                total_profit / total_revenue if total_revenue else float("nan"),
                data["Quantity_Sold"].sum(),
                len(data),
                data["Revenue"].mean(),
                revenue_growth,
                len(data),
                missing_before,
                duplicates_before,
            ],
        }
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    data.to_csv(OUTPUT_DIR / "cleaned_sales_data.csv", index=False)
    kpis.to_csv(OUTPUT_DIR / "kpis.csv", index=False)
    monthly.to_csv(OUTPUT_DIR / "monthly_trends.csv", index=False)
    quarterly.to_csv(OUTPUT_DIR / "quarterly_trends.csv", index=False)
    yearly.to_csv(OUTPUT_DIR / "yearly_trends.csv", index=False)
    product.sort_values("Revenue", ascending=False).to_csv(OUTPUT_DIR / "product_performance.csv", index=False)
    category.sort_values("Revenue", ascending=False).to_csv(OUTPUT_DIR / "category_comparison.csv", index=False)
    region.sort_values("Revenue", ascending=False).to_csv(OUTPUT_DIR / "region_comparison.csv", index=False)

    top_products = product.sort_values("Revenue", ascending=False).head(10)
    low_products = product.sort_values("Revenue", ascending=True).head(10)
    top_category = category.sort_values("Revenue", ascending=False).iloc[0]
    top_region = region.sort_values("Revenue", ascending=False).iloc[0]
    best_month = monthly.loc[monthly["Revenue"].idxmax()]
    worst_month = monthly.loc[monthly["Revenue"].idxmin()]

    report = [
        "# Sales Analysis Report",
        "",
        "## Data Preparation",
        f"- Input rows: {input_rows:,}",
        f"- Rows after removing nulls and exact duplicates: {len(data):,}",
        f"- Null values removed: {missing_before:,}",
        f"- Duplicate rows removed: {duplicates_before:,}",
        f"- Date range: {data['Sale_Date'].min():%Y-%m-%d} to {data['Sale_Date'].max():%Y-%m-%d}",
        "- Profit formula: `Sales_Amount - (Unit_Cost * Quantity_Sold)`",
        "",
        "## KPIs",
        f"- Total revenue: {format_value(total_revenue)}",
        f"- Total profit: {format_value(total_profit)}",
        f"- Profit margin: {format_percent(total_profit / total_revenue)}",
        f"- Total quantity sold: {data['Quantity_Sold'].sum():,.0f}",
        f"- Transactions: {len(data):,}",
        f"- Average transaction revenue: {format_value(data['Revenue'].mean())}",
        f"- First month to last month growth: {format_percent(revenue_growth)}",
        "",
        "## Trends",
        f"- Highest-revenue month: {best_month['Month']} ({format_value(best_month['Revenue'])})",
        f"- Lowest-revenue month: {worst_month['Month']} ({format_value(worst_month['Revenue'])})",
        "",
        "### Yearly",
        yearly.to_markdown(index=False, floatfmt=".2f"),
        "",
        "### Quarterly",
        quarterly.to_markdown(index=False, floatfmt=".2f"),
        "",
        "### Monthly",
        monthly.to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Top-Selling Products",
        top_products.to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Low-Performing Products",
        low_products.to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Region Comparison",
        f"- Top region by revenue: {top_region['Region']} ({format_value(top_region['Revenue'])})",
        region.to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Category Comparison",
        f"- Top category by revenue: {top_category['Product_Category']} ({format_value(top_category['Revenue'])})",
        category.to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Output Files",
        "See `analysis_output/` for cleaned data and CSV summaries.",
    ]
    (OUTPUT_DIR / "sales_analysis_report.md").write_text("\n".join(report), encoding="utf-8")

    print(f"Analyzed {len(data):,} rows")
    print(f"Total revenue: {format_value(total_revenue)}")
    print(f"Total profit: {format_value(total_profit)}")
    print(f"Profit margin: {format_percent(total_profit / total_revenue)}")
    print(f"Top product: {int(top_products.iloc[0]['Product_ID'])}")
    print(f"Top region: {top_region['Region']}")
    print(f"Top category: {top_category['Product_Category']}")
    print(f"Report: {OUTPUT_DIR / 'sales_analysis_report.md'}")


if __name__ == "__main__":
    main()