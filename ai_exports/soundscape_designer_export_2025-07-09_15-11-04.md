# Project Export: soundscape_designer
## Export Timestamp: 2025-07-09T15:11:04.060174
---

## AI Instructions
You are an intelligent scaffolding tool. Your task is to analyze the project's existing structure and conventions to generate boilerplate code for new features. This helps developers start new tasks quickly without writing repetitive setup code.

## Guidelines & Rules
- Analyze the project to identify recurring patterns for modules like API endpoints, UI components, data models, or services.
- Based on a user's request (e.g., 'Generate a new Flask API endpoint named UserProfile'), generate a new file or set of files.
- The generated code must include necessary imports, a basic class or function structure with clear placeholder comments (e.g., `# TODO: Implement user profile retrieval logic`), and adhere strictly to the project's naming conventions and file structure.
- If the project uses a specific framework (e.g., Flask, Django, PyQt), the boilerplate must follow that framework's best practices (e.g., using Blueprints in Flask).
- Provide the complete, generated code in a ready-to-use format, including the full suggested file path.

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
 │   └── app_state_and_events.py
 ├── crash_log.txt
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
     ├── panel_base.py
     ├── properties_panel.py
     ├── status_bar.py
     ├── toolbox_panel.py
     ├── ui_base.py
     └── ui_manager.py

```
## File Contents
### File: `/core/app_state_and_events.py`

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum, auto
from collections import defaultdict

class Tool(Enum): SELECT, MOVE, ROTATE, SCALE = auto(), auto(), auto(), auto()

class Event(Enum):
    TOOL_CHANGED,SELECTION_CHANGED,PROJECT_LOADED,ENTITY_UPDATED,ADD_ENTITY,DELETE_SELECTED,DUPLICATE_SELECTED,SAVE_PROJECT,LOAD_PROJECT,FOCUS_SELECTION,INSPECTOR_VALUE_CHANGED = auto(),auto(),auto(),auto(),auto(),auto(),auto(),auto(),auto(),auto(),auto()

class EventBus:
    def __init__(self): self._subscribers = defaultdict(list)
    def sub(self, et, h): self._subscribers[et].append(h)
    def pub(self, et, *a, **kw): [h(*a,**kw) for h in self._subscribers[et]]

@dataclass
class EditorState: grid_snap_enabled: bool = True; grid_size: float = 1.0

@dataclass
class EntityData:
    uid: int; name: str; entity_type: str
    position: List[float] = field(default_factory=lambda: [0,0,0])
    rotation: List[float] = field(default_factory=lambda: [0,0,0])
    scale: List[float] = field(default_factory=lambda: [1,1,1])
    sound_material: str = 'none'

@dataclass
class AppState:
    project_name: str = "MyScene"; active_tool: Tool = Tool.SELECT
    editor: EditorState = field(default_factory=EditorState)
    entities: Dict[int, EntityData] = field(default_factory=dict)
    selected_entity_uid: Optional[int] = None; next_uid: int = 0
    audio: Dict[str, float] = field(default_factory=lambda: {
        'master_volume':70, 'drizzle_intensity':20, 'wind_intensity':10, 'window_openness':100, 'headphone_mode':0.0
    })
```

### File: `/scene/camera_controller.py`

```python
from ursina import *
class CameraController:
    def __init__(self): self.pivot=Entity()
    def focus(self, pos, dist): camera.animate_position(pos, duration=.2); camera.animate_z(-dist, duration=.2)
    def update(self):
        if held_keys['right mouse']: camera.position += (camera.right*held_keys['d'] - camera.right*held_keys['a'] + camera.forward*held_keys['w'] - camera.forward*held_keys['s'])*time.dt*5
        if held_keys['middle mouse']: camera.y += mouse.velocity.y * 10
        camera.rotation_x -= mouse.velocity.y*held_keys['right mouse']*200
        camera.rotation_y += mouse.velocity.x*held_keys['right mouse']*200
        if mouse.scroll_up: camera.position += camera.forward * 2
        if mouse.scroll_down: camera.position -= camera.forward * 2
```

### File: `/scene/entities.py`

```python
from ursina import *; import config
class BaseEntity(Entity):
    def __init__(self, uid, **kwargs):
        super().__init__(**kwargs); self.uid=uid; self.collider='box'; self.original_color=self.color
    def on_select(self): self.color = config.THEME['button_active'].tint(.3)
    def on_deselect(self): self.color = self.original_color

class Speaker(BaseEntity):
    def __init__(self, **kwargs):
        super().__init__(model='diamond', scale=0.7, color=color.orange, **kwargs)
        self.viz = Entity(parent=self, model='sphere', scale=15, color=color.rgba(0,150,255,30), enabled=False)
    def on_select(self): super().on_select(); self.viz.enable()
    def on_deselect(self): super().on_deselect(); self.viz.disable()

class Modifier(BaseEntity):
    def __init__(self, sound_material, **kwargs):
        super().__init__(model='cube', **kwargs)
        if sound_material == 'tarp': self.color = color.rgba(0,100,200,150)
        else: self.color = color.rgba(150,150,150,200)
        self.original_color = self.color

class Window(BaseEntity):
    def __init__(self, **kwargs): super().__init__(model='quad', color=color.rgba(173,216,230,150), **kwargs)

class Room(BaseEntity):
    def __init__(self, app_state, **kwargs):
        super().__init__(**kwargs)
        self.state = app_state
        self.walls=Entity(parent=self,model='cube',texture='white_cube',color=color.rgba(200,200,200,80),collider='box')
        self.collider=None; invoke(setattr,self,'collider',self.walls,delay=0.01)
        self.original_color=self.walls.color
        self.handles={ax:Draggable(parent=self,model='sphere',scale=.35,color=config.GIZMO_COLORS[ax],lock_axis=ax) for ax in 'xyz'}
        self.update_handle_positions()
    def on_select(self): self.walls.color=config.THEME['button_active'].tint(.1);[h.enable() for h in self.handles.values()]
    def on_deselect(self): self.walls.color=self.original_color;[h.disable() for h in self.handles.values()]
    def update_handle_positions(self): s=self.walls.scale;self.handles['x'].position=(s.x/2,0,0);self.handles['y'].position=(0,s.y/2,0);self.handles['z'].position=(0,0,s.z/2)
    def update(self):
        if any(h.dragging for h in self.handles.values()):
            self.walls.scale_x = abs(self.handles['x'].x)*2; self.walls.scale_y = abs(self.handles['y'].y)*2; self.walls.scale_z = abs(self.handles['z'].z)*2
            self.state.entities[self.uid].scale=list(self.walls.scale)
```

### File: `/scene/entity_factory.py`

```python
from ursina import *;
from typing import Dict, Optional
from core.app_state_and_events import AppState, Event, EventBus, Tool, EntityData
from .entities import BaseEntity, Room, Speaker, Window, Modifier
from .entity_factory import EntityFactory


class SceneManager:
    def __init__(self, state: AppState, bus: EventBus, factory: EntityFactory):
        self.state, self.bus, self.factory = state, bus, factory;
        self.scene_entities: Dict[int, BaseEntity] = {}
        bus.sub(Event.ADD_ENTITY, self.add_entity)
        bus.sub(Event.DELETE_SELECTED, self.delete_selected)
        bus.sub(Event.SELECTION_CHANGED, self.on_selection_changed)
        bus.sub(Event.ENTITY_UPDATED, self.on_entity_updated)
        Entity(model=Grid(100, 100), rotation_x=90, color=color.dark_gray);
        AmbientLight(color=(.4, .4, .4))
        Entity(model='quad', scale=9e3, collider='box', color=color.clear, on_click=lambda: self.select_entity(None))
        self.add_entity(entity_type='Room', scale=config.INITIAL_ROOM_SCALE)

    def add_entity(self, entity_type, **kwargs):
        if 'position' not in kwargs: kwargs['position'] = camera.world_position + camera.forward * 10
        data = self.factory.create(self.state, entity_type, **kwargs)
        e = self._create_scene_entity(data);
        self.select_entity(e)

    def _create_scene_entity(self, data: EntityData):
        emap = {'Room': Room, 'Speaker': Speaker, 'Window': Window, 'Modifier': Modifier}
        cls = emap.get(data.entity_type, BaseEntity);
        params = asdict(data)
        [params.pop(k, None) for k in ['uid', 'name', 'entity_type']]
        if data.entity_type == 'Room': params['app_state'] = self.state
        e = cls(uid=data.uid, **params);
        e.name = data.name;
        self.scene_entities[data.uid] = e
        e.on_click = lambda ev=e: self.bus.pub(Event.SELECTION_CHANGED, ev)
        return e

    def select_entity(self, entity: Optional[BaseEntity]):
        uid = self.state.selected_entity_uid
        if uid in self.scene_entities: self.scene_entities[uid].on_deselect()
        self.state.selected_entity_uid = entity.uid if entity else None
        if self.state.selected_entity_uid in self.scene_entities:
            self.scene_entities[self.state.selected_entity_uid].on_select()
        self.bus.pub(Event.SELECTION_CHANGED, entity)

    def on_selection_changed(self, e):
        pass

    def on_entity_updated(self, uid, **kwargs):
        if uid in self.scene_entities and uid in self.state.entities:
            ent, data = self.scene_entities[uid], self.state.entities[uid]
            for k, v in kwargs.items(): setattr(data, k, v)
            ent.position = Vec3(*data.position);
            ent.rotation = Vec3(*data.rotation);
            ent.scale = Vec3(*data.scale)

    def delete_selected(self):
        uid = self.state.selected_entity_uid
        if uid is not None and self.state.entities[uid].entity_type != 'Room':
            self.select_entity(None);
            destroy(self.scene_entities.pop(uid));
            del self.state.entities[uid]
```

### File: `/scene/gizmo.py`

```python
from ursina import *
import config
from core.app_state_and_events import AppState, Event, EventBus, Tool
from .entities import BaseEntity

class Gizmo(Entity):
    def __init__(self, state: AppState, bus: EventBus):
        super().__init__(enabled=False)
        self.state, self.bus = state, bus
        self.target = None
        bus.sub(Event.TOOL_CHANGED, self.on_tool_changed)

    def on_tool_changed(self, tool: Tool):
        is_move = tool == Tool.MOVE
        self.model = 'arrow' if is_move else None
        if self.target:
            self.enabled = tool != Tool.SELECT

    def update(self):
        if self.target:
            self.position = self.target.position
            if held_keys['g']: # Simple Grab/Move
                self.target.position += mouse.velocity * 5
                self.bus.pub(Event.ENTITY_UPDATED, uid=self.target.uid, position=list(self.target.position))
```

### File: `/scene/scene_manager.py`

```python
from ursina import *
from typing import Dict, Optional, List
from dataclasses import asdict
import copy
import config
from core.app_state_and_events import AppState, Event, EventBus, Tool, EntityData
from .entities import BaseEntity, Room, Speaker, Window, Modifier
from .entity_factory import EntityFactory
from .gizmo import Gizmo


class SceneManager:
    def __init__(self, state: AppState, bus: EventBus, factory: EntityFactory):
        self.state, self.bus, self.factory = state, bus, factory
        self.scene_entities: Dict[int, BaseEntity] = {}
        self.gizmo = Gizmo(state, bus)

        bus.sub(Event.PROJECT_LOADED, self.rebuild_scene)
        bus.sub(Event.ADD_ENTITY, self.add_entity)
        bus.sub(Event.DELETE_SELECTED, self.delete_selected)
        bus.sub(Event.ENTITY_UPDATED, self.on_entity_updated)
        bus.sub(Event.DUPLICATE_SELECTED, self.duplicate_selected)
        bus.sub(Event.SELECTION_CHANGED, self.on_selection_changed)

    def setup_initial_scene(self):
        AmbientLight(color=(.4, .4, .4));
        DirectionalLight(color=(.7, .7, .7), direction=(1, -.7, .5))
        Entity(model=Grid(100, 100), rotation_x=90, color=color.dark_gray)
        Entity(model='quad', scale=9999, collider='box', color=color.clear, on_click=lambda: self.select_entity(None))
        self.add_entity(entity_type='Room', scale=config.INITIAL_ROOM_SCALE)

    def rebuild_scene(self):
        [destroy(e) for e in self.scene_entities.values()];
        self.scene_entities.clear()
        self.select_entity(None)
        for data in self.state.entities.values(): self._create_scene_entity(data)

    def on_entity_updated(self, uid, **kwargs):
        if uid in self.scene_entities and uid in self.state.entities:
            entity, data = self.scene_entities[uid], self.state.entities[uid]
            for key, val in kwargs.items(): setattr(data, key, val)
            entity.position = Vec3(*data.position);
            entity.rotation = Vec3(*data.rotation);
            entity.scale = Vec3(*data.scale)

    def _create_scene_entity(self, data: EntityData):
        entity_map = {'Room': Room, 'Speaker': Speaker, 'Window': Window, 'Modifier': Modifier}
        cls = entity_map.get(data.entity_type)
        if cls:
            params = asdict(data)
            [params.pop(key) for key in ['uid', 'name', 'entity_type']]
            if data.entity_type == 'Room': params['app_state'] = self.state

            new_entity = cls(uid=data.uid, **params)
            new_entity.name = data.name
            new_entity.on_click = lambda e=new_entity: self.bus.pub(Event.SELECTION_CHANGED, e)
            self.scene_entities[data.uid] = new_entity
            return new_entity

    def add_entity(self, entity_type: str, **kwargs):
        data = self.factory.create_entity(self.state, entity_type, **kwargs)
        new_entity = self._create_scene_entity(data)
        self.select_entity(new_entity)

    def select_entity(self, entity: Optional[BaseEntity]):
        uid = self.state.selected_entity_uid
        if uid is not None and uid in self.scene_entities: self.scene_entities[uid].on_deselect()
        self.state.selected_entity_uid = entity.uid if entity else None
        if self.state.selected_entity_uid in self.scene_entities:
            self.scene_entities[self.state.selected_entity_uid].on_select()
        self.bus.pub(Event.SELECTION_CHANGED, entity)

    def on_selection_changed(self, entity: Optional[BaseEntity]):
        is_valid_target = entity and entity.uid in self.state.entities and self.state.entities[
            entity.uid].entity_type != 'Room'
        self.gizmo.target = entity if is_valid_target else None
        self.gizmo.enabled = self.gizmo.target is not None and self.state.active_tool != Tool.SELECT

    def delete_selected(self):
        uid = self.state.selected_entity_uid
        if uid is not None and self.state.entities[uid].entity_type != 'Room':
            self.select_entity(None)
            destroy(self.scene_entities.pop(uid));
            del self.state.entities[uid]

    def duplicate_selected(self):
        uid = self.state.selected_entity_uid
        if uid is None or self.state.entities[uid].entity_type == 'Room': return
        new_data = copy.deepcopy(self.state.entities[uid])
        new_data.position[0] += 1.0
        self.add_entity(from_data=new_data)

    def get_sound_sources(self):
        return [asdict(d) for d in self.state.entities.values() if d.entity_type in ['Speaker', 'Window', 'Modifier']]
```

### File: `/services/audio_service.py`

```python
# /services/audio_service.py
import numpy as np, sounddevice as sd, soundfile as sf, os, random, threading, sys, traceback
from core.app_state_and_events import AppState
class AudioService:
    def __init__(self, state:AppState):
        # ... (full, correct audio service code from a previous working version)
        self.app_state = state
        self.samplerate, self.blocksize, self.channels = 44100, 2048, 2
        self.sources_to_process, self.listener_position, self.listener_right_vec = [], np.array([0,0,0]), np.array([1,0,0])
        self.lock = threading.Lock(); self.wind_playback_pos = 0; self.max_itd_samples = int(0.0007*self.samplerate)
        spos = np.array([[0,0,1],[-1,0,1],[1,0,1],[-1,0,0],[1,0,0],[-1,0,-1],[1,0,-1],[0,1,0]])
        self.speaker_vectors = spos/np.linalg.norm(spos,axis=1)[:,np.newaxis]
        self.downmix = np.array([[.7,.7],[1,.1],[.1,1],[1,.3],[.3,1],[.8,.5],[.5,.8],[.6,.6]])
        self.samples=self._load('audio/sounds/')
        self.stream=self._start()
    def update(self,s,lp,lrv):
        with self.lock: self.sources_to_process,self.listener_position,self.listener_right_vec=s,np.array(lp),np.array(lrv)
    def _start(self):
        try: s=sd.OutputStream(samplerate=self.samplerate,channels=self.channels,callback=self._callback,dtype='f4',blocksize=self.blocksize); s.start(); return s
        except Exception as e: print(f"Audio Error: {e}", file=sys.stderr)
    def _load(self, p):
        if not os.path.exists(p): os.makedirs(p)
        s={'drizzle':[],'glass':[],'tin':[],'tarp':[],'wind':[]}; [s[next((c for c in s if c in f.lower()),'drizzle')].append((lambda d:d if d.ndim==1 else d[:,0])(sf.read(os.path.join(p,f),dtype='f4')[0])) for f in os.listdir(p) if f.lower().endswith('.wav')]; return s
    def _render_b(self,buf,g,sp):
        v,d=sp-self.listener_position,np.linalg.norm(sp-self.listener_position); rd=np.dot(v/d,self.listener_right_vec); gl,gr=np.sqrt(.5*(1-rd)),np.sqrt(.5*(1+rd)); td=int(self.max_itd_samples*rd); p=random.randint(self.max_itd_samples,len(buf)-len(g)-self.max_itd_samples); a=1/(1+d*.5);
        if td>=0: buf[p+td:p+td+len(g),1]+=g*gr*a; buf[p:p+len(g),0]+=g*gl*a
        else: buf[p:p+len(g),1]+=g*gr*a; buf[p-td:p-td+len(g),0]+=g*gl*a
    def _render_s(self,buf,g,sp):
        v,d=sp-self.listener_position,np.linalg.norm(sp-self.listener_position); sg=np.dot(np.maximum(0,np.dot(self.speaker_vectors,v/d))**2,self.downmix); p=random.randint(0,len(buf)-len(g)-1); [buf[p:p+len(g),i]+=g*sg[i]/(1+d*.5) for i in range(2)]
    def _callback(self,out,fr,t,st):
        try:
            b=np.zeros((fr,2),dtype='f4'); params=self.app_state.audio
            render=self._render_b if params['headphone_mode'] else self._render_s
            with self.lock: srcs=list(self.sources_to_process)
            wind_i=params['wind_intensity']/100
            if self.samples.get('wind')and wind_i>0: w,wl=self.samples['wind'][0],len(self.samples['wind'][0]); ind=(self.wind_playback_pos+np.arange(fr))%wl;b+=w[ind,np.newaxis]*wind_i; self.wind_playback_pos=(self.wind_playback_pos+fr)%wl
            drizzle_i=params['drizzle_intensity']/100
            for src in srcs:
                mats=self.samples.get(src['sound_material'],[])
                if mats and random.random()<drizzle_i*.05 and len(mats[0])+self.max_itd_samples<fr: render(b,random.choice(mats),np.array(src['position']))
            b*=params['window_openness']/100; out[:]=np.clip(b*params['master_volume']/100,-1,1)
        except: traceback.print_exc(file=sys.stderr); out.fill(0)
```

### File: `/services/project_service.py`

```python
# /services/project_service.py
import json, copy
from pathlib import Path
from dataclasses import asdict
import config
from core.app_state_and_events import AppState, Event, EventBus, Tool, EntityData
class ProjectService:
    def __init__(self, state:AppState, bus:EventBus):
        self.state,self.bus=state,bus; Path(config.PROJ_PATH).mkdir(parents=True, exist_ok=True)
        bus.sub(Event.SAVE_PROJECT_REQUEST, self.save); bus.sub(Event.LOAD_PROJECT_REQUEST, self.load)
    def save(self, name:str):
        p=Path(config.PROJ_PATH)/(name+config.PROJ_EXT); s=asdict(self.state); s['active_tool']=self.state.active_tool.value
        try: p.write_text(json.dumps(s, indent=4))
        except Exception as e: print(f"Save failed: {e}")
    def load(self, name:str):
        p=Path(config.PROJ_PATH)/(name+config.PROJ_EXT)
        if not p.exists(): return
        try:
            d=json.loads(p.read_text()); s=self.state
            for k,v in d.items():
                if k=='active_tool': s.active_tool=Tool(v)
                elif k=='entities': s.entities={int(k_):EntityData(**v_) for k_,v_ in v.items()}
                elif hasattr(s,k): setattr(s,k,v)
            self.bus.pub(Event.PROJECT_LOADED)
        except Exception as e: print(f"Load failed: {e}")
```

### File: `/ui/panel_base.py`

```python
from ursina import *
import config

class UIPanel(Entity):
    def __init__(self, title, **kwargs):
        super().__init__(parent=camera.ui, model='quad', color=config.THEME['panel_bg'], **kwargs)
        Entity(parent=self, model='quad', scale=(1,0.07/self.scale_y), y=0.5-(0.07/2/self.scale_y), color=config.THEME['header_bg'], z=-1)
        Text(parent=self, text=title, origin=(0,0), y=0.5-(0.07/2/self.scale_y), z=-2)
```

### File: `/ui/properties_panel.py`

```python
# /ui/properties_panel.py
from ursina import *
import config
from typing import Optional
from core.app_state_and_events import AppState, EventBus, Event
from .panel_base import UIPanel
from scene.entities import SceneEntity


class PropertiesPanel(UIPanel):
    def __init__(self, app_state: AppState, event_bus: EventBus, **kwargs):
        super().__init__(title="Properties", **kwargs)
        self.app_state, self.event_bus = app_state, event_bus
        self.content_parent = Entity(parent=self.content)  # For easy clearing
        event_bus.subscribe(Event.SELECTION_CHANGED, self.rebuild)
        event_bus.subscribe(Event.ENTITY_UPDATED, self.rebuild)
        self.rebuild()

    def rebuild(self, entity: Optional[SceneEntity] = None):
        destroy(self.content_parent);
        self.content_parent = Entity(parent=self.content)
        y_cursor = 0.45

        def _label(text, y):
            Text(parent=self.content_parent, text=text, origin=(-0.5, 0.5), y=y, x=-0.5, scale=1.1,
                 color=config.UI_THEME['text_color'])

        # Inspector Section
        uid = self.app_state.selected_entity_uid
        data = self.app_state.entities.get(uid)

        if data:
            _label(f"<b>{data.name}</b>", y_cursor);
            y_cursor -= 0.05
            self._create_vec3_inputs("Position", "position", data, y_cursor);
            y_cursor -= 0.05
            self._create_vec3_inputs("Rotation", "rotation", data, y_cursor);
            y_cursor -= 0.05
            self._create_vec3_inputs("Scale", "scale", data, y_cursor);
            y_cursor -= 0.05
            if data.entity_type != 'Room':
                delete_btn = Button(parent=self.content_parent, text='Delete', scale_y=0.04, y=y_cursor,
                                    color=config.UI_THEME['delete_button'],
                                    text_entity_color=config.UI_THEME['text_color'])
                delete_btn.on_click = lambda: self.event_bus.publish(Event.DELETE_SELECTED_REQUEST)
        else:
            _label("No Object Selected", y_cursor)

        # Global Settings Section
        y_cursor = -0.05
        _label("<b>Global Settings</b>", y_cursor);
        y_cursor -= 0.05
        self._create_slider("Master Vol", 'master_volume', y_cursor);
        y_cursor -= 0.05
        self._create_slider("Drizzle", 'drizzle_intensity', y_cursor);
        y_cursor -= 0.05
        self._create_toggle("Grid Snap", 'editor', 'grid_snap_enabled', y_cursor);
        y_cursor -= 0.05
        self._create_toggle("Audio Mode", 'audio', 'headphone_mode', y_cursor);
        y_cursor -= 0.05

        y_cursor -= 0.05
        _label("<b>Project</b>", y_cursor);
        y_cursor -= 0.05
        self.filename_input = InputField(parent=self.content_parent, default_value=self.app_state.project_name,
                                         y=y_cursor, scale_y=0.04, text_field_color=config.UI_THEME['text_color'])
        y_cursor -= 0.05
        save = Button(parent=self.content_parent, text="Save", scale=(-0.5 + 0.01, 0.04), x=-0.25, y=y_cursor,
                      text_entity_color=config.UI_THEME['text_color'])
        load = Button(parent=self.content_parent, text="Load", scale=(-0.5 + 0.01, 0.04), x=0.25, y=y_cursor,
                      text_entity_color=config.UI_THEME['text_color'])
        save.on_click = lambda: self.event_bus.publish(Event.SAVE_PROJECT_REQUEST, self.filename_input.text)
        load.on_click = lambda: self.event_bus.publish(Event.LOAD_PROJECT_REQUEST, self.filename_input.text)

    def _create_vec3_inputs(self, name, attr, data, y):
        Text(parent=self.content_parent, text=name, y=y, x=-0.45, scale=1.1, color=config.UI_THEME['text_color'])

        def make_submit(i):
            def submit():
                try:
                    new_vec = list(getattr(self.app_state.entities[data.uid], attr)); new_vec[i] = float(
                        inputs[i].text); self.event_bus.publish(Event.INSPECTOR_VALUE_CHANGED, uid=data.uid,
                                                                **{attr: new_vec})
                except:
                    pass

            return submit

        inputs = []
        for i, val in enumerate(getattr(data, attr)):
            field = InputField(parent=self.content_parent, default_value=f"{val:.2f}", y=y, scale=(0.2, 0.04),
                               limit_content_to='0123456789.-')
            field.x = -0.15 + i * 0.22
            field.text_field.color = config.UI_THEME['text_color']
            field.on_submit = make_submit(i);
            inputs.append(field)

    def _create_slider(self, text, key, y):
        Text(parent=self.content_parent, text=text, y=y, x=-0.45, scale=1.1, color=config.UI_THEME['text_color'])
        slider = Slider(parent=self.content_parent, min=0, max=100, default=self.app_state.audio[key], y=y, x=0.1,
                        scale_x=0.6, knob_color=config.UI_THEME['slider_knob'])
        slider.on_value_changed = lambda k=key, s=slider: self.app_state.audio.__setitem__(k, s.value)

    def _create_toggle(self, text, group, key, y):
        Text(parent=self.content_parent, text=text, y=y, x=-0.45, scale=1.1, color=config.UI_THEME['text_color'])
        target, button = getattr(self.app_state, group), Button(parent=self.content_parent, text='', y=y, x=0.1,
                                                                scale_x=0.6, scale_y=0.04)

        def update():
            is_on = bool(target[key]) if isinstance(target, dict) else getattr(target, key)
            button.text, button.color, button.text_entity.color = (('On' if is_on else 'Off')), (
                config.UI_THEME['button_active'] if is_on else config.UI_THEME['button']), config.UI_THEME['text_color']

        def on_click():
            if isinstance(target, dict):
                target[key] = not target[key]
            else:
                setattr(target, key, not getattr(target, key))
            update()

        button.on_click = on_click;
        update()
```

### File: `/ui/status_bar.py`

```python
# /ui/status_bar.py
from ursina import *
import config
from core.app_state_and_events import AppState, EventBus, Event


class StatusBar(Entity):
    def __init__(self, app_state: AppState, event_bus: EventBus, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.app_state = app_state

        # A dark bar at the bottom of the screen
        Entity(parent=self, model='quad', scale=(2, 0.04), y=window.bottom.y + 0.02,
               color=color.black.tint(0.2))

        # Text element for the current tool
        self.tool_text = Text(parent=self, origin=(-0.5, 0), y=window.bottom.y + 0.02, x=-0.5 * window.aspect_ratio)

        # Text element for the current selection
        self.selection_text = Text(parent=self, origin=(0, 0), y=window.bottom.y + 0.02)

        event_bus.subscribe(Event.TOOL_CHANGED, self.update_tool_text)
        event_bus.subscribe(Event.SELECTION_CHANGED, self.update_selection_text)

        # Initial setup
        self.update_tool_text(app_state.active_tool)
        self.update_selection_text(None)

    def update_tool_text(self, tool):
        self.tool_text.text = f"Tool: {tool.name}"

    def update_selection_text(self, entity):
        if entity:
            self.selection_text.text = f"Selected: {entity.name}"
        else:
            self.selection_text.text = "No object selected"
```

### File: `/ui/toolbox_panel.py`

```python
from ursina import *
import config
from .panel_base import UIPanel
from core.app_state_and_events import AppState, Event, EventBus, Tool


class ToolboxPanel(UIPanel):
    def __init__(self, app_state: AppState, event_bus: EventBus, **kwargs):
        super().__init__(title="Toolbox", **kwargs)

        y_cursor = 0.35;
        spacing = 0.1
        self._add_button("Add Speaker", y_cursor, lambda: event_bus.pub(Event.ADD_ENTITY, entity_type='Speaker'))
        y_cursor -= spacing
        self._add_button("Add Window", y_cursor,
                         lambda: event_bus.pub(Event.ADD_ENTITY, entity_type='Window', sound_material='glass'))

        y_cursor -= 0.15
        self.tool_buttons = {tool: self._add_tool_button(tool, i, y_cursor) for i, tool in enumerate(Tool)}

        event_bus.sub(Event.TOOL_CHANGED, self.on_tool_change)
        self.on_tool_change(app_state.active_tool)

    def _add_button(self, text, y, func):
        btn = Button(parent=self, text=text, scale=(0.85, 0.08), y=y)
        self._style_button(btn);
        btn.on_click = func

    def _add_tool_button(self, tool, i, y):
        x_pos = -0.3 + (i * 0.2)
        btn = Button(parent=self, text=tool.name[0], scale=0.15, y=y, x=x_pos)
        btn.on_click = lambda t=tool: self.event_bus.pub(Event.TOOL_CHANGED, t)
        return btn

    def on_tool_change(self, tool):
        for t, btn in self.tool_buttons.items(): self._style_button(btn, is_active=(t == tool))

    def _style_button(self, btn, is_active=False):
        btn.color = config.THEME['button_active'] if is_active else config.THEME['button']
        btn.text_entity.color = config.THEME['text']
```

### File: `/ui/ui_base.py`

```python
# /ui/ui_base.py
from ursina import *
import config


class DraggableWindow(Draggable):
    def __init__(self, title: str, **kwargs):
        # We pop the scale so it's only used once by the Draggable constructor.
        window_scale = kwargs.pop('scale', (1, 1))

        super().__init__(
            scale=window_scale,
            origin=(0, 0),
            lock=(0, 0, 1),
            color=color.clear,
            **kwargs
        )

        # This background entity is now the ONLY scaled element.
        # All future children are parented to `self`, NOT to this.
        self.background = Entity(parent=self, model='quad', scale=1, color=config.UI_THEME['panel_background'], z=0.1)

        # The title bar for dragging and labelling
        self.title_bar = Button(
            parent=self,
            model='quad',
            text=title,
            scale=(1, 0.08),
            y=0.5 - (0.08 / 2),
            color=config.UI_THEME['header_background'],
            highlight_color=config.UI_THEME['header_background'],  # No color change on hover
        )
        self.title_bar.text_entity.color = config.UI_THEME['title_color']

        # Make the window draggable only by its title bar
        self.drag_handle = self.title_bar

        self.y_cursor = 0.4  # Start cursor just below the title bar.
```

### File: `/ui/ui_manager.py`

```python
# /ui/ui_manager.py
from ursina import *
import config
from core.app_state_and_events import AppState, EventBus
from .toolbox_panel import ToolboxPanel
from .properties_panel import PropertiesPanel

class UIManager:
    def __init__(self, app_state: AppState, event_bus: EventBus):
        self.toolbox = ToolboxPanel(app_state, event_bus,
            scale = (config.PANEL_WIDTH, 0.5),
            position = (window.left.x + config.PANEL_WIDTH/2 + 0.02, 0)
        )
        self.properties = PropertiesPanel(app_state, event_bus,
            scale = (config.PANEL_WIDTH, 0.95),
            position = (window.right.x - config.PANEL_WIDTH/2 - 0.02, 0)
        )
        Text(f"v{config.VERSION}", origin=(1,-1), position=window.bottom_right)
```

### File: `/app.py`

```python
import sys, traceback, atexit
from ursina import *
import config
from core.app_state_and_events import AppState, Event, EventBus, EntityData
from scene.entities import BaseEntity, Room, Speaker
from ui.ui_manager import UIManager


class SoundscapeApp(Ursina):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        window.color = config.BACKGROUND_COLOR;
        window.exit_button.visible = False;
        camera.clip_plane_near = 0.1
        self.state = AppState();
        self.bus = EventBus();
        self.scene_entities = {}

        # Bind events
        self.bus.sub(Event.ADD_ENTITY, self.add_entity)
        self.bus.sub(Event.SELECTION_CHANGED, self.on_selection_changed)
        self.bus.sub(Event.TOOL_CHANGED, lambda tool: setattr(self.state, 'active_tool', tool))
        self.bus.sub(Event.ENTITY_UPDATED, self.on_entity_updated)

        # Setup Scene
        AmbientLight(color=(.4, .4, .4));
        DirectionalLight(color=(.7, .7, .7), direction=(1, -1, 1))
        Entity(model=Grid(100, 100), rotation_x=90, color=color.dark_gray)
        Entity(model='quad', scale=9999, collider='box', color=color.clear, on_click=lambda: self.select_entity(None))

        # Setup UI
        self.ui_manager = UIManager(self.state, self.bus)

        # Create initial Room
        invoke(self.add_entity, entity_type='Room', scale=config.INITIAL_ROOM_SCALE, delay=0.01)

    def on_selection_changed(self, entity):
        uid = self.state.selected_uid
        if uid is not None and uid in self.scene_entities: self.scene_entities[uid].deselect()
        self.state.selected_uid = entity.uid if entity else None
        if self.state.selected_uid is not None: self.scene_entities[self.state.selected_uid].select()

    def on_entity_updated(self, uid, **kwargs):
        if uid in self.scene_entities:
            entity, data = self.scene_entities[uid], self.state.entities[uid]
            for key, val in kwargs.items(): setattr(data, key, val)
            entity.position = Vec3(*data.position);
            entity.rotation = Vec3(*data.rotation);
            entity.scale = Vec3(*data.scale)

    def add_entity(self, entity_type, **kwargs):
        uid = self.state.next_uid;
        self.state.next_uid += 1
        name = f"{entity_type}_{uid}"
        self.state.entities[uid] = EntityData(uid=uid, name=name, entity_type=entity_type, **kwargs)
        data = self.state.entities[uid]

        map = {'Room': Room, 'Speaker': Speaker}
        cls = map.get(entity_type, Speaker)
        params = {'uid': uid, 'position': Vec3(*data.position), 'scale': Vec3(*data.scale)}
        if entity_type == 'Room': params['state'] = self.state

        new_entity = cls(**params)
        new_entity.on_click = lambda e=new_entity: self.bus.pub(Event.SELECTION_CHANGED, e)
        self.scene_entities[uid] = new_entity
        self.bus.pub(Event.SELECTION_CHANGED, new_entity)

    def update(self):
        if held_keys['right mouse']:
            camera.rotation_y += mouse.velocity.x * 200
            camera.rotation_x -= mouse.velocity.y * 200


if __name__ == '__main__':
    app = SoundscapeApp(title=config.APP_TITLE, size=config.WINDOW_SIZE)
    app.run()
```

### File: `/config.py`

```python
from ursina import color, Vec3

# --- App & UI ---
APP_TITLE = "Soundscape Designer"; VERSION = "5.0-FINAL"
WINDOW_SIZE = (1600, 900); BACKGROUND_COLOR = color.dark_gray.tint(-.2)
PANEL_WIDTH = 0.2
THEME = {
    "panel_bg": color.dark_gray.tint(-.65), "header_bg": color.black.tint(.2),
    "button": color.azure.tint(-.3), "button_hover": color.azure.tint(-.1),
    "button_active": color.cyan.tint(-.2), "text": color.light_gray.tint(.3)
}
# --- Scene ---
INITIAL_ROOM_SCALE = Vec3(15, 6, 15); INITIAL_CAM_POS = (0, 10, -35)
GIZMO_COLORS = {"x":color.red, "y":color.green, "z":color.blue}
```

### File: `/crash_log.txt`

```text
Traceback (most recent call last):
  File "C:\Users\gike5\Desktop\AI Python\soundscape_designer\main.py", line 3, in <module>
    try: runpy.run_path('app.py', run_name='__main__')
  File "C:\Users\gike5\AppData\Local\Programs\Python\Python310\lib\runpy.py", line 289, in run_path
    return _run_module_code(code, init_globals, run_name,
  File "C:\Users\gike5\AppData\Local\Programs\Python\Python310\lib\runpy.py", line 96, in _run_module_code
    _run_code(code, mod_globals, init_globals,
  File "C:\Users\gike5\AppData\Local\Programs\Python\Python310\lib\runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "app.py", line 5, in <module>
    from scene.scene_manager import SceneManager
  File "C:\Users\gike5\Desktop\AI Python\soundscape_designer\scene\scene_manager.py", line 8, in <module>
    from .entity_factory import EntityFactory
  File "C:\Users\gike5\Desktop\AI Python\soundscape_designer\scene\entity_factory.py", line 5, in <module>
    from .entity_factory import EntityFactory
ImportError: cannot import name 'EntityFactory' from partially initialized module 'scene.entity_factory' (most likely due to a circular import) (C:\Users\gike5\Desktop\AI Python\soundscape_designer\scene\entity_factory.py)

```

### File: `/main.py`

```python
import runpy, sys, traceback

if __name__ == '__main__':
    try:
        runpy.run_path('app.py', run_name='__main__')
    except Exception:
        with open("crash_log.txt", 'w') as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
        sys.exit(1)
```
