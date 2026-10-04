import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv() 

OUTPUT_DIR = "data/destinations"

SYSTEM_PROMPT = """You are an expert travel editor. Here is a raw, messy web scrape of a travel guide.
It contains useless navigation menus, HTML artifacts, and overly verbose history.

Extract ONLY the most important travel information and rewrite it into this EXACT Markdown schema.
Keep it crisp, factual, and strictly focused on helping a tourist plan a short itinerary and budget.
Do NOT include exact phone numbers or long history paragraphs. Return ONLY the markdown.

# [City Name]

## Overview
[2-3 sentences max summarizing the vibe and significance]

## Best Time to Visit
- **Peak Season:** [months] ([weather])
- **Off-Peak/Monsoon:** [months]

## Top Attractions
1. **[Name]:** [Brief description and estimated entry cost if available]
(List the top 5-8 most famous attractions only)

## Budget Guide (per person per day)
- **Budget (Backpacker):** ₹[Amount] (hostels, street food, public transport)
- **Mid-range:** ₹[Amount] (hotels, cafes, autos)
- **Luxury:** ₹[Amount] (resorts, private cabs)

## Local Food & Restaurants
- **Must try:** [dishes]
- **Cost:** [typical meal cost]

## Getting There & Local Transport
[Brief summary of nearest airport/train and best way to get around locally (auto-rickshaw, walking, etc.)]

Raw Data:
"""

async def clean_file(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print(f"Cleaning {filename} ({len(raw_text)} chars)...")
    
    # We use Flash Lite because it has a massive context window and is very fast
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite", 
        temperature=0.2, 
        max_retries=3
    )
    
    try:
        response = await llm.ainvoke([
            HumanMessage(content=SYSTEM_PROMPT + "\n\n" + raw_text)
        ])
        
        # Clean up any markdown code block wrappers the LLM might add
        clean_text = response.content.replace("```markdown", "").replace("```", "").strip()
        
        # Save as new clean file
        city_name = filename.replace("_wikivoyage.md", "")
        clean_filepath = os.path.join(OUTPUT_DIR, f"{city_name}.md")
        
        with open(clean_filepath, "w", encoding="utf-8") as f:
            f.write(clean_text)
            
        print(f"Success: Saved clean version to {clean_filepath}")
        
        # Delete old raw file to prevent it from being indexed
        os.remove(filepath)
        
    except Exception as e:
        print(f"Error cleaning {filename}: {e}")

async def main():
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith("_wikivoyage.md")]
    
    print(f"Found {len(files)} raw files to clean.")
    # We run sequentially with a tiny sleep to completely avoid API rate limits
    for file in files:
        await clean_file(file)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
