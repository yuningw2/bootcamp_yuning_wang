## Data Storage

**Folders**
- `data/raw/`: time-stamped CSV snapshots directly from sources or early processing.
- `data/processed/`: cleaned Parquet files for efficient analytics and preserved dtypes.

**Formats**
- **CSV (raw)**: simple interchange format for initial captures.
- **Parquet (processed)**: compressed, better dtype fidelity for downstream work.

**Environment-Driven Paths**
Paths are set in `.env`:

**Utilities**
- `write_df(df, path)`: routes by suffix, creates parent dirs, raises clear error if Parquet engine is missing.
- `read_df(path)`: routes by suffix; for CSV, auto-parses `date` if present.
- Files are time-stamped with `YYYYMMDD-HHMMSS` via a small helper `ts()`.

**Validation**
After writing, we reload both CSV and Parquet and check:
- same shape
- `date` is datetime dtype
- `price` is numeric dtype