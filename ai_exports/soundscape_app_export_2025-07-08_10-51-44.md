# Project Export: soundscape_app
## Export Timestamp: 2025-07-08T10:51:44.094516
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
/soundscape_app
 ├── __init__.py
 ├── audio
 │   ├── __init__.py
 │   └── engine.py
 ├── boot_loader.py
 ├── main.py
 ├── main_window.py
 ├── scene3d
 │   ├── __init__.py
 │   ├── handles.py
 │   ├── modifiers.py
 │   ├── objects.py
 │   ├── room.py
 │   ├── room_editor.py
 │   └── scene.py
 └── ui
     ├── __init__.py
     ├── main_window.py
     └── settings_panel.py

```
## File Contents
### File: `/audio/__init__.py`

```python

```

### File: `/audio/engine.py`

```python
import numpy as np
import sounddevice as sd
import soundfile as sf
import os
import random
import threading


class AdvancedAudioEngine:
    def __init__(self, samplerate=44100, blocksize=2048):
        self.samplerate, self.blocksize, self.channels = samplerate, blocksize, 2
        self.sources = []  # Will now be a list of source objects, not just positions
        self.listener_position = np.array([0, 0, 0])
        self.lock = threading.Lock()

        # Default parameters
        self.global_params = {
            'master_volume': 0.7,
            'drizzle_intensity': 0.2,
            'window_openness': 1.0
        }

        # 3D Audio positioning setup (8 virtual speakers -> stereo downmix)
        self.speaker_vectors = np.array([
            [0, 0, 1], [-1, 0, 1], [1, 0, 1], [-1, 0, 0], [1, 0, 0], [-1, 0, -1], [1, 0, -1], [0, 1, 0]
        ]) / np.linalg.norm(np.array([
            [0, 0, 1], [-1, 0, 1], [1, 0, 1], [-1, 0, 0], [1, 0, 0], [-1, 0, -1], [1, 0, -1], [0, 1, 0]
        ]), axis=1)[:, np.newaxis]

        self.downmix_matrix = np.array([
            [0.7, 0.7], [1.0, 0.1], [0.1, 1.0], [1.0, 0.3], [0.3, 1.0], [0.8, 0.5], [0.5, 0.8], [0.6, 0.6]
        ])

        self.samples = self._load_samples('audio/sounds/')

        try:
            self.stream = sd.OutputStream(
                samplerate=self.samplerate, blocksize=self.blocksize,
                channels=self.channels, callback=self._audio_callback, dtype='float32'
            )
            self.stream.start()
            print("Audio Engine Initialized (Stereo Downmix Build).")
        except Exception as e:
            print(f"FATAL: COULD NOT START AUDIO STREAM. Error: {e}")
            self.stream = None

    def update_sources(self, sources, listener_position):
        """Accepts a list of source objects from the 3D scene."""
        with self.lock:
            self.sources = sources
            self.listener_position = listener_position

    def update_global_param(self, name, value):
        self.global_params[name] = value / 100.0
        print(f"Audio Param '{name}' set to {self.global_params[name]}")

    def _load_samples(self, path):
        """Loads and categorizes .wav files from the specified directory."""
        if not os.path.exists(path):
            print(f"WARNING: Audio directory not found at '{path}'. Creating it now.")
            os.makedirs(path)

        samples = {'drizzle': [], 'glass': [], 'tin': [], 'tarp': []}
        for filename in os.listdir(path):
            if filename.endswith('.wav'):
                filepath = os.path.join(path, filename)
                category = 'drizzle'  # Default
                if 'glass' in filename:
                    category = 'glass'
                elif 'tin' in filename:
                    category = 'tin'
                elif 'tarp' in filename:
                    category = 'tarp'

                try:
                    data, _ = sf.read(filepath, dtype='float32')
                    if data.ndim > 1: data = data[:, 0]  # Downmix to mono
                    samples[category].append(data)
                    print(f"Loaded sample '{filename}' into category '{category}'")
                except Exception as e:
                    print(f"Could not load sample {filename}: {e}")
        return samples

    def _audio_callback(self, outdata, frames, time, status):
        try:
            buffer = np.zeros((frames, self.channels), dtype='float32')
            with self.lock:
                master_vol = self.global_params['master_volume']

                # --- General Drizzle Sound (ambient) ---
                if self.samples['drizzle'] and random.random() < self.global_params['drizzle_intensity']:
                    grain = random.choice(self.samples['drizzle'])
                    if len(grain) < frames:
                        start_pos = random.randint(0, frames - len(grain) - 1)
                        # Ambient drizzle is less directional
                        buffer[start_pos:start_pos + len(grain), 0] += grain * 0.4
                        buffer[start_pos:start_pos + len(grain), 1] += grain * 0.4

                # --- 3D Localized Sounds from Sources ---
                for source in self.sources:
                    # Determine which sound set to use based on material
                    material_sounds = self.samples.get(source.material, None)
                    if not material_sounds: continue

                    # The chance of a sound playing is tied to drizzle intensity
                    if random.random() < self.global_params['drizzle_intensity'] * 0.6:
                        grain = random.choice(material_sounds)
                        if len(grain) >= frames: continue

                        source_pos = np.array(source.world_position)
                        sound_vec = source_pos - self.listener_position
                        dist = np.linalg.norm(sound_vec)
                        if dist == 0: continue

                        # Simple distance falloff
                        attenuation = 1 / (1 + dist * 0.2)

                        # Directional gain calculation
                        sound_vec /= dist  # Normalize
                        gains_8_channel = np.maximum(0, np.dot(self.speaker_vectors, sound_vec)) ** 2
                        stereo_gain = np.dot(gains_8_channel, self.downmix_matrix)

                        start_pos = random.randint(0, frames - len(grain) - 1)
                        for i in range(self.channels):
                            buffer[start_pos:start_pos + len(grain), i] += (
                                    grain * stereo_gain[i] * attenuation * self.global_params['window_openness']
                            )

            outdata[:] = np.clip(buffer * master_vol, -1.0, 1.0)
        except Exception as e:
            print(f"AUDIO ENGINE CRASH: {e}")
            outdata.fill(0)

    def close(self):
        if self.stream:
            print("Stopping Audio Engine...")
            self.stream.stop()
            self.stream.close()
```

### File: `/scene3d/__init__.py`

```python

```

### File: `/scene3d/handles.py`

```python
from ursina import *

class DragHandle(Draggable):
    def __init__(self, target, axis, **kwargs):
        super().__init__(**kwargs)
        self.target = target  # The entity this handle will modify
        self.axis = axis      # 'x', 'y', or 'z'
        self.plane_direction = Vec3(0,0,0)
        if self.axis == 'x':
            self.plane_direction = (0,1,0) # Drag along y-z plane
        elif self.axis == 'y':
            self.plane_direction = (0,0,1) # Drag along x-z plane
        else: # 'z'
            self.plane_direction = (0,1,0) # Drag along x-y plane

        self.start_pos = Vec3(0,0,0)
        self.start_target_scale = Vec3(0,0,0)

    def drag(self):
        # Lock the drag to the handle's axis
        self.position = self.start_pos

    def drop(self):
        # Update target scale/position based on drag
        delta = self.position - self.start_pos
        if self.axis == 'x':
            self.target.scale_x += delta.x * 2
        elif self.axis == 'y':
            self.target.scale_y += delta.y * 2
        elif self.axis == 'z':
            self.target.scale_z += delta.z * 2

        # After scaling, reposition handles
        self.parent.update_handles()
```

### File: `/scene3d/modifiers.py`

```python
from ursina import *


class ModifierShape(Draggable):
    def __init__(self, material_type, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'
        self.material_type = material_type

        if material_type == 'tarp':
            self.color = color.rgba(0, 255, 0, 150)
            self.texture = 'white_cube'
        elif material_type == 'tin':
            self.color = color.rgba(150, 150, 150, 200)
            self.texture = 'white_cube'

    def select(self):
        self.outline_color = color.yellow
        self.outline = True

    def deselect(self):
        self.outline = False
```

### File: `/scene3d/objects.py`

```python
from ursina import *


def snap_to_grid_pos(position, grid_size):
    """Snaps a Vec3 position to the nearest grid point."""
    if grid_size == 0: return position
    return Vec3(
        round(position.x / grid_size) * grid_size,
        round(position.y / grid_size) * grid_size,
        round(position.z / grid_size) * grid_size
    )


# A base class to disable Ctrl+Click reparenting and add snapping
class SafeDraggable(Draggable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Standardize highlight for all draggable objects
        self.highlight_color = self.color.tint(.3)
        self.plane_direction = (0, 1, 0)  # Default drag on X-Z plane

    def input(self, key):
        if self.hovered and key == 'left mouse down' and held_keys['control']:
            return  # Prevent Ursina's default Ctrl+Click reparenting
        super().input(key)

    def drag(self):
        super().drag()
        # Custom snapping logic (assumes the editor instance is named 'app')
        if app.grid_snap_enabled:
            self.world_position = snap_to_grid_pos(self.world_position, app.grid_size)


# --- Object Specific Classes ---

class Handle(SafeDraggable):
    def __init__(self, **kwargs):
        super().__init__(model='sphere', scale=.5, **kwargs)

    def drag(self):
        # Override drag to prevent handle from moving, instead it resizes its parent
        pass  # The parent Room's update loop handles the logic


class Room(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.walls = Entity(
            parent=self, model='cube', texture='white_cube',
            color=color.rgba(200, 200, 200, 40), collider='box'
        )
        self.walls.scale = (10, 4, 10)
        self.symmetry_enabled = False

        self.handles = {
            'x': Handle(parent=self, color=color.red, plane_direction=(0, 1, 0)),
            'y': Handle(parent=self, color=color.green, plane_direction=(0, 0, 1)),
            'z': Handle(parent=self, color=color.blue, plane_direction=(0, 1, 0)),
        }
        self.update_handle_positions()
        self.deselect()

    def update(self):
        was_resizing = False
        for axis, handle in self.handles.items():
            if handle.dragging:
                was_resizing = True
                # Move handle along its locked plane
                handle.position += Vec3(mouse.velocity[0], mouse.velocity[1],
                                        mouse.velocity[1]) * handle.plane_direction * 20 * time.dt

                # Update wall scale based on handle world position
                if axis == 'x': self.walls.scale_x = abs(handle.world_x - self.world_x) * 2
                if axis == 'y': self.walls.scale_y = abs(handle.world_y - self.world_y) * 2
                if axis == 'z': self.walls.scale_z = abs(handle.world_z - self.world_z) * 2

                if self.symmetry_enabled:
                    if axis == 'x':
                        self.walls.scale_z = self.walls.scale_x
                    elif axis == 'z':
                        self.walls.scale_x = self.walls.scale_z

        if was_resizing:
            self.update_handle_positions()

    def toggle_symmetry(self):
        self.symmetry_enabled = not self.symmetry_enabled
        if self.symmetry_enabled:
            self.walls.scale_z = self.walls.scale_x
            self.update_handle_positions()

    def update_handle_positions(self):
        s = self.walls.scale
        self.handles['x'].world_position = (self.world_x + s.x / 2, self.y, self.z)
        self.handles['y'].world_position = (self.x, self.world_y + s.y / 2, self.z)
        self.handles['z'].world_position = (self.x, self.y, self.world_z + s.z / 2)

    def select(self):
        self.walls.color = color.rgba(255, 255, 0, 70)
        for handle in self.handles.values(): handle.visible = True

    def deselect(self):
        self.walls.color = color.rgba(200, 200, 200, 40)
        for handle in self.handles.values(): handle.visible = False


class SceneWindow(SafeDraggable):
    def __init__(self, material, **kwargs):
        super().__init__(model='quad', scale=(2, 2.5), collider='box', **kwargs)
        self.material = 'none'  # Initialize before calling setter
        self.set_material(material)

    def set_material(self, material_name):
        self.material = material_name.lower()
        if self.material == 'glass':
            self.color = color.rgba(173, 216, 230, 150)  # Light blue transparent
        else:  # Default
            self.color = color.white

    def select(self):
        self.color = self.color.tint(0.5)

    def deselect(self):
        self.set_material(self.material)


class ModifierShape(SafeDraggable):
    def __init__(self, material_type, **kwargs):
        # Make these semi-transparent zones on the ground
        super().__init__(model='cube', scale=(3, 0.2, 3), collider='box', **kwargs)
        self.material = material_type

        if material_type == 'tarp':
            self.color = color.rgba(0, 100, 200, 150)  # Blue
        elif material_type == 'tin':
            self.color = color.rgba(150, 150, 150, 200)  # Gray

    def select(self):
        self.outline_color = color.yellow
        self.outline = True

    def deselect(self):
        self.outline = False
```

### File: `/scene3d/room.py`

```python
from ursina import *


# A base class to disable Ctrl+Click reparenting for all our custom objects.
class SafeDraggable(Draggable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def input(self, key):
        if self.hovered and key == 'left mouse down' and held_keys['control']:
            return  # Eat the input and do nothing if control is held.
        super().input(key)


class Handle(SafeDraggable):
    def __init__(self, **kwargs):
        super().__init__(model='sphere', scale=.5, highlight_color=self.color.tint(.2), **kwargs)


class Room(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.walls = Entity(parent=self, model='cube', texture='white_cube',
                            color=color.rgba(200, 200, 200, 40), collider='box')
        self.walls.scale = (10, 4, 10)
        self.symmetry_enabled = False

        self.handles = {
            'x': Handle(parent=self, color=color.red, plane_direction=(1, 0, 0)),
            'y': Handle(parent=self, color=color.green, plane_direction=(0, 1, 0)),
            'z': Handle(parent=self, color=color.blue, plane_direction=(0, 0, 1)),
        }
        self.update_handle_positions()
        self.deselect()

    def update(self):
        """This function provides the LIVE RESIZING logic."""
        was_resizing = False
        for axis, handle in self.handles.items():
            if handle.dragging:
                was_resizing = True
                if axis == 'x': self.walls.scale_x = abs(handle.world_x * 2)
                if axis == 'y': self.walls.scale_y = abs(handle.world_y * 2)
                if axis == 'z': self.walls.scale_z = abs(handle.world_z * 2)

                if self.symmetry_enabled:
                    if axis == 'x':
                        self.walls.scale_z = self.walls.scale_x
                    elif axis == 'z':
                        self.walls.scale_x = self.walls.scale_z

        if was_resizing:
            self.update_handle_positions()

    def toggle_symmetry(self):
        self.symmetry_enabled = not self.symmetry_enabled
        if self.symmetry_enabled:
            self.walls.scale_z = self.walls.scale_x
            self.update_handle_positions()
        # Update the button text after toggling
        from ursina.main import find_entity
        find_entity('main.py').symmetry_switch.text = f"Symmetry: {'ON' if self.symmetry_enabled else 'OFF'}"

    def update_handle_positions(self):
        s = self.walls.scale
        self.handles['x'].world_position = (self.world_x + s.x / 2, self.world_y, self.world_z)
        self.handles['y'].world_position = (self.world_x, self.world_y + s.y / 2, self.world_z)
        self.handles['z'].world_position = (self.world_x, self.world_y, self.world_z + s.z / 2)

    def select(self):
        self.walls.color = color.rgba(255, 255, 0, 70)
        for handle in self.handles.values(): handle.visible = True

    def deselect(self):
        self.walls.color = color.rgba(200, 200, 200, 40)
        for handle in self.handles.values(): handle.visible = False


# --- CRITICAL FIX: The class is now named SceneWindow ---
class SceneWindow(SafeDraggable):
    def __init__(self, material, **kwargs):
        super().__init__(origin_y=-.5, **kwargs)
        self.model = 'quad';
        self.scale = (1.5, 2.5);
        self.collider = 'box'
        self.audio_source = None;
        self.material = material
        self.set_material(material)

    def set_material(self, material_name):
        self.material = material_name
        if self.audio_source: self.audio_source.material = material_name
        if self.material == 'glass':
            self.color = color.cyan
        else:
            self.color = color.white

    def select(self):
        self.color = color.yellow

    def deselect(self):
        self.set_material(self.material)


class Speaker(SafeDraggable):
    def __init__(self, **kwargs):
        super().__init__(model='diamond', color=color.orange, **kwargs)

    def select(self): self.color = color.yellow

    def deselect(self): self.color = color.orange
```

### File: `/scene3d/room_editor.py`

```python
from ursina import *
from .objects import Room, SceneWindow, ModifierShape, snap_to_grid_pos


class Editor(Ursina):
    def __init__(self, audio_engine):
        super().__init__(
            title='Soundscape 3D View',
            borderless=False,
            # Position the window next to the UI
            window_position=(410, 50),
            size=(900, 720)
        )

        # --- Core Components ---
        self.audio_engine = audio_engine
        self.selected_entity = None
        self.show_inspector_callback = None
        self.hide_inspector_callback = None

        # --- Scene Setup ---
        self.grid_size = 1.0
        self.grid_snap_enabled = True

        self.room = Room(position=(0, 2, 0))  # Lift room slightly so grid is on the floor
        self.sound_sources = []

        # --- Visuals & Camera ---
        AmbientLight(color=color.rgba(100, 100, 100, 255))
        DirectionalLight(color=color.rgba(150, 150, 150, 255), direction=(1, -1, -1))

        self.camera_pivot = Entity()
        camera.wrtReparentTo(self.camera_pivot)
        camera.position = (0, 1, -25)
        camera.look_at(self.room)

        self.grid = Grid(100, 100, color=color.gray, thickness=1)

        self.select_entity(self.room)  # Select the room by default

    def set_ui_handles(self, show_callback, hide_callback):
        self.show_inspector_callback = show_callback
        self.hide_inspector_callback = hide_callback

    # --- Scene Interaction Methods (called from UI) ---
    def add_window(self):
        pos = camera.world_position + camera.forward * 10
        pos.y = self.room.y + self.room.walls.scale_y / 2
        new_window = SceneWindow(
            material='glass',
            position=snap_to_grid_pos(pos, self.grid_size)
        )
        self.sound_sources.append(new_window)
        self.select_entity(new_window)

    def add_modifier(self, material_type):
        pos = camera.world_position + camera.forward * 10
        pos.y = 0.1  # Place it on the floor
        new_mod = ModifierShape(
            material_type=material_type,
            position=snap_to_grid_pos(pos, self.grid_size)
        )
        self.sound_sources.append(new_mod)
        self.select_entity(new_mod)

    def delete_selected(self):
        if not self.selected_entity or self.selected_entity == self.room: return
        if self.selected_entity in self.sound_sources:
            self.sound_sources.remove(self.selected_entity)
        destroy(self.selected_entity)
        self.select_entity(self.room)

    def toggle_room_symmetry(self):
        if isinstance(self.selected_entity, Room):
            self.selected_entity.toggle_symmetry()

    def change_selected_material(self, material):
        if self.selected_entity and hasattr(self.selected_entity, 'set_material'):
            self.selected_entity.set_material(material)

    # --- Internal Selection Logic ---
    def select_entity(self, entity):
        if self.selected_entity: self.selected_entity.deselect()

        # If a handle is clicked, select its parent room
        from .objects import Handle
        if isinstance(entity, Handle):
            self.selected_entity = entity.parent
        else:
            self.selected_entity = entity

        self.selected_entity.select()
        if self.show_inspector_callback:
            self.show_inspector_callback(self.selected_entity)

    def deselect_all(self):
        if self.selected_entity: self.selected_entity.deselect()
        self.selected_entity = None
        if self.hide_inspector_callback: self.hide_inspector_callback()

    # --- Main Loops ---
    def update(self):
        # Pass all relevant scene data to the audio engine
        self.audio_engine.update_sources(self.sound_sources, camera.world_position)

        # Camera orbit controls
        if held_keys['right mouse']:
            self.camera_pivot.rotation_y -= mouse.velocity[0] * 150
            self.camera_pivot.rotation_x += mouse.velocity[1] * 150
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -80, 80)

    def input(self, key):
        # Camera zoom
        if key == 'scroll up': camera.z += 1 + (camera.z * .1)
        if key == 'scroll down': camera.z -= 1 + (camera.z * .1)

        if key == 'left mouse down':
            # Ignore clicks on UI elements that might be over the 3D window
            if mouse.hovered_entity and not isinstance(mouse.hovered_entity, (Slider, Button)):
                self.select_entity(mouse.hovered_entity)
            elif not mouse.hovered_entity:
                # If we click on empty space, select the room by default
                self.select_entity(self.room)

        if key == 'delete':
            self.delete_selected()
```

### File: `/scene3d/scene.py`

```python
from ursina import *


def create_room(width, depth, height):
    """Creates a room and returns the wall entities."""
    walls = []
    # To make normals consistent, we model the room from the outside
    # but will place the camera inside. A negative scale inverts the faces.
    room = Entity(model='cube', scale=(width, height, depth), texture='white_cube', scale_x=-1, scale_y=-1, scale_z=-1)

    # We need individual, invisible walls for mouse detection
    wall_front = Entity(model='quad', scale=(width, height), z=-depth / 2, rotation_y=180, name='wall_front')
    wall_back = Entity(model='quad', scale=(width, height), z=depth / 2, name='wall_back')
    wall_left = Entity(model='quad', scale=(depth, height), x=-width / 2, rotation_y=-90, name='wall_left')
    wall_right = Entity(model='quad', scale=(depth, height), x=width / 2, rotation_y=90, name='wall_right')

    for wall in [wall_front, wall_back, wall_left, wall_right]:
        wall.collider = 'box'
        wall.color = color.clear  # Make them invisible
        walls.append(wall)

    return walls


def create_window_entity(position, rotation, size):
    """Creates a visual representation of a window."""
    window = Entity(
        model='quad',
        position=position,
        rotation=rotation,
        scale=size,
        color=color.cyan
    )
    return window
```

### File: `/ui/__init__.py`

```python

```

### File: `/ui/main_window.py`

```python
import customtkinter
from .settings_panel import SettingsPanel # <-- ADD THIS LINE

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("3D Rain Soundscape")
        self.geometry("1100x720")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Settings",
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # create settings panel
        self.settings_panel = SettingsPanel(self.navigation_frame)
        self.settings_panel.grid(row=1, column=0, sticky="nsew")

# Optional but recommended: Remove the test code below from this file
# as it's not meant to be run directly. The main entry point is main.py
#
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()
```

### File: `/ui/settings_panel.py`

```python
import customtkinter


class SettingsPanel(customtkinter.CTkFrame):
    def __init__(self, master, editor_app, audio_engine, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.editor_app = editor_app
        self.audio_engine = audio_engine

        self.grid_columnconfigure(0, weight=1)

        # --- Creation Buttons ---
        creation_frame = customtkinter.CTkFrame(self)
        creation_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="ew")
        creation_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(creation_frame, text="Create", font=customtkinter.CTkFont(weight="bold")).grid(row=0,
                                                                                                              column=0,
                                                                                                              padx=10,
                                                                                                              pady=10)
        self.add_window_btn = customtkinter.CTkButton(creation_frame, text="Add Window",
                                                      command=self.editor_app.add_window)
        self.add_window_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.add_tarp_btn = customtkinter.CTkButton(creation_frame, text="Add Tarp Zone",
                                                    command=lambda: self.editor_app.add_modifier('tarp'))
        self.add_tarp_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.add_tin_btn = customtkinter.CTkButton(creation_frame, text="Add Tin Zone",
                                                   command=lambda: self.editor_app.add_modifier('tin'))
        self.add_tin_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # --- Inspector Frame (Managed by Room Editor) ---
        self.inspector_frame = customtkinter.CTkFrame(self)
        self.inspector_frame.grid_columnconfigure(0, weight=1)

        self.inspector_label = customtkinter.CTkLabel(self.inspector_frame, text="Selected: None",
                                                      font=customtkinter.CTkFont(weight="bold"))
        self.inspector_label.grid(row=0, column=0, pady=(0, 10))

        # Widgets for Room
        self.symmetry_switch = customtkinter.CTkSwitch(self.inspector_frame, text="Symmetry (X/Z)",
                                                       command=self.editor_app.toggle_room_symmetry)

        # Widgets for Window
        self.inspector_material_menu = customtkinter.CTkOptionMenu(
            self.inspector_frame,
            values=["glass"],  # Add more materials here if needed
            command=self.editor_app.change_selected_material
        )

        self.inspector_delete_btn = customtkinter.CTkButton(
            self.inspector_frame, text="Delete", fg_color="#D2042D", hover_color="#AA0323",
            command=self.editor_app.delete_selected
        )

        # --- Global Controls ---
        global_frame = customtkinter.CTkFrame(self)
        global_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        global_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(global_frame, text="Global Soundscape", font=customtkinter.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=10)

        self._create_slider(global_frame, "Master Volume", 1, 'master_volume', 70)
        self._create_slider(global_frame, "Drizzle Intensity", 2, 'drizzle_intensity', 20)
        self._create_slider(global_frame, "Window Openness", 3, 'window_openness', 100)

    def _create_slider(self, parent, text, row, param_name, default_val):
        """Helper to create a labeled slider."""
        label = customtkinter.CTkLabel(parent, text=text)
        label.grid(row=row * 2 - 1, column=0, padx=20, pady=(10, 0), sticky="w")
        slider = customtkinter.CTkSlider(parent, from_=0, to=100,
                                         command=lambda v: self.audio_engine.update_global_param(param_name, v))
        slider.set(default_val)
        slider.grid(row=row * 2, column=0, padx=20, pady=(0, 10), sticky="ew")

    def show_inspector(self, entity):
        self.inspector_frame.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="ew")
        self.inspector_delete_btn.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        # Hide all optional widgets first
        self.symmetry_switch.grid_forget()
        self.inspector_material_menu.grid_forget()

        from scene3d.objects import Room, SceneWindow, ModifierShape  # Avoid circular import

        if isinstance(entity, Room):
            self.inspector_label.configure(text="Selected: Room")
            self.symmetry_switch.grid(row=1, column=0, pady=5, padx=10, sticky="w")
            self.inspector_delete_btn.configure(state="disabled")  # Can't delete the room
            if entity.symmetry_enabled:
                self.symmetry_switch.select()
            else:
                self.symmetry_switch.deselect()

        elif isinstance(entity, SceneWindow):
            self.inspector_label.configure(text=f"Selected: Window")
            self.inspector_material_menu.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
            self.inspector_material_menu.set(entity.material)
            self.inspector_delete_btn.configure(state="normal")

        elif isinstance(entity, ModifierShape):
            self.inspector_label.configure(text=f"Selected: {entity.material.title()} Zone")
            self.inspector_delete_btn.configure(state="normal")

    def hide_inspector(self):
        self.inspector_frame.grid_forget()
```

### File: `/__init__.py`

```python

```

### File: `/boot_loader.py`

```python
import tkinter as tk
import random


class LoadingWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loading Soundscape...")
        self.config(bg='black')

        # Center the window
        width = 300
        height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
        self.overrideredirect(True)  # Removes window border

        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.loading_label = tk.Label(self.canvas, text="Initializing...", fg='white', bg='black', font=("Helvetica", 14))
        self.canvas.create_window(width / 2, height - 40, window=self.loading_label)

        # Rain Animation
        self.raindrops = []
        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height)
            length = random.randint(5, 15)
            speed = random.randint(2, 5)
            line = self.canvas.create_line(x, y, x, y + length, fill='cyan')
            self.raindrops.append({'line': line, 'speed': speed})

        self.animate_rain()

    def animate_rain(self):
        for drop in self.raindrops:
            self.canvas.move(drop['line'], 0, drop['speed'])
            x1, y1, x2, y2 = self.canvas.coords(drop['line'])
            if y1 > self.winfo_height():
                self.canvas.move(drop['line'], 0, -self.winfo_height() - (y2 - y1))

        # This makes the animation loop
        self.after(16, self.animate_rain)  # Approx 60fps

    def check_if_done(self, loading_thread, on_done_callback):
        """Checks if the background loading thread has finished."""
        if not loading_thread.is_alive():
            self.destroy()  # Close the loading window
            on_done_callback()  # Call the function that runs the app
        else:
            # Check again in 100ms
            self.after(100, lambda: self.check_if_done(loading_thread, on_done_callback))
```

### File: `/main.py`

```python
import tkinter as tk
import threading
import atexit
from ui.main_window import App
from scene3d.room_editor import Editor
from engine import AdvancedAudioEngine
from boot_loader import LoadingWindow


class MainApplication:
    """
    Main controller class that orchestrates the UI, 3D scene, and audio engine.
    """

    def __init__(self):
        self.ui_root = None
        self.audio_engine = None
        self.editor_app = None

    def initialize(self):
        """
        Initializes the core components of the application.
        This is run in a background thread to allow the loading screen to animate.
        """
        print("Initializing Audio Engine...")
        self.audio_engine = AdvancedAudioEngine()
        atexit.register(self.audio_engine.close)  # Ensure audio stops on exit

        print("Initializing 3D Editor...")
        # The Editor (Ursina) needs a reference to the audio engine to pass updates
        self.editor_app = Editor(self.audio_engine)

        print("Initializing UI...")
        # The UI App needs a reference to the editor to send commands
        self.ui_root = App(self.editor_app)

        # Connect the editor back to the UI's inspector panel
        self.editor_app.set_ui_handles(
            self.ui_root.settings_panel.show_inspector,
            self.ui_root.settings_panel.hide_inspector
        )
        print("Initialization Complete.")

    def run(self):
        """Starts the main UI loop and the 3D editor loop."""
        # The editor.run() starts the Ursina main loop.
        # This needs to be in a separate thread from the UI's mainloop.
        editor_thread = threading.Thread(target=self.editor_app.run, daemon=True)
        editor_thread.start()

        self.ui_root.mainloop()


if __name__ == '__main__':
    app_controller = MainApplication()

    # --- Loading Screen Logic ---
    loading_window = LoadingWindow()

    # Run the heavy initialization in a separate thread
    init_thread = threading.Thread(target=app_controller.initialize, daemon=True)
    init_thread.start()


    # Function to start the main app after loading is finished
    def start_main_app():
        app_controller.run()


    # Periodically check if the init thread is done, then close loader and run app
    loading_window.check_if_done(init_thread, start_main_app)

    loading_window.mainloop()
```

### File: `/main_window.py`

```python
import customtkinter
from .settings_panel import SettingsPanel

class App(customtkinter.CTk):
    def __init__(self, editor_app, **kwargs):
        super().__init__(**kwargs)

        self.editor_app = editor_app

        self.title("Soundscape Designer")
        self.geometry("350x720+50+50") # Set size and position
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(
            self.navigation_frame, text="  Controls",
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Create settings panel and pass the editor and audio engine references
        self.settings_panel = SettingsPanel(
            self.navigation_frame,
            editor_app=self.editor_app,
            audio_engine=self.editor_app.audio_engine
        )
        self.settings_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
```
