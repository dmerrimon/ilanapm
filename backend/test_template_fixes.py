#!/usr/bin/env python3
"""
Test script to verify template generator bug fixes
Tests US and Kenya template generation with expected task counts
"""

from services.template_generator import TemplateGenerator


def test_us_template():
    """Test US Phase III template - should have ~30-35 tasks"""
    print("\n" + "="*80)
    print("TEST 1: US Phase III Infectious Disease Template")
    print("="*80)

    generator = TemplateGenerator()
    timeline = generator.generate_template(
        country_code="US",
        study_phase="Phase III",
        therapeutic_area="Infectious Disease",
        include_optional=True
    )

    print(f"\n✓ Total Tasks: {len(timeline.tasks)}")
    print(f"✓ Total Dependencies: {len(timeline.dependencies)}")

    # Count tasks by category
    category_counts = {}
    for task in timeline.tasks:
        category = task.category
        category_counts[category] = category_counts.get(category, 0) + 1

    print(f"\n📊 Tasks by Category:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count}")

    # List all task IDs
    print(f"\n📋 All Task IDs:")
    for task in sorted(timeline.tasks, key=lambda t: t.id):
        print(f"   {task.id}: {task.name} ({task.duration_days} days)")

    # Verify expected count
    expected_min = 30
    expected_max = 35
    if expected_min <= len(timeline.tasks) <= expected_max:
        print(f"\n✅ PASS: Task count {len(timeline.tasks)} is within expected range ({expected_min}-{expected_max})")
    else:
        print(f"\n❌ FAIL: Task count {len(timeline.tasks)} is outside expected range ({expected_min}-{expected_max})")

    return timeline


def test_kenya_template():
    """Test Kenya Phase III template - should have ~95-105 tasks"""
    print("\n" + "="*80)
    print("TEST 2: Kenya Phase III Infectious Disease Template")
    print("="*80)

    generator = TemplateGenerator()
    timeline = generator.generate_template(
        country_code="KE",
        study_phase="Phase III",
        therapeutic_area="Infectious Disease",
        include_optional=True
    )

    print(f"\n✓ Total Tasks: {len(timeline.tasks)}")
    print(f"✓ Total Dependencies: {len(timeline.dependencies)}")

    # Count tasks by category
    category_counts = {}
    for task in timeline.tasks:
        category = task.category
        category_counts[category] = category_counts.get(category, 0) + 1

    print(f"\n📊 Tasks by Category:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count}")

    # Check for Kenya-specific tasks
    kenya_tasks = [t for t in timeline.tasks if 'PPB' in t.name or 'NACOSTI' in t.name or 'EC' in t.name]
    print(f"\n🇰🇪 Kenya 3-Layer Regulatory Tasks: {len(kenya_tasks)}")
    for task in kenya_tasks:
        print(f"   {task.id}: {task.name} ({task.duration_days} days)")

    # List all task IDs
    print(f"\n📋 All Task IDs:")
    for task in sorted(timeline.tasks, key=lambda t: t.id):
        print(f"   {task.id}: {task.name} ({task.duration_days} days)")

    # Verify expected count
    expected_min = 95
    expected_max = 105
    if expected_min <= len(timeline.tasks) <= expected_max:
        print(f"\n✅ PASS: Task count {len(timeline.tasks)} is within expected range ({expected_min}-{expected_max})")
    else:
        print(f"\n❌ FAIL: Task count {len(timeline.tasks)} is outside expected range ({expected_min}-{expected_max})")

    return timeline


def main():
    """Run all tests"""
    print("\n🔧 TESTING TEMPLATE GENERATOR BUG FIXES")
    print("Bug #1: Category filter now includes all 8 categories")
    print("Bug #2: Tasks now read from ontology (92 tasks) instead of hardcoded (9 tasks)")

    try:
        us_timeline = test_us_template()
        kenya_timeline = test_kenya_template()

        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"US Template: {len(us_timeline.tasks)} tasks")
        print(f"Kenya Template: {len(kenya_timeline.tasks)} tasks")
        print(f"\n✅ All tests completed!")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
