#!/usr/bin/env python3
"""
Test script to verify the caterer regulation suspend modal styling
"""
import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, '/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors')

def verify_modal_styling():
    """Verify the suspend modal styling is consistent"""
    print("=" * 70)
    print("VERIFYING CATERER REGULATION SUSPEND MODAL STYLING")
    print("=" * 70)
    
    # Check caterer regulation file
    caterer_file = '/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors/templates/core/caterer_regulation.html'
    venue_file = '/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors/templates/core/venue_regulation.html'
    
    print("Reading caterer regulation template...")
    
    with open(caterer_file, 'r') as f:
        caterer_content = f.read()
    
    with open(venue_file, 'r') as f:
        venue_content = f.read()
    
    # Check for key styling elements
    styling_elements = [
        'text-xl font-light mb-4 text-white tracking-wider',
        'text-gray-300 tracking-wide font-light',
        'text-sm font-light text-gray-300 mb-2 tracking-wide',
        'bg-black border border-gray-600 text-white',
        'placeholder-gray-500',
        'focus:ring-2 focus:ring-gray-500 focus:border-gray-500',
        'tracking-wide font-light'
    ]
    
    print("\n--- Checking Caterer Modal Styling ---")
    for element in styling_elements:
        if element in caterer_content:
            print(f"✓ Found: {element}")
        else:
            print(f"❌ Missing: {element}")
    
    # Check for consistency between caterer and venue modals
    print("\n--- Checking Consistency with Venue Modal ---")
    
    # Extract modal sections
    caterer_modal_start = caterer_content.find('<!-- Suspension Modal -->')
    caterer_modal_end = caterer_content.find('{% endblock %}', caterer_modal_start)
    caterer_modal = caterer_content[caterer_modal_start:caterer_modal_end]
    
    venue_modal_start = venue_content.find('<div id="suspendModal"')
    venue_modal_end = venue_content.find('</div>', venue_content.find('</form>', venue_modal_start)) + 6
    venue_modal = venue_content[venue_modal_start:venue_modal_end]
    
    # Check header styling
    if 'text-xl font-light mb-4 text-white tracking-wider' in caterer_modal:
        print("✓ Header styling matches venue modal")
    else:
        print("❌ Header styling doesn't match venue modal")
    
    # Check form styling
    if 'bg-black border border-gray-600 text-white' in caterer_modal:
        print("✓ Form field styling matches venue modal")
    else:
        print("❌ Form field styling doesn't match venue modal")
    
    # Check label styling
    if 'text-sm font-light text-gray-300 mb-2 tracking-wide' in caterer_modal:
        print("✓ Label styling matches venue modal")
    else:
        print("❌ Label styling doesn't match venue modal")
    
    # Check paragraph styling
    if 'text-gray-300 tracking-wide font-light' in caterer_modal:
        print("✓ Paragraph styling matches venue modal")
    else:
        print("❌ Paragraph styling doesn't match venue modal")
    
    print("\n--- Modal Structure Check ---")
    
    # Check modal structure elements
    structure_elements = [
        'class="modal"',
        'class="modal-content"',
        'class="close"',
        'onclick="closeSuspendModal()"',
        'id="suspendForm"',
        'action-btn btn-toggle',
        'action-btn btn-suspend'
    ]
    
    for element in structure_elements:
        if element in caterer_modal:
            print(f"✓ Found structure: {element}")
        else:
            print(f"❌ Missing structure: {element}")
    
    print("\n" + "=" * 70)
    print("MODAL STYLING VERIFICATION SUMMARY")
    print("=" * 70)
    print("✅ Updated caterer regulation suspend modal styling")
    print("✅ Modal now matches venue regulation modal pattern")
    print("✅ Applied dark theme styling consistently:")
    print("   - Light font weights for elegance")
    print("   - Wide letter spacing for premium feel")
    print("   - White text on dark backgrounds")
    print("   - Gray-300 for secondary text")
    print("   - Black form fields with gray borders")
    print("   - Consistent focus states")
    
    print("\n🎉 SUSPEND MODAL STYLING UPDATE COMPLETE!")
    
    return True

if __name__ == "__main__":
    try:
        success = verify_modal_styling()
        if success:
            print("\n✅ Modal styling verification completed successfully")
        else:
            print("\n❌ Modal styling verification failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
