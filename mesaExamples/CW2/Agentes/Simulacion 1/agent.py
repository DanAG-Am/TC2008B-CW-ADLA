'''Amilka Daniela Lopez Aguilar A01029277'''
from mesa.discrete_space import CellAgent, FixedAgent
from collections import deque

class RandomAgent(CellAgent):
    """Roomba que evita choques, comparte estaciones y áreas exploradas, y gestiona batería"""
    CHARGE_THRESHOLD = 20  # % mínimo de batería antes de ir a cargar para que ni muera en el camino de regreso 

    def __init__(self, model, cell):
        super().__init__(model)
        self.model = model
        self.cell = cell
        self.cell.agents.append(self)
        self.battery = 100
        self.movements = 0
        self.path = [] #aqui guardo el path calculado por el BFS. Es decir, guarda listas de celdas ya sea hacia estaciones de carga o suciedad
        self.state = "search_dirty"
        self.charging_station = cell
        self.visited = set([cell])  # celdas exploradas por este Roomba para que las comparta 

        # Registrar estación inicial en la lista que los roombas se van a compartir si son vecinos
        self.model.known_stations.add(cell)

    def recharge(self):
        """Recarga 5% si hay estación de carga en la celda por cada step"""
        if any(isinstance(a, ChargingStation) for a in self.cell.agents):
            self.battery = min(100, self.battery + 5)
            self.model.known_stations.add(self.cell)

    def needs_charge(self):
        """Decide si ir a cargar según batería y distancia a estación más cercana"""
        distance = self.bfs_distance_to_nearest_station()
        # si no está al 100% Y está en estación, debe seguir cargando
        if any(isinstance(a, ChargingStation) for a in self.cell.agents):
            return self.battery < 100

        return self.battery <= max(self.CHARGE_THRESHOLD, distance + 5) # puse este margen porque se estaban ciclando mis roombas y no llegaban a limpiar la ezquina sup. der.

    def bfs_distance_to_nearest_station(self): #logica del bfs que hice con Maria. Toda esta funcion le provee informacion a needs_charge para evitar que el roomba cargue bateria demasiado tarde, ya sea en base a un umbral o a una distancia si conoce las estaciones de carga
        """Distancia mínima a cualquier estación conocida"""
        queue = deque([(self.cell, 0)])
        visited = {self.cell}
        while queue:
            current, dist = queue.popleft()
            if current in self.model.known_stations:
                return dist
            neighbors = current.neighborhood.select(
                lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents)
            )
            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    queue.append((n, dist + 1))
        return float('inf')

    def find_path_to_station(self): #igual parte de la logica del bfs que hice con Maria
        """BFS hacia la estación más cercana evitando obstáculos y otros Roombas"""
        queue = deque([(self.cell, [self.cell])])
        visited = {self.cell}
        while queue:
            current, path = queue.popleft()
            if current in self.model.known_stations:
                return path[1:]
            neighbors = current.neighborhood.select(
                lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents) and all(not isinstance(a, RandomAgent) for a in c.agents)
            )
            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    queue.append((n, path + [n]))
        return []

    def find_nearest_dirty_bfs(self): # logica adicional dado que los roombas solian concentrarse en ciertas areas del grid, perdiendo bateria y cayendo en un ciclo de desplazamiento e ir a cargar 
        """Busca la celda sucia más cercana, priorizando celdas no limpias"""
        queue = deque([(self.cell, [self.cell])])
        visited = {self.cell}
        while queue:
            current, path = queue.popleft()
            if any(isinstance(a, DirtyCell) for a in current.agents):
                return path[1:]  # excluir la celda actual
            neighbors = current.neighborhood.select(lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents))
            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    queue.append((n, path + [n]))
        return []


    def share_with_neighbors(self):
        """Compartir estaciones y celdas exploradas con vecinos"""
        neighbors = self.cell.neighborhood.select(lambda c: True)
        for n in neighbors:
            for agent in n.agents:
                if isinstance(agent, RandomAgent):
                    # Compartir estaciones
                    self.model.known_stations.update(agent.model.known_stations)
                    agent.model.known_stations.update(self.model.known_stations)
                    # Compartir áreas exploradas
                    self.visited.update(agent.visited)
                    agent.visited.update(self.visited)

    def move_along_path(self): #aqui se asegura de que el movimiento sea evitando roombas
        if self.path:
            next_cell = self.path[0]
            if not any(isinstance(a, RandomAgent) for a in next_cell.agents):
                self._move_to(next_cell)
                self.path.pop(0)
            else:
                # Ruta bloqueada: intentar moverse a vecino libre
                free_neighbors = [c for c in self.cell.neighborhood.select(lambda c: all(not isinstance(a, ObstacleAgent) for a in c.agents) and all(not isinstance(a, RandomAgent) for a in c.agents))]
                if free_neighbors:
                    self._move_to(self.random.choice(free_neighbors))
    
    def _move_to(self, cell): #gasto de bateria y movimiento de celda. registro de esas celdas como visitadas para compartirlas despues
        self.cell.agents.remove(self)
        self.cell = cell
        self.cell.agents.append(self)
        self.movements += 1
        self.battery = max(0, self.battery - 1)
        self.visited.add(self.cell)

    def clean(self): #limpiar lol
        dirt = next((a for a in self.cell.agents if isinstance(a, DirtyCell)), None)
        if dirt:
            dirt.remove()
            self.battery = max(0, self.battery - 1)
            self.path = []

    def step(self):
        # Si está en estación y NO está al 100%, solo recargar
        if any(isinstance(a, ChargingStation) for a in self.cell.agents) and self.battery < 100:
            self.recharge()
            return  # no moverse ni hacer nada más

        # Recargar si hay estación
        self.recharge()

        # Compartir estaciones y áreas exploradas con vecinos
        self.share_with_neighbors()

        # Ir a cargar si batería baja
        if self.needs_charge():
            self.state = "go_charge"
            if not self.path:
                self.path = self.find_path_to_station()
        else:
            self.state = "search_dirty"
            if not self.path:
                self.path = self.find_nearest_dirty_bfs()

        # Moverse
        self.move_along_path()

        # Limpiar si hay suciedad
        self.clean()


''' Agente fijo que representa celda con suciedad'''
class DirtyCell(FixedAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        cell.agents.append(self)
    def step(self):
        pass

'''Agente fijo que representa obstaculos en el grid'''
class ObstacleAgent(FixedAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        cell.agents.append(self)
    def step(self):
        pass
    
'''Agente fijo que representa estaciones de carga (puntos de aparacion de los roombas) en el grid'''
class ChargingStation(FixedAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        cell.agents.append(self)
    def step(self):
        pass