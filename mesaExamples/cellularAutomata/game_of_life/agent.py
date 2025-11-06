# '''
# A01029277 Amilka Daniela Lopez Aguilar 
# '''
# #Parte 1
# # FixedAgent: Immobile agents permanently fixed to cells
# from mesa.discrete_space import FixedAgent

# class Cell(FixedAgent):
#     """Represents a single ALIVE or DEAD cell in the simulation."""

#     DEAD = 0
#     ALIVE = 1

#     @property
#     def x(self):
#         return self.cell.coordinate[0]

#     @property
#     def y(self):
#         return self.cell.coordinate[1]

#     @property
#     def is_alive(self):
#         return self.state == self.ALIVE

#     @property
#     def neighbors(self):
#         return self.cell.neighborhood.agents
    
#     def __init__(self, model, cell, init_state=DEAD):
#         """Create a cell, in the given state, at the given x, y position."""
#         super().__init__(model)
#         self.cell = cell
#         self.pos = cell.coordinate
#         self.state = init_state
#         self._next_state = None

#     def determine_state(self):
#         """Compute if the cell will be dead or alive at the next tick.  This is
#         based on the number of alive or dead neighbors.  The state is not
#         changed here, but is just computed and stored in self._nextState,
#         because our current state may still be necessary for our neighbors
#         to calculate their next state.
#         """
#         # Get the neighbors and apply the rules on whether to be alive or dead
#         # at the next tick.
#         '''live_neighbors = sum(neighbor.is_alive for neighbor in self.neighbors) no
#         necesitamos esta linea porque solo checamos 3 celdas y aplicamos nuevas reglas'''


#         # Assume nextState is unchanged, unless changed below.
#         self._next_state = self.state

#         arrIzq =[self.x - 1, self.y + 1]
#         arr = [self.x, self.y + 1]
#         arrDer = [self.x + 1, self.y + 1]

#         #Inicializar estados para cambiarlos a true conforme las reglas
#         estadoArrIzq = False
#         estadoArr = False
#         estadoArrDer = False

#         #Checar vecinos 
#         for neighbor in self.neighbors:
#             neighbor_pos = [neighbor.x, neighbor.y]
    
#             if neighbor_pos == arrIzq and neighbor.is_alive:
#                 estadoArrIzq = True
#             if neighbor_pos == arr and neighbor.is_alive:    
#                 estadoArr = True
#             if neighbor_pos == arrDer and neighbor.is_alive:
#                 estadoArrDer = True

#         #reglas segun la combinacion de bits 
#         if self.y == 49:
#             self._next_state = self.state
#         elif estadoArrIzq and estadoArr and estadoArrDer:
#             self._next_state = self.DEAD
#         elif estadoArrIzq and estadoArr and not estadoArrDer:
#             self._next_state = self.ALIVE
#         elif estadoArrIzq and not estadoArr and estadoArrDer:
#             self._next_state = self.DEAD
#         elif estadoArrIzq and not estadoArr and not estadoArrDer:
#             self._next_state = self.ALIVE
#         elif not estadoArrIzq and estadoArr and estadoArrDer:
#             self._next_state = self.ALIVE
#         elif not estadoArrIzq and estadoArr and not estadoArrDer:
#             self._next_state = self.DEAD
#         elif not estadoArrIzq and not estadoArr and estadoArrDer:
#             self._next_state = self.ALIVE
#         elif not estadoArrIzq and not estadoArr and not estadoArrDer:
#             self._next_state = self.DEAD
        
#     def assume_state(self):
#         """Set the state to the new computed state -- computed in step()."""
#         self.state = self._next_state

#Parte 2
# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """
        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        '''live_neighbors = sum(neighbor.is_alive for neighbor in self.neighbors) no
        necesitamos esta linea porque solo checamos 3 celdas y aplicamos nuevas reglas'''


        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state

        arrIzq =[(self.x - 1) % 50, (self.y + 1) % 50] # % se asegura que no se salga del grid (que se vea un desplazamiento hacia abajo)
        arr = [(self.x) % 50, (self.y + 1) % 50]
        arrDer =  [(self.x + 1) % 50, (self.y + 1) % 50] 
        '''Queremos que self.x-1, cuando sea -1, -1%50 es 49. Asi mismo, que cuando self.y+1=50, 50%50=0'''
        
        #Inicializar estados para cambiarlos a true conforme las reglas
        estadoArrIzq = False
        estadoArr = False
        estadoArrDer = False

        #Checar vecinos 
        for neighbor in self.neighbors:
            neighbor_pos = [neighbor.x, neighbor.y]
    
            if neighbor_pos == arrIzq and neighbor.is_alive:
                estadoArrIzq = True
            if neighbor_pos == arr and neighbor.is_alive:    
                estadoArr = True
            if neighbor_pos == arrDer and neighbor.is_alive:
                estadoArrDer = True

        #reglas segun la combinacion de bits, ya no depende de la primera fila
        if estadoArrIzq and estadoArr and estadoArrDer:
            self._next_state = self.DEAD
        elif estadoArrIzq and estadoArr and not estadoArrDer:
            self._next_state = self.ALIVE
        elif estadoArrIzq and not estadoArr and estadoArrDer:
            self._next_state = self.DEAD
        elif estadoArrIzq and not estadoArr and not estadoArrDer:
            self._next_state = self.ALIVE
        elif not estadoArrIzq and estadoArr and estadoArrDer:
            self._next_state = self.ALIVE
        elif not estadoArrIzq and estadoArr and not estadoArrDer:
            self._next_state = self.DEAD
        elif not estadoArrIzq and not estadoArr and estadoArrDer:
            self._next_state = self.ALIVE
        elif not estadoArrIzq and not estadoArr and not estadoArrDer:
            self._next_state = self.DEAD
        
    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state