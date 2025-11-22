import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

# Create charts directory
os.makedirs('charts', exist_ok=True)

# Load data
df = pd.read_excel('df.xlsx')

# Clean data
df = df.drop('Unnamed: 0', axis=1)
df['Phone Numbers'] = df['Phone Numbers'].fillna('Not Available')

print("="*60)
print("KAPITAL BANK PARTNER LIST ANALYSIS")
print("="*60)
print(f"\nTotal Partners: {len(df)}")
print(f"Partners with Phone Numbers: {len(df[df['Phone Numbers'] != 'Not Available'])}")
print(f"Partners without Phone Numbers: {len(df[df['Phone Numbers'] == 'Not Available'])}")
print(f"Missing Addresses: {df['Address'].isna().sum()}")

# Extract cities/regions from addresses
def extract_city(address):
    if pd.isna(address):
        return 'Unknown'
    address = str(address)
    # Common patterns in Azerbaijan addresses
    if 'Bakı' in address or 'Baku' in address:
        # Extract district from Bakı
        districts = ['Yasamal', 'Nərimanov', 'Xətai', 'Nəsimi', 'Səbail',
                    'Binəqədi', 'Nizami', 'Suraxanı', 'Xırdalan', 'Ağ Şəhər',
                    'Yasamal', 'Günəşli', 'Abşeron']
        for district in districts:
            if district in address:
                return f'Bakı - {district}'
        return 'Bakı - Other'
    elif 'Gəncə' in address:
        return 'Gəncə'
    elif 'Sumqayıt' in address:
        return 'Sumqayıt'
    elif 'Mingəçevir' in address:
        return 'Mingəçevir'
    elif 'Zaqatala' in address:
        return 'Zaqatala'
    elif 'Şəki' in address:
        return 'Şəki'
    elif 'Lənkəran' in address:
        return 'Lənkəran'
    else:
        # Try to extract any region name
        words = address.split(',')[0].split()
        if len(words) > 0:
            return words[0]
        return 'Other'

df['City'] = df['Address'].apply(extract_city)

# Get city distribution
city_counts = df['City'].value_counts()

print("\n" + "="*60)
print("GEOGRAPHIC DISTRIBUTION")
print("="*60)
for city, count in city_counts.items():
    print(f"{city}: {count} partners ({count/len(df)*100:.1f}%)")

# Chart 1: Geographic Distribution of Partners
plt.figure(figsize=(12, 8))
colors = sns.color_palette("husl", len(city_counts))
bars = plt.barh(range(len(city_counts)), city_counts.values, color=colors)
plt.yticks(range(len(city_counts)), city_counts.index)
plt.xlabel('Number of Partners', fontsize=12, fontweight='bold')
plt.title('Kapital Bank Partners: Geographic Distribution', fontsize=14, fontweight='bold', pad=20)
plt.grid(axis='x', alpha=0.3)

# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, city_counts.values)):
    plt.text(value + 0.3, bar.get_y() + bar.get_height()/2,
             f'{value} ({value/len(df)*100:.1f}%)',
             va='center', fontsize=9)

plt.tight_layout()
plt.savefig('charts/01_geographic_distribution.png', bbox_inches='tight')
print("\n✓ Chart saved: charts/01_geographic_distribution.png")
plt.close()

# Chart 2: Baku Districts Deep Dive
baku_partners = df[df['City'].str.contains('Bakı', na=False)]
baku_districts = baku_partners['City'].value_counts()

plt.figure(figsize=(10, 6))
colors = sns.color_palette("viridis", len(baku_districts))
plt.pie(baku_districts.values, labels=baku_districts.index, autopct='%1.1f%%',
        colors=colors, startangle=90, textprops={'fontsize': 9})
plt.title('Kapital Bank Partners in Baku: District Distribution',
          fontsize=14, fontweight='bold', pad=20)
plt.axis('equal')
plt.tight_layout()
plt.savefig('charts/02_baku_districts.png', bbox_inches='tight')
print("✓ Chart saved: charts/02_baku_districts.png")
plt.close()

# Chart 3: Data Completeness Analysis
data_quality = {
    'Complete Data\n(Name, Phone, Address)': len(df[(df['Phone Numbers'] != 'Not Available') & (df['Address'].notna())]),
    'Missing Phone Only': len(df[(df['Phone Numbers'] == 'Not Available') & (df['Address'].notna())]),
    'Missing Address Only': len(df[(df['Phone Numbers'] != 'Not Available') & (df['Address'].isna())]),
    'Missing Both': len(df[(df['Phone Numbers'] == 'Not Available') & (df['Address'].isna())])
}

plt.figure(figsize=(10, 6))
colors = ['#2ecc71', '#f39c12', '#e74c3c', '#95a5a6']
wedges, texts, autotexts = plt.pie(data_quality.values(), labels=data_quality.keys(),
                                     autopct='%1.1f%%', colors=colors, startangle=90,
                                     textprops={'fontsize': 10})
plt.title('Partner Data Completeness Analysis', fontsize=14, fontweight='bold', pad=20)
plt.axis('equal')
# Make percentage text bold
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
plt.tight_layout()
plt.savefig('charts/03_data_completeness.png', bbox_inches='tight')
print("✓ Chart saved: charts/03_data_completeness.png")
plt.close()

# Chart 4: Top 10 Locations by Partner Count
top_10_cities = city_counts.head(10)

plt.figure(figsize=(12, 7))
colors = sns.color_palette("coolwarm", len(top_10_cities))
bars = plt.bar(range(len(top_10_cities)), top_10_cities.values, color=colors, edgecolor='black', linewidth=1.2)
plt.xticks(range(len(top_10_cities)), top_10_cities.index, rotation=45, ha='right')
plt.ylabel('Number of Partners', fontsize=12, fontweight='bold')
plt.title('Top 10 Locations by Partner Count', fontsize=14, fontweight='bold', pad=20)
plt.grid(axis='y', alpha=0.3)

# Add value labels on top of bars
for bar, value in zip(bars, top_10_cities.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             str(value), ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('charts/04_top_10_locations.png', bbox_inches='tight')
print("✓ Chart saved: charts/04_top_10_locations.png")
plt.close()

# Chart 5: Contact Information Availability
contact_info = {
    'Phone Available': len(df[df['Phone Numbers'] != 'Not Available']),
    'Phone Missing': len(df[df['Phone Numbers'] == 'Not Available'])
}

plt.figure(figsize=(8, 6))
colors = ['#3498db', '#e67e22']
bars = plt.bar(contact_info.keys(), contact_info.values(), color=colors, edgecolor='black', linewidth=1.5, width=0.6)
plt.ylabel('Number of Partners', fontsize=12, fontweight='bold')
plt.title('Phone Number Availability', fontsize=14, fontweight='bold', pad=20)
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar, (key, value) in zip(bars, contact_info.items()):
    percentage = value / len(df) * 100
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{value}\n({percentage:.1f}%)', ha='center', va='bottom',
             fontweight='bold', fontsize=11)

plt.ylim(0, max(contact_info.values()) + 10)
plt.tight_layout()
plt.savefig('charts/05_phone_availability.png', bbox_inches='tight')
print("✓ Chart saved: charts/05_phone_availability.png")
plt.close()

# Chart 6: Regional Coverage (Major Cities vs Others)
def categorize_region(city):
    major_cities = ['Bakı', 'Gəncə', 'Sumqayıt', 'Mingəçevir']
    for major in major_cities:
        if major in city:
            return major
    return 'Other Regions'

df['Region_Category'] = df['City'].apply(categorize_region)
region_dist = df['Region_Category'].value_counts()

plt.figure(figsize=(10, 7))
colors = sns.color_palette("Set2", len(region_dist))
bars = plt.barh(range(len(region_dist)), region_dist.values, color=colors, edgecolor='black', linewidth=1.2)
plt.yticks(range(len(region_dist)), region_dist.index, fontsize=11)
plt.xlabel('Number of Partners', fontsize=12, fontweight='bold')
plt.title('Regional Coverage: Major Cities vs Other Regions', fontsize=14, fontweight='bold', pad=20)
plt.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, region_dist.values)):
    percentage = value / len(df) * 100
    plt.text(value + 0.5, bar.get_y() + bar.get_height()/2,
             f'{value} ({percentage:.1f}%)', va='center', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('charts/06_regional_coverage.png', bbox_inches='tight')
print("✓ Chart saved: charts/06_regional_coverage.png")
plt.close()

print("\n" + "="*60)
print("All charts generated successfully!")
print("="*60)

# Save summary statistics to use in README
summary_stats = {
    'total_partners': len(df),
    'with_phone': len(df[df['Phone Numbers'] != 'Not Available']),
    'without_phone': len(df[df['Phone Numbers'] == 'Not Available']),
    'phone_percentage': len(df[df['Phone Numbers'] != 'Not Available']) / len(df) * 100,
    'baku_partners': len(df[df['City'].str.contains('Bakı', na=False)]),
    'baku_percentage': len(df[df['City'].str.contains('Bakı', na=False)]) / len(df) * 100,
    'top_location': city_counts.index[0],
    'top_location_count': city_counts.values[0],
    'unique_locations': len(city_counts),
    'complete_data': data_quality['Complete Data\n(Name, Phone, Address)'],
    'complete_data_percentage': data_quality['Complete Data\n(Name, Phone, Address)'] / len(df) * 100
}

# Print summary
print("\n" + "="*60)
print("KEY INSIGHTS")
print("="*60)
print(f"• {summary_stats['baku_percentage']:.1f}% of partners are located in Baku")
print(f"• {summary_stats['phone_percentage']:.1f}% of partners have phone numbers available")
print(f"• {summary_stats['complete_data_percentage']:.1f}% of partners have complete data")
print(f"• Top location: {summary_stats['top_location']} with {summary_stats['top_location_count']} partners")
print(f"• Partners are distributed across {summary_stats['unique_locations']} different locations")
print("="*60)
