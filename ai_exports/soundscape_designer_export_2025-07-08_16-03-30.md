# Project Export: soundscape_designer
## Export Timestamp: 2025-07-08T16:03:30.367162
---

## Golden Rules
1. Only edit and add features, the only features should stay unless asked to be removed, or may be completely redundant.
2. any scripts over 1000 lines, please write in a new response.
3. multiple scripts together exceeding 2000 lines together need to be separated into smaller responses, (example: these scripts have 2340 lines together I'm going to separate it into 2 messages that way i dont lose formatting and dont accidentally remove any features)
4. Do not remove any code that is unrelated to the fix, only remove code if it is being substituted or is not needed anymore.

---

## Project Files

Here is the project context you need to work with.
## File Tree
```
/soundscape_designer
 ├── app.py
 ├── config.py
 ├── core
 │   ├── event_bus.py
 │   └── state.py
 ├── main.py
 ├── scene
 │   ├── camera_controller.py
 │   ├── entities.py
 │   ├── entity_factory.py
 │   ├── gizmo.py
 │   └── scene_manager.py
 ├── services
 │   ├── audio_service.py
 │   └── project_service.py
 └── ui
     ├── editor_panel.py
     └── panels
         ├── base_panel.py
         ├── inspector_panel.py
         ├── library_panel.py
         ├── settings_panel.py
         └── toolbar.py

```
## File Contents
### File: `/core/event_bus.py`

```python
from collections import defaultdict
import config

class EventBus:
    """A simple publish-subscribe event bus for decoupled communication."""

    def __init__(self):
        self._subscribers = defaultdict(list)
        print("EventBus initialized.")

    def subscribe(self, event_type: config.Event, handler):
        """Register a handler function to be called when an event is published."""
        self._subscribers[event_type].append(handler)
        # print(f"Handler {handler.__name__} subscribed to {event_type.name}")

    def publish(self, event_type: config.Event, *args, **kwargs):
        """Call all registered handlers for a given event type."""
        # print(f"Publishing event: {event_type.name} with args:{args} kwargs:{kwargs}")
        for handler in self._subscribers[event_type]:
            handler(*args, **kwargs)
```

### File: `/core/state.py`

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from ursina import Vec3
import config

# Note: We use basic types here (lists instead of Vec3) to make serialization
# with formats like JSON straightforward.

@dataclass
class ToolState:
    """Holds the state of editor tools."""
    active_tool: config.Tool = config.Tool.SELECT

@dataclass
class AudioState:
    """Holds the state of all global audio parameters."""
    master_volume: float = config.DEFAULT_AUDIO_PARAMS['master_volume']
    drizzle_intensity: float = config.DEFAULT_AUDIO_PARAMS['drizzle_intensity']
    wind_intensity: float = config.DEFAULT_AUDIO_PARAMS['wind_intensity']
    window_openness: float = config.DEFAULT_AUDIO_PARAMS['window_openness']
    headphone_mode: bool = False

@dataclass
class EntityData:
    """A data-only representation of an object in the scene."""
    uid: int
    name: str
    entity_type: str  # e.g., 'Speaker', 'Room'
    position: List[float] = field(default_factory=lambda: [0, 0, 0])
    rotation: List[float] = field(default_factory=lambda: [0, 0, 0])
    scale: List[float] = field(default_factory=lambda: [1, 1, 1])
    sound_material: str = 'none'

@dataclass
class SceneState:
    """Holds the state of all entities in the 3D scene."""
    entities: Dict[int, EntityData] = field(default_factory=dict)
    selected_entity_uid: Optional[int] = None
    next_uid: int = 0

@dataclass
class AppState:
    """The root state object, containing all other state branches."""
    project_name: str = "MySoundscape"
    tools: ToolState = field(default_factory=ToolState)
    audio: AudioState = field(default_factory=AudioState)
    scene: SceneState = field(default_factory=SceneState)
```

### File: `/scene/camera_controller.py`

```python
from ursina import *
import config

class CameraController:
    """Manages orbiting, panning, and zooming of the editor camera."""
    def __init__(self):
        print("CameraController initialized.")
        self.camera = camera
        self.camera_pivot = Entity(name="_camera_pivot")
        self.camera.parent = self.camera_pivot
        self.camera.position = config.INITIAL_CAMERA_POSITION
        self.camera.look_at(self.camera_pivot)

    def focus(self, target_pos: Vec3):
        """Smoothly moves the camera pivot to a target position."""
        self.camera_pivot.animate_position(target_pos, duration=0.2, curve=curve.out_quad)

    def input(self, key):
        """Handles camera zoom and focus hotkeys."""
        if key == 'scroll up':
            target_z = self.camera.z + config.CAMERA_ZOOM_SPEED * (abs(self.camera.z) * 0.2)
            self.camera.z = clamp(target_z, -100, -5)
        if key == 'scroll down':
            target_z = self.camera.z - config.CAMERA_ZOOM_SPEED * (abs(self.camera.z) * 0.2)
            self.camera.z = clamp(target_z, -100, -5)

        # Note: The 'f' key to focus will be handled by the SceneManager,
        # which knows what is selected.

    def update(self):
        """Handles continuous mouse-drag logic for orbiting and panning."""
        if held_keys['right mouse']:
            self.camera_pivot.rotation_y -= mouse.velocity[0] * config.CAMERA_ORBIT_SPEED
            self.camera_pivot.rotation_x += mouse.velocity[1] * config.CAMERA_ORBIT_SPEED
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -89, 89)

        if held_keys['middle mouse']:
            pan_speed = abs(self.camera.z) / 30
            self.camera_pivot.position -= self.camera.right * mouse.velocity[0] * config.CAMERA_PAN_SPEED * pan_speed
            self.camera_pivot.position -= self.camera.up * mouse.velocity[1] * config.CAMERA_PAN_SPEED * pan_speed
```

### File: `/scene/entities.py`

```python
from ursina import *
import config

# =============================================================================
# BASE ENTITY CLASS
# =============================================================================

class SceneEntity(Entity):
    """
    Base class for any selectable object in the 3D scene.
    It holds a unique ID (uid) to link it to its corresponding data
    in the AppState.
    """
    def __init__(self, uid: int, **kwargs):
        super().__init__(**kwargs)
        self.uid = uid
        self.collider = 'box'
        self.original_color = self.color
        self.name = f"{type(self).__name__}_{uid}"

    def select(self):
        """Visual feedback for selection."""
        self.color = color.yellow.tint(.2)

    def deselect(self):
        """Remove visual feedback for selection."""
        self.color = self.original_color

# =============================================================================
# SPECIFIC ENTITY IMPLEMENTATIONS
# =============================================================================

class Speaker(SceneEntity):
    """Visual representation of a sound source."""
    def __init__(self, uid: int, **kwargs):
        super().__init__(
            uid=uid,
            model='diamond',
            color=color.orange,
            scale=0.7,
            **kwargs
        )

class SceneWindow(SceneEntity):
    """Visual representation of a window, which affects sound material."""
    def __init__(self, uid: int, sound_material: str, **kwargs):
        super().__init__(uid=uid, model='quad', scale=(2, 2.5), **kwargs)
        self.set_material(sound_material)

    def set_material(self, material_name: str):
        """Updates the window's appearance based on its material type."""
        if material_name == 'glass':
            self.color = color.rgba(173, 216, 230, 150)
        else: # Fallback
            self.color = color.white
        self.original_color = self.color

class ModifierShape(SceneEntity):
    """Visual representation of a sound-modifying zone (e.g., tarp, tin roof)."""
    def __init__(self, uid: int, sound_material: str, **kwargs):
        # A small vertical offset to prevent z-fighting with the grid
        super().__init__(uid=uid, model='cube', scale=(3, 0.1, 3), y=0.05, **kwargs)
        
        if sound_material == 'tarp':
            self.color = color.rgba(0, 100, 200, 150)
        elif sound_material == 'tin':
            self.color = color.rgba(150, 150, 150, 200)
        
        self.original_color = self.color

# =============================================================================
# ROOM (SPECIAL CASE)
# =============================================================================

class ResizeHandle(Draggable):
    """A draggable handle for resizing the Room."""
    def __init__(self, **kwargs):
        super().__init__(
            model='sphere', scale=.3, plane_direction=(0, 1, 0),
            color=kwargs.pop('color', color.white),
            **kwargs
        )
        self.highlight_color = color.azure

class Room(SceneEntity):
    """
    The main room container. It's a special SceneEntity that is not
    moved by the gizmo but is resized via its own handles.
    """
    def __init__(self, uid: int, **kwargs):
        super().__init__(uid=uid, **kwargs)
        
        # The visible walls of the room
        self.walls = Entity(
            parent=self,
            model='cube',
            texture='white_cube',
            color=color.rgba(200, 200, 200, 20),
        )
        # Use the walls as the main collider for selection
        self.collider = self.walls
        self.original_color = self.walls.color

        self.handles = {
            'x': ResizeHandle(parent=self, lock=(0, 1, 1), color=config.GIZMO_COLORS['x']),
            'y': ResizeHandle(parent=self, lock=(1, 0, 1), color=config.GIZMO_COLORS['y']),
            'z': ResizeHandle(parent=self, lock=(1, 1, 0), color=config.GIZMO_COLORS['z']),
        }
        self.update_handle_positions()
        
    def update_handle_positions(self):
        s = self.walls.scale
        self.handles['x'].world_position = (self.world_x + s.x / 2, self.y, self.z)
        self.handles['y'].world_position = (self.x, self.world_y + s.y / 2, self.z)
        self.handles['z'].world_position = (self.x, self.y, self.world_z + s.z / 2)

    def select(self):
        self.walls.color = color.yellow.tint(.2)
        for h in self.handles.values(): h.enable()

    def deselect(self):
        self.walls.color = self.original_color
        for h in self.handles.values(): h.disable()
```

### File: `/scene/entity_factory.py`

```python
from ursina import Vec3
from core.state import AppState, EntityData

class EntityFactory:
    """Creates EntityData instances for new objects in the scene."""

    def __init__(self):
        print("EntityFactory initialized.")

    def create_entity(self, app_state: AppState, entity_type: str, **kwargs) -> EntityData:
        """
        Creates the data for a new entity, assigns it a UID, and adds it to the state.

        Args:
            app_state: The main application state object.
            entity_type: The type of entity to create (e.g., 'speaker', 'room').
            **kwargs: Additional properties like position or sound_material.

        Returns:
            The created EntityData object.
        """
        uid = app_state.scene.next_uid
        app_state.scene.next_uid += 1

        position = kwargs.get('position', [0, 0, 0])
        sound_material = kwargs.get('sound_material', 'none')
        name = f"{entity_type.capitalize()}_{uid}"

        if entity_type == 'room':
            data = EntityData(
                uid=uid,
                name=name,
                entity_type='Room',
                scale=list(kwargs.get('scale', [10, 4, 10]))
            )
        else: # Default for speakers, windows, modifiers
            data = EntityData(
                uid=uid,
                name=name,
                entity_type=entity_type.capitalize(),
                position=list(position),
                sound_material=sound_material
            )
        
        app_state.scene.entities[uid] = data
        print(f"Created EntityData for '{name}' (UID: {uid})")
        return data
```

### File: `/scene/gizmo.py`

```python
from ursina import *
from ursina.models.procedural.cone import Cone
from ursina.models.procedural.circle import Circle

import config
from core.event_bus import EventBus
from core.state import AppState

class GizmoHandle(Draggable):
    """A single draggable handle of the Gizmo."""
    def __init__(self, gizmo_parent, tool_type, axis, color, **kwargs):
        super().__init__(parent=gizmo_parent, always_on_top=True, render_queue=1, color=color, **kwargs)
        self.gizmo_parent = gizmo_parent
        self.tool_type = tool_type
        self.axis = axis
        self.lock = Vec3(1, 1, 1) - abs(self.axis)
        self.highlight_color = config.GIZMO_HOVER_COLOR

    def drag(self):
        """Stores the initial state of the target when dragging starts."""
        self.gizmo_parent.on_drag_start()

    def drop(self):
        """Called when the drag is released."""
        self.gizmo_parent.on_drag_end()

    def on_drag(self):
        self.gizmo_parent.update_target_transform(self.tool_type, self.axis)

class Gizmo(Entity):
    """The main transform gizmo, which shows handles for move, rotate, and scale."""
    def __init__(self, app_state: AppState, event_bus: EventBus):
        super().__init__(enabled=False)
        self.app_state = app_state
        self.event_bus = event_bus
        self.target = None
        self.start_drag_pos = Vec3(0,0,0)
        self.start_drag_rot = Vec3(0,0,0)
        self.start_drag_scale = Vec3(1,1,1)

        self.handles = {
            config.Tool.MOVE: self._create_move_handles(),
            config.Tool.ROTATE: self._create_rotate_handles(),
            config.Tool.SCALE: self._create_scale_handles()
        }
        self.set_tool(self.app_state.tools.active_tool)

        # Listen for events to automatically update
        event_bus.subscribe(config.Event.TOOL_CHANGED, self.set_tool)
        event_bus.subscribe(config.Event.SELECTION_CHANGED, self.set_target)

    def on_drag_start(self):
        if self.target:
            self.start_drag_pos = self.target.world_position
            self.start_drag_rot = self.target.world_rotation
            self.start_drag_scale = self.target.scale

    def on_drag_end(self):
        # The SceneManager will see the ENTITY_UPDATED event and could apply snapping
        pass 

    def update_target_transform(self, tool, axis):
        if not self.target: return

        # Universal drag amount
        drag_amount = (mouse.velocity[0] - mouse.velocity[1]) * 15

        if tool == config.Tool.MOVE:
            self.target.world_position = self.start_drag_pos + (axis * drag_amount * 0.1)
        elif tool == config.Tool.ROTATE:
            self.target.world_rotation = self.start_drag_rot - (axis * drag_amount * 5)
        elif tool == config.Tool.SCALE:
            if axis == Vec3(1, 1, 1): # Uniform scale
                self.target.scale = self.start_drag_scale + (drag_amount * 0.1)
            else: # Axis-specific scale
                new_scale = self.start_drag_scale + (axis * drag_amount * 0.1)
                self.target.scale = new_scale

        # Publish an event with the new transform data
        self.event_bus.publish(
            config.Event.ENTITY_UPDATED,
            uid=self.target.uid,
            position=list(self.target.world_position),
            rotation=list(self.target.world_rotation),
            scale=list(self.target.scale)
        )

    def set_tool(self, tool: config.Tool):
        for t, handle_list in self.handles.items():
            for handle in handle_list:
                handle.enabled = (t == tool)
        
        self.visible = self.target is not None and tool != config.Tool.SELECT

    def set_target(self, scene_entity: Optional[Entity]):
        self.target = scene_entity
        self.enabled = bool(scene_entity) and not isinstance(scene_entity, (str, type(None), list, Room))
        self.visible = self.enabled and self.app_state.tools.active_tool != config.Tool.SELECT
        if self.target:
            self.update_position()
            
    def update_position(self):
        if self.target:
            self.position = self.target.world_position
            if self.app_state.tools.active_tool == config.Tool.ROTATE:
                 self.rotation = self.target.world_rotation
            else:
                 self.rotation = Vec3.zero()
    
    def update(self):
        if self.target and self.visible:
            self.update_position()

    # --- Handle Creation Methods (for clarity) ---
    def _create_move_handles(self):
        return [
            GizmoHandle(self, config.Tool.MOVE, Vec3(1, 0, 0), config.GIZMO_COLORS['x'], model=Cone(resolution=8), scale=.5, rotation=(0, 0, -90), position=(.75, 0, 0)),
            GizmoHandle(self, config.Tool.MOVE, Vec3(0, 1, 0), config.GIZMO_COLORS['y'], model=Cone(resolution=8), scale=.5, position=(0, .75, 0)),
            GizmoHandle(self, config.Tool.MOVE, Vec3(0, 0, 1), config.GIZMO_COLORS['z'], model=Cone(resolution=8), scale=.5, rotation=(90, 0, 0), position=(0, 0, .75))
        ]
    def _create_rotate_handles(self):
        return [
            GizmoHandle(self, config.Tool.ROTATE, Vec3(1, 0, 0), config.GIZMO_COLORS['x'], model=Circle(24, radius=0.6), scale=2, rotation=(0, 90, 90)),
            GizmoHandle(self, config.Tool.ROTATE, Vec3(0, 1, 0), config.GIZMO_COLORS['y'], model=Circle(24, radius=0.6), scale=2, rotation=(90, 0, 0)),
            GizmoHandle(self, config.Tool.ROTATE, Vec3(0, 0, 1), config.GIZMO_COLORS['z'], model=Circle(24, radius=0.6), scale=2)
        ]
    def _create_scale_handles(self):
         return [
            GizmoHandle(self, config.Tool.SCALE, Vec3(1, 0, 0), config.GIZMO_COLORS['x'], model='cube', scale=0.2, position=(0.8, 0, 0)),
            GizmoHandle(self, config.Tool.SCALE, Vec3(0, 1, 0), config.GIZMO_COLORS['y'], model='cube', scale=0.2, position=(0, 0.8, 0)),
            GizmoHandle(self, config.Tool.SCALE, Vec3(0, 0, 1), config.GIZMO_COLORS['z'], model='cube', scale=0.2, position=(0, 0, 0.8)),
            GizmoHandle(self, config.Tool.SCALE, Vec3(1, 1, 1), color.light_gray, model='cube', scale=0.25)
        ]
```

### File: `/scene/scene_manager.py`

```python
from ursina import *
from typing import Dict, Optional, List

import config
from core.state import AppState, EntityData
from core.event_bus import EventBus
from .entities import SceneEntity, Room, Speaker, SceneWindow, ModifierShape
from .entity_factory import EntityFactory
from .gizmo import Gizmo

class SceneManager:
    def __init__(self, app_state: AppState, event_bus: EventBus, entity_factory: EntityFactory):
        print("SceneManager initialized.")
        self.app_state = app_state
        self.event_bus = event_bus
        self.entity_factory = entity_factory
        
        self.scene_entities: Dict[int, SceneEntity] = {} # Map from UID to Ursina entity

        # Visual elements
        self.gizmo = Gizmo(app_state, event_bus)
        self.listener_avatar = self._create_listener_avatar()
        
        # Subscribe to events that require scene changes
        self.event_bus.subscribe(config.Event.PROJECT_LOADED, self.rebuild_scene_from_state)
        self.event_bus.subscribe(config.Event.ADD_ENTITY_REQUEST, self.add_entity)
        self.event_bus.subscribe(config.Event.DELETE_SELECTED_REQUEST, self.delete_selected)
        self.event_bus.subscribe(config.Event.ENTITY_UPDATED, self.on_entity_data_updated)

    def load_initial_scene(self):
        """Sets up the initial environment and the room."""
        AmbientLight(color=color.rgba(100, 100, 100, 255))
        DirectionalLight(color=color.rgba(150, 150, 150, 255), direction=(1, -1, -1))
        Entity(model=Grid(100, 100), rotation_x=90, color=color.dark_gray.tint(0.2))

        # Create the initial room data and then sync the scene
        self.entity_factory.create_entity(self.app_state, 'room', scale=list(config.INITIAL_ROOM_SCALE))
        self.rebuild_scene_from_state()

    def rebuild_scene_from_state(self):
        """Clears the current scene and recreates all entities from the AppState."""
        print("Rebuilding scene from state...")
        for entity in self.scene_entities.values():
            destroy(entity)
        self.scene_entities.clear()
        
        # Select nothing first
        self._set_selection(None)
        
        for uid, entity_data in self.app_state.scene.entities.items():
            self._create_scene_entity_for_data(entity_data)

    def on_entity_data_updated(self, uid: int, **kwargs):
        """
        Handler for when an entity's data in AppState has changed.
        This updates the transform of the corresponding Ursina entity.
        """
        if uid in self.scene_entities:
            entity_3d = self.scene_entities[uid]
            data = self.app_state.scene.entities[uid]

            # Update state with the new values
            for key, value in kwargs.items():
                if hasattr(data, key):
                    setattr(data, key, value)
            
            # Reflect state in the 3D world
            entity_3d.position = Vec3(data.position)
            entity_3d.rotation = Vec3(data.rotation)
            entity_3d.scale = Vec3(data.scale)

    def _create_scene_entity_for_data(self, data: EntityData):
        """Instantiates the correct Ursina entity for a given EntityData object."""
        if data.uid in self.scene_entities: return # Already exists
        
        entity_type = data.entity_type
        params = {
            'uid': data.uid,
            'position': Vec3(data.position),
            'rotation': Vec3(data.rotation),
            'scale': Vec3(data.scale)
        }

        new_entity = None
        if entity_type == 'Room':
            new_entity = Room(**params)
            new_entity.walls.scale = Vec3(data.scale) # Room scale is special
            new_entity.update_handle_positions()
        elif entity_type == 'Speaker':
            new_entity = Speaker(**params)
        elif entity_type == 'Window':
            new_entity = SceneWindow(sound_material=data.sound_material, **params)
        elif entity_type == 'Modifier':
             new_entity = ModifierShape(sound_material=data.sound_material, **params)

        if new_entity:
            self.scene_entities[data.uid] = new_entity
        return new_entity
    
    def add_entity(self, entity_type: str, **kwargs):
        """Handles a request to create a new entity."""
        spawn_pos = camera.world_position + camera.forward * 10
        kwargs['position'] = list(spawn_pos)

        data = self.entity_factory.create_entity(self.app_state, entity_type, **kwargs)
        new_3d_entity = self._create_scene_entity_for_data(data)
        self._set_selection(new_3d_entity)
        
    def delete_selected(self):
        """Handles a request to delete the currently selected entity."""
        uid = self.app_state.scene.selected_entity_uid
        if uid is not None and uid in self.scene_entities:
            entity_data = self.app_state.scene.entities[uid]
            if entity_data.entity_type != 'Room': # Prevent room deletion
                print(f"Deleting entity UID: {uid}")
                # 1. Deselect first
                self._set_selection(None)
                # 2. Remove from 3D scene
                destroy(self.scene_entities.pop(uid))
                # 3. Remove from state
                del self.app_state.scene.entities[uid]
    
    def _set_selection(self, target_entity: Optional[SceneEntity]):
        """Internal method to handle the logic of changing selection."""
        # Deselect current
        current_uid = self.app_state.scene.selected_entity_uid
        if current_uid is not None and current_uid in self.scene_entities:
            self.scene_entities[current_uid].deselect()

        new_uid = target_entity.uid if target_entity else None
        
        # Update state
        self.app_state.scene.selected_entity_uid = new_uid
        
        # Select new
        if new_uid is not None:
            target_entity.select()
        
        # Notify everyone else
        self.event_bus.publish(config.Event.SELECTION_CHANGED, target_entity)

    def input(self, key):
        """Handles input related to scene management and selection."""
        # --- Tool Hotkeys ---
        tool_map = {'q': config.Tool.SELECT, 'w': config.Tool.MOVE, 'e': config.Tool.ROTATE, 'r': config.Tool.SCALE}
        if key in tool_map and self.app_state.tools.active_tool != tool_map[key]:
            self.app_state.tools.active_tool = tool_map[key]
            self.event_bus.publish(config.Event.TOOL_CHANGED, self.app_state.tools.active_tool)

        # --- Deletion ---
        if key == 'delete':
            self.event_bus.publish(config.Event.DELETE_SELECTED_REQUEST)

        # --- Selection ---
        if key == 'left mouse down' and self.app_state.tools.active_tool == config.Tool.SELECT:
            target = None
            if mouse.hovered_entity and isinstance(mouse.hovered_entity, (SceneEntity, ResizeHandle)):
                # If we click a room handle, we select the room itself
                if isinstance(mouse.hovered_entity, ResizeHandle):
                    target = mouse.hovered_entity.parent
                else:
                    target = mouse.hovered_entity
            self._set_selection(target)

    def update(self):
        """Called every frame to update continuous elements like the listener avatar."""
        self.listener_avatar.position = camera.world_position
        self.listener_avatar.rotation = camera.world_rotation

    def get_sound_sources_for_audio_engine(self) -> List[dict]:
        """Prepares a list of data dicts for the audio engine."""
        sources = []
        for uid, data in self.app_state.scene.entities.items():
            if data.entity_type in ['Speaker', 'Window', 'Modifier']:
                sources.append(data.__dict__) # Send a copy
        return sources

    def _create_listener_avatar(self):
        """Creates the 'headphone' model that shows the listener's position."""
        avatar = Entity(model='sphere', scale=0.15, color=color.black, always_on_top=True)
        Entity(parent=avatar, model='sphere', x=-0.1, scale=(0.1, 1.2, 1.2), color=color.dark_gray)
        Entity(parent=avatar, model='sphere', x=0.1, scale=(0.1, 1.2, 1.2), color=color.dark_gray)
        return avatar
```

### File: `/services/audio_service.py`

```python
import numpy as np
import sounddevice as sd
import soundfile as sf
import os
import random
import threading
import sys
import traceback
from ursina import Vec3

import config
from core.state import AppState, EntityData

class AudioService:
    def __init__(self, app_state: AppState):
        print("Initializing AudioService...")
        self.app_state = app_state
        self.samplerate = config.AUDIO_SAMPLE_RATE
        self.blocksize = config.AUDIO_BLOCK_SIZE
        self.channels = 2

        # --- Local copies for the audio thread ---
        self.sources_to_process = []
        self.listener_position = np.array([0, 0, 0])
        self.listener_right_vec = np.array([1, 0, 0])
        self.lock = threading.Lock()

        # --- Sound-specific Playback State ---
        self.wind_playback_pos = 0

        # --- Binaural Audio Constants ---
        self.max_itd_samples = int(0.0007 * self.samplerate)

        # --- Multi-Speaker Downmix Constants ---
        speaker_positions = np.array(
            [[0, 0, 1], [-1, 0, 1], [1, 0, 1], [-1, 0, 0], [1, 0, 0], [-1, 0, -1], [1, 0, -1], [0, 1, 0]])
        self.speaker_vectors = speaker_positions / np.linalg.norm(speaker_positions, axis=1)[:, np.newaxis]
        self.downmix_matrix = np.array(
            [[0.7, 0.7], [1.0, 0.1], [0.1, 1.0], [1.0, 0.3], [0.3, 1.0], [0.8, 0.5], [0.5, 0.8], [0.6, 0.6]])

        self.samples = self._load_samples('audio/sounds/')
        self.stream = self._start_stream()

    def update(self, sources: list, listener_pos: Vec3, listener_right_vec: Vec3):
        """Thread-safe method called by the main app to update audio locations."""
        with self.lock:
            self.sources_to_process = sources
            self.listener_position = np.array(listener_pos)
            self.listener_right_vec = np.array(listener_right_vec)
    
    def _start_stream(self):
        try:
            stream = sd.OutputStream(
                samplerate=self.samplerate, channels=self.channels,
                callback=self._audio_callback, dtype='float32', blocksize=self.blocksize
            )
            stream.start()
            print("Audio stream started successfully.")
            return stream
        except Exception as e:
            print(f"FATAL: COULD NOT START AUDIO STREAM. Error: {e}", file=sys.stderr)
            return None

    def _load_samples(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Warning: Audio directory not found at '{path}'. Created it.")
        
        samples = {'drizzle': [], 'glass': [], 'tin': [], 'tarp': [], 'wind': []}
        print("Loading audio samples...")
        for fname in os.listdir(path):
            if fname.lower().endswith('.wav'):
                category = next((cat for cat in samples.keys() if cat in fname.lower()), 'drizzle')
                try:
                    filepath = os.path.join(path, fname)
                    data, _ = sf.read(filepath, dtype='float32')
                    mono_data = data if data.ndim == 1 else data[:, 0]
                    samples[category].append(mono_data)
                    print(f"  - Loaded '{fname}' -> '{category}'")
                except Exception as e:
                    print(f"  - Could not load sample {fname}: {e}")
        return samples

    def _render_binaural_grain(self, buffer, grain, source_pos):
        sound_vec = source_pos - self.listener_position
        dist = np.linalg.norm(sound_vec)
        if dist < 0.1: return

        sound_vec_norm = sound_vec / dist
        right_dot = np.dot(sound_vec_norm, self.listener_right_vec)

        gain_l = np.sqrt(0.5 * (1 - right_dot))
        gain_r = np.sqrt(0.5 * (1 + right_dot))
        time_delay_samples = int(self.max_itd_samples * right_dot)

        start_pos = random.randint(self.max_itd_samples, len(buffer) - len(grain) - self.max_itd_samples)
        attenuation = 1 / (1 + dist * 0.5)

        if time_delay_samples >= 0:
            buffer[start_pos + time_delay_samples: start_pos + time_delay_samples + len(grain), 1] += grain * gain_r * attenuation
            buffer[start_pos: start_pos + len(grain), 0] += grain * gain_l * attenuation
        else:
            buffer[start_pos: start_pos + len(grain), 1] += grain * gain_r * attenuation
            buffer[start_pos - time_delay_samples: start_pos - time_delay_samples + len(grain), 0] += grain * gain_l * attenuation

    def _render_speaker_grain(self, buffer, grain, source_pos):
        sound_vec = source_pos - self.listener_position
        dist = np.linalg.norm(sound_vec)
        if dist < 0.1: return
        sound_vec /= dist

        gains_8_channel = np.maximum(0, np.dot(self.speaker_vectors, sound_vec)) ** 2
        stereo_gain = np.dot(gains_8_channel, self.downmix_matrix)
        attenuation = 1 / (1 + dist * 0.5)

        start_pos = random.randint(0, len(buffer) - len(grain) - 1)
        for i in range(self.channels):
            buffer[start_pos: start_pos + len(grain), i] += grain * stereo_gain[i] * attenuation

    def _audio_callback(self, outdata, frames, time, status):
        try:
            buffer = np.zeros((frames, self.channels), dtype='float32')
            
            # Lock to get a consistent copy of data from the main thread
            with self.lock:
                sources = list(self.sources_to_process)
            
            # Read global parameters directly from the shared AppState
            params = self.app_state.audio
            render_func = self._render_binaural_grain if params.headphone_mode else self._render_speaker_grain

            # --- Ambient Sounds ---
            wind_intensity = params.wind_intensity / 100.0
            if self.samples.get('wind') and wind_intensity > 0:
                wind_sample = self.samples['wind'][0]
                sample_len = len(wind_sample)
                indices = (self.wind_playback_pos + np.arange(frames)) % sample_len
                buffer += wind_sample[indices, np.newaxis] * wind_intensity
                self.wind_playback_pos = (self.wind_playback_pos + frames) % sample_len

            # --- 3D Localized Sounds ---
            drizzle = params.drizzle_intensity / 100.0
            for source in sources:
                material_sounds = self.samples.get(source['sound_material'], [])
                if material_sounds and random.random() < drizzle * 0.05:
                    grain = random.choice(material_sounds)
                    if len(grain) + self.max_itd_samples < frames:
                        render_func(buffer, grain, np.array(source['position']))
            
            # --- Global Filters ---
            window_openness = params.window_openness / 100.0
            if window_openness < 1.0:
                buffer *= window_openness
            
            master_volume = params.master_volume / 100.0
            outdata[:] = np.clip(buffer * master_volume, -1.0, 1.0)

        except Exception as e:
            print(f"AUDIO THREAD CRASH: {e}", file=sys.stderr)
            traceback.print_exc()
            outdata.fill(0)

    def close(self):
        if self.stream:
            print("Stopping AudioService...")
            self.stream.stop()
            self.stream.close()
            print("AudioService stopped.")
```

### File: `/services/project_service.py`

```python

```

### File: `/ui/panels/base_panel.py`

```python
from ursina import *
import config

# --- The New GridLayout Class ---
# This class is the heart of the new UI. It is simple, robust, and predictable.
class GridLayout(Entity):
    def __init__(self, cols=1, rows=1, spacing=(.01, .01), **kwargs):
        super().__init__(**kwargs)
        self.cols = cols
        self.rows = rows
        self.spacing = spacing
        self.items = []

    def add_item(self, item):
        if not item: return None
        item.parent = self
        self.items.append(item)
        self.reorganize()
        return item

    def reorganize(self):
        cell_w = 1 / self.cols
        cell_h = 1 / self.rows

        for i, item in enumerate(self.items):
            item.x = (i % self.cols * cell_w) - .5 + (cell_w / 2)
            item.y = .5 - (cell_h / 2) - (i // self.cols * cell_h)
            item.scale_x = cell_w - self.spacing[0]
            item.scale_y = cell_h - self.spacing[1]
            if hasattr(item, 'text_origin'):
                item.text_origin = (0,0)

    def clear(self):
        [destroy(item) for item in self.items]
        self.items.clear()


# --- The BasePanel, now much simpler ---
class BasePanel(Entity):
    def __init__(self, title, position, **kwargs):
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=config.PANEL_SCALE,
            position=position,
            color=config.UI_THEME['panel_background'],
            **kwargs
        )
        Text(parent=self, text=title, scale=2, origin=(0, -0.5), y=0.48, color=config.UI_THEME['title_color'])
        Entity(parent=self, model='quad', scale=(0.95, 0.005), y=0.44, color=config.UI_THEME['seperator_color'])
        self.content_parent = Entity(parent=self, scale=(0.95, 0.85), y=-0.05)
```

### File: `/ui/panels/inspector_panel.py`

```python

```

### File: `/ui/panels/library_panel.py`

```python

```

### File: `/ui/panels/settings_panel.py`

```python

```

### File: `/ui/panels/toolbar.py`

```python

```

### File: `/ui/editor_panel.py`

```python
from ursina import *
from .base_panel import BasePanel, GridLayout
import config


class EditorPanel(BasePanel):
    def __init__(self, scene_manager, editor_state, selection_manager, **kwargs):
        super().__init__(title='Editor', position=config.RIGHT_PANEL_POSITION, **kwargs)
        self.scene_manager = scene_manager
        self.editor_state = editor_state
        self.selection_manager = selection_manager

        # --- New Manual Layout with a cursor ---
        self.y_cursor = 0.5

        self._create_tool_section()
        self._create_object_creation_section()
        self._create_inspector_section()

        self.selection_manager.on_selection_changed = self.update_inspector
        self.update_inspector(None)

    def _add_header(self, text):
        header_height = 0.06
        Entity(parent=self.content_parent, model='quad', scale=(1, header_height),
               color=config.UI_THEME['header_background'], origin=(0, .5), y=self.y_cursor)
        Text(parent=self.content_parent, text=text, origin=(-.5, .5), x=-0.48, y=self.y_cursor, scale=1.8)
        self.y_cursor -= header_height + 0.01

    def _create_tool_section(self):
        self._add_header("Tools")
        grid_height = 0.08
        tool_grid = GridLayout(parent=self.content_parent, cols=4, rows=1,
                               scale_y=grid_height, origin=(0, .5), y=self.y_cursor)

        tools = ['select', 'move', 'rotate', 'scale']
        for tool in tools:
            btn = tool_grid.add_item(Button(text=tool))
            btn.on_click = lambda t=tool: self.editor_state.set_active_tool(t)

        self.y_cursor -= grid_height + 0.02

    def _create_object_creation_section(self):
        self._add_header("Create")
        grid_height = 0.38
        create_grid = GridLayout(parent=self.content_parent, cols=1, rows=4,
                                 scale_y=grid_height, origin=(0, .5), y=self.y_cursor, spacing=(0, 0.02))

        def _add_button(text, on_click):
            btn = create_grid.add_item(Button(text=text))
            btn.text_origin = (-.45, 0)
            btn.on_click = on_click

        _add_button('Add Speaker', Func(self.scene_manager.add_object, 'speaker'))
        _add_button('Add Window', Func(self.scene_manager.add_object, 'window'))
        _add_button('Add Tarp Zone', Func(self.scene_manager.add_object, 'modifier', 'tarp'))
        _add_button('Add Tin Zone', Func(self.scene_manager.add_object, 'modifier', 'tin'))

        self.y_cursor -= grid_height + 0.02

    def _create_inspector_section(self):
        self._add_header("Inspector")
        container_height = abs(-0.5 - self.y_cursor) - 0.01
        self.inspector_grid = GridLayout(parent=self.content_parent, cols=1, rows=2,
                                         scale_y=container_height, origin=(0, .5), y=self.y_cursor, spacing=(0, 0.1))

    def update_inspector(self, entity):
        self.inspector_grid.clear()

        if entity:
            self.inspector_grid.add_item(Text(text=f"Selected: {entity.name}", origin=(0, 0)))
            from scene.objects import Room
            if isinstance(entity, Room):
                btn = self.inspector_grid.add_item(Button(text='Toggle Symmetry'))
                btn.on_click = self.toggle_room_symmetry
            else:
                btn = self.inspector_grid.add_item(
                    Button(text='Delete Selected', color=color.red.tint(-.2), highlight_color=color.red))
                btn.on_click = self.scene_manager.delete_selected_object
                btn.tooltip = Tooltip("Deletes the selected object (hotkey: DEL)")
        else:
            self.inspector_grid.add_item(Text(text="No object selected.", origin=(0, 0)))

    def toggle_room_symmetry(self):
        entity = self.editor_state.selected_entity
        from scene.objects import Room
        if isinstance(entity, Room):
            entity.toggle_symmetry()
```

### File: `/app.py`

```python
import sys
import traceback
import atexit
from ursina import Ursina, window, camera, color, Text, held_keys
from ursina.prefabs.draggable import Draggable

import config
from core.state import AppState
from core.event_bus import EventBus
from services.audio_service import AudioService
from services.project_service import ProjectService
from scene.scene_manager import SceneManager
from scene.camera_controller import CameraController
from scene.entity_factory import EntityFactory
from ui.ui_manager import UIManager

class SoundscapeApp:
    def __init__(self, **kwargs):
        # Initialize the Ursina engine instance
        self.ursina_app = Ursina(
            title=config.APP_TITLE,
            size=config.WINDOW_SIZE,
            vsync=True,
            **kwargs
        )
        window.color = color.dark_gray

        # --- Core Systems ---
        # The state object holds all application data.
        # The event bus allows systems to communicate without direct dependencies.
        self.state = AppState()
        self.event_bus = EventBus()

        # --- Services (High-level, often background tasks) ---
        self.audio_service = AudioService(self.state)
        self.project_service = ProjectService(self.state, self.event_bus)

        # --- Managers (Handle real-time scene and UI) ---
        self.entity_factory = EntityFactory()
        self.scene_manager = SceneManager(self.state, self.event_bus, self.entity_factory)
        self.camera_controller = CameraController()
        self.ui_manager = UIManager(self.state, self.event_bus)

        # Connect our update/input methods to the Ursina loop
        self.ursina_app.input = self.input
        self.ursina_app.update = self.update

        # Gracefully shut down the audio engine on exit
        atexit.register(self.audio_service.close)

        # Initialize the first empty scene
        self.scene_manager.load_initial_scene()

    def run(self):
        """Starts the Ursina application loop."""
        self.ursina_app.run()

    def update(self):
        """Main update loop, called every frame by Ursina."""
        self.camera_controller.update()
        self.scene_manager.update()
        self.audio_service.update(
            sources=self.scene_manager.get_sound_sources_for_audio_engine(),
            listener_pos=self.camera_controller.camera.world_position,
            listener_right_vec=self.camera_controller.camera.right
        )

    def input(self, key):
        """Main input loop, called for every key press/release by Ursina."""
        # Let UI elements capture input first
        if mouse.hovered_entity and mouse.hovered_entity.has_ancestor(camera.ui):
            return

        self.camera_controller.input(key)
        self.scene_manager.input(key)
        
        # Failsafe for stuck draggables (gizmo handles, sliders)
        if key == 'left mouse up' and Draggable.item:
            Draggable.item.drop()
            Draggable.item = None


def run_app():
    """Main entry point for the application."""
    try:
        print("--- Soundscape Designer Initializing ---")
        app = SoundscapeApp()
        app.run()
        print("--- Soundscape Designer Exited Gracefully ---")
    except Exception:
        # Robust crash logging
        log_path = "crash_log.txt"
        with open(log_path, 'w') as f:
            f.write("--- Soundscape Designer Crash Log ---\n")
            traceback.print_exc(file=f)
        print(f"FATAL ERROR: A crash log has been saved to {log_path}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_app()
```

### File: `/config.py`

```python
from ursina import color, Vec3, Vec4
from enum import Enum, auto

class Tool(Enum):
    """Defines the available manipulation tools."""
    SELECT = auto()
    MOVE = auto()
    ROTATE = auto()
    SCALE = auto()

class Event(Enum):
    """Defines all possible events that can be published on the event bus."""
    # State change notifications
    TOOL_CHANGED = auto()
    SELECTION_CHANGED = auto()
    PROJECT_LOADED = auto()
    ENTITY_UPDATED = auto() # For transform changes from gizmo

    # User action requests
    ADD_ENTITY_REQUEST = auto()
    DELETE_SELECTED_REQUEST = auto()
    SAVE_PROJECT_REQUEST = auto()
    LOAD_PROJECT_REQUEST = auto()

# --- APPLICATION ---
APP_TITLE = "Soundscape Designer"
EDITOR_VERSION = "2.0.0"
WINDOW_SIZE = (1600, 900)

# --- UI THEME ---
UI_THEME = {
    "panel_background": color.dark_gray.tint(-.5),
    "header_background": color.black.tint(.2),
    "button": color.azure.tint(-.2),
    "button_hover": color.azure,
    "button_active": color.cyan,
    "slider_knob": color.light_gray,
    "text_color": color.light_gray,
    "title_color": color.white,
    "seperator_color": color.gray,
    "delete_button": color.red.tint(-0.2)
}
PANEL_WIDTH = 0.2
PANEL_SCALE = (PANEL_WIDTH, 0.95)

# --- SCENE & CAMERA ---
INITIAL_CAMERA_POSITION = (0, 5, -30)
CAMERA_ORBIT_SPEED = 200
CAMERA_PAN_SPEED = 15
CAMERA_ZOOM_SPEED = 1.5
INITIAL_ROOM_SCALE = Vec3(10, 4, 10)

# --- GIZMO ---
GIZMO_COLORS = {
    "x": color.red, "y": color.green, "z": color.blue
}
GIZMO_HOVER_COLOR = color.white

# --- AUDIO ---
AUDIO_SAMPLE_RATE = 44100
AUDIO_BLOCK_SIZE = 2048
DEFAULT_AUDIO_PARAMS = {
    'master_volume': 70.0,
    'drizzle_intensity': 20.0,
    'wind_intensity': 10.0,
    'window_openness': 100.0
}

# --- PROJECT ---
PROJECT_FILE_EXTENSION = ".sdesigner"
DEFAULT_PROJECT_PATH = "projects"
```

### File: `/main.py`

```python
import runpy
import sys
import traceback

if __name__ == '__main__':
    """
    Executes the main application logic in app.py.
    This two-step startup process helps prevent certain engine-level initialization
    errors and provides a clean entry point.
    """
    try:
        # Use runpy to execute 'app.py' as if it were the main script.
        # This sets its __name__ to '__main__', which is critical.
        runpy.run_path('app.py', run_name='__main__')
    except Exception as e:
        print("--- FATAL LAUNCHER ERROR ---", file=sys.stderr)
        print("The application could not be started. A critical error occurred during initialization.", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
```
