# Kapital Bank Partner List Scraper

![Data Analysis](https://img.shields.io/badge/Status-Complete-success)
![Partners](https://img.shields.io/badge/Partners-82-blue)
![Data Quality](https://img.shields.io/badge/Data%20Quality-90.2%25-brightgreen)
![Coverage](https://img.shields.io/badge/Phone%20Coverage-97.6%25-brightgreen)

## 📋 Project Overview

This project scrapes and analyzes the partner list from **Kapital Bank's** mortgage partner portal at [ipoteka.kapitalbank.az/partner/list](https://ipoteka.kapitalbank.az/partner/list).

**Purpose:** To collect, analyze, and visualize data about Kapital Bank's real estate development partners across Azerbaijan.

---

## 📊 Key Findings

### Dataset Summary
- **Total Partners:** 82
- **Geographic Coverage:** 27 locations across Azerbaijan
- **Data Completeness:** 90.2% (74 partners with complete information)
- **Phone Coverage:** 97.6% (80 out of 82 partners)

### Critical Insights

#### 🏙️ Geographic Distribution
- **70.7%** of partners are located in **Baku** (58 partners)
- **29.3%** distributed across other regions (24 partners)
- Top Baku districts: **Yasamal**, **Nərimanov**, **Binəqədi** (7 partners each)

#### 📞 Data Quality
- **90.2%** have complete data (Name, Phone, Address)
- **97.6%** have phone numbers available
- Only **2 partners** missing phone numbers
- Only **6 partners** missing addresses

#### 🌍 Regional Coverage Gap
- **Gəncə** (2nd largest city): Only 1 partner
- **Sumqayıt** (3rd largest city): Only 1 partner
- **Major opportunity** for regional expansion

---

## 📈 Data Visualizations

Comprehensive charts and analysis are available in the **[charts/](charts/)** directory:

### 1. Geographic Distribution
![Geographic Distribution Preview](charts/01_geographic_distribution.png)
*Partner distribution across all 27 locations - Baku dominates with 70.7%*

### 2. Baku Districts Analysis
![Baku Districts](charts/02_baku_districts.png)
*Detailed breakdown of partner distribution within Baku's districts*

### 3. Data Completeness
![Data Completeness](charts/03_data_completeness.png)
*90.2% of partners have complete information - excellent data quality*

### 4. Top 10 Locations
![Top Locations](charts/04_top_10_locations.png)
*Top 10 locations account for 92.7% of all partners*

### 5. Phone Number Availability
![Phone Availability](charts/05_phone_availability.png)
*97.6% phone coverage enables direct partner communication*

### 6. Regional Coverage
![Regional Coverage](charts/06_regional_coverage.png)
*Baku vs Other Regions - significant concentration in the capital*

**📁 [View Full Analysis & Insights →](charts/README.md)**

---

## 🎯 Strategic Recommendations

### Immediate Priorities
1. **Complete Data Collection**
   - Obtain 2 missing phone numbers
   - Verify 6 missing addresses
   - **Target:** 100% data completeness

2. **Regional Expansion**
   - **Gəncə:** Target 5-10 new partners
   - **Sumqayıt:** Target 5-10 new partners
   - **Goal:** Reduce Baku concentration to <60%

3. **Partner Engagement**
   - Leverage 97.6% phone coverage for direct outreach
   - Launch partner communication campaign
   - Establish district-specific support for top Baku areas

### Growth Opportunities
- **Underserved Major Cities:** Gəncə, Sumqayıt, Mingəçevir
- **Baku District Expansion:** Nizami, Səbail districts show potential
- **Regional Hubs:** Establish presence in all cities >50,000 population

---

## 🛠️ Technical Details

### Files & Structure
```
scrape_partner_list/
├── scrape.ipynb              # Web scraping notebook
├── selenium.ipynb            # Selenium-based scraper
├── df.xlsx                   # Raw partner data (82 partners)
├── analyze_and_chart.py      # Analysis & chart generation script
├── charts/                   # Generated visualizations
│   ├── README.md            # Detailed analysis & insights
│   ├── 01_geographic_distribution.png
│   ├── 02_baku_districts.png
│   ├── 03_data_completeness.png
│   ├── 04_top_10_locations.png
│   ├── 05_phone_availability.png
│   └── 06_regional_coverage.png
└── README.md                 # This file
```

### Data Schema
| Column | Type | Description | Completeness |
|--------|------|-------------|--------------|
| Name | String | Partner name | 100% |
| Phone Numbers | String/Float | Contact phone | 97.6% |
| Address | String | Physical address | 92.7% |

### Technologies Used
- **Web Scraping:** Python, Selenium, BeautifulSoup, urllib3
- **Data Processing:** pandas, numpy
- **Visualization:** matplotlib, seaborn
- **Data Storage:** Excel (xlsx)

---

## 🚀 Usage

### Running the Analysis
```bash
# Install dependencies
pip install pandas openpyxl matplotlib seaborn

# Run the analysis script
python3 analyze_and_chart.py
```

This will:
1. Load data from `df.xlsx`
2. Perform comprehensive analysis
3. Generate 6 high-resolution charts in `charts/` directory
4. Print key statistics and insights to console

### Regenerating Charts
Simply run the analysis script again:
```bash
python3 analyze_and_chart.py
```
All charts will be regenerated with the latest data.

---

## 📊 Data Insights Dashboard

### Partner Distribution Metrics
| Metric | Value | Insight |
|--------|-------|---------|
| **Total Partners** | 82 | Solid partner base |
| **Baku Concentration** | 70.7% | ⚠️ Heavy concentration risk |
| **Regional Partners** | 17.1% | 🚨 Expansion needed |
| **Data Completeness** | 90.2% | ✅ High quality |
| **Phone Coverage** | 97.6% | ✅ Communication ready |
| **Unique Locations** | 27 | Good geographic spread |

### Top 5 Partner Locations
1. **Baku - Other Districts:** 17 partners (20.7%)
2. **Baku - Yasamal:** 7 partners (8.5%)
3. **Baku - Nərimanov:** 7 partners (8.5%)
4. **Baku - Binəqədi:** 7 partners (8.5%)
5. **Baku - Xətai:** 5 partners (6.1%)

---

## 💡 Actionable Insights

### ✅ Strengths
- **Excellent data quality** (90.2% complete)
- **High contact accessibility** (97.6% with phones)
- **Strong Baku presence** across multiple districts
- **27 unique locations** showing diverse reach

### ⚠️ Opportunities for Improvement
- **Regional imbalance:** 70.7% in Baku vs 17.1% in other regions
- **Major cities underserved:** Gəncə and Sumqayıt have only 1 partner each
- **6 partners** need address updates
- **2 partners** need phone number collection

### 🎯 Strategic Actions
1. **Launch regional expansion** targeting Gəncə and Sumqayıt
2. **Complete data collection** for 100% coverage
3. **Develop district-specific strategies** for top Baku areas
4. **Implement quarterly data refresh** process
5. **Create partner performance benchmarks** by location

---

## 📅 Data Freshness

- **Last Scraped:** Check `df.xlsx` modification date
- **Last Analysis:** November 22, 2025
- **Source:** [Kapital Bank Partner List](https://ipoteka.kapitalbank.az/partner/list)
- **Recommended Refresh:** Quarterly or when major changes occur

---

## 📖 Documentation

- **[Full Analysis Report](charts/README.md)** - Detailed insights, recommendations, and strategic planning
- **[Chart Gallery](charts/)** - All 6 visualization files (high-resolution PNG)

---

## 🔄 Future Enhancements

- [ ] Automated scheduled scraping (weekly/monthly)
- [ ] Partner performance tracking over time
- [ ] Competitive analysis (compare with other banks)
- [ ] Interactive dashboard (Plotly/Dash)
- [ ] Partner categorization (size, type, specialty)
- [ ] Contact validation automation
- [ ] API integration for real-time updates

---

## 📞 Support & Contribution

For questions, issues, or contributions, please refer to the project repository.

---

## 📄 License

This project is for educational and analytical purposes.

---

**Last Updated:** November 22, 2025
**Data Source:** [Kapital Bank Partner Portal](https://ipoteka.kapitalbank.az/partner/list)
**Analysis Version:** 1.0
