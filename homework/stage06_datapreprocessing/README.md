## Data Cleaning Strategy (Stage 6)

**Goals:** Make the dataset consistent and model-ready while keeping decisions reproducible.

**Steps:**
1. **Drop mostly-missing columns**: `drop_missing(threshold=0.6, axis='columns')`  
   Rationale: Columns with <60% coverage add noise and require too many assumptions.
2. **Fill numeric NaNs with median**: `fill_missing_median(cols=None)`  
   Rationale: Median is robust to outliers and preserves distribution center.
3. **Drop sparse rows**: `drop_missing(threshold=1.0, axis='rows')`  
   Rationale: After fills, rows with any remaining NAs are removed for consistency.
4. **Normalize numeric features**: `normalize_data(cols=['age','income','score'], method='minmax')`  
   Rationale: Put numeric signals on a comparable scale.

**Assumptions & Tradeoffs:**
- `zipcode` and `city` are categorical and not normalized.
- Median imputation is preferred over mean due to potential outliers.
- 60% column coverage threshold balances retention vs. data quality.
- Min–Max scaling chosen for interpretability; `zscore` is available if preferred.

**Reproducibility:**
- Input: `data/raw/sample_data.csv`
- Output: `data/processed/sample_data_cleaned.csv`
- Logic: `src/cleaning.py`, demonstrated in the Stage 6 notebook.