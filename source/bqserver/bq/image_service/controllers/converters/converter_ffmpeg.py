"""FFMPEG command line converter"""

__Contributors__ = "Mike Goebel, Wahid Sadique Koly"
__version__ = "0.0"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import logging
from lxml import etree

from bq.util.locks import Locks
from bq.image_service.controllers.converter_base import ConverterBase, Format
from bq.util.compat import OrderedDict
from bq.image_service.controllers.exceptions import (
    ImageServiceException,
    ImageServiceFuture,
)
import subprocess
import json
import inspect
import shutil
import os

log = logging.getLogger("bq.image_service.converter_ffmpeg")


supported_formats = [
    ("MP4", "MPEG4", ["mp4"]),
    ("AVI", "Microsoft AVI", ["avi"]),
    (
        "WEBM",
        "WEBM",
        [
            "webm",
        ],
    ),
    ("MOV", "QuickTime Movie", ["mov"]),
]


def compute_new_size(imw, imh, w, h, keep_aspect_ratio, no_upsample):
    if no_upsample is True and imw <= w and imh <= h:
        return (imw, imh)

    if keep_aspect_ratio is True:
        if imw / float(w) >= imh / float(h):
            h = 0
        else:
            w = 0

    # it's allowed to specify only one of the sizes, the other one will be computed
    if w == 0:
        w = int(round(imw / (imh / float(h))))
    if h == 0:
        h = int(round(imh / (imw / float(w))))

    return (w, h)


class ConverterFfmpeg(ConverterBase):
    # All of this metadata on the converter is made up, should be fixed at some point
    # if this code becomes a significant part of bisqueConverterImgcnv
    installed = True
    version = [1, 2, 3]
    installed_formats = None
    name = "ffmpeg"
    required_version = "0.0.0"

    @classmethod
    def get_version(cls):
        return {
            "full": ".".join([str(i) for i in cls.version]),
            "numeric": cls.version,
            "major": cls.version[0],
            "minor": cls.version[1],
            "build": cls.version[2],
        }

    @classmethod
    def get_formats(cls):
        try:
            cls.installed_formats = OrderedDict()
            for name, fullname, exts in supported_formats:
                cls.installed_formats[name.lower()] = Format(
                    name=name,
                    fullname=fullname,
                    ext=exts,
                    reading=True,
                    writing=True,
                    multipage=True,
                    metadata=True,
                    samples=(0, 0),
                    bits=(8, 8),
                )
        except Exception as e:
            log.info("Get formats failed with error " + str(e))
        return cls.installed_formats

    @classmethod
    def get_installed(cls):
        return True

    @classmethod
    def supported(cls, token, **kw):
        """return True if the input file format is supported"""
        ifnm = token.first_input_file()
        fmt = kw.get('fmt', '').lower()
        
        # Check if output format is a video format that FFmpeg handles
        video_formats = ['mp4', 'webm', 'avi', 'mov']
        is_video_output = fmt in video_formats
        input_ext = ifnm.split(".")[-1].lower()
        
        # For video output, check if we support the input format
        if is_video_output:
            # Support standard video inputs
            all_exts = set()
            for supported_fmt in supported_formats:
                all_exts.update(supported_fmt[2])
            
            # Also support special input formats that we handle for video conversion
            special_video_inputs = [
                'dream3d',  # Dream3D files (HDF5-based)
                'czi', 'lsm', 'lif', 'nd2', 'oib', 'oif', 'vsi', 'ims',  # Scientific formats
                'dcm'  # DICOM files
            ]
            
            is_supported = input_ext in all_exts or input_ext in special_video_inputs
            return is_supported
        
        # For non-video output, only support standard formats
        all_exts = set()
        for supported_fmt in supported_formats:
            all_exts.update(supported_fmt[2])
        is_supported = input_ext in all_exts
        return is_supported

    @classmethod
    def convert(cls, token, ofnm, fmt=None, extra=None, **kw):
        ifnm = token.first_input_file()
        
        # Check if this is a multi-frame DICOM conversion (z-stack to video)
        is_multiframe_dicom = (
            token.dims.get("image_num_z", 1) > 1 and 
            token.dims.get("storage", "") == "multi_file_series" and
            fmt.lower() in ["webm", "mp4", "avi", "mov"]
        )
        
        # Check if this is a CZI file or other format that FFmpeg can't read directly
        is_non_ffmpeg_format = (
            ifnm.lower().endswith(('.czi', '.lsm', '.lif', '.nd2', '.oib', '.oif', '.vsi', '.ims')) and
            fmt.lower() in ["webm", "mp4", "avi", "mov"]
        )
        
        # Check if this is a Dream3D file (requires specialized processing)
        is_dream3d_format = (
            ifnm.lower().endswith('.dream3d') and
            fmt.lower() in ["webm", "mp4", "avi", "mov"]
        )
        
        with Locks(ifnm, ofnm, failonexist=True) as l:
            if l.locked:
                ifnm = token.first_input_file()
                imw = token.dims["image_num_x"]
                imh = token.dims["image_num_y"]
                ind_rs = [i for i, v in enumerate(extra) if v == "-resize"]
                resize = True
                if len(ind_rs) != 1:
                    resize = False
                else:
                    rs_string = extra[ind_rs[0] + 1]
                    width, height = [int(i) for i in rs_string.split(",")[:2]]

                if is_multiframe_dicom:
                    # For multi-frame DICOM sequences, always extract frames fresh in temporary directory
                    log.info("Creating video from DICOM file by extracting frames fresh")
                    return cls._convert_dicom_via_frames(token, ofnm, fmt, extra, **kw)
                elif is_dream3d_format:
                    # Dream3D files require specialized processing via table service
                    log.info("Creating video from Dream3D file by extracting data arrays as frames")
                    return cls._convert_dream3d_via_frames(token, ofnm, fmt, extra, **kw)
                elif is_non_ffmpeg_format:
                    # For CZI and other non-FFmpeg formats, use frame extraction approach
                    log.info(f"Creating video from {os.path.splitext(ifnm)[1]} file by extracting frames via imgcnv")
                    return cls._convert_via_frames(token, ofnm, fmt, extra, **kw)
                elif ifnm.lower().endswith('.dcm'):
                    # For single DICOM files, try standard FFmpeg conversion first
                    log.info("Using standard FFmpeg conversion for single DICOM file")
                    
                    if resize:
                        w_out, h_out = compute_new_size(
                            imw, imh, width, height,
                            keep_aspect_ratio=True, no_upsample=True,
                        )
                        cmd = [
                            "ffmpeg", "-y", "-hide_banner", "-threads", "8", "-loglevel", "error",
                            "-i", ifnm,
                            "-vf", f"scale={w_out}:{h_out}",
                            ofnm,
                        ]
                    else:
                        cmd = [
                            "ffmpeg", "-y", "-hide_banner", "-threads", "8", "-loglevel", "error",
                            "-i", ifnm,
                            ofnm,
                        ]
                    
                    log.info(f"-----Executing DICOM command: {' '.join(cmd)}")
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                        if result.returncode == 0 and os.path.exists(ofnm):
                            log.info(f"DICOM video conversion successful: {ofnm}")
                            return ofnm
                        else:
                            log.warning(f"DICOM FFmpeg conversion failed: {result.stderr}")
                            # Fall back to frame extraction approach
                            return cls._convert_dicom_via_frames(token, ofnm, fmt, extra, **kw)
                    except subprocess.TimeoutExpired:
                        log.error("DICOM FFmpeg conversion timed out")
                        # Fall back to frame extraction approach
                        return cls._convert_dicom_via_frames(token, ofnm, fmt, extra, **kw)
                    except Exception as e:
                        log.error(f"DICOM FFmpeg conversion failed with exception: {e}")
                        # Fall back to frame extraction approach
                        return cls._convert_dicom_via_frames(token, ofnm, fmt, extra, **kw)
                else:
                    # Standard single-file video conversion
                    if resize:
                        w_out, h_out = compute_new_size(
                            imw,
                            imh,
                            width,
                            height,
                            keep_aspect_ratio=True,
                            no_upsample=True,
                        )
                        cmd = [
                            "ffmpeg",
                            "-y",
                            "-hide_banner",
                            "-threads",
                            "8",
                            "-loglevel",
                            "error",
                            "-i",
                            ifnm,
                            "-vf",
                            "scale=" + str(w_out) + ":" + str(h_out),
                            ofnm,
                        ]
                    else:
                        cmd = [
                            "ffmpeg",
                            "-y",
                            "-hide_banner",
                            "-threads",
                            "8",
                            "-loglevel",
                            "error",
                            "-i",
                            ifnm,
                            ofnm,
                        ]

                # Use shlex.quote to properly escape filenames with special characters
                import shlex
                single_cmd = " ".join(shlex.quote(arg) for arg in cmd)
                log.info(f"-----Executing command: {single_cmd}")

                try:
                    # Use cmd list directly instead of shell=True to avoid shell interpretation issues
                    process = subprocess.run(
                        cmd,
                        stdin=subprocess.DEVNULL,  # avoid blocking stdin
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=os.environ.copy(),  # inherit full shell env
                        text=True,
                    )

                    # Cleanup temporary files if they were created
                    if is_multiframe_dicom:
                        concat_file = ofnm + ".frames.txt"
                        if os.path.exists(concat_file):
                            try:
                                os.remove(concat_file)
                            except:
                                pass
                        # Also clean up any temporary frame directories that might exist
                        import glob
                        temp_dirs = glob.glob("/tmp/video_frames_*")
                        for temp_dir in temp_dirs:
                            try:
                                shutil.rmtree(temp_dir)
                            except:
                                pass

                    if process.returncode == 0 and os.path.exists(ofnm):
                        log.info(f"Video conversion successful using {ofnm}")
                        return ofnm
                    else:
                        log.warning(
                            f"Video conversion failed with {ofnm}: stderr={process.stderr}, stdout={process.stdout}, returncode={process.returncode}"
                        )
                        # Clean up partial file if it exists
                        if os.path.exists(ofnm):
                            try:
                                os.remove(ofnm)
                            except:
                                pass

                except Exception as e:
                    log.error(f"FFmpeg execution failed: {e}")
                    # Clean up temporary files if they were created
                    if is_multiframe_dicom:
                        concat_file = ofnm + ".frames.txt"
                        if os.path.exists(concat_file):
                            try:
                                os.remove(concat_file)
                            except:
                                pass
                        # Also clean up any temporary frame directories that might exist
                        import glob
                        temp_dirs = glob.glob("/tmp/video_frames_*")
                        for temp_dir in temp_dirs:
                            try:
                                shutil.rmtree(temp_dir)
                            except:
                                pass

                return None

            elif l.locked is False:
                raise ImageServiceFuture((1, 15))

    @classmethod
    def _convert_via_frames(cls, token, ofnm, fmt=None, extra=None, **kw):
        """
        Generic method for files that FFmpeg cannot read directly (CZI, LSM, etc).
        Uses bioformats or imgcnv to extract frames and then creates video from those frames.
        """
        log.info("Attempting conversion via frame extraction for non-FFmpeg format")
        
        ifnm = token.first_input_file()
        imw = token.dims["image_num_x"]
        imh = token.dims["image_num_y"]
        
        # Determine which converter to use based on file format
        file_ext = os.path.splitext(ifnm)[1].lower()
        use_bioformats = file_ext in ['.lif', '.nd2', '.oib', '.oif', '.vsi']
        
        # Determine resize parameters
        ind_rs = [i for i, v in enumerate(extra) if v == "-resize"]
        resize = len(ind_rs) == 1
        if resize:
            rs_string = extra[ind_rs[0] + 1]
            width, height = [int(i) for i in rs_string.split(",")[:2]]
        
        try:
            # Import appropriate converter for frame extraction
            if use_bioformats:
                from .converter_bioformats import ConverterBioformats
                converter = ConverterBioformats
                log.info(f"Using bioformats converter for {file_ext} format")
            else:
                from .converter_imgcnv import ConverterImgcnv
                converter = ConverterImgcnv
                log.info(f"Using imgcnv converter for {file_ext} format")
            
            # Get number of frames from dimensions
            num_frames = token.dims.get("image_num_z", 1) * token.dims.get("image_num_t", 1)
            log.info(f"Generic format with {num_frames} frames")
            
            # Create temporary directory for frames
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="video_frames_")
            extracted_frames = []
            
            try:
                if use_bioformats:
                    # For bioformats-supported files (.lif, .nd2, etc.), convert to OME-TIFF first
                    log.info("Converting to OME-TIFF using bioformats before frame extraction")
                    ome_tiff_path = os.path.join(temp_dir, "temp.ome.tiff")
                    
                    # Use bioformats to convert to OME-TIFF
                    result = converter.convertToOmeTiff(token, ome_tiff_path)
                    if result is None or not os.path.exists(ome_tiff_path):
                        log.error("Failed to convert to OME-TIFF using bioformats")
                        return None
                    
                    # Now extract frames from the OME-TIFF using imgcnv
                    from .converter_imgcnv import call_imgcnvlib
                    for frame_idx in range(num_frames):
                        frame_filename = f"frame_{frame_idx:04d}.png"
                        frame_path = os.path.join(temp_dir, frame_filename)
                        
                        try:
                            command = [
                                'imgcnv',
                                '-i', ome_tiff_path,
                                '-o', frame_path,
                                '-page', str(frame_idx + 1),  # imgcnv uses 1-based indexing
                                '-t', 'png'
                            ]
                            
                            # Add depth conversion if needed
                            if token.dims.get('image_pixel_depth', 8) != 8:
                                command.extend(['-depth', '8,d,u'])
                            
                            retcode, out = call_imgcnvlib(command)
                            
                            if retcode == 0 and os.path.exists(frame_path):
                                extracted_frames.append(frame_path)
                                log.debug(f"Extracted frame {frame_idx}: {frame_path}")
                            else:
                                log.warning(f"Failed to extract frame {frame_idx}: return code {retcode}, output: {out}")
                                
                        except Exception as e:
                            log.warning(f"Error extracting frame {frame_idx}: {e}")
                            continue
                
                else:
                    # Extract frames directly using imgcnv for formats it supports
                    from .converter_imgcnv import call_imgcnvlib
                    for frame_idx in range(num_frames):
                        frame_filename = f"frame_{frame_idx:04d}.png"
                        frame_path = os.path.join(temp_dir, frame_filename)
                        
                        try:
                            # Build imgcnv command to extract specific frame
                            command = [
                                'imgcnv',
                                '-i', ifnm,
                                '-o', frame_path,
                                '-page', str(frame_idx + 1),  # imgcnv uses 1-based indexing
                                '-t', 'png'
                            ]
                            
                            # Add depth conversion if needed for proper brightness/contrast
                            if token.dims.get('image_pixel_depth', 8) != 8:
                                command.extend(['-depth', '8,d,u'])  # Convert to 8-bit with dynamic range adjustment
                            
                            retcode, out = call_imgcnvlib(command)
                            
                            if retcode == 0 and os.path.exists(frame_path):
                                extracted_frames.append(frame_path)
                                log.debug(f"Extracted frame {frame_idx}: {frame_path}")
                            else:
                                log.warning(f"Failed to extract frame {frame_idx}: return code {retcode}, output: {out}")
                        except Exception as e:
                            log.warning(f"Error extracting frame {frame_idx}: {e}")
                            continue
                
                if len(extracted_frames) < 2:
                    log.error(f"Only extracted {len(extracted_frames)} frames, need at least 2 for video")
                    return None
                
                log.info(f"Successfully extracted {len(extracted_frames)} frames")
                
                # Create FFmpeg concat file
                concat_file = os.path.join(temp_dir, "frames.txt")
                with open(concat_file, 'w') as f:
                    for frame_path in extracted_frames:
                        abs_frame_path = os.path.abspath(frame_path)
                        f.write(f"file '{abs_frame_path}'\n")
                        f.write("duration 0.1\n")  # 10 FPS
                    # Repeat last frame briefly
                    if extracted_frames:
                        abs_last_path = os.path.abspath(extracted_frames[-1])
                        f.write(f"file '{abs_last_path}'\n")
                
                # Build FFmpeg command
                if resize:
                    w_out, h_out = compute_new_size(
                        imw, imh, width, height,
                        keep_aspect_ratio=True, no_upsample=True,
                    )
                    cmd = [
                        "ffmpeg", "-y", "-hide_banner", "-threads", "8", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", concat_file,
                        "-vf", f"scale={w_out}:{h_out}",
                        "-pix_fmt", "yuv420p", "-c:v", "libvpx-vp9", "-crf", "30",
                        ofnm,
                    ]
                else:
                    cmd = [
                        "ffmpeg", "-y", "-hide_banner", "-threads", "8", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", concat_file,
                        "-pix_fmt", "yuv420p", "-c:v", "libvpx-vp9", "-crf", "30",
                        ofnm,
                    ]
                
                log.info(f"Executing frame-based conversion: {' '.join(cmd)}")
                
                # Execute FFmpeg command
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(ofnm):
                    log.info(f"Frame-based conversion successful: {ofnm}")
                    return ofnm
                else:
                    log.error(f"Frame-based conversion failed: {result.stderr}")
                    return None
                    
            finally:
                # Clean up temporary files
                try:
                    shutil.rmtree(temp_dir)
                    log.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    log.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
                    
        except ImportError:
            log.error("imgcnv converter not available for frame extraction")
            return None
        except Exception as e:
            log.error(f"Generic frame extraction conversion failed: {e}")
            return None

    @classmethod
    def _convert_dicom_via_frames(cls, token, ofnm, fmt=None, extra=None, **kw):
        """
        Fallback method for DICOM files when FFmpeg direct conversion fails.
        Uses imgcnv to extract frames and then creates video from those frames.
        """
        log.info("Attempting DICOM conversion via frame extraction")
        
        ifnm = token.first_input_file()
        imw = token.dims["image_num_x"]
        imh = token.dims["image_num_y"]
        
        # Determine resize parameters
        ind_rs = [i for i, v in enumerate(extra) if v == "-resize"]
        resize = len(ind_rs) == 1
        if resize:
            rs_string = extra[ind_rs[0] + 1]
            width, height = [int(i) for i in rs_string.split(",")[:2]]
        
        try:
            # Import imgcnv converter for frame extraction
            from .converter_imgcnv import ConverterImgcnv
            
            # Check if this is a multi-file series
            is_multifile_series = token.dims.get("storage", "") == "multi_file_series" and isinstance(token.input, list)
            
            if is_multifile_series:
                # For multi-file series, each file is a frame
                files_to_process = token.input
                num_frames = len(files_to_process)
                log.info(f"Multi-file DICOM series with {num_frames} files")
            else:
                # For single multi-frame DICOM, calculate frames from dimensions
                num_frames = token.dims.get("image_num_z", 1) * token.dims.get("image_num_t", 1)
                files_to_process = [ifnm]  # Single file
                log.info(f"Single DICOM file with {num_frames} frames (z={token.dims.get('image_num_z', 1)}, t={token.dims.get('image_num_t', 1)})")
            
            if num_frames <= 1:
                log.warning("DICOM has only 1 frame, cannot create video")
                return None
            
            log.info(f"DICOM dimensions: {token.dims}")
            
            # Create temporary directory for extracted frames
            import tempfile
            
            temp_dir = tempfile.mkdtemp(prefix="dicom_frames_")
            log.info(f"Created temporary directory: {temp_dir}")
            
            extracted_frames = []
            
            try:
                if is_multifile_series:
                    # Extract one frame from each file in the series
                    for file_idx, dicom_file in enumerate(files_to_process):
                        frame_filename = f"frame_{file_idx:04d}.png"
                        frame_path = os.path.join(temp_dir, frame_filename)
                        
                        try:
                            # Build imgcnv command to extract frame 1 from this file
                            command = [
                                'imgcnv',
                                '-i', dicom_file,
                                '-o', frame_path,
                                '-page', '1',  # Always extract first frame from each file
                                '-t', 'png',
                                '-enhancemeta'  # Enhance metadata for proper DICOM display
                            ]
                            
                            # Add depth conversion if needed for proper brightness/contrast
                            if token.dims.get('image_pixel_depth', 16) != 8:
                                command.extend(['-depth', '8,d,u'])  # Convert to 8-bit with dynamic range adjustment
                            
                            # Use the proper imgcnv interface
                            from .converter_imgcnv import call_imgcnvlib
                            retcode, out = call_imgcnvlib(command)
                            
                            if retcode == 0 and os.path.exists(frame_path):
                                extracted_frames.append(frame_path)
                                log.debug(f"Extracted frame {file_idx} from {dicom_file}: {frame_path}")
                            else:
                                log.warning(f"Failed to extract frame from {dicom_file}: return code {retcode}, output: {out}")
                        except Exception as e:
                            log.warning(f"Error extracting frame from {dicom_file}: {e}")
                            continue
                else:
                    # Extract each frame from the single multi-frame DICOM file
                    for frame_idx in range(num_frames):
                        frame_filename = f"frame_{frame_idx:04d}.png"
                        frame_path = os.path.join(temp_dir, frame_filename)
                        
                        try:
                            # Build imgcnv command to extract specific frame
                            command = [
                                'imgcnv',
                                '-i', ifnm,
                                '-o', frame_path,
                                '-page', str(frame_idx + 1),  # imgcnv uses 1-based indexing
                                '-t', 'png',
                                '-enhancemeta'  # Enhance metadata for proper DICOM display
                            ]
                            
                            # Add depth conversion if needed for proper brightness/contrast
                            if token.dims.get('image_pixel_depth', 16) != 8:
                                command.extend(['-depth', '8,d,u'])  # Convert to 8-bit with dynamic range adjustment
                            
                            # Use the proper imgcnv interface
                            from .converter_imgcnv import call_imgcnvlib
                            retcode, out = call_imgcnvlib(command)
                            
                            if retcode == 0 and os.path.exists(frame_path):
                                extracted_frames.append(frame_path)
                                log.debug(f"Extracted frame {frame_idx}: {frame_path}")
                            else:
                                log.warning(f"Failed to extract frame {frame_idx}: return code {retcode}, output: {out}")
                        except Exception as e:
                            log.warning(f"Error extracting frame {frame_idx}: {e}")
                            continue
                
                if len(extracted_frames) < 2:
                    log.error(f"Only extracted {len(extracted_frames)} frames, need at least 2 for video")
                    return None
                
                log.info(f"Successfully extracted {len(extracted_frames)} frames")
                
                # Create FFmpeg concat file
                concat_file = os.path.join(temp_dir, "frames.txt")
                with open(concat_file, 'w') as f:
                    for frame_path in extracted_frames:
                        abs_frame_path = os.path.abspath(frame_path)
                        f.write(f"file '{abs_frame_path}'\n")
                        f.write("duration 0.1\n")  # 10 FPS
                    # Repeat last frame briefly
                    if extracted_frames:
                        abs_last_path = os.path.abspath(extracted_frames[-1])
                        f.write(f"file '{abs_last_path}'\n")
                
                # Build FFmpeg command
                if resize:
                    w_out, h_out = compute_new_size(
                        imw, imh, width, height,
                        keep_aspect_ratio=True, no_upsample=True,
                    )
                    cmd = [
                        "ffmpeg", "-y", "-hide_banner", "-threads", "8", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", concat_file,
                        "-vf", f"scale={w_out}:{h_out}",
                        "-pix_fmt", "yuv420p", "-c:v", "libvpx-vp9", "-crf", "30",
                        ofnm,
                    ]
                else:
                    cmd = [
                        "ffmpeg", "-y", "-hide_banner", "-threads", "8", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", concat_file,
                        "-pix_fmt", "yuv420p", "-c:v", "libvpx-vp9", "-crf", "30",
                        ofnm,
                    ]
                
                log.info(f"Executing frame-based DICOM conversion: {' '.join(cmd)}")
                
                # Execute FFmpeg command
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(ofnm):
                    log.info(f"DICOM frame-based conversion successful: {ofnm}")
                    return ofnm
                else:
                    log.error(f"Frame-based DICOM conversion failed: {result.stderr}")
                    return None
                    
            finally:
                # Clean up temporary files
                try:
                    shutil.rmtree(temp_dir)
                    log.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    log.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
                    
        except ImportError:
            log.error("imgcnv converter not available for frame extraction")
            return None
        except Exception as e:
            log.error(f"DICOM frame extraction conversion failed: {e}")
            return None

    @classmethod
    def _convert_dream3d_via_frames(cls, token, ofnm, fmt=None, extra=None, **kw):
        """
        Convert Dream3D files to video by extracting data arrays as image frames.
        Dream3D files are HDF5-based and require table service access.
        """
        log.info("Starting Dream3D video conversion via frame extraction")
        
        ifnm = token.first_input_file()
        imw = token.dims["image_num_x"]
        imh = token.dims["image_num_y"]
        
        # Determine resize parameters
        ind_rs = [i for i, v in enumerate(extra) if v == "-resize"]
        resize = len(ind_rs) == 1
        if resize:
            rs_string = extra[ind_rs[0] + 1]
            width, height = [int(i) for i in rs_string.split(",")[:2]]
        
        try:
            # Import necessary modules for Dream3D processing
            import tempfile
            import shutil
            import numpy as np
            from PIL import Image
            from bqapi.comm import BQSession
            
            # Create temporary directory for frame extraction
            temp_dir = tempfile.mkdtemp(prefix="dream3d_frames_")
            
            try:
                # Try direct HDF5 access
                try:
                    import h5py
                    log.info("Using direct HDF5 access for Dream3D data extraction")
                    
                    # Get the specific dataset path from the token (from URL)
                    dataset_path = token.series
                    if not dataset_path:
                        log.error("No dataset path specified in token.series for Dream3D file")
                        return None
                    
                    # Remove leading slash if present
                    if dataset_path.startswith('/'):
                        dataset_path = dataset_path[1:]
                    
                    extracted_frames = []
                    data_array = None
                    
                    # Open HDF5 file directly and load the specific dataset
                    with h5py.File(ifnm, 'r') as h5file:
                        try:
                            log.info(f"Loading Dream3D data from path: {dataset_path}")
                            if dataset_path in h5file:
                                data_array = h5file[dataset_path][:]  # Load the entire array
                                log.info(f"Successfully loaded data array with shape: {data_array.shape}")
                            else:
                                log.error(f"Dataset path '{dataset_path}' not found in Dream3D file")
                                return None
                        except Exception as e:
                            log.error(f"Could not load data from {dataset_path}: {e}")
                            return None
                        
                        # Process the data array to create frames (inside h5py context)
                        extracted_frames = cls._process_dream3d_data_to_frames(data_array, temp_dir)
                        
                except ImportError:
                    log.error("h5py not available for Dream3D processing")
                    return None

                
                if len(extracted_frames) < 1:
                    log.error("No frames were successfully extracted from Dream3D data")
                    return None
                
                log.info(f"Successfully extracted {len(extracted_frames)} frames from Dream3D data")
                
                # Create FFmpeg concat file
                concat_file = os.path.join(temp_dir, "frames.txt")
                with open(concat_file, 'w') as f:
                    for frame_path in extracted_frames:
                        abs_frame_path = os.path.abspath(frame_path)
                        f.write(f"file '{abs_frame_path}'\n")
                        f.write("duration 0.5\n")  # 2 FPS for Dream3D data
                    # Repeat last frame briefly
                    if extracted_frames:
                        abs_last_path = os.path.abspath(extracted_frames[-1])
                        f.write(f"file '{abs_last_path}'\n")
                
                # Build FFmpeg command
                if resize:
                    w_out, h_out = compute_new_size(
                        imw, imh, width, height,
                        keep_aspect_ratio=True, no_upsample=True,
                    )
                    cmd = [
                        "ffmpeg", "-y", "-hide_banner", "-threads", "8", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", concat_file,
                        "-vf", f"scale={w_out}:{h_out}",
                        "-pix_fmt", "yuv420p", "-c:v", "libvpx-vp9", "-crf", "30",
                        ofnm,
                    ]
                else:
                    cmd = [
                        "ffmpeg", "-y", "-hide_banner", "-threads", "8", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", concat_file,
                        "-pix_fmt", "yuv420p", "-c:v", "libvpx-vp9", "-crf", "30",
                        ofnm,
                    ]
                
                log.info(f"Executing Dream3D frame-based conversion: {' '.join(cmd)}")
                
                # Execute FFmpeg command
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(ofnm):
                    log.info(f"Dream3D frame-based conversion successful: {ofnm}")
                    return ofnm
                else:
                    log.error(f"Dream3D frame-based conversion failed: {result.stderr}")
                    return None
                    
            finally:
                # Clean up temporary files
                try:
                    shutil.rmtree(temp_dir)
                    log.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    log.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
                    
        except ImportError as e:
            log.error(f"Required modules not available for Dream3D processing: {e}")
            return None
        except Exception as e:
            log.error(f"Dream3D frame extraction conversion failed: {e}")
            return None

    @classmethod 
    def _process_dream3d_data_to_frames(cls, data_array, temp_dir):
        """
        Process Dream3D data array and create image frames.
        """
        import numpy as np
        from PIL import Image
        
        extracted_frames = []
        
        try:
            # Process the data array to create frames
            if len(data_array.shape) == 3:
                # 3D data - use Z slices as frames
                num_frames = data_array.shape[0]  # Assuming Z is first dimension
                log.info(f"Processing 3D data with {num_frames} Z-slices as frames")
                
                for frame_idx in range(num_frames):
                    try:
                        # Extract slice
                        slice_data = data_array[frame_idx, :, :]
                        
                        # Normalize data to 0-255 range for image display
                        if slice_data.dtype in ['float32', 'float64']:
                            slice_normalized = ((slice_data - slice_data.min()) / (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)
                        else:
                            # For integer data, scale appropriately
                            if slice_data.max() <= 255:
                                slice_normalized = slice_data.astype(np.uint8)
                            else:
                                slice_normalized = ((slice_data - slice_data.min()) / (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)
                        
                        # Convert to PIL Image and save as frame
                        frame_path = os.path.join(temp_dir, f"frame_{frame_idx:04d}.png")
                        if len(slice_normalized.shape) == 2:
                            # Grayscale data
                            img = Image.fromarray(slice_normalized, mode='L')
                        else:
                            # RGB data (for IPFColor arrays)
                            img = Image.fromarray(slice_normalized)
                            
                        img.save(frame_path)
                        extracted_frames.append(frame_path)
                        log.debug(f"Created frame {frame_idx}: {frame_path}")
                        
                    except Exception as e:
                        log.warning(f"Error creating frame {frame_idx}: {e}")
                        continue
                        
            elif len(data_array.shape) == 4:
                # 4D data - typically (z, y, x, channels) or (z, x, y, channels)
                log.info(f"Processing 4D data with shape {data_array.shape}")
                
                # Determine the z-axis dimension (typically the first or largest dimension)
                z_dim = data_array.shape[0]  # Assume first dimension is z
                
                for frame_idx in range(z_dim):
                    try:
                        # Extract one z-slice 
                        frame_data = data_array[frame_idx]  # Shape: (y, x, channels) or (x, y, channels)
                        
                        # Handle different channel configurations
                        if frame_data.shape[-1] == 3:
                            # RGB data
                            if frame_data.dtype in ['float32', 'float64']:
                                # Normalize float data to 0-255
                                frame_normalized = ((frame_data - frame_data.min()) / (frame_data.max() - frame_data.min()) * 255).astype(np.uint8)
                            else:
                                if frame_data.max() <= 255:
                                    frame_normalized = frame_data.astype(np.uint8)
                                else:
                                    frame_normalized = ((frame_data - frame_data.min()) / (frame_data.max() - frame_data.min()) * 255).astype(np.uint8)
                            
                            img = Image.fromarray(frame_normalized, mode='RGB')
                        elif frame_data.shape[-1] == 4:
                            # 4-channel data (e.g., RGBA or quaternions)
                            # For quaternions or other 4D data, convert to RGB by using first 3 channels
                            frame_data_rgb = frame_data[:, :, :3]  # Take first 3 channels
                            if frame_data_rgb.dtype in ['float32', 'float64']:
                                frame_normalized = ((frame_data_rgb - frame_data_rgb.min()) / (frame_data_rgb.max() - frame_data_rgb.min()) * 255).astype(np.uint8)
                            else:
                                if frame_data_rgb.max() <= 255:
                                    frame_normalized = frame_data_rgb.astype(np.uint8)
                                else:
                                    frame_normalized = ((frame_data_rgb - frame_data_rgb.min()) / (frame_data_rgb.max() - frame_data_rgb.min()) * 255).astype(np.uint8)
                            
                            img = Image.fromarray(frame_normalized, mode='RGB')
                        elif frame_data.shape[-1] == 1:
                            # Single channel - treat as grayscale
                            frame_data_2d = frame_data.squeeze()
                            if frame_data_2d.dtype in ['float32', 'float64']:
                                frame_normalized = ((frame_data_2d - frame_data_2d.min()) / (frame_data_2d.max() - frame_data_2d.min()) * 255).astype(np.uint8)
                            else:
                                frame_normalized = frame_data_2d.astype(np.uint8)
                            img = Image.fromarray(frame_normalized, mode='L')
                        else:
                            log.warning(f"Unsupported channel count: {frame_data.shape[-1]} for frame {frame_idx}")
                            continue
                        
                        frame_path = os.path.join(temp_dir, f"frame_{frame_idx:04d}.png")
                        img.save(frame_path)
                        extracted_frames.append(frame_path)
                        
                    except Exception as e:
                        log.warning(f"Error creating frame {frame_idx}: {e}")
                        continue
                        
            elif len(data_array.shape) == 2:
                # 2D data - create a single frame (not really a video)
                log.info("Processing 2D data as single frame")
                
                # Normalize data
                if data_array.dtype in ['float32', 'float64']:
                    data_normalized = ((data_array - data_array.min()) / (data_array.max() - data_array.min()) * 255).astype(np.uint8)
                else:
                    if data_array.max() <= 255:
                        data_normalized = data_array.astype(np.uint8)
                    else:
                        data_normalized = ((data_array - data_array.min()) / (data_array.max() - data_array.min()) * 255).astype(np.uint8)
                
                # Create multiple copies to make a short video
                for frame_idx in range(5):  # Create 5 duplicate frames
                    frame_path = os.path.join(temp_dir, f"frame_{frame_idx:04d}.png")
                    img = Image.fromarray(data_normalized, mode='L')
                    img.save(frame_path)
                    extracted_frames.append(frame_path)
                    
            else:
                log.error(f"Unsupported data array shape: {data_array.shape}")
                return []
                
        except Exception as e:
            log.error(f"Error processing Dream3D data: {e}")
            return []
            
        return extracted_frames

    @classmethod
    def thumbnail(cls, token, ofnm, width, height, **kw):
        ifnm = token.first_input_file()
        with Locks(ifnm, ofnm, failonexist=True) as l:
            if l.locked is False:
                raise ImageServiceFuture((1, 15))
            # log.info('Creating thumbnail:')

            ifnm = token.first_input_file()
            imw = token.dims["image_num_x"]
            imh = token.dims["image_num_y"]

            w_out, h_out = compute_new_size(
                imw, imh, width, height, keep_aspect_ratio=True, no_upsample=True
            )

            cmd = [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-threads",
                "1",
                "-loglevel",
                "error",
                "-i",
                ifnm,
                "-vframes",
                "1",
                "-s",
                str(w_out) + "x" + str(h_out),
                ofnm,
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output, error = process.communicate()

            if error is not None:
                return None

            return ofnm

    @classmethod
    def slice(cls, token, ofnm, z, t, roi=None, **kw):
        ifnm = token.first_input_file()
        with Locks(ifnm, ofnm, failonexist=True) as l:
            if l.locked is False:
                raise ImageServiceFuture((1, 15))

            # # log.info('Creating slice:')
            # cmd = [
            #     "ffmpeg",
            #     "-y",
            #     "-hide_banner",
            #     "-threads",
            #     "1",
            #     "-loglevel",
            #     "error",
            #     "-i",
            #     ifnm,
            #     "-vf",
            #     "select=eq(n\\," + str(t[0] - 1) + ")",
            #     "-vframes",
            #     "1",
            #     "-compression_algo",
            #     "raw",
            #     "-pix_fmt",
            #     "rgb24",
            #     ofnm,
            # ]

            # Use time-based seek instead of NAL-fragile frame selection
            time_in_sec = (
                float(t[0]) / 25
            )  # assuming 25 fps, will need to adjust based on actual frame rate later
            cmd = [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                f"{time_in_sec:.3f}",
                "-i",
                ifnm,
                "-frames:v",
                "1",
                "-pix_fmt",
                "rgb24",
                ofnm,
            ]

            # Use shlex.quote to properly escape filenames with special characters
            import shlex
            single_cmd = " ".join(shlex.quote(arg) for arg in cmd)
            log.info(f"-----Executing command: {single_cmd}")

            process = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,  # avoid blocking stdin
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy(),  # inherit full shell env
                text=True,
            )

            if process.returncode == 0 and os.path.exists(ofnm):
                log.info(f"Video conversion successful using of {ofnm}")
                return ofnm
            else:
                log.warning(f"Video conversion failed of {ofnm}: {process.stderr}")
                # Clean up partial file if it exists
                if os.path.exists(ofnm):
                    try:
                        os.remove(ofnm)
                    except:
                        pass

            return None

    @classmethod
    def tile(cls, token, ofnm, level, x, y, sz, **kw):
        return None

    @classmethod
    def info(cls, token, **kw):

        ifnm = token.first_input_file()
        if not cls.supported(token):
            return None

        with Locks(ifnm, failonread=(True)) as l:
            if l.locked is False:
                raise ImageServiceFuture((1, 15))

            cmd = [
                "ffprobe",
                "-hide_banner",
                "-threads",
                "4",
                "-loglevel",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                "-i",
                ifnm,
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output, error = process.communicate()

            if error is not None:
                return dict()

            data = json.loads(output)

            if "streams" not in list(data.keys()):
                return dict()

            if "format" not in list(data.keys()):
                return dict()

            vid_stream = [s for s in data["streams"] if s["codec_type"] == "video"][0]
            f_format = data["format"]

            try:
                cmd = ["file", ifnm]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                output, error = process.communicate()
                endian = output.decode().split("(")[1].split("-")[0]

            except Exception as e:
                endian = "little"

            out_dict = dict()
            out_dict["image_num_x"] = vid_stream["width"]
            out_dict["image_num_y"] = vid_stream["height"]
            out_dict["image_num_z"] = 1
            out_dict["converter"] = "ffmpeg"
            out_dict["format"] = f_format["format_name"]
            out_dict["image_num_resolution_levels"] = 0
            out_dict["raw_endian"] = endian
            out_dict["image_pixel_depth"] = 8
            out_dict["image_pixel_format"] = "unsigned integer"
            out_dict["image_mode"] = "RGB"
            out_dict["image_series_index"] = 0
            out_dict["image_num_p"] = 1
            out_dict["image_num_c"] = 3
            out_dict["image_num_series"] = 0
            out_dict["filesize"] = f_format["size"]
            # log.info("FOOBAR " + str(f_format) + '\n\n' + str(vid_stream))
            if "nb_frames" in list(vid_stream.keys()):
                out_dict["image_num_t"] = vid_stream["nb_frames"]
            else:
                duration = float(f_format["duration"])
                frame_rate = float(
                    float(vid_stream["avg_frame_rate"].split("/")[0])
                    / float(vid_stream["avg_frame_rate"].split("/")[1])
                )
                out_dict["image_num_t"] = int(duration * frame_rate)

            log.info(f"-----Video info: {out_dict}")

            return out_dict

    def meta(cls, token, **kw):
        return cls.info(token, **kw)


try:
    ConverterFfmpeg.init()
except Exception:
    log.warning("FFMPEG not available")
