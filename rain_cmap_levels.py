import numpy as np
import matplotlib.colors as mcolors

clevs = [0, 1, 2.5, 5, 7.5, 10, 15, 20, 30, 40,
         50, 70, 100, 150, 200, 250, 300, 400, 500, 600, 750]
# In future MetPy
# norm, cmap = ctables.registry.get_with_boundaries('precipitation', clevs)
cmap_data = [
    (1.0, 1.0, 1.0),  # 白
    (0.95, 1.0, 0.95),
    (0.85, 1.0, 0.85),
    (0.7, 1.0, 0.7),
    (0.5, 1.0, 0.5),
    (0.3, 1.0, 0.3),
    (0.1, 0.9, 0.1),
    (0.0, 0.8, 0.0),
    (0.0, 0.7, 0.0),
    (0.6, 1.0, 0.0),
    (0.8, 1.0, 0.0),
    (1.0, 1.0, 0.0),
    (1.0, 0.9, 0.0),
    (1.0, 0.8, 0.0),
    (1.0, 0.7, 0.0),
    (1.0, 0.5, 0.0),
    (1.0, 0.3, 0.0),
    (1.0, 0.2, 0.2),
    (1.0, 0.0, 0.0),
    (0.9, 0.0, 0.0),
    (0.8, 0.0, 0.0)
]
cmap = mcolors.ListedColormap(cmap_data, 'precipitation')
norm = mcolors.BoundaryNorm(clevs, cmap.N)