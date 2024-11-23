import heapq

from queue import Queue
from django.db.models import Q
from api.models import Location

TIME_PER_LOCATION = 60

def calculate_shortets_travel_time(source_location, target_location):
    time_per_location = 60

    adjacency_map = create_adjacency_map()

    shortest_path = bfs(adjacency_map, source_location, target_location)

    travel_time_seconds = len(shortest_path) * time_per_location

    return int(travel_time_seconds)


def create_adjacency_map():
    adjacency_map = {}

    all_locations = Location.objects.all()
    for location in all_locations:
        adjacency_map[location] = get_neighboring_locations(location)
        print(adjacency_map[location])

    return adjacency_map
        

class PathItem:
    def __init__(self, isVisited, previous):
        self.isVisited = isVisited
        self.previous = previous


def dijkstra(locations, source_location, target_location):
    priority_queue = []
    heapq.heappush(priority_queue, (0, source_location, [source_location]))

    visited = set()

    while priority_queue:
        cost, current_location, path = heapq.heappop(priority_queue)
    
        if current_location in visited:
            continue

        visited.add(current_location)
        if current_location == target_location:
            return cost, path
        
        for neighboor in locations[current_location]:
            if neighboor not in visited:
                new_cost = cost + TIME_PER_LOCATION
                heapq.heappush(priority_queue, (new_cost, neighboor, path + [neighboor]))
    
    return float('inf'), []