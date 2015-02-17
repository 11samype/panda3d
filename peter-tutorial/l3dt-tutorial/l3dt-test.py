from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeoMipTerrain

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        terrain = GeoMipTerrain("worldTerrain")
        terrain.setHeightfield("height-map.png")
        terrain.setColorMap("texture-map.png")
        terrain.setBruteforce(True)
        root = terrain.getRoot()
        root.reparentTo(render)
        root.setSz(60)
        terrain.generate()
        
app = MyApp()
app.run()