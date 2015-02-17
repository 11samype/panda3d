import direct.directbase.DirectStart
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32,GeomNode, Fog
from panda3d.core import TransparencyAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.particles.ParticleEffect import ParticleEffect
from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from panda3d.ai import *
import random, sys, os, math, time

def grabPie(pieCount):
    return OnscreenText(text = "Pies Scavenged: " + str(pieCount), style = 3, pos = (-1.3, .90), fg=(1,0.3,0.3,1),
        align = TextNode.ALeft, scale = .1)

def displayGameOver():
    return OnscreenText(text = "Game Over!", style = 3, pos = (0, .95-.05*14), fg=(1,0.3,0.3,1),
        align = TextNode.ACenter, scale = .10)
                      
class World(DirectObject):
    def freezeGame():
        # Pause all of the AI, stop model animations, cease taking inputs, except for reset
        return 0
        
    def resetGame():
        # Set everything back to its starting position and remove the game over message
        return 0
    
    
    def __init__(self):
        # Sound
        # music = loader.loadMusic("sounds/Enchanted-Woods.mp3")
        # music.setLoop(1)
        # music.play()
        
        self.collectSoundEffect = loader.loadMusic("sounds/item_collect.mp3")
        
        self.footstepSound = loader.loadMusic("sounds/footsteps.mp3")
        self.footstepSound.setLoop(1);
        
        audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], base.camera)
        
    
        # Sky Box
        starTexture = loader.loadTexture("models/stars.jpg")
        self.sky = loader.loadModel("models/box.egg")
        self.sky.setScale(300)
        self.sky.setPos(-200,-150,0)
        self.sky.setBin('background', 0)
        self.sky.setDepthWrite(0)
        self.sky.setTwoSided(True)
        self.sky.setTexture(starTexture, 1)
        
        self.sky.reparentTo(render)
        self.sky.set_compass()
    
        # allow transparency
        render.setTransparency(TransparencyAttrib.MAlpha)

        self.pieCount = 0
        self.pieDisplay = grabPie(self.pieCount)
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
        print(eveStartPos)
        self.gameOver = 0
        self.eve.reparentTo(render)
        self.eve.setScale(.2)
        self.eve.setPos(eveStartPos)

        self.eateve = Actor("models/eve")
        self.eateve.reparentTo(render)
        self.eateve.setScale(.2)
        self.eateve.setPos(eveStartPos)
        self.eateve.hide()
        
        self.pie = Actor("models/fruit-pie-slice")
        self.pie.reparentTo(render)
        self.pie.setScale(.5)
        self.pie.setPos(Vec3(-50, -30, 10))
        #self.pie.setP(20)
        
        self.rand = Actor("models/eve")
        self.rand.reparentTo(render)
        self.rand.setScale(.2)
        self.rand.setPos(Vec3(-70, -5, eveStartPos.getZ() + 5))
        self.rand.hide()       
         
        self.rand2 = Actor("models/eve")
        self.rand2.reparentTo(render)
        self.rand2.setScale(.2)
        self.rand2.setPos(Vec3(-70, -5, eveStartPos.getZ() + 10))
        self.rand2.hide()
        # print(eveStartPos)
        
        # Blue Dragon
        self.character3=Actor()
        self.character3.loadModel('models/nik-dragon')
        self.character3.reparentTo(render)
        self.character3.loadAnims({'win': 'models/nik-dragon'})
        self.character3.loop('win')
        self.character3.setPlayRate(.5,'win')
        self.character3.setScale(.23)
        self.character3.setTransparency(1)
        #self.character3.setColorScale(0.4,0.2,.4,.7)
        self.character3.setColorScale(9,9,9,.3)
        self.character3.setPos(-114,11,1.9)
        
        blueDragonSound = audio3d.loadSfx("sounds/Snoring Giant.mp3")
        audio3d.attachSoundToObject(blueDragonSound, self.character3)
        blueDragonSound.setLoop(True)
        blueDragonSound.play()
        
        # Red Dragon
        self.character2=Actor()
        self.character2.loadModel('models/nik-dragon')
        self.character2.reparentTo(render)
        self.character2.loadAnims({'win': 'models/nik-dragon'})
        self.character2.loop('win')
        self.character2.setPlayRate(1.5,'win')
        self.character2.setScale(.06)
        self.character2.setColorScale(6,0.2,0.2,50)
        self.character2.setPos(-108,11,.3)

        self.redDragonStartPos = self.character2.getPos()
        self.redDragonCollideCount = 0
        
        redDragonSound = audio3d.loadSfx("sounds/Velociraptor Call.mp3")
        audio3d.attachSoundToObject(redDragonSound, self.character3)
        redDragonSound.setLoop(True)
        redDragonSound.play()
        
        # Green Dragon
        self.character=Actor()
        self.character.loadModel('models/nik-dragon')
        self.character.reparentTo(render)
        self.character.loadAnims({'win': 'models/nik-dragon'})
        self.character.loop('win')
        self.character.setScale(.1)
        self.character.setPos(-118,21,0)
        
        greenDragonSound = audio3d.loadSfx("sounds/Raptor Call.mp3")
        audio3d.attachSoundToObject(greenDragonSound, self.character3)
        greenDragonSound.setLoop(True)
        greenDragonSound.play()
        
        self.dragonStartPos = self.character.getPos()
        self.dragonCollideCount = 0
        self.AIworld = AIWorld(render)
        #self.AIworld.addObstacle(self.environ)
        
        self.dragonAI = AICharacter("character", self.character, 100, 0.05, 5)
        self.AIworld.addAiChar(self.dragonAI)
        self.AIbehaviors = self.dragonAI.getAiBehaviors()
        #self.AIbehaviors.seek(self.character2)
        #self.AIbehaviors.wander(2, 0, 5, .5)
        self.AIbehaviors.pursue(self.eateve, 1)
        #self.AIbehaviors.wander(5,0,10,.5)
        #self.AIbehaviors.evade(self.character3, 10, 20, 300)
        #self.AIbehaviors.seek(self.eve, .5)
        #self.AIbehaviors.obstacleAvoidance(1)
        
        self.randomChase = AICharacter("rand", self.rand, 50, 20, 20)
        self.AIworld.addAiChar(self.randomChase)
        self.AIbehaviorsRand = self.randomChase.getAiBehaviors()
        self.AIbehaviorsRand.wander(10,0,47,.5)
        
        self.randomChase2 = AICharacter("rand2", self.rand2, 50, 20, 20)
        self.AIworld.addAiChar(self.randomChase2)
        self.AIbehaviorsRand2 = self.randomChase2.getAiBehaviors()
        self.AIbehaviorsRand2.wander(10,0,47,.5)

        self.ghostDragonAI = AICharacter("character3", self.character3, 250, .05, 5)
        self.AIworld.addAiChar(self.ghostDragonAI)
        self.AIbehaviors3 = self.ghostDragonAI.getAiBehaviors()
        self.AIbehaviors3.pursue(self.rand, 1)
        #self.AIbehaviors3.wander(5,0,10,.5)
        
        self.redDragonChasingEve = 0
        self.redDragonAI = AICharacter("character2", self.character2, 100, .05, 7)
        self.AIworld.addAiChar(self.redDragonAI)
        self.AIbehaviors2 = self.redDragonAI.getAiBehaviors()
        self.AIbehaviors2.pursue(self.rand2, 1)
        
        taskMgr.add(self.AIUpdate, "AIUpdate")

    
        # Create a floater object to use for camera management
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)
        
        # Enable Particles
        base.enableParticles()

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
        self.eveGroundRay.setOrigin(0,0,4.5)
        self.eveGroundRay.setDirection(0,0,-1)
        self.eveGroundCol = CollisionNode('eveRay')
        self.eveGroundCol.addSolid(self.eveGroundRay)
        self.eveGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.eveGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.eveGroundColNp = self.eve.attachNewNode(self.eveGroundCol)
        self.eveGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.eveGroundColNp, self.eveGroundHandler)

        self.dragonGroundRay = CollisionRay()
        self.dragonGroundRay.setOrigin(0,0,10)
        self.dragonGroundRay.setDirection(0,0,-1)
        self.dragonGroundCol = CollisionNode('dragonRay')
        self.dragonGroundCol.addSolid(self.dragonGroundRay)
        self.dragonGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.dragonGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.dragonGroundColNp = self.character.attachNewNode(self.dragonGroundCol)
        self.dragonGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.dragonGroundColNp, self.dragonGroundHandler)

        self.ghostDragonGroundRay = CollisionRay()
        self.ghostDragonGroundRay.setOrigin(0,0,25)
        self.ghostDragonGroundRay.setDirection(0,0,-1)
        self.ghostDragonGroundCol = CollisionNode('ghostDragonRay')
        self.ghostDragonGroundCol.addSolid(self.ghostDragonGroundRay)
        self.ghostDragonGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ghostDragonGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ghostDragonGroundColNp = self.character3.attachNewNode(self.ghostDragonGroundCol)
        self.ghostDragonGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ghostDragonGroundColNp, self.ghostDragonGroundHandler)

        self.redDragonGroundRay = CollisionRay()
        self.redDragonGroundRay.setOrigin(0,0,5)
        self.redDragonGroundRay.setDirection(0,0,-1)
        self.redDragonGroundCol = CollisionNode('redDragonRay')
        self.redDragonGroundCol.addSolid(self.redDragonGroundRay)
        self.redDragonGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.redDragonGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.redDragonGroundColNp = self.character2.attachNewNode(self.ghostDragonGroundCol)
        self.redDragonGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.redDragonGroundColNp, self.redDragonGroundHandler)
        
        self.pieRay = CollisionRay()
        self.pieRay.setOrigin(0,0,10)
        self.pieRay.setDirection(0,0,-1)
        self.pieCol = CollisionNode('pieRay')
        self.pieCol.addSolid(self.pieRay)
        self.pieCol.setFromCollideMask(BitMask32.bit(0))
        self.pieCol.setIntoCollideMask(BitMask32.allOff())
        self.pieColNp = self.pie.attachNewNode(self.pieCol)
        self.pieHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.pieColNp, self.pieHandler)
        
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
        self.eveGroundColNp.show()
        self.camGroundColNp.show()
       
        # Shows collisions
        self.cTrav.showCollisions(render)
        
        self.fixPieZ()
        
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
    
    def AIUpdate(self, task):
        self.AIworld.update()
        return task.cont
    
    def fixPieZ(self):
        self.cTrav.traverse(render)
        entries = []
        for i in range(self.pieHandler.getNumEntries()):
            entry = self.pieHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            print("lift off of ground")
            self.pie.setZ(entries[0].getSurfacePoint(render).getZ() + .5)
            return False
        else:
            print("collision")
            return True
    
    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        if math.sqrt((self.eve.getX() - self.pie.getX())**2 + (self.eve.getY() - self.pie.getY())**2) < .6:
            # particle effect
            self.p = ParticleEffect()
            self.p.loadConfig("models/sparkleparticlerenderer.ptf")
            
            self.copyPie = self.pie.copyTo(render)
            self.copyPie.setColor(0.0, 0.0, 0.0, 0.0)
            
            self.p.start(parent = self.copyPie, renderParent = render)
            taskMgr.add(self.timedParticle, "timedParticle")
            
            # play collect sounds
            self.collectSoundEffect.play()
            
            # collect pie
            try:
                self.pie.setPos(Vec3(random.randrange(-120,-19), random.randrange(-60,51), 10))
                while self.fixPieZ():
                    self.pie.setPos(Vec3(random.randrange(-120,-19), random.randrange(-60,51), 10))
            except Exception as ex:
                print ex
                raw_input()
            self.pieDisplay.clearText()
            self.pieCount = self.pieCount + 1
            self.pieDisplay = grabPie(self.pieCount)
            
            
        if math.sqrt((self.eve.getX() - self.character.getX())**2 + (self.eve.getY() - self.character.getY())**2) < 1 and self.gameOver == 0:
            self.caught = displayGameOver()
            self.gameOver = 1

        if math.sqrt((self.eve.getX() - self.character2.getX())**2 + (self.eve.getY() - self.character2.getY())**2) < 1 and self.gameOver == 0:
            self.caught = displayGameOver()
            self.gameOver = 1
            
        if math.sqrt((self.eve.getX() - self.character3.getX())**2 + (self.eve.getY() - self.character3.getY())**2) < 1.3 and self.gameOver == 0:
            self.caught = displayGameOver()
            self.gameOver = 1

        if math.sqrt((self.eve.getX() - self.character2.getX())**2 + (self.eve.getY() - self.character2.getY())**2) < 12.5 and self.redDragonCollideCount == 0 and self.redDragonChasingEve == 0:
            self.redDragonChasingEve = 1
            self.AIbehaviors2.removeAi("pursue")
            self.AIbehaviors2.pauseAi("seek")
            self.AIbehaviors2.pursue(self.eve, 1)
            
        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.
        base.camera.lookAt(self.eve)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        self.pie.setH(self.pie.getH() + 100 * globalClock.getDt())

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
                    self.footstepSound.setPlayRate(1.3)
                    self.footstepSound.play()

                else:
                    self.eve.loop("walk")
                    self.eve.setPlayRate(2.0, "walk")
                    self.isMoving = True
                    self.isWalking = True
                    self.isRunning = False
                    self.footstepSound.setPlayRate(1.0)
                    self.footstepSound.play()
            else:
                if (self.keyMap["run"] != 0 and self.isWalking):
                    self.eve.loop("run" )
                    self.isRunning = True
                    self.isWalking = False
                    self.footstepSound.setPlayRate(1.3)

                elif (self.keyMap["run"] == 0 and self.isRunning):
                    self.eve.loop("walk")
                    self.eve.setPlayRate(2.0, "walk")
                    self.isWalking = True
                    self.isRunning = False
                    self.footstepSound.setPlayRate(1.0)
                    
        else:
            if self.isMoving:
                self.eve.stop()
                self.eve.pose("walk",10)
                self.isMoving = False
                self.footstepSound.stop()

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

        # Adjust eve's Z coordinate. If eve's ray hit terrain,s
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
            
            

        
        # Adjust the dragon's Z coordinate like with eve. Additionally, if
        # the dragon has hit an object, have it seek a location behind it
        # temporarily.
        if self.dragonCollideCount == 0:
            self.AIbehaviors.resumeAi("pursue")
            self.AIbehaviors.pauseAi("seek")
        else:
            self.dragonCollideCount = self.dragonCollideCount - 1
        
        entries = []
        for i in range(self.dragonGroundHandler.getNumEntries()):
            entry = self.dragonGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.character.setZ(entries[0].getSurfacePoint(render).getZ() + 1)
        elif (self.dragonCollideCount == 0):
            try:
                self.AIbehaviors.pauseAi("pursue")
            except Exception as ex:
                print ex
                raw_input()
            self.AIbehaviors.seek(Vec3(self.character.getX() + 2000*(-self.character.getX() + self.dragonStartPos.getX()), self.character.getY() + 2000*(-self.character.getY() + self.dragonStartPos.getY()), self.character.getZ() + 2000*(-self.character.getZ() + self.dragonStartPos.getZ())), 20000)
            #self.AIbehaviors.seek(self.character3)
            self.dragonCollideCount = 100
            #self.AIbehaviors.flee(self.character.getPos(), 1, 10, 10000)
            #self.character.setPos(dragonStartPos)
        else:
            #do nothing
            self.dragonCollideCount = self.dragonCollideCount
        
        if self.redDragonCollideCount == 0 and self.redDragonChasingEve == 0:
            self.AIbehaviors2.pursue(self.rand2, 1)
            self.AIbehaviors2.pauseAi("seek")
        elif self.redDragonChasingEve == 0:
            self.redDragonCollideCount = self.redDragonCollideCount - 1
        
        # Red dragon z correcting and collision detecting
        entries = []
        for i in range(self.redDragonGroundHandler.getNumEntries()):
            entry = self.redDragonGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.character2.setZ(entries[0].getSurfacePoint(render).getZ() + .6)
        elif (self.redDragonCollideCount == 0):
            try:
                self.AIbehaviors2.removeAi("pursue")
            except Exception as ex:
                print ex
                raw_input()
            self.redDragonChasingEve = 0
            self.AIbehaviors2.seek(Vec3(self.character2.getX() + 2000*(-self.character2.getX() + self.redDragonStartPos.getX()), self.character2.getY() + 2000*(-self.character2.getY() + self.redDragonStartPos.getY()), self.character2.getZ() + 2000*(-self.character2.getZ() + self.redDragonStartPos.getZ())), 20000)
            #self.AIbehaviors.seek(self.character3)
            self.redDragonCollideCount = 100
            #self.AIbehaviors.flee(self.character.getPos(), 1, 10, 10000)
            #self.character.setPos(dragonStartPos)
        else:
            #do nothing
            self.redDragonCollideCount = self.redDragonCollideCount
        
        # Adjust the ghost dragon's Z coordinate like with eve.
        # Additionally, if the ghost dragon has hit an object, have it
        # seek a location behind it temporarily.
        #if self.ghostDragonCollideCount == 0:
        #    self.AIbehaviors.resumeAi("wander")
        #    self.AIbehaviors3.pauseAi("seek")
        #else:
        #    self.ghostDragonCollideCount = self.dragonCollideCount - 1
        
        entries = []
        for i in range(self.ghostDragonGroundHandler.getNumEntries()):
            entry = self.ghostDragonGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: ghostDragonCmp(x,y))
        
        if (len(entries)>0):
            self.character3.setZ(entries[0].getSurfacePoint(render).getZ() + 2.5)
        #elif (self.ghostDragonCollideCount == 0):
        #    self.AIbehaviors3.pauseAi("wander")
        #    self.AIbehaviors3.seek(Vec3(self.character.getX() + 2000*(-self.character.getX() + self.dragonStartPos.getX()), self.character.getY() + 2000*(-self.character.getY() + self.dragonStartPos.getY()), self.character.getZ() + 2000*(-self.character.getZ() + self.dragonStartPos.getZ())), 20000)
            #self.AIbehaviors.seek(self.character3)
        #    self.ghostDragonCollideCount = 100
            #self.AIbehaviors.flee(self.character.getPos(), 1, 10, 10000)
            #self.character.setPos(dragonStartPos)
        #else:
            #do nothing
         #   self.ghostDragonCollideCount = self.ghostDragonCollideCount
            
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


        self.eateve.setPos(self.eve.getX(), self.eve.getY(), self.eve.getZ() + 1)
        self.dragonStartPos = self.character.getPos()
        self.redDragonStartPos = self.character2.getPos()
        return task.cont

    def timedParticle(self, task):
        if task.time < 1.0:
            return task.cont
        
        self.p.disable()
        self.copyPie.removeNode()
        return task.done

def ghostDragonCmp(x,y):
    if x.getIntoNode().getName() == "terrain" and y.getIntoNode().getName() != "terrain":
        return -1
    elif y.getIntoNode().getName() == "terrain" and x.getIntoNode().getName() != "terrain":
        return 1
    else:
        return cmp(y.getSurfacePoint(render).getZ(), x.getSurfacePoint(render).getZ())

# Instantiate a world and start it running
w = World()
base.run()
