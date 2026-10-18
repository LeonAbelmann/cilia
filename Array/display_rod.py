# test_rod.py
import numpy as np
import matplotlib.pyplot as plt
from rods import RodDescription

rod = RodDescription('Rod_0.csv')

print("Metadata:")
for key, value in rod.metadata.items():
    print(f"  {key:12s}: {value}")
print(f"L = {rod.L*1000:.2f} mm, samples: {len(rod.samples()[0])}")

# Interpolated quantities on a fine grid
s_fine = np.linspace(0, rod.L, 1000)
EI = rod.EI(s_fine)
w0 = rod.w_prefactor(s_fine)
al = rod.alpha(s_fine)

# For your uniform rod: check against the closed-form values
print(f"max |EI - E*pi*D^4/64| : "
      f"{np.max(np.abs(EI - 1.429e6*np.pi*(1e-3)**4/64)):.3e}")
print(f"max |w0 - Mr*pi*D^2/4|: "
      f"{np.max(np.abs(w0 - 52e3*np.pi*(0.5e-3)**2)):.3e}")

fig, axes = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
axes[0].plot(s_fine*1000, EI);    axes[0].set_ylabel('EI [N.m2]')
axes[1].plot(s_fine*1000, 1000*w0); axes[1].set_ylabel('Mr A [mA m]')
axes[2].plot(s_fine*1000, np.degrees(al))
axes[2].set_ylabel('alpha [deg]'); axes[2].set_xlabel('s [mm]')
for ax in axes: ax.grid(True)
fig.suptitle(rod.metadata.get('description', 'Rod'))
plt.tight_layout(); plt.savefig('rod_test.png', dpi=150); plt.show()
