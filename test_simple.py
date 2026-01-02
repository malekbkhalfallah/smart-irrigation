# test_simple.py
print("=== TEST SIMPLE ===")

# 1. Test imports de base
try:
    print("1. Import configuration...")
    from config.settings import config
    print("   ✅ Config OK")
except Exception as e:
    print(f"   ❌ Config error: {e}")

# 2. Test GPIO
try:
    print("\n2. Test GPIO...")
    from core.gpio_manager import gpio_central
    print("   ✅ GPIO central OK")
except Exception as e:
    print(f"   ❌ GPIO error: {e}")

# 3. Test capteurs
try:
    print("\n3. Test capteurs...")
    from sensors.sensor_manager import sensor_manager
    print("   ✅ Capteurs OK")
except Exception as e:
    print(f"   ❌ Capteurs error: {e}")

print("\n=== FIN TEST ===")