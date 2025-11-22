'''Amilka Daniela Lopez Aguilar A01029277'''
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import RandomAgent, ObstacleAgent, DirtyCell, ChargingStation

class RandomModel(Model):
    def __init__(self, width=8, height=8, dirty_percent=0.2,
                 obstacle_percent=0.1, seed=42, num_agents=4,
                 max_steps=300):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.dirty_percent = dirty_percent
        self.obstacle_percent = obstacle_percent
        self.num_agents = num_agents
        self.steps_count = 0
        self.max_steps = max_steps
        self.running = True

        # conjunto compartido globalmente
        self.known_stations = set()
        self.global_visited = set()

        self.grid = OrthogonalMooreGrid([self.width, self.height],
                                        torus=False, random=self.random)
        # bordes como obstáculos
        border = [(x, y)
                  for y in range(self.height)
                  for x in range(self.width)
                  if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1]

        for cell in self.grid.all_cells:
            if cell.coordinate in border:
                ObstacleAgent(self, cell)

        # crear agentes y estaciones
        self.roombas = []
        available_cells = [c for c in self.grid.empties if not c.agents and c.coordinate not in border]

        for _ in range(self.num_agents):
            start_cell = self.random.choice(available_cells)
            available_cells.remove(start_cell)
            ChargingStation(self, start_cell)
            self.known_stations.add(start_cell)
            agent = RandomAgent(self, start_cell)
            agent.charging_station = start_cell
            self.roombas.append(agent)
            self.global_visited.add(start_cell)

        # Dirty cells
        available_cells = [c for c in self.grid.empties if not c.agents and c.coordinate not in border]
        num_dirty = int(len(available_cells) * self.dirty_percent)
        dirty_cells = self.random.sample(available_cells, k=num_dirty)

        for c in dirty_cells:
            DirtyCell(self, c)
        self.initial_dirty = num_dirty
        # Obstáculos internos
        available_cells = [c for c in self.grid.empties if not c.agents and c.coordinate not in border]
        num_obstacles = int(len(available_cells) * self.obstacle_percent)
        obstacle_cells = self.random.sample(available_cells, k=num_obstacles)
        
        for c in obstacle_cells:
            ObstacleAgent(self, c)
        # Datacollector
        self.datacollector = DataCollector({
            "DirtyCells": lambda m: len([a for cell in m.grid.all_cells for a in cell.agents if isinstance(a, DirtyCell)]),
            **{f"Roomba_{i}_Battery": (lambda m, i=i: m.roombas[i].battery)
               for i in range(self.num_agents)}, # le pedi prestada esta logica a Maria 
            "Steps": lambda m: m.steps_count,
            "CleanedPercentage": lambda m:
                ((m.initial_dirty - len([a for cell in m.grid.all_cells for a in cell.agents if isinstance(a, DirtyCell)])) / m.initial_dirty * 100)
                if m.initial_dirty > 0 else 0 })
        self.datacollector.collect(self)

    def step(self):
        if not self.running:
            return
        if self.steps_count >= self.max_steps:
            self.running = False
            return
        self.agents.shuffle_do("step")
        self.steps_count += 1
        self.datacollector.collect(self)
