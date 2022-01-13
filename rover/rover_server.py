from os.path import dirname
from math import comb
from itertools import combinations, chain
import justpy as jp
from groundplane import groundplane
import asyncio


rover_interface = groundplane(f"{dirname(__file__)}/rover.gp")


class node:
    node_string = '<a-sphere id="{nodeId}" position="{position}" radius="1.25" color="{color}"></a-sphere>'  # Core a-frame html snippet for defining a node
    active_color = 16711680  # 0xFF0000 - hex code for red
    inactive_color = 10462934 # 0x9FA6D6 - hex code for bluish-gray
    gradient = 1114112  # 0x110000 - shade of red to use when showing state change
    nodes = {"right": rover_interface.right, "center": rover_interface.center, "left": rover_interface.left}

    @classmethod
    def position(cls, pos):
        positions =  {
            "left": "3 -7.3 -15",
            "right": "-4 -7.3 -15",
            "center": "-0.5 -12 -15"}
        assert pos in positions.keys(), f"Unrecognized position {pos}"
        return positions[pos]


class button:
    button_string = '<a-box position="{position}" rotation="0 45 0" color="{color}"></a-box>'
    num_buttons = sum([comb(len(node.nodes), num_active) for num_active in range(1, len(node.nodes))])  # aggregated nCr for r in [1, # of Nodes)
    button_classes = 'h-64 w-64 text-3xl mr-2 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full'
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
        print("Rewarding!!")
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


def AframeDoc():
    state = rover_interface.state()
    print(f"Generating AFrame Interface for:\n{state}")
    activity = {
        nodeName: hex(node.active_color
                      if state[nodeName]['state'] == 1 else
                      node.inactive_color).replace("0x", "#")
        for nodeName in node.nodes.keys()
    }
    scene_elements = "\n".join([
        node.node_string.format(
            nodeId=f"node_{nodeName}",
            position=node.position(nodeName),
            color=activity[nodeName]
        ) for nodeName in node.nodes.keys()
    ])
    aframe_doc = f"""
        <a-scene device-orientation-permission-ui="enabled: false">
            <a-asset>
                <a-asset-item response-type="arraybuffer" id="dogModel" src="/static/static/Dog.stl"></a-asset-item>
            </a-asset>
            <a-entity rotation="20 10 0" position="3 2 -3">
                <a-entity stl-model="src: #dogModel" position="-5 -14 -20" rotation="-90 0 0" scale="0.005 0.005 0.005"
                    material="color: #00d000; roughness: 1; metalness: 0"></a-entity>
                {scene_elements}
            </a-entity>
        </a-scene>
    """
    return aframe_doc


simulator = jp.WebPage(delete_flag=False)
simulator.add(jp.Div(text="umm"))


async def getSimulator():
    simulator.head_html = """
    <script src="https://aframe.io/releases/1.2.0/aframe.min.js"></script>
    <script src="/static/static/aframe-stl-model.js"></script>
"""
    async def node_monitor(webpage):
        while True:
            if (aframeDoc := AframeDoc()) != webpage.body_html:
                print("Rebuilding")
                webpage.body_html = aframeDoc
                await webpage.update()
                print("Rebuild complete!")
            await asyncio.sleep(0.1)

    # Build AFrame scene continuously every 0.1 seconds
    simulator.body_html = AframeDoc()
    jp.run_task(node_monitor(simulator))
    return simulator


ui = jp.WebPage(delete_flag=False)


async def rover_ui():
    wp = ui
    wp.title = "RoverPy"
    jp.Div(a=wp, text="Welcome to Rover")
    content_container = jp.Div(a=wp, id="coreContainer", classes="grid grid-cols-1")
    jp.Div(
        a=content_container,
        inner_html=f"""<iframe src="/simulator" width=100% height="300" style:"border:1px solid black;">"""
    )
    jp.Div(a=content_container, classes="flex justify-center").add(
        jp.Button(text="Reward", classes=button.button_classes, id="reward", click=button.reward))
    btnDiv = jp.Div(a=content_container, classes="flex-wrap text-center") 
    for btn in button.buttons.values():
        btnDiv.add(btn)
    jp.Div(a=content_container, classes="flex justify-center").add(
        jp.Button(text="Silence", classes=button.button_classes, id="silence", click=button.silence))

    return wp

if __name__ == "__main__":
    jp.Route("/simulator", getSimulator)
    jp.justpy(rover_ui, host="0.0.0.0")

