import math

def solve(input: str) -> str:
    from math import atan2, cos, sin, pi
    from sys import stdin
    import sys

    def rotate_point(x, y, theta):
        return (x * cos(theta) - y * sin(theta), x * sin(theta) + y * cos(theta))
    
    def point_in_convex_polygon(polygon, point):
        """Check if a point is strictly inside a convex polygon."""
        x, y = point
        n = len(polygon)
        epsilon = 1e-9
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i+1)%n]
            cross = (x2 - x1)*(y - y1) - (y2 - y1)*(x - x1)
            if cross <= epsilon:
                return False
        return True

    def sutherland_hodgman_clip(polygon, edge):
        """Clip a polygon with a single edge."""
        clipped = []
        n = len(polygon)
        for i in range(n):
            curr = polygon[i]
            prev = polygon[i-1]
            # Determine if current and previous points are inside
            if edge['type'] == 'left':
                inside_curr = curr[0] > edge['value']
                inside_prev = prev[0] > edge['value']
            elif edge['type'] == 'right':
                inside_curr = curr[0] < edge['value']
                inside_prev = prev[0] < edge['value']
            elif edge['type'] == 'bottom':
                inside_curr = curr[1] > edge['value']
                inside_prev = prev[1] > edge['value']
            elif edge['type'] == 'top':
                inside_curr = curr[1] < edge['value']
                inside_prev = prev[1] < edge['value']
            
            if inside_curr:
                if not inside_prev:
                    # Compute intersection
                    intersect = compute_intersection(prev, curr, edge)
                    if intersect is not None:
                        clipped.append(intersect)
                clipped.append(curr)
            elif inside_prev:
                # Compute intersection
                intersect = compute_intersection(prev, curr, edge)
                if intersect is not None:
                    clipped.append(intersect)
        return clipped

    def compute_intersection(p1, p2, edge):
        """Compute intersection point of segment p1-p2 with the clipping edge."""
        x1, y1 = p1
        x2, y2 = p2
        if edge['type'] in ['left', 'right']:
            x_edge = edge['value']
            if x2 != x1:
                t = (x_edge - x1) / (x2 - x1)
                if 0 <= t <= 1:
                    y = y1 + t * (y2 - y1)
                    return (x_edge, y)
        elif edge['type'] in ['bottom', 'top']:
            y_edge = edge['value']
            if y2 != y1:
                t = (y_edge - y1) / (y2 - y1)
                if 0 <= t <= 1:
                    x = x1 + t * (x2 - x1)
                    return (x, y_edge)
        return None

    def clip_polygon(polygon, clip_edges):
        """Clip a polygon against multiple edges."""
        clipped = polygon[:]
        for edge in clip_edges:
            clipped = sutherland_hodgman_clip(clipped, edge)
            if not clipped:
                break
        return clipped

    data = input.strip().split('\n')
    T = int(data[0])
    ptr = 1
    results = []
    for test_case in range(1, T+1):
        N, W, D = map(float, data[ptr].strip().split())
        N = int(N)
        W = float(W)
        D = float(D)
        ptr +=1
        polygon = []
        for _ in range(N):
            x, y = map(float, data[ptr].strip().split())
            polygon.append( (x, y) )
            ptr +=1
        answer = "No"
        for i in range(N):
            xi, yi = polygon[i]
            if xi == 0 and yi ==0:
                theta = 0.0
            else:
                theta = math.atan2(-yi, xi)
            # Rotate all points
            rotated = [rotate_point(x, y, theta) for (x, y) in polygon]
            # Translate so that the i-th vertex is on x-axis
            rotated_i_x, rotated_i_y = rotated[i]
            translated = [ (x, y - rotated_i_y) for (x, y) in rotated ]
            # Check all y >=0
            valid = all( y >= -1e-9 for (x, y) in translated )
            if not valid:
                continue
            # Check rotated vertex i's x is between 0 and W
            rotated_i_x_trans, rotated_i_y_trans = translated[i]
            if not ( -1e-9 <= rotated_i_x_trans <= W +1e-9 ):
                continue
            # Step c: Clip polygon with (0, W) x (0, D)
            clip_edges = [
                {'type': 'left', 'value': 0.0},
                {'type': 'right', 'value': W},
                {'type': 'bottom', 'value': 0.0},
                {'type': 'top', 'value': D}
            ]
            clipped = clip_polygon(translated, clip_edges)
            if not clipped:
                continue
            # Check if any point in clipped polygon has 0 <x < W and 0 < y < D
            step_c = False
            for (x, y) in clipped:
                if 0.0 < x < W and 0.0 < y < D:
                    step_c = True
                    break
            if not step_c:
                continue
            # Step d: Check no point on sauce cup boundary is inside polygon
            # Sample points on left and right boundaries
            step_size = 0.5
            num_steps = int(D / step_size) +1
            step_d_failed = False
            for k in range(1, num_steps):
                y = k * step_size
                if y >= D:
                    y = D - 1e-6
                # Left boundary
                if point_in_convex_polygon(translated, (0.0, y)):
                    step_d_failed = True
                    break
                # Right boundary
                if point_in_convex_polygon(translated, (W, y)):
                    step_d_failed = True
                    break
            if step_d_failed:
                continue
            # Additionally, check points very close to bottom except the vertex
            # Since one vertex is on y=0, check other points near y=0
            # Sample x from 0 to W in steps
            num_x_steps = int(W / step_size) +1
            for k in range(num_x_steps +1):
                x = k * step_size
                if x > W:
                    x = W -1e-6
                # Avoid the vertex on x-axis
                if abs(x - rotated_i_x_trans) < 1e-3 and abs(0.0) <1e-6:
                    continue
                if point_in_convex_polygon(translated, (x, 0.0)):
                    step_d_failed = True
                    break
            if step_d_failed:
                continue
            # If all checks passed
            answer = "Yes"
            break
        results.append(f"Case #{test_case}: {answer}")
    return '\n'.join(results)