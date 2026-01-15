#!/usr/bin/env python3
"""
Parse Regulatory Authorities Database

Extracts structured data from the comprehensive regulatory authorities text file
and generates YAML configuration for 23 countries.

Usage:
    python scripts/parse_regulatory_data.py
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional


# Mapping of country names to authority codes
COUNTRY_TO_CODE = {
    "Zimbabwe": "MCAZ_ZW",
    "Australia": "TGA_AU",
    "Bangladesh": "BFDA_BD",
    "Brazil": "ANVISA_BR",
    "Canada": "HEALTH_CANADA",
    "China": "NMPA_CN",
    "DRC": "DGRDF_CD",
    "Guinea": "DNPL_GN",
    "India": "CDSCO_IN",
    "Kenya": "PPB_KE",
    "Liberia": "LMHRA_LR",
    "Malawi": "MCAZ_MW",
    "Mali": "DPM_ML",
    "Mexico": "COFEPRIS_MX",
    "Peru": "DIGEMID_PE",
    "Sierra Leone": "PSLB_SL",
    "South Africa": "SAHPRA_ZA",
    "Tanzania": "TFDA_TZ",
    "Thailand": "FDA_TH",
    "Uganda": "NDA_UG",
    "United Kingdom": "MHRA_UK",
    "United States": "FDA_US",
    "Vietnam": "MOH_VN"
}


def parse_regulatory_file(file_path: str) -> Dict[str, Dict]:
    """
    Parse the regulatory authorities file and extract structured data

    Args:
        file_path: Path to the Regulatory Authorities.txt file

    Returns:
        Dictionary mapping country codes to extracted data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by "Skip to main content" which marks new country sections
    sections = content.split('Skip to main content')

    countries_data = {}

    for section in sections[1:]:  # Skip first empty split
        # Extract country name (usually appears after Menu around line 8)
        lines = section.split('\n')
        country_name = None

        for i, line in enumerate(lines[5:15]):  # Check lines 5-15 for country name
            stripped = line.strip()
            if stripped and stripped in COUNTRY_TO_CODE:
                country_name = stripped
                break

        if not country_name:
            continue

        print(f"Processing: {country_name}")

        # Extract data for this country
        country_data = extract_country_data(country_name, section)

        if country_data:
            code = COUNTRY_TO_CODE[country_name]
            countries_data[code] = country_data

    return countries_data


def extract_country_data(country_name: str, section: str) -> Optional[Dict]:
    """
    Extract regulatory data for a specific country

    Args:
        country_name: Name of the country
        section: Text section for this country

    Returns:
        Dictionary with structured country data
    """
    data = {
        "country": country_name,
        "name": None,
        "regulatory_authority": {},
        "ethics_committee": {},
        "regulatory_gates": [],
        "review_timelines": {},
        "fees": {},
        "contact": {}
    }

    # Extract authority name
    auth_name = extract_authority_name(section)
    if auth_name:
        data["name"] = auth_name

    # Extract review timelines
    timelines = extract_review_timelines(section)
    data["review_timelines"] = timelines

    # Extract fees
    fees = extract_fees(section)
    data["fees"] = fees

    # Extract contact information
    contact = extract_contact_info(section)
    data["contact"] = contact

    # Extract regulatory gates
    gates = extract_regulatory_gates(country_name, section, timelines)
    data["regulatory_gates"] = gates

    return data


def extract_authority_name(section: str) -> Optional[str]:
    """Extract the regulatory authority name from section"""
    # Look for patterns like "Medicines Control Authority of Zimbabwe (MCAZ)"
    # or "Therapeutic Goods Administration (TGA)"
    patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Authority|Administration|Agency|Board|Council)(?:\s+of\s+[A-Z][a-z]+)?)\s*\(',
        r'(?:The\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Authority|Administration|Agency|Board|Council))',
    ]

    for pattern in patterns:
        match = re.search(pattern, section[:2000])  # Check first 2000 chars
        if match:
            return match.group(1).strip()

    return None


def extract_review_timelines(section: str) -> Dict:
    """Extract review timeline information"""
    timelines = {}

    # Look for patterns like "30-day review", "60 days", "30 to 90 days"
    patterns = {
        'standard_review_days': r'(\d+)[-\s]day\s+(?:review|evaluation|assessment)',
        'expedited_review_days': r'(?:expedited|fast[- ]track|priority).*?(\d+)[-\s]day',
        'amendment_review_days': r'amendment.*?(\d+)[-\s]day',
    }

    for key, pattern in patterns.items():
        matches = re.findall(pattern, section, re.IGNORECASE)
        if matches:
            # Take the first match, convert to int
            try:
                timelines[key] = int(matches[0])
            except ValueError:
                pass

    return timelines


def extract_fees(section: str) -> Dict:
    """Extract fee information"""
    fees = {}

    # Look for fee patterns: "$X USD", "$X,XXX USD", "X AUD", etc.
    fee_patterns = [
        (r'local\s+sponsor.*?\$?([\d,]+)\s*(?:USD|AUD|EUR|GBP)', 'local_sponsor_usd'),
        (r'foreign\s+sponsor.*?\$?([\d,]+)\s*(?:USD|AUD|EUR|GBP)', 'foreign_sponsor_usd'),
        (r'application\s+fee.*?\$?([\d,]+)\s*(?:USD|AUD|EUR|GBP)', 'application_fee_usd'),
        (r'expedited.*?\$?([\d,]+)\s*(?:USD|AUD|EUR|GBP)', 'expedited_fee_usd'),
        (r'amendment.*?\$?([\d,]+)\s*(?:USD|AUD|EUR|GBP)', 'amendment_fee_usd'),
    ]

    for pattern, key in fee_patterns:
        matches = re.findall(pattern, section, re.IGNORECASE)
        if matches:
            try:
                # Remove commas and convert to int
                fee_str = matches[0].replace(',', '')
                fees[key] = int(fee_str)
            except ValueError:
                pass

    return fees


def extract_contact_info(section: str) -> Dict:
    """Extract contact information"""
    contact = {}

    # Extract email
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    emails = re.findall(email_pattern, section)
    if emails:
        # Filter out common non-relevant emails
        valid_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'noreply'])]
        if valid_emails:
            contact['email'] = valid_emails[0]

    # Extract phone numbers
    phone_pattern = r'(?:Phone|Tel|Telephone):\s*([+\d\s()-]+)'
    phones = re.findall(phone_pattern, section, re.IGNORECASE)
    if phones:
        contact['phone'] = phones[0].strip()

    return contact


def extract_regulatory_gates(country_name: str, section: str, timelines: Dict) -> List[Dict]:
    """Extract regulatory gates/requirements"""
    gates = []

    # Default gate structure based on country patterns
    # This is simplified - real extraction would parse more details

    standard_days = timelines.get('standard_review_days', 60)

    # Most countries have some form of clinical trial application
    gate1 = {
        "gate_id": f"{COUNTRY_TO_CODE[country_name]}-CTA",
        "name": "Clinical Trial Authorization",
        "typical_duration_days": standard_days,
        "description": f"Regulatory authority review and approval",
        "blocking": True,
        "required_documents": [
            "Protocol",
            "Investigator's Brochure",
            "Informed Consent Forms"
        ]
    }

    # Add fees if available
    if 'application_fee_usd' in timelines:
        gate1['fees'] = {'application_usd': timelines['application_fee_usd']}

    gates.append(gate1)

    # Most countries also have ethics committee requirement
    gate2 = {
        "gate_id": f"{COUNTRY_TO_CODE[country_name]}-ETHICS",
        "name": "Ethics Committee Approval",
        "typical_duration_days": timelines.get('ethics_review_days', 45),
        "description": "National or institutional ethics committee review",
        "blocking": True,
        "required_documents": [
            "Protocol",
            "Informed Consent Forms",
            "Investigator CVs"
        ]
    }

    gates.append(gate2)

    return gates


def generate_yaml_output(countries_data: Dict) -> str:
    """Generate YAML configuration from extracted data"""
    import yaml

    # Structure for authority_timelines.yaml
    output = {
        "version": "1.0",
        "description": "Global Regulatory Authorities - 23 Countries",
        "authorities": {}
    }

    for code, data in sorted(countries_data.items()):
        authority_entry = {
            "name": data["name"] or f"Regulatory Authority - {data['country']}",
            "country": data["country"],
            "regulatory_gates": data["regulatory_gates"],
            "contact": data["contact"]
        }

        # Add review timelines
        if data["review_timelines"]:
            authority_entry["review_timelines"] = data["review_timelines"]

        # Add fees
        if data["fees"]:
            authority_entry["fees"] = data["fees"]

        # Add milestone timelines
        standard_days = data["review_timelines"].get("standard_review_days", 60)
        authority_entry["milestone_timelines"] = {
            "first_patient_in": {
                "min_days_from_application": standard_days + 30,
                "typical_days_from_application": standard_days + 60
            }
        }

        output["authorities"][code] = authority_entry

    return yaml.dump(output, default_flow_style=False, sort_keys=False)


def main():
    """Main execution function"""
    print("=" * 80)
    print("Regulatory Authorities Data Parser")
    print("=" * 80)
    print()

    # File paths
    project_root = Path(__file__).parent.parent
    input_file = project_root / "Regulatory Authorities.txt"
    output_dir = project_root / "config-templates"
    output_file = output_dir / "authority_timelines_expanded.yaml"
    json_file = output_dir / "regulatory_data_extracted.json"

    # Check input file exists
    if not input_file.exists():
        print(f"❌ ERROR: Input file not found: {input_file}")
        return

    print(f"📄 Reading file: {input_file}")
    print(f"   Size: {input_file.stat().st_size / 1024 / 1024:.1f} MB")
    print()

    # Parse the file
    print("🔍 Parsing regulatory data...")
    countries_data = parse_regulatory_file(str(input_file))

    print()
    print(f"✅ Extracted data for {len(countries_data)} countries:")
    for code in sorted(countries_data.keys()):
        data = countries_data[code]
        gates_count = len(data.get('regulatory_gates', []))
        print(f"   - {code:15} ({data['country']:20}) - {gates_count} gates")

    # Save as JSON for inspection
    print()
    print(f"💾 Saving JSON to: {json_file}")
    with open(json_file, 'w') as f:
        json.dump(countries_data, f, indent=2)

    # Generate YAML
    print()
    print(f"📝 Generating YAML configuration...")
    yaml_content = generate_yaml_output(countries_data)

    # Save YAML
    print(f"💾 Saving YAML to: {output_file}")
    with open(output_file, 'w') as f:
        f.write(yaml_content)

    print()
    print("=" * 80)
    print("✅ COMPLETE!")
    print(f"   - Processed {len(countries_data)} countries")
    print(f"   - Generated: {output_file}")
    print(f"   - Raw data: {json_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
