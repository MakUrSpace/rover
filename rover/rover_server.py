from os.path import dirname
from math import comb
from itertools import combinations, chain
import justpy as jp
from groundplane import groundplane


rover_interface = groundplane(f"{dirname(__file__)}/rover.gp")


class node:
    node_string = '<a-sphere position="{position}" radius="1.25" color="{color}"></a-sphere>'  # Core a-frame html snippet for defining a node
    active_color = 16711680  # 0xFF0000 - hex code for red
    gradient = 1114112  # 0x110000 - shade of red to use when showing state change
    nodes = {"right": rover_interface.right, "center": rover_interface.center, "left": rover_interface.left}

    @classmethod
    def position(cls, pos):
        positions =  {
            "left": "-10 0 -10",
            "right": "10 0 -10",
            "center": "0 0 -10"}
        assert pos in positions.keys(), f"Unrecognized position {pos}"
        return positions[pos]


class button:
    button_string = '<a-box position="{position}" rotation="0 45 0" color="{color}"></a-box>'
    num_buttons = sum([comb(len(node.nodes), num_active) for num_active in range(1, len(node.nodes))])  # aggregated nCr for r in [1, # of Nodes)
    button_classes = 'w-32 mr-2 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full'
    buttons = {}
    button_handlers = {}

    @classmethod
    def buttonHandler(cls, event):
        active_nodes = event['id'].split('-')
        cls.silence()
        for node in active_nodes:
            getattr(rover_interface, node).request_state({"state": 1})
        assert len(active_nodes) > 0

    @classmethod
    def reward(cls, *args, **kwargs):
        rover_interface.request_state({"center": {"state": 1}, "right": {"state": 1}, "left": {"state": 1}})

    @classmethod
    def silence(cls, *args, **kwargs):
        rover_interface.request_state({"center": {"state": 0}, "right": {"state": 0}, "left": {"state": 0}})


button.buttons = {
    (button_name := "-".join(active_nodes)): jp.Button(
       id=button_name,
       text=button_name,
       classes=button.button_classes,
       click=button.buttonHandler)
    for idx, active_nodes in enumerate(chain(*[
       combinations(node.nodes.keys(), num_active)
       for num_active in range(1, len(node.nodes))]))
}


async def simulator():
    wp = jp.WebPage()
    wp.head_html = '<script src="https://aframe.io/releases/1.2.0/aframe.min.js"></script>'
    wp.add(jp.Div(text="umm"))

    ## Build scene
    scene_elements = [
            node.node_string.format(
                position=node.position(nodeName),
                color=hex(node.active_color).replace('0x', '#')
            ) for nodeName in node.nodes.keys()
    ]
    scene_elements = "\n".join(scene_elements)

    wp.body_html = f"""
    <a-scene>
        {scene_elements}
    </a-scene>
"""
    return wp


async def rover_ui():
    wp = jp.WebPage()
    wp.title = "RoverPy"
    jp.Div(a=wp, text="Welcome to Rover")
    jp.Div(
        a=wp,
        inner_html=f"""<iframe src="/simulator" width=100% height="300" style:"border:1px solid black;">"""
    )
    jp.Div(a=wp, classes="flex justify-center").add(
        jp.Button(text="Reward", classes=button.button_classes, id="reward", click=button.reward))
    btnDiv = jp.Div(a=wp, classes="flex-wrap justify-center") 
    for btn in button.buttons.values():
        btnDiv.add(btn)
    jp.Div(a=wp, classes="flex justify-center").add(
        jp.Button(text="Silence", classes=button.button_classes, id="silence", click=button.silence))
    return wp


jp.Route("/simulator", simulator)
jp.justpy(rover_ui, host="0.0.0.0")
