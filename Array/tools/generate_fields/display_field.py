# test_fields.py
"""Quick test of the FieldSequence module: load a field CSV,
verify the known values, and plot the interpolated field."""

import numpy as np
import matplotlib.pyplot as plt
from engine import FieldSequence

# --- Load ---
field = FieldSequence("Constant_50mT.csv")

print("--- metadata ---")
for key, value in field.metadata.items():
    print(f"  {key:12s}: {value}")

print("--- acceptance checks ---")
print(f"  t range : {field.t_start} .. {field.t_end} s")
print(f"  samples : {len(field.t)}")

# Known values for this file: B = 50 mT everywhere,
# phi = 2*pi*t/60 (one revolution in 60 s)
t_check = np.linspace(field.t_start, field.t_end, 1001)
B_check = field.B(t_check)
phi_check = field.phi(t_check)

assert np.allclose(B_check, 0.050, atol=1e-9), \
    f"B not constant: min={B_check.min()}, max={B_check.max()}"
assert np.allclose(phi_check, 2*np.pi*t_check/60, atol=1e-9), \
    f"phi deviates from linear ramp by max " \
    f"{np.max(np.abs(phi_check - 2*np.pi*t_check/60))} rad"
assert np.isclose(field.phi(field.t_end), 2*np.pi, atol=1e-6), \
    "phi at t_end should be exactly 2*pi (one full revolution)"

print("  all checks passed")

# --- Plot ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

# B(t): interpolated curve + raw samples
ax1.plot(t_check, 1000*B_check, 'b-', label='interpolated')
ax1.plot(field.t, 1000*field._B, 'r.', markersize=3, label='samples')
ax1.set_ylabel('B [mT]')
ax1.set_title('Field magnitude')
ax1.legend()
ax1.grid(True)

# phi(t): interpolated + samples, in degrees for readability
ax2.plot(t_check, np.degrees(phi_check), 'b-', label='interpolated')
ax2.plot(field.t, np.degrees(field._phi), 'r.', markersize=3, label='samples')
ax2.set_xlabel('t [s]')
ax2.set_ylabel('phi [deg]')
ax2.set_title('Field angle (unwrapped)')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('test_fields.png', dpi=150)
plt.show()
