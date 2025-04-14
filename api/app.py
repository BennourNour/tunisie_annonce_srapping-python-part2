from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Ajouter le dossier scrapper au PYTHONPATH
current_dir = Path(__file__).parent.absolute()
scrapper_dir = current_dir.parent / 'scrapper'
sys.path.append(str(scrapper_dir))

from scraper import scrape_all_pages, save_to_postgres

# Initialize FastAPI app
app = FastAPI(
    title="Tunisie Annonce API",
    description="API pour scraper et accéder aux annonces immobilières",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def read_csv() -> pd.DataFrame:
    """Lit le fichier CSV des annonces."""
    try:
        csv_path = current_dir.parent / 'tunisie_annonce_listings.csv'
        if not csv_path.exists():
            return None
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        logger.error(f"Error reading the CSV file: {e}")
        return None

@app.get("/")
async def home() -> Dict[str, Any]:
    """Page d'accueil de l'API."""
    return {
        "status": "API is running",
        "endpoints": {
            "/": "GET - Page d'accueil",
            "/annonces": "GET - Retourne toutes les annonces",
            "/scrape": "POST - Lance le scraping"
        }
    }

@app.get("/annonces")
async def get_annonces() -> Dict[str, Any]:
    """Récupère toutes les annonces."""
    logger.info("Fetching announcements...")
    df = read_csv()
    
    if df is not None:
        annonces = df.to_dict(orient='records')
        logger.info(f"Found {len(annonces)} announcements")
        return {
            "status": "success",
            "count": len(annonces),
            "data": annonces
        }
    else:
        logger.error("No data available")
        raise HTTPException(
            status_code=404,
            detail="Aucune donnée disponible. Veuillez d'abord lancer le scraping."
        )

@app.post("/scrape")
async def scrape_annonces() -> Dict[str, Any]:
    """Lance une nouvelle session de scraping."""
    try:
        logger.info("Starting scraping process...")
        
        base_url = "http://www.tunisie-annonce.com/AnnoncesImmobilier.asp?rech_cod_cat=1&rech_cod_rub=&rech_cod_typ=&rech_cod_sou_typ=&rech_cod_pay=TN&rech_cod_reg=&rech_cod_vil=&rech_cod_loc=&rech_prix_min=&rech_prix_max=&rech_surf_min=&rech_surf_max=&rech_age=&rech_photo=&rech_typ_cli=&rech_order_by=31"
        
        # Lancer le scraping
        listings_data = scrape_all_pages(base_url, start_page=489, end_page=855)
        
        if not listings_data:
            logger.error("No data retrieved during scraping")
            raise HTTPException(
                status_code=400,
                detail="Aucune donnée n'a été récupérée pendant le scraping"
            )

        try:
            # Sauvegarder dans PostgreSQL
            save_to_postgres(listings_data)
            logger.info("Data saved to PostgreSQL successfully")
        except Exception as e:
            logger.error(f"Error saving to PostgreSQL: {e}")
            # Continue même si PostgreSQL échoue

        # Sauvegarder dans CSV
        try:
            df = pd.DataFrame(listings_data)
            csv_path = current_dir.parent / 'tunisie_annonce_listings.csv'
            df.to_csv(csv_path, index=False)
            logger.info("Data saved to CSV successfully")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la sauvegarde du CSV: {str(e)}"
            )

        return {
            "status": "success",
            "message": "Scraping terminé avec succès",
            "annonces_count": len(listings_data)
        }

    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du scraping: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
