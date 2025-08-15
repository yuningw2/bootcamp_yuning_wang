# NYC Weather Trends Analysis
**Stage:** Problem Framing & Scoping (Stage 01)

## Problem Statement
New York City residents often experience unpredictable weather patterns.  
This project aims to analyze daily temperature data for NYC over the past month to determine if there is a noticeable warming or cooling trend.  
The results can help local residents and outdoor event planners make short-term decisions about operations.

## Stakeholder & User
- **Primary Stakeholder:** Local event planners.
- **End Users:** Residents and outdoor vendors.
- **Timing:** Analysis will be updated monthly

## Useful Answer & Decision
- **Type:** Descriptive and predictive.
- **Metric:** Average daily temperature and rate of change over time
- **Artifact:** A simple graph and detailed summary table

## Assumptions & Constraints
- Historical temperature data for NYC is freely available online
- Only temperature will be analyzed; humidity, wind, rain are excluded.

## Known Unknowns / Risks
- Weather data quality and availability.
- Missing data for certain days.

## Lifecycle Mapping
Goal → Stage → Deliverable
- Understand recent NYC weather trends → Problem Framing & Scoping (Stage 01) → Scoping stakeholder memo.
- Gather weather data → Data Acquisition (Stage 02) → CSV data file.
- Produce summary and visualization → Analysis (Stage 03) → Graph and table

## Repo Plan
- /data/ → Store raw data.
- /src/ → Python scripts for data analysis.
- /notebooks/ → Jupyter notebooks for exploratory analysis.
- /docs/ → Stakeholder memo and presentation slide.