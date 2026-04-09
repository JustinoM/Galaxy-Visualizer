"""Functions to generate 3D galaxy visualizations."""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull
from typing import Tuple, Optional


def generate_sphere(ax, center=(0,0,0), box=(1,1,1), radius=1.0, color='blue',
                    alpha=0.3, n_meridians=20, n_circles=10):
    """Plot a visually spherical sphere regardless of axis scaling."""
    x0, y0, z0 = center
   
    # Adjusted radii to obtain an sphere independently of axis aspect ratio
    rx = radius  
    ry = radius * box[1] / box[0]
    rz = radius * box[2] / box[0]
    
    # Create mesh
    u = np.linspace(0, 2 * np.pi, n_meridians)
    v = np.linspace(0, np.pi, n_circles)
    u, v = np.meshgrid(u, v)
    
    x = x0 + rx * np.sin(v) * np.cos(u)
    y = y0 + ry * np.sin(v) * np.sin(u)
    z = z0 + rz * np.cos(v)
    
    ax.plot_surface(x, y, z, color=color, alpha=alpha,
                   linewidth=0, antialiased=True, shade=False)


def _add_bar(ax, center, width, height, plane='xy', color='red', alpha=1.0):
    """Add a 2D rectangle on a specific plane."""
    x, y, z = center
    w, h = width/2, height/2
    
    if plane == 'xy':
        vertices = [
            [x-w, y-h, z], [x+w, y-h, z],
            [x+w, y+h, z], [x-w, y+h, z]
        ]
    elif plane == 'xz':
        vertices = [
            [x-w, y, z-h], [x+w, y, z-h],
            [x+w, y, z+h], [x-w, y, z+h]
        ]
    else:  # yz
        vertices = [
            [x, y-w, z-h], [x, y+w, z-h],
            [x, y+w, z+h], [x, y-w, z+h]
        ]
    
    rect = Poly3DCollection([vertices], alpha=alpha, facecolor=color,
                           shade=False, edgecolor=None)
    ax.add_collection3d(rect)


def generate_spiral_galaxy(ax, center, size=30, arms=2, tightness=0.5,
                          num_points=1000, cycles=2, barred=False, color='gold'):
    """Generate a parametric spiral galaxy."""
    x0, y0, z0 = center
    
    a, b = 0.2, 0.3  # Spiral parameters
    current_b = 1.5 if barred else b
    
    theta_max = cycles * 2 * np.pi
    
    # factor to adapt to the real size (kpc)
    factor = 0.5 * size / (a + current_b * theta_max)
    
    for arm in range(arms):
        theta_offset = arm * np.pi
        theta = np.linspace(0, theta_max, num_points)
        
        x_offset = -5 * (2*arm - 1) * a if barred else 0        
        
        r = factor*(a + current_b * theta + np.random.normal(0, 0.05, len(theta)))
        
        x = x0 + r * np.cos(theta + theta_offset) + x_offset
        y = y0 + r * np.sin(theta + theta_offset) * tightness
        z = z0
        
        ax.plot(x, y, z, color, linewidth=2, alpha=0.7)
    
    if barred:
        _add_bar(ax, center, width=10*a, height=5*a, color=color)

def generate_elliptic_galaxy(ax, center, radii, rotation_matrix=None,
                             color='blue', alpha=0.3, resolution=20):
    """
    Add a 3D ellipsoid with optional rotation.
    """    
    x0, y0, z0 = center
    rx, ry, rz = radii
    
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    
    # Base ellipsoid coordinates (centered at origin)
    x_base = rx * np.outer(np.cos(u), np.sin(v))
    y_base = ry * np.outer(np.sin(u), np.sin(v))
    z_base = rz * np.outer(np.ones_like(u), np.cos(v))
    
    # Apply rotation if provided
    if rotation_matrix is not None:
        # Flatten arrays for rotation
        points = np.array([x_base.flatten(), y_base.flatten(), z_base.flatten()]).T
        rotated_points = points @ rotation_matrix.T
        
        # Reshape back to grid
        x_rot = rotated_points[:, 0].reshape(x_base.shape)
        y_rot = rotated_points[:, 1].reshape(y_base.shape)
        z_rot = rotated_points[:, 2].reshape(z_base.shape)
    else:
        x_rot, y_rot, z_rot = x_base, y_base, z_base
    
    # Translate to center
    x = x0 + x_rot
    y = y0 + y_rot
    z = z0 + z_rot
    
    ax.plot_surface(x, y, z, color=color, alpha=alpha, 
                   linewidth=0, antialiased=True)
 

def generate_3d_irregular_galaxy(ax, center=(0,0,0), size=1.0, color='gold',
                                 alpha=0.7, n_points=200, irregularity=0.5):
    """
    Generate a truly 3D irregular galaxy with realistic structure.
    """
    x0, y0, z0 = center
    np.random.seed(42)  # For reproducibility
    
    # Generate points with irregular distribution in 3D
    phi = np.random.uniform(0, 2*np.pi, n_points)
    theta = np.random.uniform(0, np.pi, n_points)
    
    r_base = size * (0.5 + 0.5 * np.random.rand(n_points))
    r = r_base * (
        1 + irregularity * 0.3 * np.sin(3*phi) * np.cos(2*theta) +
        irregularity * 0.2 * np.sin(5*phi + 2) * np.sin(3*theta) +
        irregularity * 0.15 * np.random.randn(n_points)
    )
    
    # Get Z scaling
    xlim = ax.get_xlim3d()
    ylim = ax.get_ylim3d()
    zlim = ax.get_zlim3d()
    
    x_size = xlim[1] - xlim[0]
    y_size = ylim[1] - ylim[0]
    z_size = zlim[1] - zlim[0]
    
    flatten_z=8*z_size/np.max([x_size,y_size])
    
    x = x0 + r * np.sin(theta) * np.cos(phi)
    y = y0 + r * np.sin(theta) * np.sin(phi)
    z = z0 + r * np.cos(theta) * flatten_z
    
    # 2. Add overdensities (clusters)
    n_clusters = 5
    for i in range(n_clusters):
        cx = np.random.randn() * size * 0.4
        cy = np.random.randn() * size * 0.4
        cz = np.random.randn() * size * 0.4 * flatten_z
        cr = size * 0.2 * (0.5 + 0.5 * np.random.rand())
        
        n_cluster_points = np.random.randint(20, 50)
        cluster_phi = np.random.uniform(0, 2*np.pi, n_cluster_points)
        cluster_theta = np.random.uniform(0, np.pi, n_cluster_points)
        cluster_r = cr * np.random.rand(n_cluster_points)**0.5
        
        cx_pts = x0 + cx + cluster_r * np.sin(cluster_theta) * np.cos(cluster_phi)
        cy_pts = y0 + cy + cluster_r * np.sin(cluster_theta) * np.sin(cluster_phi)
        cz_pts = z0 + cz + cluster_r * np.cos(cluster_theta) * flatten_z
        
        x = np.append(x, cx_pts)
        y = np.append(y, cy_pts)
        z = np.append(z, cz_pts)
    
    # 3. Add tidal tails/streams - FIXED VERSION
    n_streams = 3
    for i in range(n_streams):
        # Direction of stream as a vector
        dir_vec = np.random.randn(3)
        dir_vec = dir_vec / np.linalg.norm(dir_vec)
        
        # Generate points along this direction
        n_stream_points = 30
        t = np.linspace(0, size * 1.5, n_stream_points)
        spread = size * 0.1 * np.random.randn(n_stream_points)
        
        # Find a perpendicular vector
        if abs(dir_vec[0]) < 0.9:
            perp1 = np.array([-dir_vec[1], dir_vec[0], 0.0])
        else:
            perp1 = np.array([0.0, -dir_vec[2], dir_vec[1]])
        perp1 = perp1 / np.linalg.norm(perp1)
        
        # Second perpendicular using cross product - FIXED
        # np.cross takes two vectors as arguments
        perp2 = np.cross(dir_vec, perp1)
        perp2 = perp2 / np.linalg.norm(perp2)
        
        # Stream points
        stream_x = x0 + dir_vec[0] * t + perp1[0] * spread + perp2[0] * spread * 0.3
        stream_y = y0 + dir_vec[1] * t + perp1[1] * spread + perp2[1] * spread * 0.3
        stream_z = z0 + dir_vec[2] * t * flatten_z + perp1[2] * spread + perp2[2] * spread * 0.3 * flatten_z
        
        x = np.append(x, stream_x)
        y = np.append(y, stream_y)
        z = np.append(z, stream_z)
    
    # Combine all points
    points = np.column_stack([x, y, z])
    
    # Calculate convex hull for the outer envelope
    try:
        from scipy.spatial import ConvexHull
        hull = ConvexHull(points)
        
        # Create a 3D polygon collection from hull simplices
        hull_polys = [points[simplex] for simplex in hull.simplices]
        
        # Plot the hull as a transparent mesh
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        mesh = Poly3DCollection(hull_polys, 
                               facecolor=color,
                               alpha=alpha*0.15,
                               edgecolor=None,
                               linewidth=0)
        ax.add_collection3d(mesh)
        
        # Plot hull edges (optional, for definition)
        '''
        for simplex in hull.simplices:
            for i in range(3):
                p1 = points[simplex[i]]
                p2 = points[simplex[(i+1)%3]]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                       color='darkorange', alpha=0.2, linewidth=0.3)
        '''
    except Exception as e:
        print(f"  ⚠ Convex hull failed: {e}")
        # Fallback: just plot points
        ax.scatter(x, y, z, c=color, alpha=alpha*0.2, s=2)
    
    # Plot individual stars (dimmer)
    ax.scatter(x, y, z, c=color, alpha=alpha*0.3, s=2, edgecolors='none')
    
    # Highlight denser regions
    n_bright = len(x) // 10
    bright_idx = np.random.choice(len(x), n_bright, replace=False)
    ax.scatter(x[bright_idx], y[bright_idx], z[bright_idx],
              c='yellow', alpha=alpha*0.8, s=3, edgecolors='none')
    