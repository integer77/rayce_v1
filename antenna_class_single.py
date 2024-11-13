import numpy as np
import matplotlib.pyplot as plt
from phidl import Device
import phidl.geometry as pg

class Resonator:
    def __init__(self, num_resonators=1, max_size=50, resonators=None):
        if resonators is not None:
            self.resonators = resonators
        else:
            self.resonators = self.generate_random_antenna_parameters(num_resonators, max_size)
     #   self.points = self.get_points()

    def generate_random_antenna_parameters(self, num_resonators, max_size):
        resonators = []
        gap_positions = ['top', 'bottom', 'left', 'right']
        current_size = max_size
        i = 0
        for _ in range(num_resonators):
            i = i + 1

            size = current_size
            frame_width = np.random.randint(2, max(3, size // 10))  # Ensure minimum size constraints
            gap_size = np.random.randint(frame_width + 1, max(frame_width + 2, size // 4))  # Ensure gap_size > frame_width
            gap_position = np.random.choice(gap_positions)
            
            resonators.append((size, frame_width, gap_size, gap_position))
            
            current_size -= np.random.randint(10, 20)  # Decrease size for the next resonator
            if current_size <= 2 * frame_width:  # Prevent negative or zero dimensions
                i = i - 1
                self.num_resonators = i
                self.downsize = True
                break

        
        return resonators
    
    def get_points_defined(self, points):
        points0 = []
        points0.append(points)
        return points0
    
    def get_points(self):
        points = []
        print ('mrdka', self.resonators)
        for resonator in self.resonators:
            size, frame_width, gap_size, gap_position= resonator
            res_p = self.create_resonator_polygon(size, frame_width, gap_size, gap_position)
            points.append(res_p)
        return points
    
    def create_resonator_matrix_with_gap(self, size, frame_width, gap_size, gap_position):
        """
        Creates a matrix representation of a square-shaped split-ring resonator with a gap on one of the sides.
        
        Parameters:
        - size: The outer size of the square (length of a side).
        - frame_width: The width of the resonator frame.
        - gap_size: The size of the gap in the split.
        - gap_position: Position of the gap ('top', 'bottom', 'left', 'right').
        
        Returns:
        - A numpy matrix representing the resonator with a gap.
        """
        # Initialize matrix with zeros
        matrix = np.zeros((size, size))
        
        # Draw the full frame first
        print (frame_width)
        matrix[:frame_width, :] = 1  # Top
        matrix[-frame_width:, :] = 1  # Bottom
        matrix[:, :frame_width] = 1  # Left
        matrix[:, -frame_width:] = 1  # Right
        
        # Add the gap
        if gap_position == 'top':
            gap_start = (size - gap_size) // 2
            matrix[:frame_width, gap_start:gap_start + gap_size] = 0
        elif gap_position == 'bottom':
            gap_start = (size - gap_size) // 2
            matrix[-frame_width:, gap_start:gap_start + gap_size] = 0
        elif gap_position == 'left':
            gap_start = (size - gap_size) // 2
            matrix[gap_start:gap_start + gap_size, :frame_width] = 0
        elif gap_position == 'right':
            gap_start = (size - gap_size) // 2
            matrix[gap_start:gap_start + gap_size, -frame_width:] = 0
        
        return matrix
    
    def create_resonator_polygon(self, size, frame_width, gap_size, gap_position):
        outer_half = size / 2
        inner_half = outer_half - frame_width
        gap_half = gap_size/2
    
        # Initialize the points list
        points = []
    
        # Determine the coordinates based on the gap's position
        if gap_position == 'top':
            start_gap = (-gap_half, outer_half)
            end_gap = (gap_half, outer_half)
            # Moving counterclockwise on the outer square
            points += [start_gap, (-outer_half, outer_half), (-outer_half, -outer_half),
                       (outer_half, -outer_half), (outer_half, outer_half), end_gap]
            # Switching to the inner square, top right corner of the gap
            points += [(gap_half, inner_half)]
            # Moving clockwise on the inner square
            points += [(inner_half, inner_half), (inner_half, -inner_half), 
                       (-inner_half, -inner_half), (-inner_half, inner_half), 
                       (-gap_half, inner_half)]
        elif gap_position == 'bottom':
            start_gap = (-gap_half, -inner_half)
            end_gap = (gap_half, -inner_half)
            # Moving counterclockwise on the inner square
            points += [start_gap, (-inner_half, -inner_half), (-inner_half, inner_half),
                       (inner_half, inner_half), (inner_half, -inner_half), end_gap]
            # Switching to the outer square, bottom right corner of the gap
            points += [(gap_half, -outer_half)]
            # Moving clockwise on the outer square
            points += [(outer_half, -outer_half), (outer_half, outer_half), 
                       (-outer_half, outer_half), (-outer_half, -outer_half), 
                       (-gap_half, -outer_half)]
        elif gap_position == 'left':
            start_gap = (-outer_half, -gap_half)
            end_gap = (-outer_half, gap_half)
            # Moving counterclockwise on the outer square
            points += [start_gap, (-outer_half, -outer_half), (outer_half, -outer_half),
                       (outer_half, outer_half), (-outer_half, outer_half), end_gap]
            # Switching to the inner square, left bottom corner of the gap
            points += [(-inner_half, gap_half)]
            # Moving clockwise on the inner square
            points += [(-inner_half, inner_half), (inner_half, inner_half), 
                       (inner_half, -inner_half), (-inner_half, -inner_half), 
                       (-inner_half, -gap_half)]
        elif gap_position == 'right':
            start_gap = (inner_half, gap_half)
            end_gap = (inner_half, -gap_half)
            # Moving counterclockwise on the inner square
            points += [start_gap, (inner_half, inner_half), (-inner_half, inner_half),
                       (-inner_half, -inner_half), (inner_half, -inner_half), end_gap]
            # Switching to the outer square, right top corner of the gap
            points += [(outer_half, -gap_half)]
            # Moving clockwise on the outer square
            points += [(outer_half, -outer_half), (-outer_half, -outer_half), 
                       (-outer_half, outer_half), (outer_half, outer_half), 
                       (outer_half, gap_half)]
        
        # Close the polygon by returning to the starting point
        points.append(start_gap)
    
        return points
    
    def create_split_resonator_gds_phidl(self, filename):
        D = Device('SplitRingResonators')
        
        for size, frame_width, gap_size, gap_position in self.resonators:
            coords = self.create_resonator_polygon(size, frame_width, gap_size, gap_position)
            D.add_polygon(coords, layer=1)
        
        # Optionally show the design (if running in an environment that supports it)
        # qp(D)

        # Write the design to a GDS file
        D.write_gds(filename)
        
    def plot_concentric_antenna(self, canvas_size):
        """
        Plots an antenna composed of concentric square-shaped split-ring resonators with gaps.
        
        Parameters:
        - resonators: A list of tuples, each representing a resonator's (size, frame_width, gap_size, gap_position).
        - canvas_size: The size of the canvas for plotting the antenna.
        """
        # Initialize canvas
        canvas = np.zeros((canvas_size, canvas_size))
        
        # Center of the canvas
        center = canvas_size // 2
        
        for size, frame_width, gap_size, gap_position in self.resonators:
            # Create resonator matrix with a gap
            resonator_matrix = self.create_resonator_matrix_with_gap(size, frame_width, gap_size, gap_position)
            
            # Calculate top-left corner of the resonator
            start_x = center - size // 2
            start_y = center - size // 2
            
            # Place the resonator matrix onto the canvas
            canvas[start_x:start_x+size, start_y:start_y+size] = np.maximum(canvas[start_x:start_x+size, start_y:start_y+size], resonator_matrix)
        
        # Plotting
        plt.figure(figsize=(6, 6))
        plt.imshow(canvas, cmap='gray')
        plt.axis('off')
        plt.show()