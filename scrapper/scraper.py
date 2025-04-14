import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2  # For PostgreSQL integration
from datetime import datetime

def scrape_tunisie_annonce(url):
    """
    Scrape a single page of listings and filter for January and February 2025 announcements.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('tr')  

    data = []
    for listing in listings:
        cols = listing.find_all('td')  
        if len(cols) == 13: 
            title = cols[7].find('a').text.strip() if cols[7].find('a') else "N/A"
            price = cols[9].text.strip() if cols[9].text else "N/A"
            property_type = cols[5].text.strip() if cols[5].text else "N/A"
            location = cols[1].find('a').text.strip() if cols[1].find('a') else "N/A"
            publication_date = cols[11].text.strip() if cols[11].text else "N/A"
            link = cols[7].find('a')['href'] if cols[7].find('a') else "N/A"

            # Convert date string to datetime object
            try:
                date_obj = datetime.strptime(publication_date, '%d/%m/%Y')
                # Check if the month is January (1) or February (2) AND year is 2025
                if date_obj.month in [1, 2] and date_obj.year == 2025:
                    data.append({
                        'title': title,
                        'price': price,
                        'property_type': property_type,
                        'location': location,
                        'publication_date': publication_date,
                        'link': link
                    })
            except ValueError:
                # Skip entries with invalid dates
                continue

    return data

def scrape_all_pages(base_url, start_page=489, end_page=855):
    """
    Scrape les pages de listings dans une plage spécifique.
    """
    all_data = []
    for page in range(start_page, end_page + 1):
        url = f"{base_url}&rech_page_num={page}"  
        print(f"Scraping page {page}...")
        page_data = scrape_tunisie_annonce(url)
        
        if not page_data:
            print(f"Aucune donnée trouvée sur la page {page}, arrêt du scraping")
            break
            
        all_data.extend(page_data)
        print(f"Trouvé {len(page_data)} annonces sur la page {page}")
        
    print(f"Scraping terminé. Total des annonces trouvées: {len(all_data)}")
    return all_data

def save_to_postgres(data):
    """
    Save scraped data to PostgreSQL.
    """
    # Database connection details
    conn = psycopg2.connect(
        dbname="tunisie_annonce",  # Your database name
        user="postgres",      # Your PostgreSQL username
        password="root",  # Your PostgreSQL password
        host="localhost",          # Your database host
        port="5432"                # Your database port
    )
    cursor = conn.cursor()

    # Insert data into the table
    for item in data:
        # Nettoyer le prix : supprimer les espaces et convertir en entier
        clean_price = item['price'].replace(" ", "").replace(",", "").strip()
        clean_price = int(clean_price) if clean_price.isdigit() else None  # Convertir en entier ou None si invalide

        cursor.execute("""
            INSERT INTO annonces (title, price, property_type, location, publication_date, link)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            item['title'],
            clean_price,
            item['property_type'],
            item['location'],
            item['publication_date'],
            item['link']
        ))

    # Commit and close the connection
    conn.commit()
    cursor.close()
    conn.close()
    print("Data saved to PostgreSQL database.")


base_url = "http://www.tunisie-annonce.com/AnnoncesImmobilier.asp?rech_cod_cat=1&rech_cod_rub=&rech_cod_typ=&rech_cod_sou_typ=&rech_cod_pay=TN&rech_cod_reg=&rech_cod_vil=&rech_cod_loc=&rech_prix_min=&rech_prix_max=&rech_surf_min=&rech_surf_max=&rech_age=&rech_photo=&rech_typ_cli=&rech_order_by=31"

# Scraper uniquement les pages 489 à 855
listings_data = scrape_all_pages(base_url, start_page=489, end_page=855)

# Save the data to PostgreSQL
save_to_postgres(listings_data)


df = pd.DataFrame(listings_data)
df.to_csv('tunisie_annonce_listings.csv', index=False)
print("Data saved to tunisie_annonce_listings.csv")
