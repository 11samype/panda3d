import direct.directbase.DirectStart
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math

class World(DirectObject):

    def __init__(self):
        
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0, "run":0}
        base.win.setClearColor(Vec4(0,0,0,1))
        self.environ = loader.loadModel("models/world")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        
        # Create the main character
        eveStartPos = self.environ.find("**/start_point").getPos()
        self.eve = Actor("models/eve",
                                 {"run":"models/eve_run",
                                  "walk":"models/eve_walk"})
        self.eve.reparentTo(render)
        self.eve.setScale(.2)
        self.eve.setPos(eveStartPos)

        # print(eveStartPos)

        # Green Dragon
        self.character=Actor()
        self.character.loadModel('models/nik-dragon')
        self.character.reparentTo(render)
        self.character.loadAnims({'win': 'models/nik-dragon'})
        self.character.loop('win')
        self.character.setScale(.1)
        self.character.setPos(-108,11,.1)
        
        # Red Dragon
        self.character2=Actor()
        self.character2.loadModel('models/nik-dragon')
        self.character2.reparentTo(render)
        self.character2.loadAnims({'win': 'models/nik-dragon'})
        self.character2.loop('win')
        self.character2.setPlayRate(1.5,'win')
        self.character2.setScale(.06)
        self.character2.setColorScale(6,0.2,0.2,1)
        self.character2.setPos(-102,11,.3)
        
        # Blue Dragon
        self.character3=Actor()
        self.character3.loadModel('models/nik-dragon')
        self.character3.reparentTo(render)
        self.character3.loadAnims({'win': 'models/nik-dragon'})
        self.character3.loop('win')
        self.character3.setPlayRate(.5,'win')
        self.character3.setScale(.23)
        self.character3.setColorScale(0.4,0.2,.4,.2)
        self.character3.setPos(-114,11,1.9)
    
        # Create a floater object to use for camera management
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Accept the control keys for movement and rotation
        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("space", self.setKey, ["run",1])
        self.accept("space-up", self.setKey, ["run",0])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

        taskMgr.add(self.move,"moveTask")

        # Game state variables
        self.isMoving = False
        self.isRunning = False
        self.isWalking = False

        # Set up the camera
        base.disableMouse()
        base.camera.setPos(self.eve.getX(),self.eve.getY()+10,2)
        
        # Collision detection for eve against the ground and against objects
        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above eve's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.
        self.cTrav = CollisionTraverser()

        self.eveGroundRay = CollisionRay()
        self.eveGroundRay.setOrigin(0,0,1000)
        self.eveGroundRay.setDirection(0,0,-1)
        self.eveGroundCol = CollisionNode('eveRay')
        self.eveGroundCol.addSolid(self.eveGroundRay)
        self.eveGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.eveGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.eveGroundColNp = self.eve.attachNewNode(self.eveGroundCol)
        self.eveGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.eveGroundColNp, self.eveGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

        # Shows collision rays
        #self.eveGroundColNp.show()
        #self.camGroundColNp.show()
       
        # Shows collisions
        #self.cTrav.showCollisions(render)
        
        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(-5, -5, -5))
        directionalLight.setColor(Vec4(1, 1, 1, 1))
        directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))
    
	# Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
    
	# Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.
        base.camera.lookAt(self.eve)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        # save eve's initial position so that we can restore it,
        # in case she falls off the map or runs into something.
        startpos = self.eve.getPos()

        # If a move-key is pressed, move eve in the specified direction.
        if (self.keyMap["left"]!=0):
            self.eve.setH(self.eve.getH() + 300 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.eve.setH(self.eve.getH() - 300 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            if (self.keyMap["run"] != 0):
                self.eve.setY(self.eve, -30 * globalClock.getDt())
            else:
                self.eve.setY(self.eve, -10 * globalClock.getDt())
                
        # If eve is moving, loop the run animation.
        # If she is standing still, stop the animation.
        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                if (self.keyMap["run"] != 0):
                    self.eve.loop("run")
                    self.isMoving = True
                    self.isRunning = True
                    self.isWalking = False
                else:
                    self.eve.loop("walk")
                    self.eve.setPlayRate(2.0, "walk")
                    self.isMoving = True
                    self.isWalking = True
                    self.isRunning = False
            else:
                if (self.keyMap["run"] != 0 and self.isWalking):
                    self.eve.loop("run")
                    self.isRunning = True
                    self.isWalking = False
                elif (self.keyMap["run"] == 0 and self.isRunning):
                    self.eve.loop("walk")
                    self.eve.setPlayRate(2.0, "walk")
                    self.isWalking = True
                    self.isRunning = False
        else:
            if self.isMoving:
                self.eve.stop()
                self.eve.pose("walk",10)
                self.isMoving = False

        # If the camera is too far from eve, move it closer.
        # If the camera is too close to eve, move it farther.
        camvec = self.eve.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0

        # Now check for collisions.
        self.cTrav.traverse(render)

        # Adjust eve's Z coordinate.  If eve's ray hit terrain,
        # update her Z. If it hit anything else, or didn't hit anything, put
        # her back where she was last frame.
        entries = []
        for i in range(self.eveGroundHandler.getNumEntries()):
            entry = self.eveGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.eve.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.eve.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above eve, whichever is greater.
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
        if (base.camera.getZ() < self.eve.getZ() + 2.0):
            base.camera.setZ(self.eve.getZ() + 2.0)
            
        # The camera should look in eve's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above eve's head.
        self.floater.setPos(self.eve.getPos())
        self.floater.setZ(self.eve.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        return task.cont


# Instantiate a world and start it running
w = World()
run()