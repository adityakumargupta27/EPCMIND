import os
import sys

# Ensure backend path is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.rfi_service import seed_initial_rfis

def main():
    demo_mode = os.getenv("DEMO_MODE", "false").lower()
    if demo_mode != "true":
        print("Demo mode is disabled. Set DEMO_MODE=true to seed demo RFIs.")
        return
    print("Seeding demo RFIs...")
    seed_initial_rfis()
    print("Demo RFIs seeded.")

if __name__ == "__main__":
    main()
