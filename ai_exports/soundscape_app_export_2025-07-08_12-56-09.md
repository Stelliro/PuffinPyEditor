# Project Export: soundscape_app
## Export Timestamp: 2025-07-08T12:56:09.849308
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
 ├── audio
 │   └── engine.py
 ├── config.py
 ├── core
 │   ├── editor_state.py
 │   └── selection_manager.py
 ├── main.py
 ├── project
 │   └── project_manager.py
 ├── scene
 │   ├── camera_controller.py
 │   ├── gizmo.py
 │   ├── objects.py
 │   └── scene_manager.py
 ├── soundscape_app.py
 └── ui
     ├── base_panel.py
     ├── editor_panel.py
     ├── soundscape_panel.py
     └── ui_manager.py

```
## File Contents
### File: `/audio/engine.py`

```python
import numpy as np
import sounddevice as sd
import soundfile as sf
import os
import random
import threading
import time
import config


# --- THE PLAN ---
# This is the dedicated audio processing system. Its responsibilities are:
# 1. Run in a completely separate thread to ensure smooth, non-blocking audio,
#    regardless of what's happening in the main 3D visualization thread.
# 2. Load and categorize all .wav files from a specified folder at startup.
# 3. Process sound sources using two distinct, switchable methods:
#    a) Multi-speaker "Surround Sound" simulation for room speaker setups.
#    b) "Binaural" simulation (using ITD and ILD) for realistic headphone 3D audio.
# 4. Handle global ambient sounds like wind and intermittent events like thunder.
# 5. Receive real-time updates from the main thread about sound source positions
#    and the listener's (camera's) position and orientation.
# 6. Be entirely self-contained. The main application only needs to call `update_sources`
#    and `update_global_param`. It doesn't need to know *how* the audio is generated.

class AdvancedAudioEngine:
    def __init__(self):
        print("Initializing AdvancedAudioEngine...")
        # --- Audio Stream Parameters ---
        self.samplerate = config.AUDIO_SAMPLE_RATE
        self.blocksize = config.AUDIO_BLOCK_SIZE
        self.channels = 2

        # --- Data Containers ---
        # These are accessed from both the main thread and the audio thread,
        # so they must be protected by a lock.
        self.sources = []
        self.listener_position = np.array([0, 0, 0])
        self.listener_right_vec = np.array([1, 0, 0])
        self.lock = threading.Lock()

        # --- State Variables ---
        self.headphone_mode = False
        self.global_params = {
            'master_volume': config.AUDIO_DEFAULT_MASTER_VOLUME / 100.0,
            'drizzle_intensity': config.AUDIO_DEFAULT_DRIZZLE_INTENSITY / 100.0,
            'wind_intensity': config.AUDIO_DEFAULT_WIND_INTENSITY / 100.0,
            'window_openness': config.AUDIO_DEFAULT_WINDOW_OPENNESS / 100.0,
        }

        # --- Sound-specific Playback State ---
        self.wind_playback_pos = 0

        # --- Binaural Audio Constants ---
        # The max interaural time difference for the human ear is ~0.7ms.
        # We calculate how many samples this corresponds to.
        self.max_itd_samples = int(0.0007 * self.samplerate)

        # --- Multi-Speaker Downmix Constants ---
        speaker_positions = np.array(
            [[0, 0, 1], [-1, 0, 1], [1, 0, 1], [-1, 0, 0], [1, 0, 0], [-1, 0, -1], [1, 0, -1], [0, 1, 0]])
        self.speaker_vectors = speaker_positions / np.linalg.norm(speaker_positions, axis=1)[:, np.newaxis]
        self.downmix_matrix = np.array(
            [[0.7, 0.7], [1.0, 0.1], [0.1, 1.0], [1.0, 0.3], [0.3, 1.0], [0.8, 0.5], [0.5, 0.8], [0.6, 0.6]])

        # --- Initialization ---
        self.samples = self._load_samples('audio/sounds/')
        self.stream = self._start_stream()

    def _start_stream(self):
        try:
            stream = sd.OutputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                callback=self._audio_callback,
                dtype='float32',
                blocksize=self.blocksize
            )
            stream.start()
            print("Audio stream started successfully.")
            return stream
        except Exception as e:
            print(f"FATAL: COULD NOT START AUDIO STREAM. Error: {e}")
            return None

    def update_sources(self, sources, listener_pos, listener_right_vec):
        """Thread-safe method called by the main app to update audio locations."""
        with self.lock:
            self.sources = sources
            self.listener_position = listener_pos
            self.listener_right_vec = listener_right_vec

    def update_global_param(self, name: str, value: float):
        """Thread-safe method to update global sound parameters from the UI."""
        with self.lock:
            if name in self.global_params:
                self.global_params[name] = value / 100.0
                print(f"Audio Param '{name}' set to {self.global_params[name]:.2f}")

    def toggle_headphone_mode(self, enabled: bool):
        """Switches the audio rendering mode."""
        with self.lock:
            self.headphone_mode = enabled
            print(f"Audio mode switched to: {'Binaural (Headphones)' if enabled else 'Multi-speaker Simulation'}")

    def _load_samples(self, path):
        """Loads and categorizes all .wav files from the audio directory."""
        if not os.path.exists(path):
            print(f"Warning: Audio directory not found at '{path}'. Creating it now.")
            os.makedirs(path)

        samples = {'drizzle': [], 'glass': [], 'tin': [], 'tarp': [], 'wind': []}
        print("Loading audio samples...")
        for fname in os.listdir(path):
            if not fname.lower().endswith('.wav'): continue

            category = 'drizzle'  # Default category
            for cat_name in samples.keys():
                if cat_name in fname.lower():
                    category = cat_name
                    break

            try:
                filepath = os.path.join(path, fname)
                data, _ = sf.read(filepath, dtype='float32')
                # Ensure all samples are mono for our processing
                mono_data = data if data.ndim == 1 else data[:, 0]
                samples[category].append(mono_data)
                print(f"  - Loaded '{fname}' -> '{category}'")
            except Exception as e:
                print(f"  - Could not load sample {fname}: {e}")
        return samples

    def _render_binaural_grain(self, buffer, grain, source_pos):
        """Processes a single sound event using headphone-optimized 3D audio."""
        sound_vec = source_pos - self.listener_position
        dist = np.linalg.norm(sound_vec)
        if dist < 0.1: return  # Too close to process

        sound_vec_norm = sound_vec / dist
        right_dot = np.dot(sound_vec_norm, self.listener_right_vec)

        # ILD (Interaural Level Difference): Quieter in the ear facing away.
        gain_l = np.sqrt(0.5 * (1 - right_dot))
        gain_r = np.sqrt(0.5 * (1 + right_dot))

        # ITD (Interaural Time Difference): Arrives later at the ear facing away.
        time_delay_samples = int(self.max_itd_samples * right_dot)

        start_pos = random.randint(self.max_itd_samples, len(buffer) - len(grain) - self.max_itd_samples)

        # Attenuate by distance (inverse square law, softened)
        attenuation = 1 / (1 + dist * 0.5)

        # Apply grain to buffer with calculated delays and gains
        if time_delay_samples >= 0:  # Sound on the right
            buffer[start_pos + time_delay_samples: start_pos + time_delay_samples + len(grain),
            1] += grain * gain_r * attenuation
            buffer[start_pos: start_pos + len(grain), 0] += grain * gain_l * attenuation
        else:  # Sound on the left
            buffer[start_pos: start_pos + len(grain), 1] += grain * gain_r * attenuation
            buffer[start_pos - time_delay_samples: start_pos - time_delay_samples + len(grain),
            0] += grain * gain_l * attenuation

    def _render_speaker_grain(self, buffer, grain, source_pos):
        """Processes a single sound event using multi-speaker panning simulation."""
        sound_vec = source_pos - self.listener_position
        dist = np.linalg.norm(sound_vec)
        if dist < 0.1: return
        sound_vec /= dist  # Normalize

        gains_8_channel = np.maximum(0, np.dot(self.speaker_vectors, sound_vec)) ** 2
        stereo_gain = np.dot(gains_8_channel, self.downmix_matrix)
        attenuation = 1 / (1 + dist * 0.5)

        start_pos = random.randint(0, len(buffer) - len(grain) - 1)
        for i in range(self.channels):
            buffer[start_pos: start_pos + len(grain), i] += grain * stereo_gain[i] * attenuation

    def _audio_callback(self, outdata, frames, t, status):
        """This function is the heart of the audio thread. It's called continuously."""
        try:
            buffer = np.zeros((frames, self.channels), dtype='float32')

            # We lock here to get a consistent copy of the data from the main thread
            with self.lock:
                # Make local copies of shared data to use inside the loop
                sources = list(self.sources)
                render_func = self._render_binaural_grain if self.headphone_mode else self._render_speaker_grain
                params = dict(self.global_params)

            # --- AMBIENT SOUNDS ---
            # Ambient wind sound, looped seamlessly
            if self.samples.get('wind') and params['wind_intensity'] > 0:
                wind_sample = self.samples['wind'][0]
                sample_len = len(wind_sample)
                indices = (self.wind_playback_pos + np.arange(frames)) % sample_len
                buffer += wind_sample[indices, np.newaxis] * params['wind_intensity']
                self.wind_playback_pos = (self.wind_playback_pos + frames) % sample_len

            # --- 3D LOCALIZED SOUNDS ---
            drizzle = params['drizzle_intensity']
            for source in sources:
                material_sounds = self.samples.get(source.sound_material, [])
                # Trigger a sound based on a random chance proportional to drizzle intensity
                if material_sounds and random.random() < drizzle * 0.05:
                    grain = random.choice(material_sounds)
                    # Ensure the sound grain can fit in the buffer
                    if len(grain) + self.max_itd_samples < frames:
                        render_func(buffer, grain, np.array(source.world_position))

            # Attenuate overall sound based on how "open" the windows are
            if params['window_openness'] < 1.0:
                buffer *= params['window_openness']

            # Apply master volume and clip to prevent speaker damage
            outdata[:] = np.clip(buffer * params['master_volume'], -1.0, 1.0)

        except Exception as e:
            # If anything goes wrong, print the error and output silence
            print(f"AUDIO ENGINE CRASH: {e}", file=sys.stderr)
            traceback.print_exc()
            outdata.fill(0)

    def close(self):
        """Gracefully stops and closes the audio stream."""
        if self.stream:
            print("Stopping Audio Engine...")
            self.stream.stop()
            self.stream.close()
            print("Audio Engine stopped.")
```

### File: `/core/editor_state.py`

```python
import config

# --- THE PLAN ---
# This class acts as a centralized "single source of truth" for the editor's state.
# Instead of different modules tracking their own versions of "what tool is active"
# or "what object is selected", they will all ask this class.
#
# This solves a huge category of bugs in complex applications where different parts
# of the UI can get out of sync. For example, if the UI panel *thinks* the
# 'move' tool is active, but the gizmo *thinks* the 'scale' tool is active,
# you get chaos. With EditorState, they both just check `window.app.editor_state.active_tool`.
#
# It holds simple data, but its role in organizing the application is critical.

class EditorState:
    def __init__(self):
        """
        Initializes the editor's state with default values from our config file.
        """
        print("Initializing EditorState...")

        # --- Tool State ---
        # The currently active manipulation tool ('select', 'move', 'rotate', 'scale').
        # The default is 'select'.
        self.active_tool = 'select'

        # --- Selection State ---
        # A direct reference to the currently selected entity in the scene.
        # Starts as None because nothing is selected at launch.
        self.selected_entity = None

        # --- Scene/Grid State ---
        # A boolean flag to control if objects should snap to the grid.
        self.grid_snap_enabled = config.DEFAULT_GRID_SNAP

        # The current size of the grid, in world units (meters).
        self.grid_size = config.DEFAULT_GRID_SIZE

        # --- UI State ---
        # This could be used in the future to track which panels are open/closed, etc.
        # For now, it's a placeholder to demonstrate the concept.
        self.is_left_panel_visible = True
        self.is_right_panel_visible = True

    def set_active_tool(self, tool_name: str):
        """
        Sets the active manipulation tool.
        This function would be called by the UI buttons.

        :param tool_name: The name of the tool, e.g., 'move'.
        """
        # We can add validation here to ensure only valid tools are set.
        valid_tools = ['select', 'move', 'rotate', 'scale']
        if tool_name in valid_tools:
            print(f"Active tool changed to: {tool_name}")
            self.active_tool = tool_name
        else:
            print(f"Warning: Tried to set an invalid tool '{tool_name}'")

    def set_selection(self, entity):
        """
        Updates the currently selected entity.
        This would be called by the SelectionManager.

        :param entity: The Ursina entity that has been selected, or None.
        """
        # We don't print a message here as selection can happen many times a second
        # during mouse drags, which would flood the console.
        self.selected_entity = entity

    def toggle_grid_snap(self):
        """
        Toggles the grid snap setting and returns the new state.
        """
        self.grid_snap_enabled = not self.grid_snap_enabled
        print(f"Grid Snap toggled: {'ON' if self.grid_snap_enabled else 'OFF'}")
        return self.grid_snap_enabled
```

### File: `/core/selection_manager.py`

```python
from ursina import *


# --- THE PLAN ---
# This class is a dedicated controller for all selection-related logic.
# Its responsibilities are:
# 1. To be the ONLY class that directly listens for the "select" mouse click.
# 2. To determine what entity the user intended to select based on the mouse position.
# 3. To handle the visual state change of objects (calling their `.select()` and `.deselect()` methods).
# 4. To update the central `EditorState` with the newly selected entity.
# 5. To provide a clear, public `select_entity()` method that other parts of the app can
#    use if they need to programmatically change the selection (e.g., after creating a new object).

# This design prevents selection logic from being scattered all over the codebase,
# making it easy to debug and extend (e.g., adding multi-select in the future).

class SelectionManager:
    def __init__(self):
        """
        Initializes the SelectionManager.
        It needs access to the global EditorState to function.
        """
        print("Initializing SelectionManager...")
        # A convenient shorthand to access the globally available EditorState.
        self.editor_state = window.app.editor_state

    def input(self, key):
        """
        This method is called by the main application's input loop.
        It only cares about mouse clicks when the 'select' tool is active.
        """
        if self.editor_state.active_tool != 'select':
            # If any other tool (move, rotate, scale) is active, this manager does nothing.
            return

        if key == 'left mouse down':
            # Check if the mouse is over a 3D entity.
            if mouse.hovered_entity:
                # We need to find the "top-level" selectable object.
                # If we clicked on a gizmo handle or part of a complex object, we want
                # to select the main parent object.
                target = self.find_selectable_parent(mouse.hovered_entity)
                self.select_entity(target)
            else:
                # If we clicked on empty space, deselect everything.
                self.select_entity(None)

    def find_selectable_parent(self, entity):
        """
        Traverses up the entity hierarchy to find the main object that should be selected.
        This is a 'beefy' feature that handles complex objects correctly. For example, if you
        click on a wheel of a car model, this function will ensure you select the whole car.

        In our case, it's used for the Room's handles.
        """
        from scene.objects import ResizeHandle, Room  # Avoid circular import at top level

        # If we clicked a resize handle, we actually want to select its parent, the Room.
        if isinstance(entity, ResizeHandle):
            return entity.parent

        # Otherwise, the entity we clicked is the one we want to select.
        return entity

    def select_entity(self, entity, from_code=False):
        """
        The core function for changing the selection.

        :param entity: The entity to select, or None to deselect all.
        :param from_code: A flag to prevent console flooding from programmatic selection.
        """

        # --- DESELECTION LOGIC ---
        # First, deselect the currently selected entity, if any.
        current_selection = self.editor_state.selected_entity
        if current_selection and current_selection != entity:
            if hasattr(current_selection, 'deselect'):
                current_selection.deselect()

        # --- SELECTION LOGIC ---
        # Now, select the new entity.
        if entity:
            if hasattr(entity, 'select'):
                entity.select()
            if not from_code:
                print(f"Selected: {entity.name} (Type: {type(entity).__name__})")
        else:
            if not from_code:
                print("Selection cleared.")

        # --- UPDATE CENTRAL STATE ---
        # Finally, update the global EditorState with the new selection.
        # This is the "single source of truth" update.
        self.editor_state.set_selection(entity)

        # --- THE FINAL CONNECTION ---
        if self.on_selection_changed:
            self.on_selection_changed(entity)
```

### File: `/project/project_manager.py`

```python
import json
from pathlib import Path
import config
from ursina import *


# --- THE PLAN ---
# This class will be responsible for saving the state of the entire 3D scene
# to a file and loading it back. This is a critical feature for any creative tool.
#
# Its responsibilities will be:
# 1. To collect all necessary data from the scene:
#    - The position, rotation, and scale of every object.
#    - The type of each object (e.g., 'Speaker', 'Tarp Zone').
#    - The main room's dimensions.
#
# 2. To serialize this data into a human-readable format (JSON).
#
# 3. To write this data to a file with a custom extension (`.scape`).
#
# 4. To provide a `load_project` method that reads a file, clears the current
#    scene, and rebuilds it from the saved data.
#
# For now, we will implement a basic version that can be expanded upon.

class ProjectManager:
    def __init__(self):
        print("Initializing ProjectManager...")

        # We need access to the other managers to get scene data and create objects.
        self.scene_manager = window.app.scene_manager

        # Ensure the default save directory exists.
        Path(config.DEFAULT_PROJECT_SAVE_PATH).mkdir(parents=True, exist_ok=True)

    def save_project(self, filename: str = config.DEFAULT_PROJECT_NAME):
        """
        Gathers scene data, serializes it, and saves it to a .scape file.
        """
        print(f"Saving project to '{filename}{config.PROJECT_FILE_EXTENSION}'...")

        # --- Data Gathering ---
        project_data = {
            'version': config.EDITOR_VERSION,
            'scene': {
                'room': {
                    'scale': list(self.scene_manager.room.walls.scale)
                },
                'objects': []
            }
        }

        for obj in self.scene_manager.get_all_sound_sources():
            obj_data = {
                'type': type(obj).__name__,  # e.g., 'Speaker'
                'sound_material': obj.sound_material,
                'position': list(obj.position),
                'rotation': list(obj.rotation),
                'scale': list(obj.scale),
            }
            project_data['scene']['objects'].append(obj_data)

        # --- Serialization & Saving ---
        filepath = Path(config.DEFAULT_PROJECT_SAVE_PATH) / f"{filename}{config.PROJECT_FILE_EXTENSION}"
        try:
            with open(filepath, 'w') as f:
                json.dump(project_data, f, indent=4)
            print(f"Project saved successfully to {filepath}")

        except Exception as e:
            print(f"Error: Could not save project. Reason: {e}")

    def load_project(self, filename: str = config.DEFAULT_PROJECT_NAME):
        """
        Loads a .scape file, clears the current scene, and rebuilds it.
        """
        filepath = Path(config.DEFAULT_PROJECT_SAVE_PATH) / f"{filename}{config.PROJECT_FILE_EXTENSION}"
        if not filepath.exists():
            print(f"Error: Project file not found at {filepath}")
            return

        print(f"Loading project from {filepath}...")

        try:
            with open(filepath, 'r') as f:
                project_data = json.load(f)

            # --- Scene Reconstruction ---
            print("Clearing current scene...")
            # We must iterate over a copy of the list when deleting.
            for obj in list(self.scene_manager.get_all_sound_sources()):
                self.scene_manager.delete_selected_object()  # This needs to select the obj first

            print("Rebuilding scene from project data...")
            # Load room dimensions
            room_scale = project_data['scene']['room']['scale']
            self.scene_manager.room.walls.scale = Vec3(room_scale)
            self.scene_manager.room.update_handle_positions()

            # Load all other objects
            for obj_data in project_data['scene']['objects']:
                obj_type = obj_data['type']

                # Use the SceneManager's factory to create the object
                new_obj = self.scene_manager.add_object(
                    obj_type.lower(),
                    material=obj_data.get('sound_material')  # get() is safer
                )

                # Apply saved transform data
                if new_obj:
                    new_obj.position = Vec3(obj_data['position'])
                    new_obj.rotation = Vec3(obj_data['rotation'])
                    new_obj.scale = Vec3(obj_data['scale'])

            print("Project loaded successfully.")

        except Exception as e:
            print(f"Error: Could not load project. File may be corrupted. Reason: {e}")
```

### File: `/scene/camera_controller.py`

```python
from ursina import *
import config


# --- THE PLAN ---
# This class encapsulates all logic related to camera movement. Its responsibilities are:
# 1. To create and manage a "pivot" entity, which is the point the camera orbits around.
# 2. To listen for specific mouse inputs (right-click drag, middle-click drag, scroll wheel)
#    to control orbiting, panning, and zooming.
# 3. To read all its speed and sensitivity settings from `config.py`, making it easy to tune.
# 4. To implement constraints, such as limiting how far you can zoom or preventing the
#    camera from flipping upside down.
# 5. To provide a "focus" function (F-key) that smoothly animates the camera to look
#    at a specific target, which is a great user-experience feature.

class CameraController:
    def __init__(self):
        """
        Initializes the camera pivot and sets the initial camera position.
        """
        print("Initializing CameraController...")

        # The 'camera' is a global Ursina object.
        self.camera = camera

        # --- Camera Pivot System ---
        # The camera is parented to a pivot point. This makes orbiting and panning
        # mathematically simple and robust. Rotating the pivot orbits the camera.
        # Moving the pivot pans the camera.
        self.camera_pivot = Entity()
        self.camera.parent = self.camera_pivot

        # Set the initial camera position based on our config file.
        self.camera.position = config.INITIAL_CAMERA_POSITION
        self.camera.look_at(self.camera_pivot)

        # A visual representation of the listener, which moves with the camera.
        self.listener_avatar = self._create_listener_avatar()

        # Storing the last known position to detect if the user tries to pan while zoomed.
        self.last_zoom_pos = self.camera.z

    def _create_listener_avatar(self):
        """Creates the 'headphone' model that shows the listener's position."""
        # This avatar is always on top so it can be seen even when inside objects.
        avatar = Entity(
            model='sphere',
            scale=0.15,
            color=color.black,
            always_on_top=True,
            render_queue=1  # Ensures it renders after most objects
        )
        # Two spheres to represent the ear cups.
        Entity(parent=avatar, model='sphere', x=-0.1, scale=(0.1, 1.2, 1.2), color=color.dark_gray)
        Entity(parent=avatar, model='sphere', x=0.1, scale=(0.1, 1.2, 1.2), color=color.dark_gray)
        return avatar

    def input(self, key):
        """
        Handles mouse scroll wheel for zooming and the 'f' key for focusing.
        """
        if key == 'scroll up':
            # Zoom in by moving the camera forward along its local z-axis.
            # We use a non-linear speed to make zooming feel more natural.
            target_z = self.camera.z + config.CAMERA_ZOOM_SPEED * (abs(self.camera.z) * 0.2)
            self.camera.z = clamp(target_z, -config.CAMERA_ZOOM_MAX, -config.CAMERA_ZOOM_MIN)

        if key == 'scroll down':
            # Zoom out by moving the camera backward.
            target_z = self.camera.z - config.CAMERA_ZOOM_SPEED * (abs(self.camera.z) * 0.2)
            self.camera.z = clamp(target_z, -config.CAMERA_ZOOM_MAX, -config.CAMERA_ZOOM_MIN)

        if key == 'f':
            # Focus on the currently selected object, or the center of the room if nothing is selected.
            target_entity = window.app.editor_state.selected_entity
            target_pos = target_entity.world_position if target_entity else Vec3.zero()
            # Animate the pivot's movement for a smooth transition.
            self.camera_pivot.animate_position(target_pos, duration=0.2, curve=curve.out_quad)

    def update(self):
        """
        Handles continuous mouse-drag logic for orbiting and panning.
        Called every frame by the main application.
        """

        # --- Orbit Logic (Right Mouse Button) ---
        if held_keys['right mouse']:
            self.camera_pivot.rotation_y -= mouse.velocity[0] * config.CAMERA_ORBIT_SPEED
            self.camera_pivot.rotation_x += mouse.velocity[1] * config.CAMERA_ORBIT_SPEED

            # Clamp the x rotation to prevent the camera from flipping upside-down.
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -89, 89)

        # --- Pan Logic (Middle Mouse Button) ---
        if held_keys['middle mouse']:
            # Panning speed is adjusted by how far the camera is zoomed out.
            # This is a key feature for usability: panning is slower when zoomed in.
            pan_speed_multiplier = abs(self.camera.z) / 30

            # We use the camera's local right and up vectors to ensure that
            # moving the mouse left always pans the view left, regardless of rotation.
            self.camera_pivot.position -= self.camera.right * mouse.velocity[
                0] * config.CAMERA_PAN_SPEED * pan_speed_multiplier
            self.camera_pivot.position -= self.camera.up * mouse.velocity[
                1] * config.CAMERA_PAN_SPEED * pan_speed_multiplier

        # Keep the listener avatar synced with the camera's actual world position and rotation.
        self.listener_avatar.position = self.camera.world_position
        self.listener_avatar.rotation = self.camera.world_rotation
```

### File: `/scene/gizmo.py`

```python
from ursina import *
import config


# --- THE PLAN ---
# This file defines the complete transform gizmo system.
#
# 1. A `GizmoHandle` class will be a smart, draggable entity. Each handle (e.g., the
#    X-axis move arrow) will be an instance of this class. It will know how to modify
#    its target entity based on its type (move, rotate, or scale).
#
# 2. A main `Gizmo` class will act as a container for all possible handles.
#    - It holds separate sets of handles for 'move', 'rotate', and 'scale'.
#    - It synchronizes its position and rotation with the selected object.
#    - Its `set_tool` method shows/hides the appropriate handles based on the
#      active tool from `EditorState`.
#
# 3. The math for rotation and scaling is handled carefully to feel intuitive.
#    Rotation is based on projecting mouse movement onto a plane, and scaling
#    is cumulative.

# =============================================================================
# --- THE INDIVIDUAL GIZMO HANDLES ---
# =============================================================================
class GizmoHandle(Draggable):
    def __init__(self, gizmo_parent, handle_type, axis, color, **kwargs):
        """
        The base for all gizmo handles (arrows, rings, cubes).

        :param gizmo_parent: A reference to the main Gizmo entity.
        :param handle_type: 'move', 'rotate', or 'scale'.
        :param axis: A Vec3 representing the axis this handle controls, e.g., (1,0,0) for X.
        """
        # We start with default values; specific handles will override them.
        super().__init__(
            model='cube',
            parent=gizmo_parent,
            color=color,
            always_on_top=True,
            render_queue=1,  # Render after everything else
            **kwargs
        )
        self.gizmo_parent = gizmo_parent
        self.handle_type = handle_type
        self.axis = axis
        self.lock = Vec3(1, 1, 1) - abs(self.axis)  # Lock movement to the specified axis
        self.highlight_color = config.GIZMO_HOVER_COLOR

    def on_drag(self):
        """Called every frame while the handle is being dragged."""
        if not self.gizmo_parent.target:
            return

        target = self.gizmo_parent.target

        # --- Handle logic based on type ---
        if self.handle_type == 'move':
            target.world_position += self.axis * sum(mouse.velocity) * config.GIZMO_DRAG_SENSITIVITY

        elif self.handle_type == 'rotate':
            # Project mouse movement onto the rotation axis plane.
            # This provides intuitive orbital rotation.
            rotation_amount = (mouse.velocity[0] + mouse.velocity[1]) * config.GIZMO_DRAG_SENSITIVITY * 2
            target.world_rotation += self.axis * rotation_amount

        elif self.handle_type == 'scale':
            # Scaling is cumulative and applied uniformly along the axis.
            scale_amount = sum(mouse.velocity) * config.GIZMO_DRAG_SENSITIVITY / 2
            current_scale = getattr(target.scale, self.axis.name)  # Get e.g., target.scale.x
            setattr(target.scale, self.axis.name, current_scale + scale_amount)

    def drop(self):
        """Called when the drag is released."""
        super().drop()

        # Apply grid snapping after the drag is complete for Move and Scale tools.
        if self.handle_type == 'move' and window.app.editor_state.grid_snap_enabled:
            gs = window.app.editor_state.grid_size
            pos = self.gizmo_parent.target.position
            self.gizmo_parent.target.position = Vec3(round(pos.x / gs) * gs, round(pos.y / gs) * gs,
                                                     round(pos.z / gs) * gs)

        # Ensure scale doesn't go to zero or negative, which can cause issues.
        if self.handle_type == 'scale':
            target = self.gizmo_parent.target
            target.scale = Vec3(max(target.scale.x, 0.1), max(target.scale.y, 0.1), max(target.scale.z, 0.1))


# =============================================================================
# --- THE MAIN GIZMO CONTAINER ---
# =============================================================================
class Gizmo(Entity):
    def __init__(self, **kwargs):
        super().__init__(enabled=False, **kwargs)  # Start disabled until an object is selected
        self._target = None
        self.current_tool = 'select'

        self.handles = {'move': [], 'rotate': [], 'scale': []}

        # --- Create Move Handles (Arrows) ---
        move_handles_parent = Entity(parent=self)
        self.handles['move'].extend([
            GizmoHandle(self, 'move', Vec3(1, 0, 0), config.GIZMO_MOVE_COLORS['x'], model='arrow',
                        rotation=(0, 0, -90)),
            GizmoHandle(self, 'move', Vec3(0, 1, 0), config.GIZMO_MOVE_COLORS['y'], model='arrow'),
            GizmoHandle(self, 'move', Vec3(0, 0, 1), config.GIZMO_MOVE_COLORS['z'], model='arrow', rotation=(90, 0, 0))
        ])

        # --- Create Rotate Handles (Rings) ---
        rotate_handles_parent = Entity(parent=self)
        self.handles['rotate'].extend([
            GizmoHandle(self, 'rotate', Vec3(1, 0, 0), config.GIZMO_ROTATE_COLORS['x'], model=Circle(24, radius=0.6),
                        scale=2, rotation=(0, 90, 90)),
            GizmoHandle(self, 'rotate', Vec3(0, 1, 0), config.GIZMO_ROTATE_COLORS['y'], model=Circle(24, radius=0.6),
                        scale=2, rotation=(90, 0, 0)),
            GizmoHandle(self, 'rotate', Vec3(0, 0, 1), config.GIZMO_ROTATE_COLORS['z'], model=Circle(24, radius=0.6),
                        scale=2)
        ])

        # --- Create Scale Handles (Cubes) ---
        scale_handles_parent = Entity(parent=self)
        self.handles['scale'].extend([
            GizmoHandle(self, 'scale', Vec3(1, 0, 0), config.GIZMO_SCALE_COLORS['x'], model='cube', scale=0.2,
                        position=(0.8, 0, 0)),
            GizmoHandle(self, 'scale', Vec3(0, 1, 0), config.GIZMO_SCALE_COLORS['y'], model='cube', scale=0.2,
                        position=(0, 0.8, 0)),
            GizmoHandle(self, 'scale', Vec3(0, 0, 1), config.GIZMO_SCALE_COLORS['z'], model='cube', scale=0.2,
                        position=(0, 0, 0.8)),
            GizmoHandle(self, 'scale', Vec3(1, 1, 1), color.light_gray, model='cube', scale=0.25, position=(0, 0, 0))
            # Uniform scale
        ])

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value
        # Automatically enable/disable the entire gizmo when a target is set.
        self.enabled = bool(value)

    def set_tool(self, tool_name):
        """Shows and hides the handle sets based on the active tool."""
        self.current_tool = tool_name
        for tool, handle_list in self.handles.items():
            is_active = (tool == tool_name)
            for handle in handle_list:
                handle.enabled = is_active
                handle.visible = is_active

    def update(self):
        if self.target:
            # The gizmo constantly syncs its position with its target.
            self.position = self.target.world_position
            # For move and scale, the gizmo should align with the world axes for clarity.
            # For rotate, it should align with the object's local rotation.
            if self.current_tool == 'rotate':
                self.rotation = self.target.world_rotation
            else:
                self.rotation = Vec3.zero()
```

### File: `/scene/objects.py`

```python
from ursina import *
import config


# --- THE PLAN ---
# This file defines all the physical objects that can exist in our scene.
# It's built on a clear and powerful inheritance model to maximize code reuse
# and minimize bugs.

# 1. A `SceneObject` base class will provide shared functionality for all items:
#    - A selection state and visual feedback (changing color).
#    - A `sound_material` property for the audio engine to read.
#
# 2. Concrete classes like `Speaker` and `SceneWindow` will inherit from `SceneObject`
#    and define their specific appearance (model, color, scale).
#
# 3. A special `ResizeHandle` class for the room will be Draggable, but all other
#    objects will not, as their movement will be controlled by the new Gizmo system.

# =============================================================================
# --- BASE CLASS FOR ALL SELECTABLE OBJECTS ---
# =============================================================================
class SceneObject(Entity):
    def __init__(self, **kwargs):
        """
        The base constructor for all objects in our scene.
        """
        super().__init__(**kwargs)

        # All objects must have a 'sound_material' for the audio engine.
        self.sound_material = 'none'

        # All objects must have a 'collider' so they can be clicked by the mouse.
        # We use 'box' as a simple, efficient default.
        self.collider = 'box'

        # Store the object's original color so we can restore it on deselect.
        self.original_color = self.color

        # Add a name to the entity for easier debugging and identification.
        self.name = f"{type(self).__name__}_{self.id}"

    def select(self):
        """Visual feedback for when the object is selected."""
        self.color = color.yellow.tint(.2)
        # In the future, we could add an outline or other effects here.

    def deselect(self):
        """Removes the selection feedback."""
        self.color = self.original_color


# =============================================================================
# --- ROOM AND ITS RESIZE HANDLES (SPECIAL CASE) ---
# =============================================================================
class ResizeHandle(Draggable):
    """
    A special draggable handle used ONLY for resizing the Room.
    It does not inherit from SceneObject as it's not a selectable sound source.
    """

    def __init__(self, **kwargs):
        super().__init__(model='sphere', scale=.3, color=color.white, plane_direction=(0, 1, 0), **kwargs)
        self.highlight_color = color.azure

    def on_drag(self):
        """Custom logic during drag to apply snapping."""
        if window.app.editor_state.grid_snap_enabled:
            gs = window.app.editor_state.grid_size
            self.position = Vec3(round(self.x / gs) * gs, round(self.y / gs) * gs, round(self.z / gs) * gs)


class Room(Entity):
    """
    The main room object. It's a special case because it's not moved by the
    gizmo, but is resized by its own handles.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.walls = Entity(
            parent=self,
            model='cube',
            texture='white_cube',
            color=color.rgba(200, 200, 200, 20),
            scale=config.INITIAL_ROOM_SCALE
        )
        self.collider = self.walls  # Clicks on the walls should select the room.
        self.name = "Room"
        self.sound_material = 'room'  # This object doesn't make sound but is identifiable.
        self.original_color = self.walls.color

        # The room has its own set of handles for resizing.
        self.handles = {
            'x': ResizeHandle(parent=self, lock=(0, 1, 1), color=color.red),
            'y': ResizeHandle(parent=self, lock=(1, 0, 1), color=color.green),
            'z': ResizeHandle(parent=self, lock=(1, 1, 0), color=color.blue),
        }
        self.update_handle_positions()
        self.deselect()  # Start with handles hidden.

    def update(self):
        # The room's update loop checks if any of its handles are being dragged.
        if any(h.dragging for h in self.handles.values()):
            for axis, handle in self.handles.items():
                if handle.dragging:
                    # Update wall scale based on the handle's world position.
                    scale_val = abs(getattr(handle, f'world_{axis}') - getattr(self, f'world_{axis}')) * 2
                    setattr(self.walls, f'scale_{axis}', scale_val)
            self.update_handle_positions()

    def update_handle_positions(self):
        s = self.walls.scale
        self.handles['x'].world_position = (self.world_x + s.x / 2, self.y, self.z)
        self.handles['y'].world_position = (self.x, self.world_y + s.y / 2, self.z)
        self.handles['z'].world_position = (self.x, self.y, self.world_z + s.z / 2)

    def select(self):
        """When the room is selected, show its walls in yellow and enable handles."""
        self.walls.color = color.yellow.tint(.2)
        for h in self.handles.values(): h.enable()

    def deselect(self):
        """When deselected, return to original color and hide handles."""
        self.walls.color = self.original_color
        for h in self.handles.values(): h.disable()


# =============================================================================
# --- GIZMO-COMPATIBLE SCENE OBJECTS ---
# =============================================================================

class Speaker(SceneObject):
    def __init__(self, **kwargs):
        super().__init__(model='diamond', color=color.orange, scale=0.7, **kwargs)
        self.sound_material = 'drizzle'


class SceneWindow(SceneObject):
    def __init__(self, material='glass', **kwargs):
        super().__init__(model='quad', scale=(2, 2.5), **kwargs)
        self.set_sound_material(material)

    def set_sound_material(self, material_name):
        self.sound_material = material_name.lower()
        # Set appearance based on material.
        if self.sound_material == 'glass':
            self.color = color.rgba(173, 216, 230, 150)
        else:  # Default/fallback appearance
            self.color = color.white
        self.original_color = self.color

    def deselect(self):
        """Overridden to restore material color instead of just a single color."""
        self.set_sound_material(self.sound_material)


class ModifierShape(SceneObject):
    def __init__(self, material_type='tarp', **kwargs):
        # We add some vertical offset so it doesn't z-fight with the grid.
        super().__init__(model='cube', scale=(3, 0.1, 3), y=0.05, **kwargs)
        self.sound_material = material_type
        # Set appearance based on material type.
        if material_type == 'tarp':
            self.color = color.rgba(0, 100, 200, 150)
        elif material_type == 'tin':
            self.color = color.rgba(150, 150, 150, 200)
        self.original_color = self.color
```

### File: `/scene/scene_manager.py`

```python
from ursina import *
import config

# --- THE PLAN ---
# This class is the definitive authority on what exists in the 3D scene.
# Its responsibilities are:
# 1. To create the initial scene, including lighting and the main room.
# 2. To provide public methods for adding new objects to the scene
#    (e.g., `add_object('speaker')`), which will be called by the UI.
# 3. To handle the deletion of objects from the scene.
# 4. To keep a master list of all "sound source" objects, which it provides
#    to the AudioEngine.
# 5. To manage the transform Gizmo, telling it which entity to attach to
#    based on the current selection state.
#
# This design is highly scalable. To add a new type of object to the application,
# we would only need to define its class in `objects.py` and add a new
# creation case in the `add_object` method here. No other files would need to change.

from .objects import Room, SceneWindow, Speaker, ModifierShape
from .gizmo import Gizmo


class SceneManager:
    def __init__(self):
        """Initializes the SceneManager and creates core scene components."""
        print("Initializing SceneManager...")
        self.editor_state = window.app.editor_state
        self.selection_manager = window.app.selection_manager

        self.room = None
        self.sound_sources = []

        # The Gizmo is a core part of the scene, controlled by this manager.
        self.gizmo = Gizmo()

    def setup_initial_scene(self):
        """Creates the lights, ground plane, and the initial room."""
        print("Setting up initial scene...")

        # -- Lighting --
        # A soft ambient light to fill in shadows.
        AmbientLight(color=color.rgba(100, 100, 100, 255))
        # A directional light to create highlights and a sense of direction.
        DirectionalLight(color=color.rgba(150, 150, 150, 255), direction=(1, -1, -1))

        # -- Ground Plane --
        # An infinite grid to help with spatial awareness.
        Entity(model=Grid(100, 100), rotation_x=90, color=color.dark_gray.tint(0.2))

        # -- The Room --
        # The one and only room object.
        self.room = Room(position=(0, config.INITIAL_ROOM_SCALE[1] / 2, 0))

    def add_object(self, obj_type: str, material: str = None):
        """
        Factory method for creating and adding new objects to the scene.
        Called by the UI buttons.
        """
        camera = window.app.camera_controller.camera

        # Calculate a spawn position 10 units in front of the camera.
        spawn_pos = camera.world_position + camera.forward * 10

        new_obj = None

        if obj_type == 'speaker':
            new_obj = Speaker(position=spawn_pos)
        elif obj_type == 'window':
            new_obj = SceneWindow(material='glass', position=spawn_pos)
        elif obj_type == 'modifier' and material:
            new_obj = ModifierShape(material_type=material, position=spawn_pos)

        if new_obj:
            print(f"Created new object: {type(new_obj).__name__}")
            # All objects except the room itself are potential sound sources.
            self.sound_sources.append(new_obj)

            # After creating the object, we immediately select it for a smooth workflow.
            self.selection_manager.select_entity(new_obj, from_code=True)

        return new_obj

    def delete_selected_object(self):
        """Deletes the currently selected object if it's not the room."""
        entity = self.editor_state.selected_entity
        if entity and entity != self.room:
            print(f"Deleting object: {entity.name}")

            # If the object is a sound source, remove it from our list.
            if entity in self.sound_sources:
                self.sound_sources.remove(entity)

            # Deselect it first to clear any UI/Gizmo state.
            self.selection_manager.select_entity(None, from_code=True)

            # Destroy the entity from the scene graph.
            destroy(entity)
        elif entity == self.room:
            print("Cannot delete the main room.")

    def get_all_sound_sources(self):
        """Returns the list of objects for the audio engine."""
        return self.sound_sources

    def input(self, key):
        """
        Handles input related to scene management, like hotkeys for tools or deletion.
        """
        # --- Tool Hotkeys ---
        if key == 'q': self.editor_state.set_active_tool('select')
        if key == 'w': self.editor_state.set_active_tool('move')
        if key == 'e': self.editor_state.set_active_tool('rotate')
        if key == 'r': self.editor_state.set_active_tool('scale')

        # --- Deletion Hotkey ---
        if key == 'delete':
            self.delete_selected_object()

    def update(self):
        """
        Called every frame by the main application. Handles continuous logic,
        primarily keeping the Gizmo in sync with the current selection.
        """
        # Ensure the gizmo is attached to the currently selected entity.
        if self.gizmo.target != self.editor_state.selected_entity:
            self.gizmo.target = self.editor_state.selected_entity

        # The gizmo needs to know which tool is active.
        if self.gizmo.current_tool != self.editor_state.active_tool:
            self.gizmo.set_tool(self.editor_state.active_tool)
```

### File: `/ui/base_panel.py`

```python
from ursina import *
import config


# --- THE PLAN ---
# This class is a template for all our UI panels.
# Its responsibilities are:
# 1. To create a consistent-looking panel background using settings from `config.py`.
# 2. To automatically create a title bar for the panel.
# 3. To provide a `content_parent` entity, which is a neat container where all
#    the buttons and sliders of child panels will be placed.
# 4. To use a `ListLayout` to automatically organize all the content vertically,
#    saving us a lot of manual positioning code.
#
# By inheriting from this class, both `SoundscapePanel` and `EditorPanel` will
# instantly have a professional, consistent look and feel with minimal code.

class BasePanel(Entity):
    def __init__(self, title, position, **kwargs):
        """
        The base constructor for all UI panels.

        :param title: The text to display in the panel's title bar.
        :param position: The screen position for the panel (e.g., window.left).
        """
        # --- Main Panel Entity ---
        # This is the semi-transparent background quad.
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=config.PANEL_SCALE,
            position=position,
            color=config.UI_THEME['panel_background'],
            **kwargs
        )

        # --- Title Bar ---
        # A separate entity for the title text to give it a distinct look.
        Text(
            parent=self,
            text=title,
            scale=1.2,  # Relative to the panel's scale
            origin=(0, -0.5),
            y=0.48,  # Positioned at the very top of the panel
            color=config.UI_THEME['title_color']
        )

        # --- Separator Line ---
        # A thin line to visually separate the title from the content.
        Entity(
            parent=self,
            model='quad',
            scale=(0.95, 0.005),
            y=0.44,
            color=config.UI_THEME['seperator_color']
        )

        # --- Content Area ---
        # This is the most important part. We create a dedicated, scrolling entity
        # that will hold all the buttons, sliders, etc.
        self.content_parent = Entity(
            parent=self,
            model='quad',
            color=color.clear,  # Invisible, just for layout
            scale=(0.95, 0.85),
            y=-0.05
        )

        # --- Auto-Layout ---
        # We attach a ListLayout to the content parent. Any UI element parented
        # to it will automatically be arranged in a vertical list with consistent
        # spacing. This is a massive time-saver.
        self.layout = ListLayout(
            parent=self.content_parent,
            y=-0.5,  # Start from the top
            spacing=0.01,
            dynamic=False  # We will manually add items
        )
```

### File: `/ui/editor_panel.py`

```python
from ursina import *
from .base_panel import BasePanel
import config


# --- THE PLAN ---
# This is the final script, defining the right-hand UI panel for scene editing.
# Its responsibilities are:
# 1. Inherit from `BasePanel` for consistent styling.
# 2. Create UI widgets for editor functions:
#    - A `ButtonGroup` for selecting the active tool (Select, Move, Rotate, Scale).
#    - Buttons for creating new scene objects.
#    - A "Delete" button.
# 3. Create a dynamic "Inspector" section that changes its content based on
#    what object is currently selected. For example, it will show a "Symmetry"
#    toggle only when the Room is selected.
# 4. Connect all these widgets to the appropriate managers (`SceneManager`, `EditorState`).

class EditorPanel(BasePanel):
    def __init__(self, scene_manager, editor_state, selection_manager, **kwargs):
        """
        Initializes the Editor Panel.

        :param scene_manager: Reference to the app's SceneManager.
        :param editor_state: Reference to the app's EditorState.
        """
        # Call the parent BasePanel constructor.
        super().__init__(
            title='Editor',
            position=config.RIGHT_PANEL_POSITION,
            **kwargs
        )

        # Store references to the managers this panel needs to interact with.
        self.scene_manager = scene_manager
        self.editor_state = editor_state
        self.selection_manager = selection_manager

        # --- Create Static UI Sections ---
        # These sections are always visible.
        self._create_tool_selection()
        self._create_object_creation_buttons()

        # Spacer for visual separation.
        Entity(parent=self.layout, model='quad', scale=(1, 0.2), color=color.clear)

        # --- Create Dynamic Inspector Section ---
        # This will hold widgets that appear/disappear based on selection.
        self.inspector_layout = self._create_inspector_section()

        # A "Delete" button is part of the inspector but often shown.
        self.delete_button = Button(
            parent=self.inspector_layout,
            text='Delete Selected',
            color=color.red.tint(-.2),
            highlight_color=color.red,
            scale=(.95, .1)
        )
        self.delete_button.on_click = self.scene_manager.delete_selected_object
        self.delete_button.tooltip = Tooltip("Deletes the selected object (hotkey: DEL)")

        # --- Link Inspector to Selection Changes ---
        # This is a crucial connection. We tell the SelectionManager that whenever
        # a selection changes, it should call our `update_inspector` method.
        self.selection_manager.on_selection_changed = self.update_inspector

    def _create_tool_selection(self):
        """Creates the 'Select, Move, Rotate, Scale' tool buttons."""
        Text(parent=self.layout, text='Tools', scale=1.1, origin=(-.5, 0), x=-0.45)

        tools = ButtonGroup(['select', 'move', 'rotate', 'scale'], min_selection=1, default='select')
        tools.parent = self.layout
        tools.scale = (.95, .08)

        # Connect the ButtonGroup's value change to the EditorState's method.
        # This is peak decoupling: the UI just reports the change to the state.
        tools.on_value_change = Func(self.editor_state.set_active_tool, tools.value)

    def _create_object_creation_buttons(self):
        """Creates the 'Add...' buttons."""
        Text(parent=self.layout, text='Create', scale=1.1, origin=(-.5, 0), x=-0.45)

        Button(parent=self.layout, text='Add Speaker', on_click=Func(self.scene_manager.add_object, 'speaker'),
               scale=(.95, .08))
        Button(parent=self.layout, text='Add Window', on_click=Func(self.scene_manager.add_object, 'window'),
               scale=(.95, .08))
        Button(parent=self.layout, text='Add Tarp Zone',
               on_click=Func(self.scene_manager.add_object, 'modifier', 'tarp'), scale=(.95, .08))
        Button(parent=self.layout, text='Add Tin Zone', on_click=Func(self.scene_manager.add_object, 'modifier', 'tin'),
               scale=(.95, .08))

    def _create_inspector_section(self):
        """Creates the container and specific widgets for the inspector."""
        Text(parent=self.layout, text='Inspector', scale=1.1, origin=(-.5, 0), x=-0.45)

        # The inspector has its own layout so we can show/hide the whole group.
        inspector_container = Entity(parent=self.layout, scale=(.95, .9))
        inspector_layout = ListLayout(parent=inspector_container, y=-0.5, spacing=0.01)

        self.inspector_text = Text(parent=inspector_layout, text="No object selected.")

        # Create all possible inspector widgets now, but keep them disabled.
        # We will enable them as needed.
        self.symmetry_switch = Button(
            parent=inspector_layout,
            text='Toggle Symmetry',
            on_click=self.toggle_room_symmetry,
            scale=(.95, .08),
            enabled=False
        )
        return inspector_layout

    def toggle_room_symmetry(self):
        """A specific UI callback for the symmetry button."""
        entity = self.editor_state.selected_entity
        from scene.objects import Room
        if isinstance(entity, Room):
            entity.toggle_symmetry()

    def update_inspector(self, entity):
        """
        The core of the dynamic UI. Hides/shows widgets based on the selected entity.
        This is called by the SelectionManager.
        """
        # First, disable all optional widgets.
        self.symmetry_switch.enabled = False
        self.delete_button.enabled = False

        if entity:
            # An object is selected.
            self.inspector_text.text = f"Selected: {entity.name}"
            self.delete_button.enabled = True

            # Now, show context-specific widgets.
            from scene.objects import Room
            if isinstance(entity, Room):
                self.symmetry_switch.enabled = True
                self.delete_button.enabled = False  # Can't delete the room
        else:
            # Nothing is selected.
            self.inspector_text.text = "No object selected."
```

### File: `/ui/soundscape_panel.py`

```python
from ursina import *
from .base_panel import BasePanel
import config


# --- THE PLAN ---
# This class defines the left-hand UI panel for controlling global audio.
# Its responsibilities are:
# 1. To inherit all the visual styling and layout capabilities from `BasePanel`.
# 2. To create the specific UI widgets for audio control (sliders and a toggle button).
# 3. To connect each widget to the appropriate function in the `AudioEngine`.
#
# Thanks to our architecture, this class is extremely focused. It doesn't need
# to know about scene objects, selection, or tools—only audio parameters.

class SoundscapePanel(BasePanel):
    def __init__(self, audio_engine, **kwargs):
        """
        Initializes the Soundscape Panel.

        :param audio_engine: A direct reference to the app's audio engine.
        """
        # Call the parent BasePanel constructor to create the panel background and title.
        super().__init__(
            title='Soundscape',
            position=config.LEFT_PANEL_POSITION,
            **kwargs
        )

        # We need a reference to the audio engine to control its parameters.
        self.audio_engine = audio_engine

        # --- Create and Add Widgets to the Auto-Layout ---
        # The self.layout was created by the BasePanel. Any entity parented to it
        # will be automatically arranged in a vertical list.

        # Master Volume Slider
        self._create_slider(
            name='master_volume',
            text='Master Volume',
            default=config.AUDIO_DEFAULT_MASTER_VOLUME
        )

        # Drizzle Intensity Slider
        self._create_slider(
            name='drizzle_intensity',
            text='Drizzle',
            default=config.AUDIO_DEFAULT_DRIZZLE_INTENSITY
        )

        # Wind Intensity Slider
        self._create_slider(
            name='wind_intensity',
            text='Wind',
            default=config.AUDIO_DEFAULT_WIND_INTENSITY
        )

        # Window Openness Slider
        self._create_slider(
            name='window_openness',
            text='Openness',
            default=config.AUDIO_DEFAULT_WINDOW_OPENNESS
        )

        # Spacer to create some visual separation.
        Entity(parent=self.layout, model='quad', scale=(1, 0.2), color=color.clear)

        # Headphone Mode Button
        # We store the button as a member variable so we can change its color.
        self.headphone_button = Button(
            parent=self.layout,
            text='Headphone Mode',
            color=config.UI_THEME['button'],
            highlight_color=config.UI_THEME['button_hover'],
            scale=(.95, .1),
        )
        self.headphone_button.on_click = self.toggle_headphone_mode
        self.headphone_button.tooltip = Tooltip(
            "Toggles between multi-speaker simulation\nand 3D binaural audio for headphones.")

    def _create_slider(self, name, text, default):
        """A helper function to create a labeled slider and add it to the layout."""
        # A container to hold the text label and the slider together.
        container = Entity(parent=self.layout, scale=(.95, .08))

        Text(parent=container, text=text, origin=(-.5, 0), x=-0.5, color=config.UI_THEME['text_color'])

        slider = Slider(
            parent=container,
            min=0,
            max=100,
            default=default,
            x=0.15,
            scale=0.7,
            knob_color=config.UI_THEME['slider_knob'],
        )

        # The magic connection: when the slider's value changes, call the audio engine's function.
        slider.on_value_changed = Func(self.audio_engine.update_global_param, name, slider.value)

    def toggle_headphone_mode(self):
        """Updates the button's appearance and tells the audio engine to switch modes."""
        # A simple toggle based on the button's current color.
        is_on = (self.headphone_button.color == config.UI_THEME['button_hover'])
        new_state = not is_on

        # Update button visual
        self.headphone_button.color = config.UI_THEME['button_hover'] if new_state else config.UI_THEME['button']
        self.headphone_button.text = "Headphone Mode (ON)" if new_state else "Headphone Mode (OFF)"

        # Tell the engine to switch
        self.audio_engine.toggle_headphone_mode(new_state)
```

### File: `/ui/ui_manager.py`

```python
from ursina import *

# --- THE PLAN ---
# This class acts as the main controller for all UI-related elements.
# Its responsibilities are:
# 1. To instantiate and hold references to all major UI panels (in our case,
#    the left 'Soundscape' panel and the right 'Editor' panel).
# 2. To act as a central hub for any high-level UI logic. For now, its role
#    is primarily initialization, but in a larger application, it might handle
#    things like opening/closing modal dialogs, managing themes, or coordinating
#    updates between multiple panels.
# 3. To connect UI elements to the application's backend logic. While the panels
#    will handle their own button clicks, the UIManager is what provides them
#    with the necessary references to the other managers (like SceneManager or
#    AudioEngine).
#
# This design keeps our main `soundscape_app.py` clean, as all UI setup is
# delegated to this specialized manager.

# We will import the panels we are about to create.
from .soundscape_panel import SoundscapePanel
from .editor_panel import EditorPanel
import config


class UIManager:
    def __init__(self):
        """
        Initializes the UIManager and creates all the main UI panels.
        """
        print("Initializing UIManager...")

        # We need access to the application's core systems to pass them to the panels.
        self.app = window.app

        # Store references to the panels it creates.
        self.soundscape_panel = None
        self.editor_panel = None

        # --- Create the UI Panels ---
        self._create_panels()

        # --- Version Watermark ---
        # A small, non-interactive text element to display the app version.
        Text(
            parent=camera.ui,
            text=f"v{config.EDITOR_VERSION}",
            origin=(1, -1),
            position=window.bottom_right,
            color=color.gray
        )

    def _create_panels(self):
        """
        Instantiates the left and right UI panels.
        """
        print("Creating UI panels...")

        # Create the left panel for soundscape controls.
        self.soundscape_panel = SoundscapePanel(
            audio_engine=self.app.audio_engine  # Pass the audio engine reference
        )

        # Create the right panel for editor controls.
        self.editor_panel = EditorPanel(
            scene_manager=self.app.scene_manager,  # Pass the scene manager reference
            editor_state=self.app.editor_state,  # Pass the editor state reference
            selection_manager=self.app.selection_manager  # Pass the selection manager reference
        )

    def update_inspector(self):
        """
        This is a 'bridge' function. It tells the editor panel to update
        its content based on the currently selected entity.
        This would be called by the SelectionManager after a selection changes.
        """
        # Note: The `soundscape_app.py` doesn't call this yet, but the hook is here
        # for our final script to use. We are building the API for our UI.
        self.editor_panel.update_inspector(self.app.editor_state.selected_entity)
```

### File: `/config.py`

```python
from ursina import color, Vec4

# --- THE PLAN ---
# This file centralizes all application-wide constants and settings.
# By keeping them here, we can easily tweak the application's behavior
# without modifying the core logic. This includes window settings,
# UI styling, default values, and even hotkeys.

# =============================================================================
# --- APPLICATION SETTINGS ---
# =============================================================================
APP_TITLE = "Soundscape Designer"
EDITOR_VERSION = "1.0.0-beta"

# Window settings
BORDERLESS = False
FULLSCREEN = False
WINDOW_SIZE = (1600, 900)
VSYNC = True

# =============================================================================
# --- UI STYLING & SETTINGS ---
# =============================================================================
# We can define a color palette to ensure a consistent UI theme.
# Using Vec4 allows us to control RGBA values (Red, Green, Blue, Alpha).
# Alpha is from 0 (transparent) to 255 (opaque).

UI_THEME = {
    "panel_background": color.dark_gray.tint(-.4),
    "button": color.azure.tint(-.2),
    "button_hover": color.azure,
    "slider_knob": color.light_gray,
    "text_color": color.light_gray,
    "title_color": color.white,
    "seperator_color": color.gray,
}

# Specific UI dimensions and positions
PANEL_WIDTH = 0.2         # 20% of the window width
PANEL_SCALE = (PANEL_WIDTH, 0.95)
LEFT_PANEL_POSITION = (-0.5 + (PANEL_WIDTH / 2), 0)
RIGHT_PANEL_POSITION = (0.5 - (PANEL_WIDTH / 2), 0)

# =============================================================================
# --- EDITOR & SCENE DEFAULTS ---
# =============================================================================
DEFAULT_GRID_SIZE = 1.0
DEFAULT_GRID_SNAP = True
INITIAL_ROOM_SCALE = (10, 4, 10)
INITIAL_CAMERA_POSITION = (0, 5, -30)
BACKGROUND_COLOR = color.dark_gray

# Camera controller settings
CAMERA_ORBIT_SPEED = 200
CAMERA_PAN_SPEED = 15
CAMERA_ZOOM_SPEED = 1.5
CAMERA_ZOOM_MIN = 5
CAMERA_ZOOM_MAX = 100
CAMERA_SMOOTHING = 0.2

# =================================e============================================
# --- GIZMO SETTINGS ---
# =============================================================================
GIZMO_SCALE = 1.0
GIZMO_THICKNESS = 1.2
GIZMO_HOVER_COLOR = color.white
GIZMO_DRAG_SENSITIVITY = 15

# Specific tool colors
GIZMO_MOVE_COLORS = {"x": color.red, "y": color.green, "z": color.blue}
GIZMO_ROTATE_COLORS = {"x": color.red, "y": color.green, "z": color.blue}
GIZMO_SCALE_COLORS = {"x": color.red, "y": color.green, "z": color.blue}

# =============================================================================
# --- AUDIO DEFAULTS ---
# =============================================================================
AUDIO_DEFAULT_MASTER_VOLUME = 70.0
AUDIO_DEFAULT_DRIZZLE_INTENSITY = 20.0
AUDIO_DEFAULT_WIND_INTENSITY = 10.0
AUDIO_DEFAULT_WINDOW_OPENNESS = 100.0

AUDIO_SAMPLE_RATE = 44100
AUDIO_BLOCK_SIZE = 2048

# =============================================================================
# --- PROJECT SAVE/LOAD ---
# =============================================================================
PROJECT_FILE_EXTENSION = ".scape"
PROJECT_AUTOSAVE_INTERVAL_SECONDS = 300  # 5 minutes
DEFAULT_PROJECT_SAVE_PATH = "projects/"
DEFAULT_PROJECT_NAME = "MySoundscape"
```

### File: `/main.py`

```python
import sys
import traceback
import time
from pathlib import Path


# --- THE PLAN ---
# This is the primary entry point for the application. Its role is intentionally minimal:
# 1. Prepare the environment.
# 2. Import the main application class.
# 3. Instantiate and run the application inside a robust error-catching block.
# 4. If a critical, unhandled error occurs anywhere in the application, this
#    top-level catch will log it to a file for easy debugging.

# This approach ensures that even if the app crashes, we get a clear record of
# what happened, preventing silent failures.

def main():
    """
    Initializes and runs the Soundscape Application.
    """
    try:
        # We import here, inside the function, so that any import errors are
        # also caught by our robust error handler.
        from soundscape_app import SoundscapeApp

        print("--- Soundscape Designer Initializing ---")
        app = SoundscapeApp()
        app.run()
        print("--- Soundscape Designer Exited Gracefully ---")

    except Exception as e:
        # --- ROBUST ERROR LOGGING ---
        # This is our safety net. If any part of the application fails spectacularly,
        # we will log the details instead of just crashing.

        # Create a "logs" directory if it doesn't exist.
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)

        # Define a timestamped log file name.
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = log_dir / f"crash_{timestamp}.log"

        print(f"FATAL ERROR: An unhandled exception occurred. Details are being logged to: {log_file_path}")

        # Get the full traceback information.
        exc_type, exc_value, exc_traceback = sys.exc_info()

        # Write the detailed traceback to the log file.
        with open(log_file_path, 'w') as f:
            f.write("--- Soundscape Designer Crash Log ---\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Exception Type: {exc_type.__name__}\n")
            f.write(f"Exception Value: {exc_value}\n")
            f.write("----------------------------------------\n\n")
            f.write("Traceback:\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

        # Also print a simplified traceback to the console for immediate feedback.
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

        # Exit the program with an error code.
        sys.exit(1)


# This standard Python construct ensures that the `main` function is called
# only when this script is executed directly.
if __name__ == '__main__':
    main()
```

### File: `/soundscape_app.py`

```python
import atexit
from ursina import *

# --- THE PLAN ---
# This is the core application class. Its responsibilities are:
# 1. Initialize the Ursina window with settings from our upcoming `config.py`.
# 2. Create and hold instances of all our major "manager" classes. This is a form of
#    dependency injection that keeps our code clean and decoupled.
# 3. Provide a global access point (`window.app`) for other parts of the engine
#    to easily access the managers and application state.
# 4. Run the main `update` and `input` loops, but delegate all the complex logic
#    to the specialized managers (e.g., CameraController, SelectionManager).
# 5. Handle top-level application concerns like a debug FPS counter and graceful shutdown.

# We will be importing classes that we haven't created yet. This is part of the plan.
# As we create each new file, these imports will become valid.

from core.editor_state import EditorState
from core.selection_manager import SelectionManager
from audio.engine import AdvancedAudioEngine
from scene.scene_manager import SceneManager
from scene.camera_controller import CameraController
from project.project_manager import ProjectManager
from ui.ui_manager import UIManager
import config


class SoundscapeApp(Ursina):
    def __init__(self, **kwargs):
        # 1. INITIALIZE URSINA WINDOW
        # We load settings from our dedicated config file.
        super().__init__(
            title=config.APP_TITLE,
            borderless=config.BORDERLESS,
            fullscreen=config.FULLSCREEN,
            size=config.WINDOW_SIZE,
            vsync=config.VSYNC,
            **kwargs
        )

        # This small line is incredibly important. It makes the instance of this class
        # accessible globally via `window.app`, avoiding complex import chains.
        window.app = self

        # 2. CREATE AND "INJECT" MANAGERS
        # We instantiate all our core systems in a clear, organized way.
        print("Initializing managers...")
        self.editor_state = EditorState()
        self.audio_engine = AdvancedAudioEngine()
        self.selection_manager = SelectionManager()
        self.scene_manager = SceneManager()
        self.camera_controller = CameraController()
        self.project_manager = ProjectManager()

        # The UIManager is created last, as it may need references to the other managers
        # to connect UI buttons to their functions.
        self.ui_manager = UIManager()
        print("Managers initialized.")

        # 3. SETUP INITIAL SCENE
        # The SceneManager is responsible for setting up lights and the base room.
        self.scene_manager.setup_initial_scene()

        # We must select the room by default to start.
        self.selection_manager.select_entity(self.scene_manager.room)

        # 4. DEBUG FEATURES
        # A simple FPS counter that can be toggled.
        self.fps_counter = Text(text='0 FPS', origin=(-.5, .5), position=window.top_left, color=color.white,
                                background=True)
        self.fps_counter.enabled = False

        # 5. REGISTER SHUTDOWN HOOK
        # atexit ensures that the audio engine is closed properly, even if the app crashes.
        atexit.register(self.audio_engine.close)

    def update(self):
        """
        Ursina's main update loop. It runs every frame.
        We delegate tasks to our managers to keep this loop clean.
        """
        # Let the camera controller handle its logic (rotation, panning).
        self.camera_controller.update()

        # Let the scene manager handle its logic (e.g., updating the gizmo).
        self.scene_manager.update()

        # Update the audio engine with the camera's current position for 3D sound.
        self.audio_engine.update_sources(
            self.scene_manager.get_all_sound_sources(),
            self.camera_controller.camera.world_position,
            self.camera_controller.camera.right
        )

        # Update debug info if enabled.
        if self.fps_counter.enabled:
            self.fps_counter.text = f"{round(time.fps)} FPS"

    def input(self, key):
        """
        Ursina's main input loop. It captures all keyboard and mouse events.
        """
        # First, give UI elements a chance to process the input. If they use it, stop.
        if mouse.hovered_entity and mouse.hovered_entity.has_ancestor(camera.ui):
            return

        # Let our dedicated managers handle the input they care about.
        self.camera_controller.input(key)
        self.selection_manager.input(key)
        self.scene_manager.input(key)

        # Handle global, top-level hotkeys here.
        if key == 'f1':
            self.fps_counter.enabled = not self.fps_counter.enabled
```
