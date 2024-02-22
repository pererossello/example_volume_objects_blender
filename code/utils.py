import numpy as np
import matplotlib.pyplot as plt

class Sample:
    def __init__(self, radial_profile, r_max=5):
        self.r_max = r_max
        self.M = 1000
        self.r_vals = np.linspace(0, self.r_max, self.M)

        # Define the radial profile as given, but no need to adjust here.
        self.radial_profile = radial_profile

        # Pre-calculate the normalization factor over the intended active range.
        r_vals = np.linspace(0, self.r_max, self.M)
        func_vals = self.radial_profile(r_vals) * r_vals**2
        integral_r = np.trapz(func_vals, r_vals)
        self.r_norm = integral_r

        # Normalized radial profile function.
        self.radial_profile_norm = lambda r: self.radial_profile(r) * r**2 / self.r_norm

        self.a = 1
        self.b = 1
        self.c = 1

    def sample_points(self, N=10000):
        N = int(N)
        r = []

        while len(r) < N:
            radius = np.random.uniform(0, self.r_max)  # Sample within the entire range.
            density = self.radial_profile_norm(radius)
            
            # Since we're already considering the active range in normalization,
            # directly compare against a uniform distribution.
            if np.random.uniform(0, max(self.radial_profile_norm(self.r_vals))) < density:
                r.append(radius)

        r = np.array(r)
        theta = np.arccos(1 - 2 * np.random.random(N))  # Uniform distribution over theta
        phi = 2 * np.pi * np.random.random(N)  # Uniform distribution over phi

        # Convert to Cartesian coordinates.
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)

        points = np.array([x * self.a, y * self.b, z * self.c]).T

        self.points = points

        return points

    def compute_density(self, ranges=[1, 1, 1], resolution=10, return_value=False):
        """
        Computes the volumetric density of points within each voxel.
        """

        if not hasattr(self, 'points'):
            raise ValueError('Points have not been sampled yet.')

        # Creating a histogram with the specified resolution
        hist, edges = np.histogramdd(self.points, bins=resolution, range=[[-ranges[0], ranges[0]], [-ranges[1], ranges[1]], [-ranges[2], ranges[2]]])
        
        hist = hist

        density = hist #/ np.nansum(hist)
        self.density = density
        self.edges = edges

        if return_value:
            return density
        else:
            return




    def plot_density(self):
        """
        Plot the three projections (XY, XZ, YZ) of the voxel density.

        :param voxel_density: 3D numpy array representing the volumetric density.
        """

        if not hasattr(self, 'density'):
            raise ValueError('Density has not been computed yet.')

        # Fig = pu.Figure(subplots=(1,3), ratio=3, sw=0.2)
        # axs = Fig.axes
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        x_edges, y_edges, z_edges = self.edges

        cmap = 'binary_r'

        xy_projection = np.sum(self.density, axis=2)
        axs[0].imshow(xy_projection.T, extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]], origin='lower', cmap=cmap)

        xz_projection = np.sum(self.density, axis=1)
        axs[1].imshow(xz_projection.T, extent=[x_edges[0], x_edges[-1], z_edges[0], z_edges[-1]], origin='lower', cmap=cmap)

        yz_projection = np.sum(self.density, axis=0)
        axs[2].imshow(yz_projection.T, extent=[y_edges[0], y_edges[-1], z_edges[0], z_edges[-1]], origin='lower', cmap=cmap)


    def save_density(self, filename, float_precision='float32', compressed=False):
        """
        Saves the volumetric density data to a raw binary file with specified precision.
        :param filename: The name of the file to save.
        :param float_precision: The floating-point precision ('float64', 'float32', or 'float16').
        """

        if not hasattr(self, 'density'):
            raise ValueError('Density data is not available.')

        # Convert to specified precision
        if float_precision in ['float64', 'float32', 'float16']:
            density_data = self.density.astype(float_precision)
        else:
            raise ValueError('Invalid float precision specified.')

        if compressed == True:
            np.savez_compressed(f'{filename}.npz', density_data)
        else:
            np.save(f'{filename}.npy', density_data)

