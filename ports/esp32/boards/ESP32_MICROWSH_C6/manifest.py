include("$(PORT_DIR)/boards/manifest.py")

# drivers
freeze("modules")
require("ssd1306")

# wsh/prometheus addons
include('$(MPY_DIR)/../prometheus.micropython.manifest.py')
