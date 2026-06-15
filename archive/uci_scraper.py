import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import os

def setup_scraper():
    """Opsætter cloudscraper med realistiske browser-headers for Mac"""
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',  # Ændret fra 'macos' til 'darwin'
            'mobile': False
        }
    )
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.procyclingstats.com/',
        'DNT': '1',
    }
    
    scraper.headers.update(headers)
    return scraper

def parse_ranking_table(html):
    """Parser HTML og ekstraherer data fra tabellen"""
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    
    if not table:
        return []
    
    all_rows = []
    rows = table.find_all('tr')
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if not cells:
            continue
            
        row_data = []
        for cell in cells:
            # Fjern overflødige whitespace og linjeskift
            text = cell.get_text(' ', strip=True)
            # Fjern eventuelle ekstra mellemrum
            text = ' '.join(text.split())
            row_data.append(text)
        
        # Vi forventer mindst 5 kolonner: #, Prev., Diff., Rider, Team, Points
        if len(row_data) >= 5:
            all_rows.append(row_data)
    
    return all_rows

def update_url_offset(url, offset):
    """Opdaterer offset-parameteren i en URL"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['offset'] = [str(offset)]
    new_query = urlencode(query_params, doseq=True)
    
    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))

def scrape_all_pages(base_url, max_pages=30):
    """Henter alle sider fra ranking-siden"""
    scraper = setup_scraper()
    all_data = []
    
    current_offset = 0
    page_count = 0
    consecutive_empty = 0
    
    print(f"🔄 Starter scraping af UCI World Ranking...")
    print(f"📊 Baseret på: {base_url}")
    print("-" * 60)
    
    while page_count < max_pages and consecutive_empty < 2:
        try:
            current_url = update_url_offset(base_url, current_offset)
            print(f"📥 Side {page_count + 1}: Henter offset {current_offset}...")
            
            # Tilfældig forsinkelse for at være server-venlig
            time.sleep(random.uniform(1.5, 3))
            
            response = scraper.get(current_url, timeout=30)
            
            if response.status_code != 200:
                print(f"   ❌ HTTP {response.status_code} - stopper")
                break
            
            page_data = parse_ranking_table(response.text)
            
            if page_data:
                all_data.extend(page_data)
                print(f"   ✅ Hentet {len(page_data)} rækker")
                consecutive_empty = 0
                
                # Hvis vi får mindre end 50 rækker (undtagen første side), kan det være slut
                if page_count > 0 and len(page_data) < 50:
                    print(f"   ⚠️  Kun {len(page_data)} rækker - kan være sidste side")
            else:
                print(f"   ⚠️  Ingen data på offset {current_offset}")
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    print(f"   🛑 2 tomme sider i træk - stopper")
                    break
            
            current_offset += 100
            page_count += 1
            
        except Exception as e:
            print(f"   ❌ Fejl: {e}")
            time.sleep(5)
            consecutive_empty += 1
            if consecutive_empty >= 3:
                break
    
    print("-" * 60)
    print(f"✅ Scraping færdig! Samlet: {len(all_data)} rækker fra {page_count} sider")
    return all_data

def clean_and_save_to_excel(data, filename='UCI_World_Ranking.xlsx'):
    """Renser data og gemmer som Excel-fil"""
    if not data:
        print("❌ Ingen data at gemme")
        return None
    
    # Opret DataFrame
    df = pd.DataFrame(data)
    
    # Hvis første række ligner en header, brug den som kolonnenavne
    if len(df) > 0:
        first_row = df.iloc[0].astype(str).str.cat(sep=' ')
        
        # Tjek om første række indeholder header-nøgleord
        header_keywords = ['#', 'Prev.', 'Diff.', 'Rider', 'Team', 'Points']
        if any(keyword in first_row for keyword in header_keywords):
            print("📋 Header identificeret i første række")
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
        else:
            # Brug standard kolonnenavne
            df.columns = ['Rank', 'Previous', 'Difference', 'Rider', 'Team', 'Points']
    
    # Rens kolonnenavne
    if isinstance(df.columns, pd.Index):
        df.columns = [str(col).strip() for col in df.columns]
    
    # Fjern tomme rækker
    df = df.dropna(how='all')
    
    # Konverter Points til tal (hvis kolonnen findes)
    if 'Points' in df.columns:
        # Fjern eventuelle kommaer og konverter til tal
        df['Points'] = pd.to_numeric(df['Points'].astype(str).str.replace(',', ''), errors='coerce')
    
    # Gem til Excel med formattering
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='UCI Ranking', index=False)
            
            # Auto-juster kolonnebredder
            worksheet = writer.sheets['UCI Ranking']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Get file path
        file_path = os.path.abspath(filename)
        
        print(f"💾 Data gemt som Excel-fil: {filename}")
        print(f"📁 Sti: {file_path}")
        print(f"📊 Form: {df.shape[0]} rækker × {df.shape[1]} kolonner")
        
        return df, file_path
        
    except Exception as e:
        print(f"❌ Fejl ved skrivning til Excel: {e}")
        # Fallback: Gem som CSV
        csv_filename = filename.replace('.xlsx', '.csv')
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"💾 Fallback: Data gemt som CSV: {csv_filename}")
        return df, os.path.abspath(csv_filename)

def main():
    """Hovedfunktion"""
    print("=" * 60)
    print("🚴 UCI World Ranking Scraper for Mac")
    print("=" * 60)
    
    # URL for side 1
    base_url = "https://www.procyclingstats.com/rankings.php?p=uci-season-individual&s=&date=2026-01-25&nation=&age=&page=smallerorequal&team=&offset=0&teamlevel=&filter=Filter"
    
    # Hent alle data
    all_data = scrape_all_pages(base_url, max_pages=30)
    
    # Gem som Excel-fil
    if all_data:
        df, file_path = clean_and_save_to_excel(all_data, 'UCI_World_Ranking.xlsx')
        
        # Ekstra analyse
        if df is not None and len(df) > 0:
            print("\n📈 Statistik:")
            print(f"   Antal ryttere: {len(df)}")
            
            if 'Points' in df.columns:
                try:
                    points_series = pd.to_numeric(df['Points'], errors='coerce')
                    print(f"   Højeste point: {points_series.max():.0f}")
                    print(f"   Laveste point: {points_series.min():.0f}")
                    print(f"   Gennemsnit: {points_series.mean():.1f}")
                    
                    # Top 5 ryttere
                    print("\n🏆 Top 5 ryttere:")
                    top_5 = df.nlargest(5, 'Points') if 'Points' in df.columns else df.head(5)
                    for i, (_, row) in enumerate(top_5.iterrows(), 1):
                        rider = row.get('Rider', row.get('Rider Name', 'N/A'))
                        points = row.get('Points', 'N/A')
                        team = row.get('Team', 'N/A')
                        print(f"   {i}. {rider} ({team}): {points} point")
                except Exception as e:
                    print(f"   Note: Kunne ikke analysere points: {e}")
            
            print("\n✅ Færdig! Åbn filen i Excel eller Numbers.")
            print(f"💡 Tip: Kør 'open {os.path.basename(file_path)}' i Terminal for at åbne filen.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()