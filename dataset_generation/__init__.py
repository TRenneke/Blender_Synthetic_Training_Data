bl_info = {
    "name": "Synthetic Data Generation",
    "blender": (3, 4, 0),
    "category": "Rendering",
    "author": "Tilman Renneke",
    "version": (0, 0, 1),
}

# ----------------------------------------------
# Import modules
# ----------------------------------------------
if "bpy" in locals():
    import importlib
    importlib.reload(sdg_utils)
    importlib.reload(sdg_randomisation)
else:
    from . import sdg_utils
    from . import sdg_randomisation


import bpy
from bpy.app.handlers import persistent
import os
import random

backup_path = "temp.blend"
default_context = None
randomisation: sdg_randomisation.Randomization = None
def getDatasetPath(scene: bpy.types.Scene):
    return os.path.dirname(os.path.dirname(scene.render.filepath))
def runRandomisation(scene):
    global randomisation
    if randomisation is None:
        randomisation = sdg_randomisation.Randomization.from_file(scene.randomisation_file)
        print("Loaded randomisation file:", scene.randomisation_file)
    randomisation(None)
def createDataset(scene: bpy.types.Scene):
    start = scene.frame_start
    end = scene.frame_end
    for i in range(start, end+1):
        scene.frame_current = i
        scene.frame_start = i
        scene.frame_end = i
        random.seed = i    
        runRandomisation(scene)
        sdg_utils.save_annotations(i, sdg_utils.getLabelObjects(), getDatasetPath(scene))
        bpy.ops.render.render(animation=True)
    scene.frame_start = start
    scene.frame_end = end

@persistent
def resetRandomisation():
    bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)



class sdg_Properties(bpy.types.PropertyGroup):
    randomisation_file: bpy.props.StringProperty(name="randomisation_file")
class SyntheticDataPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Synthetic Data"
    bl_idname = "OBJECT_PT_my_addon"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Create a simple row.
        layout.label(text=" Simple Row:")

        row = layout.row()
        row.prop(scene, "randomisation_file")
        row.operator("scene.load_rand_file")
        
        row = layout.row()
        row.operator("scene.setup_compositing")
        
        row = layout.row()
        row.operator("scene.randomize")
        row.operator("scene.reset")
        
        row = layout.row()
        row.operator("scene.create")
        
class SetupCompositing(bpy.types.Operator):
    """Setup Compositing for Synthetic data generation"""
    bl_idname = "scene.setup_compositing"
    bl_label = "Setup Compositing"

    def execute(self, context):
        sdg_utils.setup_compositing(getDatasetPath(context.scene), context.scene)
        return {'FINISHED'}

class Randomize(bpy.types.Operator):
    """Randomize the Szene"""
    bl_idname = "scene.randomize"
    bl_label = "Randomize"

    def execute(self, context):
        runRandomisation(context.scene)
        return {'FINISHED'}
class Create(bpy.types.Operator):
    """Create the dataset"""
    bl_idname = "scene.create"
    bl_label = "Create Dataset"

    def execute(self, context):
        createDataset(context.scene)
        return {'FINISHED'}

class Reset(bpy.types.Operator):
    """Setup Compositing for Synthetic data generation"""
    bl_idname = "scene.reset"
    bl_label = "Reset"

    def execute(self, context):
        resetRandomisation()
        return {'FINISHED'}

class LoadRandFileOperator(bpy.types.Operator):
    """Load a Yaml file"""
    bl_idname = "scene.load_rand_file"
    bl_label = "Load Randomisation File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    def execute(self, context):
        print("FilePath:", self.filepath)
        context.scene.randomisation_file = self.filepath
        global randomisation
        randomisation = sdg_randomisation.Randomization.from_file(context.scene.randomisation_file)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.types.Scene.randomisation_file = bpy.props.StringProperty(
        name="randomisation_file",
        description="Path to the randomisation file",
        default=""
    )
    bpy.utils.register_class(SyntheticDataPanel)
    bpy.utils.register_class(LoadRandFileOperator)
    bpy.utils.register_class(SetupCompositing)
    bpy.utils.register_class(Randomize)
    bpy.utils.register_class(Reset)
    bpy.utils.register_class(Create)
def unregister():
    del bpy.types.Scene.randomisation_file
    bpy.utils.unregister_class(SyntheticDataPanel)
    bpy.utils.unregister_class(LoadRandFileOperator)
    bpy.utils.unregister_class(SetupCompositing)
    bpy.utils.unregister_class(Randomize)
    bpy.utils.unregister_class(Reset)
    bpy.utils.unregister_class(Create)
if __name__ == "__main__":
    register()
#    unregister()