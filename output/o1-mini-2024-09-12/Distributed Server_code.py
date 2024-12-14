from collections import deque, defaultdict
import sys

def solve(input: str) -> str:
    import sys
    from collections import deque, defaultdict

    def readints():
        return list(map(int, sys.stdin.readline().split()))
    
    def hopcroft_karp(n, m, graph):
        pair_u = [-1] * n
        pair_v = [-1] * m
        dist = [0] * n

        queue = deque()

        def bfs():
            nonlocal dist
            queue.clear()
            for u in range(n):
                if pair_u[u] == -1:
                    dist[u] = 0
                    queue.append(u)
                else:
                    dist[u] = float('inf')
            dist_null = float('inf')
            while queue:
                u = queue.popleft()
                if dist[u] < dist_null:
                    for v in graph[u]:
                        if pair_v[v] == -1:
                            dist_null = dist[u] + 1
                        elif dist[pair_v[v]] == float('inf'):
                            dist[pair_v[v]] = dist[u] + 1
                            queue.append(pair_v[v])
            return dist_null != float('inf')

        def dfs(u):
            for v in graph[u]:
                if pair_v[v] == -1 or (dist[pair_v[v]] == dist[u] +1 and dfs(pair_v[v])):
                    pair_u[u] = v
                    pair_v[v] = u
                    return True
            dist[u] = float('inf')
            return False

        matching = 0
        while bfs():
            for u in range(n):
                if pair_u[u] == -1:
                    if dfs(u):
                        matching +=1
        return matching, pair_u

    data = input.split('\n')
    T = int(data[0])
    ptr = 1
    results = []

    for test_case in range(1, T+1):
        while ptr < len(data) and data[ptr].strip() == '':
            ptr +=1
        if ptr >= len(data):
            break
        R, C = map(int, data[ptr].strip().split())
        ptr +=1
        grid = []
        for _ in range(R):
            row = data[ptr].strip()
            grid.append(row)
            ptr +=1
        # Collect robots
        robots = []
        for r in range(R):
            for c in range(C):
                if 'A' <= grid[r][c] <= 'Z':
                    robots.append( (r, c) )
        robot_count = len(robots)
        if robot_count ==0:
            results.append(f"Case #{test_case}: ")
            continue
        # Initialize S as empty
        S = ''
        # Initialize robot positions
        robot_positions = robots.copy()
        # Active robots set
        active = [True]*robot_count
        while True:
            best_c = None
            best_possible = False
            for c_ord in range(ord('z'), ord('a')-1, -1):
                c = chr(c_ord)
                possible = True
                # For each active robot, check if it can append c
                for i in range(robot_count):
                    if not active[i]:
                        continue
                    r, col = robot_positions[i]
                    can_move = False
                    # Check down
                    if r +1 < R and grid[r+1][col].lower() == c:
                        can_move = True
                    # Check right
                    if col +1 < C and grid[r][col+1].lower() == c:
                        can_move = True
                    if not can_move:
                        possible = False
                        break
                if possible:
                    best_c = c
                    break
            if best_c is None:
                break
            # Now, move robots to append best_c
            # Assign robots to move to cells with best_c
            cells_with_c = []
            for r in range(R):
                for col in range(C):
                    if grid[r][col].lower() == best_c:
                        cells_with_c.append( (r, col) )
            if len(cells_with_c) < active.count(True):
                # Not enough cells to assign
                break
            # For each active robot, find possible cells to move
            robot_to_cells = []
            for i in range(robot_count):
                if not active[i]:
                    robot_to_cells.append([])
                    continue
                r, col = robot_positions[i]
                possible = []
                if r +1 < R and grid[r+1][col].lower() == best_c:
                    possible.append( (r+1, col) )
                if col +1 < C and grid[r][col+1].lower() == best_c:
                    possible.append( (r, col+1) )
                robot_to_cells.append(possible)
            # Map cells to indices
            cell_to_idx = {cell:i for i, cell in enumerate(cells_with_c)}
            # Build bipartite graph
            graph = [[] for _ in range(robot_count)]
            for i in range(robot_count):
                if not active[i]:
                    continue
                for cell in robot_to_cells[i]:
                    if cell in cell_to_idx:
                        j = cell_to_idx[cell]
                        graph[i].append(j)
            # Attempt to find matching
            n = robot_count
            m = len(cells_with_c)
            matching_size, pair_u = hopcroft_karp(n, m, graph)
            if matching_size < active.count(True):
                # Cannot assign, proceed to deactivate some robots
                # For simplicity, deactivate all robots that cannot assign
                for i in range(robot_count):
                    if not active[i]:
                        continue
                    if pair_u[i] == -1:
                        active[i] = False
                # Continue
                break
            else:
                # Assign the matching
                S += best_c
                new_positions = [None]*robot_count
                for i in range(robot_count):
                    if not active[i]:
                        new_positions[i] = robot_positions[i]
                        continue
                    if pair_u[i] != -1:
                        new_positions[i] = cells_with_c[pair_u[i]]
                robot_positions = new_positions
        results.append(f"Case #{test_case}: {S}")

    return '\n'.join(results)