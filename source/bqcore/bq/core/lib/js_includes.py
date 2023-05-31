# -*- coding: utf-8 -*-

"""WebHelpers used in bqcore."""

import tg
import os
from minimatic import *

import bq
from bq.util.paths import bisque_path

def generate_css_files(root=None, public=None):
    public = public or tg.config.get('bisque.paths.public', 'public')

    if tg.config.get('bisque.js_environment', None) != 'development':
        css_kw = dict (fs_root=public,
                    combined='/core/css/all_css.css',
                    combined_path = os.path.join(public,'core/css/all_css.css'),
                    checkts = False,
                    version=bq.release.__VERSION_HASH__ )
    else:
        # point root to public deployment, it's linked and so all changes should be reflected properly
        # if new files appear since links are per files the deployment should simply be re-run
        css_kw = {
            'fs_root': public,
        }

    return stylesheet_link (
        '/core/css/bq.css',
        '/core/css/bq_ui_toolbar.css',
        '/core/js/bq_ui_misc.css',
        '/core/js/ResourceBrowser/ResourceBrowser.css',
        '/core/js/ResourceTagger/Tagger.css',
        '/core/js/DatasetBrowser/DatasetBrowser.css',
        '/core/js/Share/BQ.share.Dialog.css',
        '/core/js/settings/BQ.settings.Panel.css',
        '/core/js/admin/BQ.user.Manager.css',
        '/core/js/picker/Path.css',
        '/core/js/tree/files.css',
        '/core/js/tree/organizer.css',
#        { 'file' : '/image_service/public/converter.css', 'path' : root + 'bqserver/bq' },
        '/image_service/converter.css',
        '/core/panojs3/styles/panojs.css',
        '/core/js/slider/slider.css',
        '/core/js/picker/Color.css',
        '/core/js/form/field/Color.css',
        '/core/css/imgview.css',
        '/core/js/movie/movie.css',
#        { 'file': '/dataset_service/public/dataset_panel.css', 'path' : root + 'bqserver/bq' },
        '/dataset_service/dataset_panel.css',
        '/core/js/renderers/dataset.css',
        '/core/js/graphviewer/graphviewer.css',
        '/core/js/volume/bioWeb3D.css',
#        {'file' : '/import_service/public/bq_ui_upload.css', 'path' : root + 'bqserver/bq'},
        '/import/bq_ui_upload.css',
#        {'file' : '/export_service/public/css/BQ.Export.css', 'path' : root + 'bqserver/bq'},
        '/export/css/BQ.Export.css',
        '/core/css/bisquik_extjs_fix.css',
	    '/core/js/drawing/drawing.css',

        # -- modules
        '/core/js/modules/bq_ui_renderes.css',
        '/core/js/modules/bq_webapp.css',


        # -- plugin css
        #plugins = { 'path': root + 'bq/core/public/plugins/', 'file': '/plugins/' },
        plugins = { 'file': '/core/plugins/', 'path' : public + "/core/plugins/" },

        # combined will not work for now due to relative urls in .css files
        #fs_root=public,
        #combined='/core/css/all_css.css',
        #combined_path = root + '/bqcore/bq/core/public/css/all_css.css',
        #checkts = False,
        #version=bq.release.__VERSION_HASH__

        **css_kw
    )

def generate_js_files(root=None, public=None):
    public = public or tg.config.get('bisque.paths.public', 'public')

    if tg.config.get('bisque.js_environment', None) != 'development':
        link_kw = dict (fs_root = public,
                      combined= '/core/js/all_js.js',
                      combined_path = os.path.join(public, 'core/js/all_js.js'),
                      checkts = False,
                      minify= 'minify', # D3 breaks with minify
                      version=bq.release.__VERSION_HASH__)
    else:
        # point root to public deployment, it's linked and so all changes should be reflected properly
        # if new files appear since links are per files the deployment should simply be re-run
        link_kw = {
            'fs_root': public,
        }

    return javascript_link(

        # Pre-required libraries
        #'/d3/d3.js',
        #'/threejs/three.js',
        '/core/threejs/TypedArrayUtils.js',
        '/core/threejs/math/ColorConverter.js',
        #-- Async.js --
        #'/async/async.js',
        #-- jquery --
        #'/jquery/jquery.min.js',
        #-- proj4 --
        #'/proj4js/proj4.js',
        #-- Raphael --
        #'/raphael/raphael.js',
        #-- kinetic --
        #'/core/js/viewer/kinetic-v5.1.0.js',

        #'/core/js/bq_ui_extjs_fix.js',
        # --Bisque JsApi - this needs cleaning and updating--
        '/core/js/utils.js',
        '/core/js/bq_api.js',
        '/core/js/bq_ui_application.js',
        '/core/js/bq_ui_toolbar.js',
        '/core/js/bq_ui_misc.js',
        '/core/js/date.js',
        '/core/js/encoder.js',
	    '/core/js/drawing/drawing.js',

        # -- ResourceBrowser code --
        '/core/js/ResourceBrowser/Browser.js',
        '/core/js/ResourceBrowser/LayoutFactory.js',
        '/core/js/ResourceBrowser/ResourceQueue.js',
        '/core/js/ResourceBrowser/DatasetManager.js',
        '/core/js/ResourceBrowser/CommandBar.js',
        '/core/js/ResourceBrowser/viewStateManager.js',
        '/core/js/ResourceBrowser/OperationBar.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceFactory.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceImage.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceMex.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceModule.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceDataset.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceFile.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceUser.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceTemplate.js',
        '/core/js/ResourceBrowser/ResourceFactory/ResourceDir.js',
        '/core/js/ResourceBrowser/Misc/MessageBus.js',
        '/core/js/ResourceBrowser/Misc/Slider.js',
        '/core/js/ResourceBrowser/Misc/DataTip.js',

        # -- Gesture manager --
        '/core/js/senchatouch/sencha-touch-gestures.js',
        '/core/js/ResourceBrowser/Misc/GestureManager.js',

        # -- Share dialog files --
        '/core/js/Share/BQ.share.Dialog.js',
        '/core/js/Share/BQ.share.Multi.js',

        # -- ResourceTagger --
        '/core/js/ResourceTagger/ComboBox.js',
        '/core/js/ResourceTagger/RowEditing.js',
        '/core/js/ResourceTagger/Tagger.js',
        '/core/js/ResourceTagger/TaggerOffline.js',
        '/core/js/ResourceTagger/ResourceRenderers/BaseRenderer.js',

        # -- Preferences --
        '/core/js/Preferences/BQ.Preferences.js',
        '/core/js/Preferences/PreferenceViewer.js',
        '/core/js/Preferences/PreferenceTagger.js',

        # -- Settings Page --
        '/core/js/settings/BQ.settings.Panel.js',
        '/core/js/settings/BQ.ModuleManager.js',
        '/core/js/settings/BQ.ModuleDeveloper.js',
        '/core/js/settings/BQ.PreferenceManager.js',

        # -- Admin --
        '/core/js/admin/BQ.user.Manager.js',

        # -- Modules --
        '/core/js/modules/bq_webapp.js',
        '/core/js/modules/bq_module_webapp_default.js',
        '/core/js/modules/bq_webapp_service.js',

        #-- DatasetBrowser --
#        {'file': '/dataset_service/public/dataset_service.js', 'path': root + 'bqserver/bq/'},
        {'file': '/dataset_service/dataset_service.js'},
        '/core/js/DatasetBrowser/DatasetBrowser.js',

        # -- TemplateManager --
        '/core/js/TemplateManager/TemplateTagger.js',
        '/core/js/TemplateManager/TemplateManager.js',
        '/core/js/TemplateManager/TagRenderer.js',

        # -- Tree Organizer --
        '/core/js/picker/Path.js',
        '/core/js/tree/files.js',
        '/core/js/tree/organizer.js',

        # -- PanoJS3 --
        '/core/panojs3/panojs/utils.js',
        '/core/panojs3/panojs/PanoJS.js',
        '/core/panojs3/panojs/controls.js',
        '/core/panojs3/panojs/pyramid_Bisque.js',
        '/core/panojs3/panojs/control_thumbnail.js',
        '/core/panojs3/panojs/control_info.js',
        '/core/panojs3/panojs/control_svg.js',

        # -- Image Service --
#        { 'file' : '/image_service/public/converter.js', 'path': root + 'bqserver/bq/'},
        { 'file' : '/image_service/converter.js'},
#        { 'file' : '/image_service/public/bq_is_formats.js', 'path': root + 'bqserver/bq/'},
        { 'file' : '/image_service/bq_is_formats.js'},

        '/core/js/slider/inversible.js',
        '/core/js/slider/slider.js',
        '/core/js/slider/tslider.js',
        '/core/js/slider/zslider.js',

        '/core/js/picker/AnnotationStatus.js',
        '/core/js/picker/Color.js',
        '/core/js/form/field/Color.js',

        '/core/js/viewer/menu_gobjects.js',
        '/core/js/viewer/scalebar.js',
        # '/core/js/viewer/2D.js', # dima: clashes with Plotly, not required
        '/core/js/viewer/imgview.js',
        '/core/js/viewer/imgops.js',
        '/core/js/viewer/imgslicer.js',
        '/core/js/viewer/imgstats.js',
        '/core/js/viewer/listner_zoom.js',
        '/core/js/viewer/tilerender.js',
        '/core/js/viewer/svgrender.js',
        '/core/js/viewer/shapeanalyzer.js',
        '/core/js/viewer/canvasshapes.js',
        '/core/js/viewer/canvasrender.js',
        '/core/js/viewer/imgedit.js',
        '/core/js/viewer/imgmovie.js',
        '/core/js/viewer/imageconverter.js',
        '/core/js/viewer/imgexternal.js',
        '/core/js/viewer/imgscalebar.js',
        '/core/js/viewer/imginfobar.js',
        '/core/js/viewer/progressbar.js',
        '/core/js/viewer/widget_extjs.js',
        '/core/js/viewer/imgpixelcounter.js',
        '/core/js/viewer/imgcurrentview.js',
        '/core/js/viewer/imgcalibration.js',
        '/core/js/viewer/simplify.js',


        #-- Movie player --
        '/core/js/movie/movie.js',

        #-- Stats --
#        { 'file' : '/stats/public/js/stats.js', 'path': root + 'bqserver/bq/'},
        { 'file' : '/stats/js/stats.js'},
        '/core/js/bq_ui_progress.js',

        #-- GMaps API --
        '/core/js/map/map.js',

        #-- Resource dispatch --
#        { 'file': '/dataset_service/public/dataset_service.js','path': root + 'bqserver/bq/'},
        { 'file': '/dataset_service/dataset_service.js'},
#        { 'file': '/dataset_service/public/dataset_operations.js','path': root + 'bqserver/bq/'},
        { 'file': '/dataset_service/dataset_operations.js'},
#        { 'file': '/dataset_service/public/dataset_panel.js','path': root + 'bqserver/bq/'},
        { 'file': '/dataset_service/dataset_panel.js'},
        '/core/js/renderers/dataset.js',
        '/core/js/resourceview.js',

        # -- Import Service --
#        { 'file' : '/import_service/public/File.js', 'path': root + 'bqserver/bq/'},
        { 'file' : '/import/File.js'},
#        { 'file' : '/import_service/public/bq_file_upload.js', 'path': root + 'bqserver/bq/'},
        { 'file' : '/import/bq_file_upload.js' },
#        { 'file' : '/import_service/public/bq_ui_upload.js', 'path': root + 'bqserver/bq/'},
        { 'file' : '/import/bq_ui_upload.js'},

        # -- Export Service --
#        { 'file' : '/export_service/public/js/BQ.Export.js', 'path': root + 'bqserver/bq/'},
        { 'file' : '/export/js/BQ.Export.js'},

        # -- Request Animation Frame --
        '/core/js/requestAnimationFrame.js',

        # -- Graph viewer --
        '/core/js/d3Component.js',
        '/core/js/graphviewer/dagre-d3.js',
        '/core/js/graphviewer/GraphViewer.js',

        # -- WebGL viewer --
        '/core/js/volume/lib/whammy.js',
        '/core/js/volume/lib/polygon.js',
        '/core/js/volume/threejs/AnaglyphEffect.js',
        '/core/js/volume/threejs/RotationControls.js',
        '/core/js/volume/threejs/OrbitControls.js',
        '/core/js/volume/threejs/TrackballControls.js',
        '/core/js/volume/volumeConfig.js',
        '/core/js/volume/renderingControls.js',
        '/core/js/volume/lightingControls.js',
        '/core/js/volume/animationControls.js',
        '/core/js/volume/extThreeJS.js',
        '/core/js/volume/gobjectbuffers.js',
        '/core/js/picker/Excolor.js',
        '/core/js/volume/transferEditorD3.js',
        '/core/js/volume/scalebar.js',
        '/core/js/volume/bioWeb3D.js',
        '/core/js/volume/lightingControls.js',

        # -- Modules --
        '/core/js/modules/bq_grid_panel.js',
        '/core/js/modules/bq_ui_renderes.js',

        # -- plugin renderers
        #plugins = { 'path': root + 'bqcore/bq/core/public/plugins/', 'file': '/plugins/' },
        plugins = { 'file': '/core/plugins/',  'path' : public + "/core/plugins/" },

        # --
        **link_kw
    )
