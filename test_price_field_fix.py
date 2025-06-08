#!/usr/bin/env python
"""
Test script to verify that the MenuPackage price field fixes are working correctly.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from caterers.models import MenuPackage, Caterer
from django.template import Context, Template

def test_price_property():
    """Test that the price_per_person property works correctly"""
    print("🔍 Testing MenuPackage price_per_person property...")
    
    packages = MenuPackage.objects.all()
    if not packages.exists():
        print("❌ No MenuPackage objects found in database")
        return False
    
    package = packages.first()
    
    # Test direct access
    base_price = package.base_price_per_person
    property_price = package.price_per_person
    
    if base_price == property_price:
        print(f"✅ price_per_person property works: {property_price}")
        return True
    else:
        print(f"❌ Price mismatch: base={base_price}, property={property_price}")
        return False

def test_template_rendering():
    """Test that templates can use both price fields"""
    print("\n🔍 Testing template rendering with price fields...")
    
    package = MenuPackage.objects.first()
    if not package:
        print("❌ No package found for template test")
        return False
    
    # Test template with both fields
    template_str = """
    Base price: {{ package.base_price_per_person }}
    Property price: {{ package.price_per_person }}
    """
    
    template = Template(template_str)
    context = Context({'package': package})
    result = template.render(context)
    
    if str(package.base_price_per_person) in result and str(package.price_per_person) in result:
        print("✅ Both price fields render correctly in templates")
        return True
    else:
        print("❌ Template rendering failed")
        print(f"Result: {result}")
        return False

def test_caterer_packages():
    """Test caterers with and without packages"""
    print("\n🔍 Testing caterers with/without menu packages...")
    
    caterers = Caterer.objects.all()
    caterers_with_packages = 0
    caterers_without_packages = 0
    
    for caterer in caterers:
        package_count = caterer.menu_packages.count()
        if package_count > 0:
            caterers_with_packages += 1
            print(f"✅ {caterer.provider.business_name}: {package_count} packages")
        else:
            caterers_without_packages += 1
            print(f"⚠️  {caterer.provider.business_name}: 0 packages (tests empty state)")
    
    print(f"\nSummary: {caterers_with_packages} with packages, {caterers_without_packages} without packages")
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 TESTING MENUPACKAGE PRICE FIELD FIXES")
    print("=" * 50)
    
    tests = [
        test_price_property,
        test_template_rendering,
        test_caterer_packages
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The price field fixes are working correctly.")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
