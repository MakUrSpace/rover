# Development

Use [ampy](https://github.com/scientifichackers/ampy) to interface with the ESP32C2 MicroPython board

* `pip install adafruit-ampy`
* `ampy -p COM3 -b 115200 ls`


```python
from time import sleep
files = ['boot.py', 'main.py', 'static/rover.html', 'edaphic/device_utilities.py', 'edaphic/HTTPServer.py', 'edaphic/__init__.py']
for f in files:
	print(f)
	!ampy -p COM3 -b 115200 put $f
	sleep(1)
```