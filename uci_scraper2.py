import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

def improved_scraper():
    """Forbedret scraper med bedre stop-logik"""
    print("=" * 60)
    print("🚴 Forbedret UCI Ranking Scraper")
    print("=" * 60)
    
    # Brug cloudscraper til at omgå Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'mobile': False
        }
    )
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
    }
    scraper.headers.update(headers)
    
    all_data = []
    offset = 0
    page_num = 1
    MAX_PAGES = 20  # Sikkerhedsstop
    
    print(f"🔄 Starter scraping...")
    print("-" * 60)
    
    while page_num <= MAX_PAGES:
        url = f"https://www.procyclingstats.com/rankings.php?p=uci-season-individual&s=&date=2026-01-25&nation=&age=&page=smallerorequal&team=&offset={offset}&teamlevel=&filter=Filter"
        
        print(f"📥 Side {page_num}: Henter offset {offset}...")
        
        try:
            # Tilfældig forsinkelse
            time.sleep(random.uniform(1.5, 3))
            
            response = scraper.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"   ❌ HTTP {response.status_code} - stopper")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                print("   ❌ Ingen tabel fundet - stopper")
                break
            
            # Find alle rækker med data (spring over tomme rækker)
            rows = table.find_all('tr')
            data_rows = []
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [cell.get_text(' ', strip=True) for cell in cells]
                    # Kun gem rækker der ligner rigtige data (min. 4 celler)
                    if len(row_data) >= 4:
                        # Tjek om det er en data-række (indeholder et tal i første eller sidste kolonne)
                        if any(cell.strip().isdigit() for cell in row_data[:1]) or \
                           any('.' in cell or cell.replace('.', '').isdigit() for cell in row_data[-1:]):
                            data_rows.append(row_data)
            
            print(f"   📊 Fundet {len(rows)} rækker totalt, {len(data_rows)} data-rækker")
            
            # Stop-betingelser:
            # 1. Ingen data-rækker
            # 2. Kun header-rækken (rækker med '#', 'Rider', 'Points' osv.)
            # 3. Meget få data-rækker (under 5) EFTER første side
            
            if not data_rows:
                print("   ✅ Ingen data - færdig!")
                break
            
            # Tjek om det kun er header
            header_keywords = ['#', 'Rider', 'Team', 'Points', 'Prev.', 'Diff.']
            is_header_only = all(
                any(keyword in str(row) for keyword in header_keywords)
                for row in data_rows
            )
            
            if is_header_only and page_num > 1:
                print("   ✅ Kun header fundet - færdig!")
                break
            
            # Tjek for meget få data-rækker (efter første side)
            if page_num > 1 and len(data_rows) < 5:
                print(f"   ⚠️  Kun {len(data_rows)} data-rækker - antager det er slut")
                
                # Tjek om det virkelig er data eller bare header
                has_real_data = False
                for row in data_rows:
                    # Tjek om rækken indeholder point (tal med decimal)
                    if len(row) >= 6:
                        points = row[-1]
                        if '.' in points or points.isdigit():
                            has_real_data = True
                            break
                
                if not has_real_data:
                    print("   ✅ Ingen rigtige data - færdig!")
                    break
            
            # Tilføj data
            all_data.extend(data_rows)
            
            # Hvis vi får mindre end 50 data-rækker (efter første side), stop
            if page_num > 1 and len(data_rows) < 50:
                print(f"   ⚠️  Kun {len(data_rows)} rækker - sidste side nået")
                break
            
            # Øg offset
            offset += 100
            page_num += 1
            
        except Exception as e:
            print(f"   ❌ Fejl: {e}")
            break
    
    print("-" * 60)
    
    if not all_data:
        print("❌ Ingen data blev hentet")
        return
    
    # Konverter til DataFrame
    df = pd.DataFrame(all_data)
    
    # Find header automatisk
    if len(df) > 0:
        # Kig på første række for header-nøgleord
        first_row_str = ' '.join(df.iloc[0].astype(str))
        header_found = any(keyword in first_row_str for keyword in 
                          ['#', 'Rider', 'Team', 'Points', 'Prev.', 'Diff.'])
        
        if header_found:
            print("📋 Header identificeret - bruger som kolonnenavne")
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
    
    # Rens data
    df = df.dropna(how='all')
    
    # Gem som Excel
    excel_file = 'UCI_Ranking_Korrigeret.xlsx'
    try:
        df.to_excel(excel_file, index=False)
        file_path = os.path.abspath(excel_file)
        
        print(f"✅ Scraping færdig!")
        print(f"📊 Hentet {len(df)} ryttere")
        print(f"💾 Gemt som: {excel_file}")
        print(f"📁 Sti: {file_path}")
        
        # Vis statistik
        if len(df) > 0:
            print(f"\n🏆 Top 5 ryttere:")
            for i in range(min(5, len(df))):
                rider = df.iloc[i].get('Rider', '') if 'Rider' in df.columns else df.iloc[i][3] if len(df.iloc[i]) > 3 else 'N/A'
                points = df.iloc[i].get('Points', '') if 'Points' in df.columns else df.iloc[i][5] if len(df.iloc[i]) > 5 else 'N/A'
                print(f"   {i+1}. {rider}: {points} point")
        
        print(f"\n🎯 Åbn filen med: open '{excel_file}'")
        
    except Exception as e:
        print(f"❌ Fejl ved skrivning til Excel: {e}")
        # Fallback til CSV
        csv_file = 'UCI_Ranking_Korrigeret.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 Fallback: Gemt som CSV: {csv_file}")
    
    print("=" * 60)

if __name__ == "__main__":
    improved_scraper()