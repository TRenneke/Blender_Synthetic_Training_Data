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
import os

randomisation: sdg_randomisation.Randomization = None
def getDatasetPath(scene: bpy.types.Scene):
    return os.path.dirname(os.path.dirname(scene.render.filepath))
def runRandomisation(scene):
    global randomisation
    if randomisation is None:
        randomisation = sdg_randomisation.Randomization.from_file(scene.randomisation_file)
        print("Loaded randomisation file:", scene.randomisation_file)
    randomisation(bpy.data.objects.values())
            
def onFrameChangePost(scene: bpy.types.Scene):
    # Randomize the Scene
    runRandomisation(scene)
    # Store Scene Data the Scene
    sdg_utils.save_annotations(scene.frame_current, randomisation.getAnnotatedObjects(), getDatasetPath(scene))
    
class sdg_Properties(bpy.types.PropertyGroup):
    randomisation_file: bpy.props.StringProperty(name="randomisation_file")
class SyntheticDataPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Synthetic Data"
    bl_idname = "OBJECT_PT_my_addon"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Create a simple row.
        layout.label(text=" Simple Row:")

        row = layout.row()
        row.prop(scene, "randomisation_file")
        row.operator("output.load_rand_file")
        
        row = layout.row()
        row.operator("output.setup_compositing")
        
        row = layout.row()
        row.operator("output.randomize")
        
class SetupCompositing(bpy.types.Operator):
    """Setup Compositing for Synthetic data generation"""
    bl_idname = "output.setup_compositing"
    bl_label = "Setup Compositing"

    def execute(self, context):
        sdg_utils.setup_compositing(getDatasetPath(context.scene), context.scene)
        return {'FINISHED'}

class Randomize(bpy.types.Operator):
    """Setup Compositing for Synthetic data generation"""
    bl_idname = "output.randomize"
    bl_label = "Randomize"

    def execute(self, context):
        runRandomisation(context.scene)
        return {'FINISHED'}


class LoadRandFileOperator(bpy.types.Operator):
    """Load a Yaml file"""
    bl_idname = "output.load_rand_file"
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
    
    bpy.app.handlers.frame_change_post.append(onFrameChangePost)
    
def unregister():
    del bpy.types.Scene.randomisation_file
    bpy.utils.unregister_class(SyntheticDataPanel)
    bpy.utils.unregister_class(LoadRandFileOperator)
    bpy.utils.unregister_class(SetupCompositing)
    bpy.utils.unregister_class(Randomize)
    bpy.app.handlers.frame_change_post.remove(onFrameChangePost)
if __name__ == "__main__":
    register()
#    unregister()