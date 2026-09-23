# Power BI Dashboard Blueprint

The semantic model is in `powerbi_model/` and imports `analysis_output/cleaned_sales_data.csv`.

## Page 1: Executive Overview

- Card: `Total Revenue`
- Card: `Total Profit`
- Card: `Profit Margin`
- Card: `Revenue Growth Rate`
- Card: `Transactions`
- Line chart: `Month` by `Total Revenue`
- Clustered column chart: `Quarter` by `Total Revenue` and `Total Profit`
- Slicers: `Year`, `Quarter`, `Region`, `Product_Category`, `Sales_Channel`

## Page 2: Product Performance

- Bar chart: `Product_ID` by `Total Revenue`, descending
- Bar chart: `Product_ID` by `Total Profit`, ascending for low performers
- Matrix: `Product_Category` > `Product_ID` with `Total Revenue`, `Total Profit`, `Quantity Sold`
- Slicers: `Product_Category`, `Year`, `Region`

## Page 3: Regional and Category Comparison

- Bar chart: `Region` by `Total Revenue`
- Bar chart: `Product_Category` by `Total Revenue`
- Matrix: `Region` by `Product_Category` with `Total Revenue`, `Total Profit`, `Profit Margin`
- Slicers: `Year`, `Sales_Channel`, `Customer_Type`

## Model Notes

- Null rows and exact duplicate rows were removed before import.
- Profit is calculated as `Sales_Amount - (Unit_Cost * Quantity_Sold)`.
- January 2024 contains only three transactions and should be treated as a partial period.
- The model is ready for report visuals once opened in Power BI Desktop.