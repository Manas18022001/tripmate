import os
import httpx
import asyncio

# A curated list of top Indian destinations on Wikivoyage
DESTINATIONS = {
    "agra": "https://en.wikivoyage.org/wiki/Agra",
    "udaipur": "https://en.wikivoyage.org/wiki/Udaipur",
    "varanasi": "https://en.wikivoyage.org/wiki/Varanasi",
    "darjeeling": "https://en.wikivoyage.org/wiki/Darjeeling",
    "hampi": "https://en.wikivoyage.org/wiki/Hampi",
    "mumbai": "https://en.wikivoyage.org/wiki/Mumbai",
    "leh": "https://en.wikivoyage.org/wiki/Leh",
    "andaman": "https://en.wikivoyage.org/wiki/Andaman_and_Nicobar_Islands"
}

OUTPUT_DIR = "data/destinations"
JINA_BASE = "https://r.jina.ai/"

async def scrape_url(client, name, url):
    print(f"Scraping {name}...")
    try:
        # We use Jina's API to instantly fetch the markdown version of the page
        # Passing headers to ask for clean markdown
        headers = {
            "Accept": "text/markdown",
            "X-Return-Format": "markdown"
        }
        response = await client.get(f"{JINA_BASE}{url}", headers=headers, timeout=60.0)
        response.raise_for_status()
        
        # Save the resulting markdown
        filepath = os.path.join(OUTPUT_DIR, f"{name}_wikivoyage.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(f"✅ Successfully saved {name} to {filepath}")
    except Exception as e:
        print(f"❌ Failed to scrape {name}: {e}")

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # We use limits to avoid overwhelming the free Jina API
    limits = httpx.Limits(max_connections=3)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [scrape_url(client, name, url) for name, url in DESTINATIONS.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("Starting Wikivoyage scraper using Jina AI...")
    asyncio.run(main())
    print("Scraping complete!")
