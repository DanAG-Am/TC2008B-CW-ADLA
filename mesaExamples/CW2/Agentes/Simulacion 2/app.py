'''Amilka Daniela Lopez Aguilar A01029277
'''
from mesa.visualization import Slider, SolaraViz, make_space_component, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle
from random_agents.agent import RandomAgent, ObstacleAgent, DirtyCell, ChargingStation
from random_agents.model import RandomModel

def random_portrayal(agent):
    if agent is None:
        return
    portrayal = AgentPortrayalStyle(size=50, marker="o")
    if isinstance(agent, RandomAgent):
        portrayal.color = "blue"
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "gray"
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, DirtyCell):
        portrayal.color = "black"
    elif isinstance(agent, ChargingStation):
        portrayal.color = "green"
        portrayal.marker = "s"
        portrayal.size = 100
    return portrayal

def post_process(ax):
    ax.set_aspect("equal")

model_params = {
    "seed": {"type": "InputText", "value": 42, "label": "Random Seed"},
    "width": Slider("Grid width", 28, 1, 50),
    "height": Slider("Grid height", 28, 1, 50),
    "dirty_percent": Slider("Dirty cells %", 0.2, 0.0, 1.0, 0.05),
    "obstacle_percent": Slider("Obstacle %", 0.1, 0.0, 0.5, 0.05),
}

NUM_ROOMBAS = 4
MAX_STEPS = 300

model = RandomModel(
    width=model_params["width"].value,
    height=model_params["height"].value,
    seed=model_params["seed"]["value"],
    num_agents=NUM_ROOMBAS,
    max_steps=MAX_STEPS,
    dirty_percent=model_params["dirty_percent"].value,
    obstacle_percent=model_params["obstacle_percent"].value
)

space_component = make_space_component(
    random_portrayal,
    draw_grid=False,
    post_process=post_process
)

dirty_count_plot = make_plot_component({"DirtyCells": "black"})
roomba_colors = {f"Roomba_{i}_Battery": f"C{i}" for i in range(NUM_ROOMBAS)} #en teoria la bateria es lo unico que cambia entre roombas entonces que itere por la cantidad que tengo 
battery_plot = make_plot_component(roomba_colors)
steps_plot = make_plot_component({"Steps": "green"})
cleaned_plot = make_plot_component({"CleanedPercentage": "orange"})

page = SolaraViz(
    model,
    components=[space_component, dirty_count_plot, battery_plot, steps_plot, cleaned_plot],
    model_params=model_params,
    name="Roomba Cleaning Simulation",
)