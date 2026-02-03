#!/usr/bin/env python3
"""
Test script to verify authority names are specific (not generic) in generated templates
"""
import requests
import json

API_BASE_URL = "https://ilanapm.onrender.com/api/v1"

def test_country_template(country_code, country_name, expected_authorities):
    """Test template generation for a country and verify authority names"""
    print(f"\n{'='*80}")
    print(f"Testing {country_name} ({country_code})")
    print(f"{'='*80}")

    # Generate template
    response = requests.post(
        f"{API_BASE_URL}/templates/generate",
        json={
            "country_code": country_code,
            "study_phase": "Phase III",
            "therapeutic_area": "Infectious Disease",
            "include_optional": True
        }
    )

    if response.status_code != 200:
        print(f"❌ ERROR: API returned status {response.status_code}")
        print(f"Response: {response.text}")
        return False

    timeline = response.json()

    # Find regulatory tasks
    regulatory_tasks = [t for t in timeline['tasks'] if t.get('category') == 'Regulatory']

    print(f"\nFound {len(regulatory_tasks)} regulatory tasks:")
    print(f"\nTask Names:")
    for task in regulatory_tasks[:10]:  # Show first 10
        print(f"  - {task['name']}")

    # Check for generic names (should NOT contain these)
    generic_names = ["Ethics Committee Approval", "Regulatory Authority Approval"]
    found_generic = False

    for task in regulatory_tasks:
        task_name = task['name']
        for generic in generic_names:
            if generic in task_name and country_name not in task_name:
                print(f"❌ FAIL: Found generic name without country: {task_name}")
                found_generic = True

    # Check for expected specific authority names
    missing_authorities = []
    for auth_name in expected_authorities:
        found = False
        for task in regulatory_tasks:
            if auth_name in task['name']:
                found = True
                print(f"✅ PASS: Found specific authority: {auth_name}")
                break
        if not found:
            missing_authorities.append(auth_name)

    if missing_authorities:
        print(f"❌ FAIL: Missing expected authorities: {', '.join(missing_authorities)}")
        return False

    if found_generic:
        print(f"\n❌ FAIL: Found generic authority names (should be specific)")
        return False

    print(f"\n✅ PASS: All authority names are specific for {country_name}")
    return True

def main():
    print("Testing Authority Names Across Countries")
    print("="*80)

    test_cases = [
        {
            "country_code": "KE",
            "country_name": "Kenya",
            "expected_authorities": [
                "Pharmacy and Poisons Board",
                "NACOSTI"
            ]
        },
        {
            "country_code": "VN",
            "country_name": "Vietnam",
            "expected_authorities": [
                "CEBRGL",
                "ASTT",
                "NECBR"
            ]
        },
        {
            "country_code": "US",
            "country_name": "United States",
            "expected_authorities": [
                "FDA",
                "IRB"
            ]
        },
        {
            "country_code": "GB",
            "country_name": "United Kingdom",
            "expected_authorities": [
                "MHRA"
            ]
        }
    ]

    results = []
    for test_case in test_cases:
        result = test_country_template(**test_case)
        results.append((test_case["country_name"], result))

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")

    for country_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {country_name}")

    all_passed = all(r[1] for r in results)
    if all_passed:
        print(f"\n✅ ALL TESTS PASSED: Authority names are specific across all countries")
    else:
        print(f"\n❌ SOME TESTS FAILED: Check output above for details")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
