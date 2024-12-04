# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 07:58:26 2024

@author: maseb
"""

import numpy as np
import matplotlib.pyplot as plt
from phidl import Device

class BowtieAntenna:
    def __init__(self, length, width, tip_diameter, gap_size):
        """
        Initializes a BowtieAntenna object with the given parameters.

        Parameters:
        - length: Length of the triangle part of the bowtie
        - width: Width of the triangle part of the bowtie
        - tip_diameter: Diameter of the curvature at the tip
        - gap_size: Gap between the two bowtie halves
        """
        self.length = length
        self.width = width
        self.tip_diameter = tip_diameter
        self.gap_size = gap_size

    def generate_bowtie_points(self, flip=False):
        """
        Generates the points for one half of the bowtie antenna.

        Parameters:
        - flip: If True, flip the antenna horizontally

        Returns:
        - points: A list of points defining the bowtie half
        """
        tip_radius = self.tip_diameter / 2
        base_left = [0, -self.width / 2]
        base_right = [0, self.width / 2]

        # Points for the tip arc
        arc_points = []
        num_arc_points = 20
        for i in range(num_arc_points + 1):
            angle = np.pi * i / num_arc_points - np.pi / 2
            arc_x = self.length + tip_radius * np.cos(angle)
            arc_y = tip_radius * np.sin(angle)
            arc_points.append([arc_x, arc_y])

        points = [base_left] + arc_points + [base_right]

        if flip:
            # Flip the antenna horizontally
            points = [[-x, y] for [x, y] in points]

        return points

    def generate_bowtie_design(self):
        """
        Generates a bowtie design and plots it.

        Returns:
        - fig: The matplotlib figure object containing the plot
        """
        # Generate points for both halves
        points1 = self.generate_bowtie_points(flip=True)
        points2 = self.generate_bowtie_points(flip=False)

        # Shift the second half horizontally to create the gap
        points2 = [[x - self.length - self.gap_size - self.tip_diameter / 2, y] for [x, y] in points2]
        points1 = [[x + self.length + self.gap_size + self.tip_diameter / 2, y] for [x, y] in points1]

        # Plot the bowtie design
        fig, ax = plt.subplots()
        polygon1 = plt.Polygon(points1, closed=True, edgecolor='black', fill=None)
        polygon2 = plt.Polygon(points2, closed=True, edgecolor='black', fill=None)
        ax.add_patch(polygon1)
        ax.add_patch(polygon2)
        ax.set_xlim([-self.length - self.gap_size - self.tip_diameter, self.length + self.gap_size + self.tip_diameter])
        ax.set_ylim([-self.width / 2 - self.tip_diameter, self.width / 2 + self.tip_diameter])
        ax.set_aspect('equal')
        ax.axis('off')
        plt.show()

        return fig

    def create_bowtie_gds_file(self, filename="bowtie_output.gds"):
        """
        Creates a GDS file for the bowtie antenna.

        Parameters:
        - filename: Name of the output GDS file
        """
        D = Device("BowtieAntenna")

        # Generate points for both halves
        points1 = self.generate_bowtie_points(flip=True)
        points2 = self.generate_bowtie_points(flip=False)

        # Shift the second half horizontally to create the gap
        points2 = [[x - self.length - self.gap_size - self.tip_diameter / 2, y] for [x, y] in points2]
        points1 = [[x + self.length + self.gap_size + self.tip_diameter / 2, y] for [x, y] in points1]

        # Add polygons to the GDS file
        D.add_polygon(points1, layer=1)
        D.add_polygon(points2, layer=1)

        # Write the GDS file
        D.write_gds(filename)


# Create an instance of BowtieAntenna and plot the design
#bowtie = BowtieAntenna(length=50, width=30, tip_diameter=5, gap_size=2)
#bowtie.generate_bowtie_design()