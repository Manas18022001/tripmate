from pathlib import Path

def test_destinations_directory():
    dest_dir = Path("data/destinations")
    assert dest_dir.exists(), "data/destinations/ directory should exist"
    
    md_files = list(dest_dir.glob("*.md"))
    assert len(md_files) > 0, "Should have at least one .md file"
    
    expected_sections = ["## Overview", "## Top Attractions"]
    
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        for section in expected_sections:
            assert section in content, f"File {md_file.name} missing section: {section}"

def test_chroma_db_directory():
    chroma_dir = Path("data/chroma_db")
    assert chroma_dir.exists(), "data/chroma_db/ directory should exist"
