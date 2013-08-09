# Save this file as init.py in your nuke plug-in path as described here:
#
#   http://docs.thefoundry.co.uk/nuke/63/pythondevguide/startup.html
#
def init_sgtk(studio_root, default_work_area_path):
    """
    Minimal setup to ensure the tk-nuke engine is up
    and running when Nuke is started outside or the
    Tank command or Shotgun context menus 
    """    
    import sys, os

    # make sure sgtk module can be found in the python path:
    core_python_path = os.path.abspath(os.path.join(studio_root, "tank/install/core/python"))
    if core_python_path not in sys.path: 
        sys.path.append(core_python_path)

    # Check that we need to start the engine:
    if "TANK_ENGINE" in os.environ:
        # tk-nuke engine is going to be set up by
        # tk-multi-launchapp so we don't need to bother
        return

    # Check that the engine isn't already running
    if "TANK_NUKE_ENGINE_MOD_PATH" in os.environ:
        # tk-nuke engine is running which will handle all 
        # engine & context management from now on
        return

    # initialize tk-nuke engine:
    try:
        # Determine the work area path that will be used to
        # create the initial context the engine will be
        # started with.  If a file path was specified on the
        # command line then this will be sys.argv[0]
        work_area_path = default_work_area_path
        if len(sys.argv) > 0 and sys.argv[0].endswith(".nk") and os.path.exists(sys.argv[0]):
            # file path was passed through the command line
            work_area_path = sys.argv[0] 

        import sgtk
        tk = sgtk.Sgtk(default_work_area_path)

        # First, create a context from the current file path:
        ctx = tk.context_from_path(work_area_path)
        
        # now, find a template that matches this path.  If 
        # we find one and it contains the "filetag" key then we
        # can use that to try to find a Task and refine 
        # the context:
        try:
            template = tk.template_from_path(work_area_path)
            if template and "filetag" in template.keys:
                fields = template.get_fields(work_area_path)
                file_tag = fields.get("filetag")
                if file_tag:
                    # use the file tag to look up the task from Shotgun
                    # for this entity:
                    filters = [["sg_filetag", "is", file_tag], ["entity", "is", ctx.entity]]
                    sg_results = tk.shotgun.find("Task", filters)
                    
                    if sg_results:
                        # awesome, found a task so lets create a new 
                        # context from it:
                        sg_result = sg_results[0]
                        
                        ctx = tk.context_from_entity(sg_result["type"], sg_result["id"])
        except:
            # failed to find a task so lets just go with the non-task context
            pass

        # and start the engine:
        sgtk.platform.start_engine("tk-nuke", tk, ctx)
    except Exception, e:
        print "Failed to start Toolkit Engine - %s" % e

# pass in sensible values for studio_root & default_work_area_path
studio_root = "K:/Tank" # The location of the Toolkit code on disk
default_work_area_path = "M:/00719_grandpa" # The default work area to be used if no .nk file is specified on the command line
init_sgtk(studio_root, default_work_area_path)