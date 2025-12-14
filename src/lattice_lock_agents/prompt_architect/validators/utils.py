from typing import Dict

def parse_sections(content: str) -> Dict[str, str]:
    """
    Parse content into sections based on ## headers.
    
    Args:
        content: The text content to parse.
        
    Returns:
        Dict mapping section names to their body text.
    """
    sections = {}
    current_section = None
    current_content = []

    for line in content.split('\n'):
        # Check for section header
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()

            # Start new section
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections
