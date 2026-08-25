#!/usr/bin/env python3
"""
Shared XML parsing utilities for TF Harmony subgroups.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import  Optional, Dict, List

# Common namespace definitions
NAMESPACES = {
    'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'datacite': 'http://datacite.org/schema/kernel-4',
    'marc': 'http://www.loc.gov/MARC21/slim'
}

def parse_xml_file(file_path: str) -> Optional[ET.Element]:
    """
    Parse an XML file and return the root element.
    
    Args:
        file_path (str): Path to the XML file
        
    Returns:
        ET.Element or None: Root element if successful, None if error
    """
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error with {file_path}: {e}")
        return None

def parse_xml_string(rec_string: str) -> Optional[ET.Element]:
    """
    Parse an XML file and return the root element.

    Args:
        string (str): string to parse

    Returns:
        ET.Element or None: Root element if successful, None if error
    """
    try:
        root = ET.fromstring(rec_string)
        return root
    except ET.ParseError as e:
        print(f"Error parsing {rec_string}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error with {rec_string}: {e}")
        return None

def extract_elements(root: ET.Element, xpath: str, namespaces: dict[str, str] = None) -> list[str]:
    """
    Extract text content from elements matching an XPath.
    
    Args:
        root (ET.Element): Root element to search
        xpath (str): XPath expression
        namespaces (dict): Namespace mapping
        
    Returns:
        list: List of text content from matching elements
    """
    if namespaces is None:
        namespaces = NAMESPACES
        
    elements = root.findall(xpath, namespaces)
    return [elem.text.strip() for elem in elements if elem.text]

def extract_dc_elements(root: ET.Element) -> Dict[str, List[str]]:
    """
    Navigates the parsed XML to extract all Dublin Core elements.

    Since the root here is the <metadata> element, we look for oai_dc:dc directly
    inside the root, and then iterate over its children (the dc: elements).
    """
    dc_data: Dict[str, List[str]] = {}

    # 1. Find the Dublin Core block: /metadata/oai_dc:dc
    # The root element here is <metadata>, so we search for oai_dc:dc inside it.
    dc_element = root.find('.//oai_dc:dc', NAMESPACES)

    if dc_element is None:
        # If oai_dc:dc is missing, return empty data
        return dc_data

    # 2. Iterate over all Dublin Core children elements (dc:title, dc:creator, etc.)
    # We loop through all children of the <oai_dc:dc> element.
    for child in dc_element:
        # The child's tag will be the full URI: e.g., {http://purl.org/dc/elements/1.1/}title

        # Check if the element belongs to the Dublin Core namespace
        if True:  # child.tag.startswith(NAMESPACES['dc']):
            # Strip the namespace URI to get the simple tag name (e.g., 'title')
            tag_name = child.tag.replace(NAMESPACES['dc'], '').strip('{}')

            # Initialize list for the field if it doesn't exist (handles multivalued)
            if tag_name not in dc_data:
                dc_data[tag_name] = []

            # .text retrieves the content of the element. Use strip() for clean data.
            if child.text:
                # Use .strip() to remove leading/trailing whitespace
                dc_data[tag_name].append(child.text.strip())

    return dc_data

def find_provider_files(base_dir: str, format_type: str = "oai_dc") -> dict[str, list[Path]]:
    """
    Find metadata files organized by provider.
    
    Args:
        base_dir (str): Base directory to search
        format_type (str): Metadata format subdirectory name
        
    Returns:
        dict: Provider name -> list of file paths
    """
    provider_files = {}
    base_path = Path(base_dir)
    
    for provider_dir in base_path.iterdir():
        if provider_dir.is_dir() and provider_dir.name != 'README.md':
            provider_name = provider_dir.name
            format_dir = provider_dir / format_type
            
            if format_dir.exists() and format_dir.is_dir():
                xml_files = list(format_dir.glob('*.xml'))
                if xml_files:
                    provider_files[provider_name] = xml_files
    
    return provider_files
