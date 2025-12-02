""" BioImageConvert command line converter
"""

__Contributors__    = "Dmitry Fedorov, Griffin Danninger (Upgraded by Wahid Sadique Koly)"
__version__   = "1.3"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

# !!! upgraded new code for python3.10+
import logging
import os.path
import math
from itertools import groupby
from lxml import etree

import os
import sys
import ctypes

from tg import config
#from collections import OrderedDict
from bq.util.compat import OrderedDict
from bq.util.locks import Locks
from bq.util.read_write_locks import HashedReadWriteLock
import bq.util.io_misc as misc
import bq.util.responses as responses

from bq.image_service.controllers.exceptions import ImageServiceException, ImageServiceFuture
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converter_base import ConverterBase, Format
from bq.image_service.controllers.defaults import block_reads, block_tile_reads

import subprocess

log = logging.getLogger('bq.image_service.converter_imgcnv')

try:
	import pydicom
	# Backward compatibility alias for legacy code
	dicom = pydicom
except ImportError:
	try:
		import dicom
		log.warning('Using legacy dicom module. Please upgrade to pydicom.')
	except ImportError:
		log.warning('Neither pydicom nor legacy dicom module found. DICOM support disabled.')
		pydicom = None
		dicom = None

################################################################################
# dynlib misc
################################################################################

# thread level lock on libimgcnv
rw = HashedReadWriteLock()

imgcnv_lib_name = 'libimgcnv.so'
if os.name == 'nt':
	imgcnv_lib_name = 'libimgcnv.dll'
elif sys.platform == 'darwin':
	imgcnv_lib_name = 'libimgcnv.dylib'
try:
	imgcnvlib = ctypes.cdll.LoadLibrary(imgcnv_lib_name)
except OSError as e:
	log.exception('Failed to load %s: %s', imgcnv_lib_name, e)
	imgcnvlib = None

if os.name == 'nt':
	def call_imgcnvlib(command):
		if imgcnvlib is None:
			raise ImageServiceException(404, 'imgcnvlib not found')
		arr = (ctypes.c_wchar_p * len(command))()
		arr[:] = [misc.tounicode(i) for i in command]
		res = ctypes.pointer(ctypes.c_char_p())

		try:
			rw.acquire_write('libimgcnv')
			r = imgcnvlib.imgcnv(len(command), arr, res)
			rw.release_write('libimgcnv')
		except Exception:
			log.exception('Exception calling libbioimage')
			return 100, None

		out = res.contents.value
		_ = imgcnvlib.imgcnv_clear(res)
		return r, out
else:
	# !!! Subprocess approach, as using ctypes is really hard to debug
	def call_imgcnvlib(command):
		if not isinstance(command, (list, tuple)):
			raise ValueError("Command must be a list or tuple of strings")

		try:
			result = subprocess.run(
				command,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=False
			)
			r = result.returncode
			out = result.stdout.strip()
			if result.stderr:
				log.warning(f"--- call_imgcnv stderr: {result.stderr.strip()}")
		except Exception as e:
			log.exception("Exception calling imgcnv subprocess")
			return 100, None

		return r, out

################################################################################
# misc
################################################################################

def readAndSet(el, attr, d, key, defval=None, f=None):
	v = el.get(attr, defval)
	if v is None:
		return
	if f is not None:
		d[key] = f(v)
	else:
		d[key] = v

################################################################################
# DICOM misc
################################################################################

# Map DICOM Specific Character Set to python equivalent
dicom_encoding = {
	'': 'iso8859',           # default character set for DICOM
	'ISO_IR 6': 'iso8859',   # alias for latin_1 too
	'ISO_IR 100': 'latin_1',
	'ISO 2022 IR 87': 'iso2022_jp',
	'ISO 2022 IR 13': 'iso2022_jp',
	'ISO 2022 IR 149': 'euc_kr',
	'ISO_IR 192': 'UTF8',
	'GB18030': 'GB18030',
	'ISO_IR 126': 'iso_ir_126',
	'ISO_IR 127': 'iso_ir_127',
	'ISO_IR 138': 'iso_ir_138',
	'ISO_IR 144': 'iso_ir_144',
}

def dicom_init_encoding(dataset):
	# Modern pydicom access pattern
	try:
		# Try modern pydicom first
		encoding = dataset.get(('0008', '0005'), 'ISO_IR 6')
		if hasattr(encoding, 'value'):
			encoding = encoding.value
	except:
		# Fallback for legacy access
		try:
			encoding = dataset[0x0008, 0x0005].value
		except:
			encoding = 'ISO_IR 6'
	
	if encoding not in dicom_encoding:
		return 'latin_1'
	return dicom_encoding[encoding]

def safedecode(s, encoding):
	if isinstance(s, str):
		return s
	if isinstance(s, bytes):
		try:
			return s.decode(encoding)
		except UnicodeDecodeError:
			try:
				return s.decode('utf-8')
			except UnicodeDecodeError:
				try:
					return s.decode('latin-1')
				except UnicodeDecodeError:
					return s.decode('ascii', 'replace')
	# Handle other types (int, float, etc.)
	return str(s)

def dicom_parse_date(v):
	v = str(v)  # Ensure string type
	if len(v) < 1:
		return v
	if '.' in v:
		return v.replace('.', '-')
	if '/' in v:
		return v.replace('/', '-')
	if len(v) >= 8:
		return '%s-%s-%s' % (v[0:4], v[4:6], v[6:8])
	return v

def dicom_parse_time(v):
	v = str(v)  # Ensure string type
	if len(v) < 1:
		return v
	if ':' in v:
		return v
	if '.' in v:
		return v.replace('.', ':')
	if len(v) >= 6:
		return '%s:%s:%s' % (v[0:2], v[2:4], v[4:6])
	return v

################################################################################
# ConverterImgcnv
################################################################################

class ConverterImgcnv(ConverterBase):
	installed = False
	version = None
	installed_formats = None
	CONVERTERCOMMAND = 'imgcnv' if os.name != 'nt' else 'imgcnv.exe'
	name = 'imgcnv'
	required_version = '2.0.1'

	info_map = {
		'image_num_x'        : 'image_num_x',
		'image_num_y'        : 'image_num_y',
		'image_num_z'        : 'image_num_z',
		'image_num_t'        : 'image_num_t',
		'image_num_c'        : 'image_num_c',
		'image_num_series'   : 'image_num_series',
		'image_series_index' : 'image_series_index',
		'image_num_fovs'     : 'image_num_fovs',
		'image_num_labels'   : 'image_num_labels',
		'image_num_previews' : 'image_num_previews',
		'format'             : 'format',
		'file_mode'          : 'file_mode',
		'image_mode'         : 'image_mode',
		'image_pixel_format' : 'image_pixel_format',
		'image_pixel_depth'  : 'image_pixel_depth',
		'raw_endian'         : 'raw_endian',
		'dimensions'         : 'dimensions',
		'pixel_resolution_x' : 'pixel_resolution_x',
		'pixel_resolution_y' : 'pixel_resolution_y',
		'pixel_resolution_z' : 'pixel_resolution_z',
		'pixel_resolution_unit_x' : 'pixel_resolution_unit_x',
		'pixel_resolution_unit_y' : 'pixel_resolution_unit_y',
		'pixel_resolution_unit_z' : 'pixel_resolution_unit_z',
		'image_num_resolution_levels': 'image_num_resolution_levels',
		'image_resolution_level_scales': 'image_resolution_level_scales',
		'tile_num_x': 'tile_num_x',
		'tile_num_y': 'tile_num_y',
	}

	extended_dimension_names = ['serie', 'fov', 'rotation', 'scene', 'illumination', 'phase', 'view', 'label', 'preview']

	#######################################
	# Version and Installed
	#######################################

	@classmethod
	def get_version(cls):
		'''returns the version of command line utility'''
		o = cls.run_command([cls.CONVERTERCOMMAND, '-v'])
		try:
			d = [int(s) for s in o.split('.')]
		except ValueError:
			log.error('imgcnv is too old, cannot proceed')
			raise Exception('imgcnv is too old, cannot proceed')
		if len(d) < 3:
			d.append(0)
		return {
			'full': '.'.join([str(i) for i in d]),
			'numeric': d,
			'major': d[0],
			'minor': d[1],
			'build': d[2]
		}

	#######################################
	# Formats
	#######################################

	@classmethod
	def get_formats(cls):
		'''inits supported file formats'''
		if cls.installed_formats is None:
			formats_xml = cls.run_command([cls.CONVERTERCOMMAND, '-fmtxml'])
			formats = etree.fromstring('<formats>%s</formats>' % formats_xml)

			cls.installed_formats = OrderedDict()
			codecs = formats.xpath('//codec')
			for c in codecs:
				try:
					name = c.get('name')
					fullname = c.xpath('tag[@name="fullname"]')[0].get('value', '')
					exts = c.xpath('tag[@name="extensions"]')[0].get('value', '').split('|')
					reading = len(c.xpath('tag[@name="support" and @value="reading"]')) > 0
					writing = len(c.xpath('tag[@name="support" and @value="writing"]')) > 0
					multipage = len(c.xpath('tag[@name="support" and @value="writing multiple pages"]')) > 0
					metadata = len(c.xpath('tag[@name="support" and @value="reading metadata"]')) > 0 or len(c.xpath('tag[@name="support" and @value="writing metadata"]')) > 0
					samples_min = misc.safeint(c.xpath('tag[@name="min-samples-per-pixel"]')[0].get('value', '0'))
					samples_max = misc.safeint(c.xpath('tag[@name="max-samples-per-pixel"]')[0].get('value', '0'))
					bits_min = misc.safeint(c.xpath('tag[@name="min-bits-per-sample"]')[0].get('value', '0'))
					bits_max = misc.safeint(c.xpath('tag[@name="max-bits-per-sample"]')[0].get('value', '0'))
				except IndexError:
					continue
				cls.installed_formats[name.lower()] = Format(
					name=name,
					fullname=fullname,
					ext=exts,
					reading=reading,
					writing=writing,
					multipage=multipage,
					metadata=metadata,
					samples=(samples_min, samples_max),
					bits=(bits_min, bits_max)
				)

	#######################################
	# Supported
	#######################################

	@classmethod
	def supported(cls, token, **kw):
		'''return True if the input file format is supported'''
		ifnm = token.first_input_file()
		log.debug('Supported for: %s', ifnm)
		supported = cls.run_read(ifnm, [cls.CONVERTERCOMMAND, '-supported', '-i', ifnm])
		return supported.startswith('yes')

	#######################################
	# Conversion
	#######################################

	@classmethod
	def run_command(cls, command):
		retcode, out = call_imgcnvlib(command)
		if retcode == 100 or retcode == 101:
			log.error('Libioimage retcode %s: retry once: %s', retcode, command)
			retcode, out = call_imgcnvlib(command)
		return out

	@classmethod
	def run_read(cls, ifnm, command):
		with Locks(ifnm, failonread=(not block_reads)) as l:
			if l.locked is False:
				raise ImageServiceFuture((1, 15))
			log.info('run_read dylib command: %s', misc.tounicode(command))
			retcode, out = call_imgcnvlib(command)
			if retcode == 100 or retcode == 101:
				log.error('Libioimage retcode %s: retry once: %s', retcode, command)
				retcode, out = call_imgcnvlib(command)
		return out

	@classmethod
	def run(cls, ifnm, ofnm, args, **kw):
		'''converts input filename into output using exact arguments as provided in args'''
		if not cls.installed:
			return None
		failonread = kw.get('failonread') or (not block_reads)
		tmp = None
		with Locks(ifnm, ofnm, failonexist=True) as l:
			if l.locked:
				command = [cls.CONVERTERCOMMAND]
				command.extend(args)
				log.debug('Run dylib command: %s', misc.tounicode(command))
				proceed = True
				if ofnm is not None and os.path.exists(ofnm) and os.path.getsize(ofnm) > 16:
					if kw.get('nooverwrite', False) is True:
						proceed = False
						log.warning('Run: output exists before command [%s], skipping', misc.tounicode(ofnm))
					else:
						log.warning('Run: output exists before command [%s], overwriting', misc.tounicode(ofnm))
				if proceed is True:
					retcode, out = call_imgcnvlib(command)
					if retcode == 100 or retcode == 101:
						log.error('Libioimage retcode %s: retry once: %s', retcode, command)
						retcode, out = call_imgcnvlib(command)
					if retcode == 99:
						log.info('Run: timed-out for [%s]', misc.tounicode(command))
						if ofnm is not None and os.path.exists(ofnm):
							os.remove(ofnm)
						raise ImageServiceException(412, 'Requested timeout reached')
					if retcode != 0:
						log.info('Run: returned [%s] for [%s]', retcode, misc.tounicode(command))
						return None
					if ofnm is None:
						return str(retcode)
			elif l.locked is False:
				raise ImageServiceFuture((1, 15))

		if ofnm is not None and os.path.exists(ofnm):
			with Locks(ofnm, failonread=failonread) as l:
				if l.locked is False:
					raise ImageServiceFuture((1, 15))

		if os.path.exists(ofnm) and os.path.getsize(ofnm) < cls.MINIMUM_FILE_SIZE:
			log.error('Run: output file is smaller than %s bytes, probably an error, removing [%s]', cls.MINIMUM_FILE_SIZE, ofnm)
			os.remove(ofnm)
			return None
		return ofnm

	#######################################
	# Meta - returns a dict with all the metadata fields
	#######################################

	@classmethod
	def meta(cls, token, **kw):
		'''returns a dict with file metadata'''
		if not cls.installed:
			return {}
		ifnm = token.first_input_file()
		log.debug('Meta for: %s', ifnm)

		command = [cls.CONVERTERCOMMAND, '-meta', '-i', ifnm]
		if token.series is not None and token.series != 0:
			command.extend(['-path', token.series])

		meta = cls.run_read(ifnm, command)
		if meta is None:
			return {}
		rd = {}
		for line in meta.splitlines():
			if not line:
				continue
			try:
				tag, val = [l.lstrip() for l in line.split(':', 1)]
			except ValueError:
				continue
			tag = safedecode(tag, 'utf-8').replace('%3A', ':')
			val = safedecode(val, 'utf-8').replace('\n', '').replace('%3E', '>').replace('%3C', '<').replace('%3A', ':').replace('%22', '"').replace('%0A', '\n')
			if val != '':
				log.debug("Meta Tag: %s ; Value: %s", tag, val)
				if tag == 'image_num_z' and 'image_num_z' in rd:
					log.debug("Slices already found: %s", rd['image_num_z'])
					pass
				elif tag == 'image_num_t' and 'image_num_t' in rd:
					log.debug("Frames already found: %s", rd['image_num_t'])
					pass
				else:
					rd[tag] = misc.safetypeparse(val)
				if tag[-16:] == 'ImageDescription':
					if val[:6] == "ImageJ":
						log.debug("ImageJ Description found")
						ijresult = {}
						for line in val.split('\n'):
							try:
								key, ijval = line.split('=')
							except Exception:
								continue
							key = key.strip()
							ijval = ijval.strip()
							ijresult[key] = ijval
						if 'slices' in ijresult:
							rd['image_num_z'] = int(ijresult['slices'])
						if 'frames' in ijresult:
							rd['image_num_t'] = int(ijresult['frames'])
		if 'dimensions' in rd:
			rd['dimensions'] = rd['dimensions'].replace(' ', '')

		if rd.get('image_num_z', 0) == 1 and rd.get('image_num_t', 0) == 1 and rd.get('image_num_p', 0) > 1:
			log.debug('Guessing meta z: %d', rd['image_num_p'])
			rd['image_num_z'] = rd['image_num_p']
		rd.setdefault('image_num_series', 0)
		rd.setdefault('image_series_index', 0)

		if token.is_multifile_series() is True:
			rd.update(token.meta)
			if token.meta.get('image_num_c', 0) > 1:
				if 'channel_color_0' in rd:
					del rd['channel_color_0']
				if 'channel_0_name' in rd:
					del rd['channel_0_name']

		for i in range(int(rd.get('image_num_c', 0))):
			path = 'channels/channel_%.5d' % i
			readAndSet(rd, 'channel_%s_name' % i, rd, '%s/name' % path)
			readAndSet(rd, 'channel_color_%s' % i, rd, '%s/color' % path)
		log.debug('RD: %s', str(rd))
		return rd

	#######################################
	# The info command returns the "core" metadata
	#######################################

	@classmethod
	def info(cls, token, **kw):
		'''returns a dict with file info'''
		ifnm = token.first_input_file()
		log.info('Info for: %s', ifnm)
		if not cls.installed:
			return {}
		if not os.path.exists(ifnm):
			return {}

		command = [cls.CONVERTERCOMMAND, '-meta-parsed', '-i', ifnm]
		if token.series is not None and token.series != 0:
			command.extend(['-path', token.series])
		if 'speed' in kw:
			command.extend(['-speed', kw.get('speed')])

		info = cls.run_read(ifnm, command)
		if info is None:
			return {}
		rd = {}
		for line in info.splitlines():
			if not line:
				continue
			try:
				tag, val = [l.strip() for l in line.split(':', 1)]
			except ValueError:
				continue
			tag = safedecode(tag, 'utf-8').replace('%3A', ':')
			val = safedecode(val, 'utf-8').replace('\n', '')
			if tag[-16:] == 'ImageDescription':
				if val[:6] == "ImageJ":
					ijresult = {}
					for line in val.split('%0A'):
						try:
							key, ijval = line.split('=')
						except Exception:
							continue
						key = key.strip()
						ijval = ijval.strip()
						ijresult[key] = ijval
					try:
						rd[cls.info_map['image_num_z']] = int(ijresult['slices'])
					except:
						continue
					try:
						rd[cls.info_map['image_num_t']] = int(ijresult['frames'])
					except:
						continue
			if tag == 'image_num_z' and 'image_num_z' in rd:
				log.debug("Slices already found: %s", rd['image_num_z'])
				continue
			if tag == 'image_num_t' and 'image_num_t' in rd:
				log.debug("Frames already found: %s", rd['image_num_t'])
				continue
			if tag not in cls.info_map:
				continue
			else:
				rd[cls.info_map[tag]] = misc.safetypeparse(val.replace('\n', ''))

		if 'dimensions' in rd:
			rd['dimensions'] = rd['dimensions'].replace(' ', '')

		rd.setdefault('image_num_series', 0)
		rd.setdefault('image_series_index', 0)
		rd.setdefault('image_num_z', 1)
		rd.setdefault('image_num_t', 1)
		rd.setdefault('image_num_p', 1)
		if rd['image_num_z'] == 1 and rd['image_num_t'] == 1 and rd['image_num_p'] > 1:
			log.debug('Guessing info z: %d', rd['image_num_p'])
			rd['image_num_z'] = rd['image_num_p']

		if token.is_multifile_series() is True:
			rd.update(token.meta)

		return rd

	#######################################
	# multi-file series misc
	#######################################

	@classmethod
	def write_files(cls, files, ofnm):
		'''writes a list of files into a file readable by imgcnv'''
		with open(ofnm, 'w', encoding='utf-8') as f:
			f.write('\n'.join(files))

	#######################################
	# Conversion
	#######################################

	@classmethod
	def convert(cls, token, ofnm, fmt=None, extra=None, **kw):
		'''converts a file and returns output filename'''
		ifnm = token.first_input_file()
		log.debug('convert: [%s] -> [%s] into %s for series %s with [%s]', ifnm, ofnm, fmt, token.series, extra)

		command = []
		if token.is_multifile_series() is False:
			if '-i' not in extra and '-il' not in extra:
				command.extend(['-i', ifnm])
		else:
			if '-i' not in extra and '-il' not in extra:
				files = token.input
				fl = '%s.files' % ofnm
				cls.write_files(files, fl)
				command.extend(['-il', fl])

			meta = token.meta or {}

			if '-geometry' not in extra:
				geom = '%s,%s' % (meta.get('image_num_z', 1), meta.get('image_num_t', 1))
				if meta.get('image_num_c', 0) > 1:
					geom = '%s,%s' % (geom, meta.get('image_num_c', 0))
				command.extend(['-geometry', geom])

			meta.update(token.dims)

			if '-resolution' not in extra:
				res = '%s,%s,%s,%s' % (meta.get('pixel_resolution_x', 0), meta.get('pixel_resolution_y', 0), meta.get('pixel_resolution_z', 0), meta.get('pixel_resolution_t', 0))
				command.extend(['-resolution', res])

		if token.series is not None and token.series != 0:
			command.extend(['-path', token.series])

		dims = token.dims or {}
		nz = dims.get('image_num_z', 1)
		nt = dims.get('image_num_t', 1)

		if token.histogram is not None and '-ihst' not in extra:
			command.extend(['-ihst', token.histogram])
		if ofnm is not None and '-o' not in extra:
			command.extend(['-o', ofnm])
		if fmt is not None and '-t' not in extra:
			command.extend(['-t', fmt])
			if cls.installed_formats[fmt].multipage is True:
				pass
			elif '-page' not in extra and nz * nt > 1:
				extra.extend(['-page', '1'])
		if extra is not None:
			command.extend(extra)
		return cls.run(ifnm, ofnm, command)

	@classmethod
	def thumbnail(cls, token, ofnm, width, height, **kw):
		'''converts input filename into output thumbnail'''
		ifnm = token.first_input_file()
		series = token.series
		log.debug('Thumbnail: %s %s %s for [%s]', width, height, series, ifnm)
		fmt = kw.get('fmt', 'jpeg')
		preproc = kw.get('preproc', '')
		preproc = preproc if preproc != '' else 'mid'

		command = ['-o', ofnm, '-t', fmt]
		if token.series is not None and token.series != 0:
			command.extend(['-path', token.series])

		info = token.dims or {}
		num_z = info.get('image_num_z', 1)
		num_t = info.get('image_num_t', 1)
		num_l = info.get('image_num_resolution_levels', 1)
		page = 0
		if preproc == 'mid':
			if num_z > 1 or num_t > 1:
				mx = (num_z if num_z > 1 else min(num_t, 500)) - 1
				page = min(max(0, mx // 2), mx)
		elif preproc != '':
			return None

		if num_l > 1:
			try:
				num_x = int(info.get('image_num_x', 1))
				num_y = int(info.get('image_num_y', 1))
				scales = [float(i) for i in info.get('image_resolution_level_scales', '').split(',')]
				sizes = [(round(num_x * i), round(num_y * i)) for i in scales]
				relatives = [max(width / sz[0], height / sz[1]) for sz in sizes]
				relatives = [i if i <= 1 else 0 for i in relatives]
				level = relatives.index(max(relatives))
				command.extend(['-res-level', str(level)])
			except Exception:
				pass

		queue = token.getQueue()
		if token.is_multifile_series() is False:
			if '-i' in queue:
				command.extend(['-i', ifnm])
			if '-page' not in queue:
				command.extend(['-page', str(page + 1)])
		else:
			files = token.input
			meta = token.meta or {}
			log.debug('thumbnail files: %s', files)

			samples = meta.get('image_num_c', 0)
			if samples < 2:
				token.input = files[page]
			else:
				page = page * samples
				command.extend(['-i', files[page]])
				for s in range(1, samples):
					command.extend(['-c', files[page + s]])

		command.extend(['-enhancemeta'])
		if info.get('image_pixel_depth', 16) != 8:
			command.extend(['-depth', '8,d,u'])

		method = kw.get('method', 'BC')
		command.extend(['-resize', '%s,%s,%s,AR' % (width, height, method)])

		command.extend(['-fusemeta'])
		if info.get('image_num_c', 1) < 4:
			command.extend(['-fusemethod', 'm'])
		else:
			command.extend(['-fusemethod', 'm'])

		if fmt == 'jpeg':
			command.extend(['-options', 'quality 95 progressive yes'])

		return command

	@classmethod
	def slice(cls, token, ofnm, z, t, roi=None, **kw):
		'''extract Z,T plane from input filename into output in OME-TIFF format'''
		ifnm = token.first_input_file()
		series = token.series

		log.debug('Slice: z=%s t=%s roi=%s series=%s for [%s]', z, t, roi, series, ifnm)
		z1, z2 = z
		t1, t2 = t
		x1, x2, y1, y2 = roi
		fmt = kw.get('fmt', 'bigtiff')
		info = token.dims or {}

		command = []
		if token.series is not None and token.series != 0:
			command.extend(['-path', token.series])

		if t2 == 0:
			t2 = t1
		if z2 == 0:
			z2 = z1

		pages = []
		for ti in range(t1, t2 + 1):
			for zi in range(z1, z2 + 1):
				if info.get('image_num_t', 1) == 1:
					page_num = zi
				elif info.get('image_num_z', 1) == 1:
					page_num = ti
				elif info.get('dimensions', 'XYCZT').replace(' ', '').startswith('XYCT') is False:
					page_num = (ti - 1) * info.get('image_num_z', 1) + zi
				else:
					page_num = (zi - 1) * info.get('image_num_t', 1) + ti
				pages.append(page_num)

		log.debug('slice pages: %s', pages)

		if token.is_multifile_series() is False:
			log.debug('Slice for single-file series')
			command.extend(['-page', ','.join([str(p) for p in pages])])
		else:
			log.debug('Slice for multi-file series')
			files = token.input
			meta = token.meta or {}
			channels = meta.get('image_num_c', 0)

			if len(pages) == 1 and channels <= 1:
				token.input = files[pages[0] - 1]
			else:
				if channels > 1:
					geom = '1,1,%s' % (channels)
					command.extend(['-geometry', geom])
					cpages = []
					for p in [p - 1 for p in pages]:
						for c in range(channels):
							cpages.append(p * channels + c)
					token.input = [files[p] for p in cpages]
				else:
					token.input = [files[p - 1] for p in pages]

		if not x1 == x2 or not y1 == y2:
			if not x1 == x2:
				if x1 > 0:
					x1 = x1 - 1
				if x2 > 0:
					x2 = x2 - 1
			if not y1 == y2:
				if y1 > 0:
					y1 = y1 - 1
				if y2 > 0:
					y2 = y2 - 1
			command.extend(['-roi', '%s,%s,%s,%s' % (x1, y1, x2, y2)])

		nd = []
		for k, v in kw.items():
			if k in cls.extended_dimension_names:
				if len(v) > 1:
					raise ImageServiceException(responses.UNPROCESSABLE_ENTITY, 'Ranges in extended dimensions are not yet supported')
				nd.append('%s:%s' % (k, v[0]))
		if len(nd) > 0:
			command.extend(['-slice', ','.join(nd)])

		return command

	@classmethod
	def tile(cls, token, ofnm, level, x, y, sz, **kw):
		'''extract tile Level,X,Y tile from input filename into output in OME-TIFF format'''

		if kw.get('arbitrary_size', False) == True or level is None or sz is None:
			return None

		ifnm = token.first_input_file()
		series = token.series
		page = 0
		log.debug('Tile: %s %s %s %s %s for [%s]', level, x, y, sz, series, ifnm)

		info = token.dims or {}
		tile_w = info.get('tile_num_x', 0)
		tile_h = info.get('tile_num_y', 0)
		num_l = info.get('image_num_resolution_levels', 1)
		if num_l <= 1 or tile_w < 1 or tile_h < 1:
			log.debug('Image does not contain tiles, skipping...')
			return None

		queue = token.getQueue()
		command = []
		if token.series is not None and token.series != 0:
			command.extend(['-path', token.series])

		if '-i' not in queue and '-il' not in queue and '-page' not in queue:
			if token.is_multifile_series() is False:
				command.extend(['-i', ifnm])
				command.extend(['-page', str(page + 1)])
			else:
				files = token.input
				meta = token.meta or {}
				samples = meta.get('image_num_c', 0)
				if samples < 2:
					command.extend(['-i', files[page]])
				else:
					page = page * samples
					command.extend(['-i', files[page]])
					for s in range(1, samples):
						command.extend(['-c', files[page + s]])

		level = misc.safeint(level, 0)
		x = misc.safeint(x, 0)
		y = misc.safeint(y, 0)
		sz = misc.safeint(sz, 0)
		command.extend(['-tile', '%s,%s,%s,%s' % (sz, x, y, level)])

		command.extend(['-speed', token.get_speed_file()])

		return command

	#######################################
	# Special methods
	#######################################

	@classmethod
	def writeHistogram(cls, token, ofnm, **kw):
		'''writes Histogram in libbioimage format'''
		ifnm = token.first_input_file()
		log.debug('Writing histogram for %s into: %s', ifnm, ofnm)
		command = ['-ohst', ofnm]
		if token.series is not None and token.series != 0:
			command.extend(['-path', token.series])
		queue = token.getQueue()
		page = 0
		if '-i' not in queue and '-il' not in queue:
			if token.is_multifile_series() is False:
				command.extend(['-i', ifnm])
			else:
				files = token.input
				meta = token.meta or {}
				samples = meta.get('image_num_c', 0)
				if samples < 2:
					command.extend(['-i', files[page]])
				else:
					page = page * samples
					command.extend(['-i', files[page]])
					for s in range(1, samples):
						command.extend(['-c', files[page + s]])
		command.extend(queue)

		info = token.dims or {}
		num_l = info.get('image_num_resolution_levels', 1)
		if num_l > 1:
			try:
				width = 500
				height = 500
				num_x = int(info.get('image_num_x', 1))
				num_y = int(info.get('image_num_y', 1))
				scales = [float(i) for i in info.get('image_resolution_level_scales', '').split(',')]
				sizes = [(round(num_x * i), round(num_y * i)) for i in scales]
				relatives = [max(width / sz[0], height / sz[1]) for sz in sizes]
				relatives = [i if i <= 1 else 0 for i in relatives]
				level = relatives.index(max(relatives))
				command.extend(['-res-level', str(level)])
			except Exception:
				pass

		return cls.run(ifnm, ofnm, command, failonread=(not block_tile_reads))

	#######################################
	# Sort and organize files
	#######################################

	@classmethod
	def group_files_dicom(cls, files, **kw):
		'''return list with lists containing grouped and ordered dicom file paths'''

		if pydicom is None:
			log.warning('pydicom not available, cannot group DICOM files')
			return False

		def read_tag(ds, key, default=None):
			"""Read DICOM tag with modern pydicom compatibility"""
			try:
				# Modern pydicom approach
				if hasattr(ds, 'get'):
					element = ds.get(key)
				else:
					element = ds[key] if key in ds else None
				
				if element is None:
					return default if default is not None else ''
				
				# Handle value extraction
				if hasattr(element, 'value'):
					return element.value
				else:
					return element
			except (KeyError, AttributeError):
				return default if default is not None else ''

		def read_tag_float(ds, key, default=None):
			try:
				val = read_tag(ds, key)
				if val is None or val == '':
					return default
				return float(val)
			except (ValueError, TypeError):
				return default

		def read_tag_int(ds, key, default=None):
			try:
				val = read_tag(ds, key)
				if val is None or val == '':
					return default
				return int(val)
			except (ValueError, TypeError):
				return default

		if not cls.installed:
			return False
		log.debug('Group %s files', len(files))
		data = []
		groups = []
		blobs = []
		
		for f in files:
			try:
				# Modern pydicom file reading
				ds = pydicom.dcmread(f, force=True)
			except Exception:
				blobs.append(f)
				continue

			# Check for pixel data using modern approach
			if not hasattr(ds, 'PixelData') and 'PixelData' not in ds:
				blobs.append(f)
				continue

			modality = read_tag(ds, ('0008', '0060'))
			patient_id = read_tag(ds, ('0010', '0020'))
			study_uid = read_tag(ds, ('0020', '000d'))
			series_uid = read_tag(ds, ('0020', '000e'))
			series_num = read_tag(ds, ('0020', '0012'))
			acqui_num = read_tag(ds, ('0020', '0011'))
			instance_num = read_tag_int(ds, ('0020', '0013'), 0)
			slice_loc = read_tag_float(ds, ('0020', '1041'), 0.0)

			num_temp_p = read_tag_int(ds, ('0020', '0105'), 0)
			num_frames = read_tag_int(ds, ('0028', '0008'), 0)

			mr_acq_typ = read_tag(ds, ('0018', '0023'))
			force_time = False
			
			# Logic for determining time series vs volume
			if mr_acq_typ == '3D' and ('0020', '1041') not in ds:
				force_time = True
			if mr_acq_typ == '2D' and ('0020', '1041') in ds:
				force_time = False

			key = '%s/%s/%s/%s/%s' % (modality, patient_id, study_uid, series_uid, acqui_num)
			d = (key, slice_loc or instance_num, f, num_temp_p or num_frames or force_time)
			data.append(d)
			log.debug('Key: %s, series_num: %s, instance_num: %s, num_temp_p: %s, num_frames: %s, slice_loc: %s', 
					 key, series_num, instance_num, num_temp_p, num_frames, slice_loc)
			log.debug('Data: %s', d)

		# Group and sort
		data = sorted(data, key=lambda x: x[0])
		for k, g in groupby(data, lambda x: x[0]):
			groups.append(sorted(list(g), key=lambda x: x[1]))

		# Prepare output
		images = []
		geometry = []
		for g in groups:
			l = [f[2] for f in g]
			images.append(l)
			frame_num = g[0][3]
			if frame_num is True:
				frame_num = len(l)
			if len(l) == 1:
				geometry.append({'t': 1, 'z': 1})
			elif frame_num > 0:
				z = len(l) // frame_num
				geometry.append({'t': frame_num, 'z': z})
			else:
				geometry.append({'t': 1, 'z': len(l)})

		log.debug('group_files_dicom found: %s image groups, %s blobs', len(images), len(blobs))
		return (images, blobs, geometry)

	#######################################
	# DICOM metadata parser
	#######################################

	@classmethod
	def meta_dicom(cls, ifnm, series=0, xml=None, **kw):
		'''appends nodes to XML'''
		if os.path.basename(ifnm) == 'DICOMDIR':
			return

		if pydicom is None:
			log.warning('pydicom not available, skipping DICOM metadata...')
			return

		def recurse_tree(dataset, parent, encoding='latin-1'):
			for de in dataset:
				if de.tag == ('7fe0', '0010'):
					continue
				node = etree.SubElement(parent, 'tag', name=de.name, type=':///DICOM#%04.x,%04.x' % (de.tag.group, de.tag.element))

				if de.VR == "SQ":
					for i, dataset in enumerate(de.value):
						recurse_tree(dataset, node, encoding)
				else:
					# Handle MultiValue properly for modern pydicom
					if hasattr(pydicom, 'multival') and isinstance(de.value, pydicom.multival.MultiValue):
						value = ','.join(safedecode(i, encoding) for i in de.value)
					elif hasattr(de.value, '__iter__') and not isinstance(de.value, (str, bytes)):
						# Handle other iterable types
						value = ','.join(safedecode(i, encoding) for i in de.value)
					else:
						value = safedecode(de.value, encoding)
					try:
						node.set('value', value.strip())
					except (ValueError, Exception):
						pass

		try:
			_, tmp = misc.start_nounicode_win(ifnm, [])
			ds = pydicom.dcmread(tmp or ifnm, force=True)
		except Exception:
			misc.end_nounicode_win(tmp)
			return
		
		encoding = dicom_init_encoding(ds)
		recurse_tree(ds, xml, encoding=encoding)
		misc.end_nounicode_win(tmp)

	#######################################
	# Most important DICOM metadata
	#######################################

	@classmethod
	def meta_dicom_parsed(cls, ifnm, xml=None, **kw):
		'''appends nodes to XML'''

		if pydicom is None:
			log.warning('pydicom not available, skipping DICOM metadata...')
			return

		def append_tag(dataset, tag, parent, name=None, fmt=None, safe=True, encoding='latin-1'):
			"""Modern pydicom compatible tag appending"""
			try:
				# Modern access pattern
				if hasattr(dataset, 'get'):
					de = dataset.get(tag, None)
				else:
					de = dataset[tag] if tag in dataset else None
			except (KeyError, AttributeError):
				return

			if de is None:
				return
			
			name = name or de.name
			typ = ':///DICOM#%04.x,%04.x' % (de.tag.group, de.tag.element)

			# Extract value
			if hasattr(de, 'value'):
				raw_value = de.value
			else:
				raw_value = de

			if fmt is None:
				# Handle MultiValue for modern pydicom
				if hasattr(pydicom, 'multival') and isinstance(raw_value, pydicom.multival.MultiValue):
					value = ','.join(safedecode(i, encoding) for i in raw_value)
				elif hasattr(raw_value, '__iter__') and not isinstance(raw_value, (str, bytes)):
					value = ','.join(safedecode(i, encoding) for i in raw_value)
				else:
					value = safedecode(raw_value, encoding)
			else:
				if safe is True:
					try:
						value = fmt(safedecode(raw_value, encoding))
					except Exception:
						value = safedecode(raw_value, encoding)
				else:
					value = fmt(safedecode(raw_value, encoding))
			
			value = value.strip()
			if len(value) > 0:
				etree.SubElement(parent, 'tag', name=name, value=value, type=typ)

		try:
			_, tmp = misc.start_nounicode_win(ifnm, [])
			ds = pydicom.dcmread(tmp or ifnm, force=True)
		except Exception:
			misc.end_nounicode_win(tmp)
			return

		encoding = dicom_init_encoding(ds)

		# Extract key DICOM tags
		append_tag(ds, ('0010', '0020'), xml, encoding=encoding)  # Patient ID
		try:
			append_tag(ds, ('0010', '0010'), xml, name='Patient\'s First Name', safe=False, fmt=lambda x: x.split('^', 1)[1], encoding=encoding)
			append_tag(ds, ('0010', '0010'), xml, name='Patient\'s Last Name', safe=False, fmt=lambda x: x.split('^', 1)[0], encoding=encoding)
		except Exception:
			append_tag(ds, ('0010', '0010'), xml, encoding=encoding)
		
		append_tag(ds, ('0010', '0040'), xml, encoding=encoding)  # Patient's Sex
		append_tag(ds, ('0010', '1010'), xml, encoding=encoding)  # Patient's Age
		append_tag(ds, ('0010', '0030'), xml, fmt=dicom_parse_date)  # Patient's Birth Date
		append_tag(ds, ('0012', '0062'), xml, encoding=encoding)  # Patient Identity Removed
		append_tag(ds, ('0008', '0020'), xml, fmt=dicom_parse_date)  # Study Date
		append_tag(ds, ('0008', '0030'), xml, fmt=dicom_parse_time)  # Study Time
		append_tag(ds, ('0008', '0060'), xml, encoding=encoding)  # Modality
		append_tag(ds, ('0008', '1030'), xml, encoding=encoding)  # Study Description
		append_tag(ds, ('0008', '103e'), xml, encoding=encoding)  # Series Description
		append_tag(ds, ('0008', '0080'), xml, encoding=encoding)  # Institution Name
		append_tag(ds, ('0008', '0090'), xml, encoding=encoding)  # Referring Physician's Name
		append_tag(ds, ('0008', '0008'), xml)  # Image Type
		append_tag(ds, ('0008', '0012'), xml, fmt=dicom_parse_date)  # Instance Creation Date
		append_tag(ds, ('0008', '0013'), xml, fmt=dicom_parse_time)  # Instance Creation Time
		append_tag(ds, ('0008', '1060'), xml, encoding=encoding)  # Name of Physician(s) Reading Study
		append_tag(ds, ('0008', '2111'), xml, encoding=encoding)  # Derivation Description

		misc.end_nounicode_win(tmp)

try:
	ConverterImgcnv.init()
except Exception as e:
	log.warning(f"Imgcnv not available, issue: {e}")


# !!! old codes
# import logging
# import os.path
# import math
# from itertools import groupby
# from lxml import etree

# import os
# import sys
# import ctypes

# from tg import config
# #from collections import OrderedDict
# from bq.util.compat import OrderedDict
# from bq.util.locks import Locks
# from bq.util.read_write_locks import HashedReadWriteLock
# import bq.util.io_misc as misc
# import bq.util.responses as responses

# from bq.image_service.controllers.exceptions import ImageServiceException, ImageServiceFuture
# from bq.image_service.controllers.process_token import ProcessToken
# from bq.image_service.controllers.converter_base import ConverterBase, Format
# from bq.image_service.controllers.defaults import block_reads, block_tile_reads

# import subprocess

# log = logging.getLogger('bq.image_service.converter_imgcnv')

# try:
# 	import pydicom
# 	# Backward compatibility alias for legacy code
# 	dicom = pydicom
# except ImportError:
# 	try:
# 		import dicom
# 		log.warning('Using legacy dicom module. Please upgrade to pydicom.')
# 	except ImportError:
# 		log.warning('Neither pydicom nor legacy dicom module found. DICOM support disabled.')
# 		pydicom = None
# 		dicom = None

# ################################################################################
# # dynlib misc
# ################################################################################

# # thread level lock on libimgcnv
# rw = HashedReadWriteLock()

# imgcnv_lib_name = 'libimgcnv.so'
# if os.name == 'nt':
# 	imgcnv_lib_name = 'libimgcnv.dll'
# elif sys.platform == 'darwin':
# 	imgcnv_lib_name = 'libimgcnv.dylib'
# try:
# 	imgcnvlib = ctypes.cdll.LoadLibrary(imgcnv_lib_name)
# except OSError as e:
# 	log.exception('Failed to load %s: %s', imgcnv_lib_name, e)
# 	imgcnvlib = None

# if os.name == 'nt':
# 	def call_imgcnvlib(command):
# 		if imgcnvlib is None:
# 			raise ImageServiceException(404, 'imgcnvlib not found')
# 		arr = (ctypes.c_wchar_p * len(command))()
# 		arr[:] = [misc.tounicode(i) for i in command]
# 		res = ctypes.pointer(ctypes.c_char_p())

# 		try:
# 			rw.acquire_write('libimgcnv')
# 			r = imgcnvlib.imgcnv(len(command), arr, res)
# 			rw.release_write('libimgcnv')
# 		except Exception:
# 			log.exception('Exception calling libbioimage')
# 			return 100, None

# 		out = res.contents.value
# 		_ = imgcnvlib.imgcnv_clear(res)
# 		return r, out
# else:
# 	# !!! Subprocess approach, as using ctypes is really hard to debug
# 	def call_imgcnvlib(command):
# 		if not isinstance(command, (list, tuple)):
# 			raise ValueError("Command must be a list or tuple of strings")

# 		try:
# 			result = subprocess.run(
# 				command,
# 				stdout=subprocess.PIPE,
# 				stderr=subprocess.PIPE,
# 				text=True,
# 				check=False
# 			)
# 			r = result.returncode
# 			out = result.stdout.strip()
# 			if result.stderr:
# 				log.warning(f"--- call_imgcnv stderr: {result.stderr.strip()}")
# 		except Exception as e:
# 			log.exception("Exception calling imgcnv subprocess")
# 			return 100, None

# 		return r, out

# ################################################################################
# # misc
# ################################################################################

# def readAndSet(el, attr, d, key, defval=None, f=None):
# 	v = el.get(attr, defval)
# 	if v is None:
# 		return
# 	if f is not None:
# 		d[key] = f(v)
# 	else:
# 		d[key] = v

# ################################################################################
# # DICOM misc
# ################################################################################

# # Map DICOM Specific Character Set to python equivalent
# dicom_encoding = {
# 	'': 'iso8859',           # default character set for DICOM
# 	'ISO_IR 6': 'iso8859',   # alias for latin_1 too
# 	'ISO_IR 100': 'latin_1',
# 	'ISO 2022 IR 87': 'iso2022_jp',
# 	'ISO 2022 IR 13': 'iso2022_jp',
# 	'ISO 2022 IR 149': 'euc_kr',
# 	'ISO_IR 192': 'UTF8',
# 	'GB18030': 'GB18030',
# 	'ISO_IR 126': 'iso_ir_126',
# 	'ISO_IR 127': 'iso_ir_127',
# 	'ISO_IR 138': 'iso_ir_138',
# 	'ISO_IR 144': 'iso_ir_144',
# }

# def dicom_init_encoding(dataset):
# 	# Modern pydicom access pattern
# 	try:
# 		# Try modern pydicom first
# 		encoding = dataset.get(('0008', '0005'), 'ISO_IR 6')
# 		if hasattr(encoding, 'value'):
# 			encoding = encoding.value
# 	except:
# 		# Fallback for legacy access
# 		try:
# 			encoding = dataset[0x0008, 0x0005].value
# 		except:
# 			encoding = 'ISO_IR 6'
	
# 	if encoding not in dicom_encoding:
# 		return 'latin_1'
# 	return dicom_encoding[encoding]

# def safedecode(s, encoding):
# 	if isinstance(s, str):
# 		return s
# 	if isinstance(s, bytes):
# 		try:
# 			return s.decode(encoding)
# 		except UnicodeDecodeError:
# 			try:
# 				return s.decode('utf-8')
# 			except UnicodeDecodeError:
# 				try:
# 					return s.decode('latin-1')
# 				except UnicodeDecodeError:
# 					return s.decode('ascii', 'replace')
# 	# Handle other types (int, float, etc.)
# 	return str(s)

# def dicom_parse_date(v):
# 	v = str(v)  # Ensure string type
# 	if len(v) < 1:
# 		return v
# 	if '.' in v:
# 		return v.replace('.', '-')
# 	if '/' in v:
# 		return v.replace('/', '-')
# 	if len(v) >= 8:
# 		return '%s-%s-%s' % (v[0:4], v[4:6], v[6:8])
# 	return v

# def dicom_parse_time(v):
# 	v = str(v)  # Ensure string type
# 	if len(v) < 1:
# 		return v
# 	if ':' in v:
# 		return v
# 	if '.' in v:
# 		return v.replace('.', ':')
# 	if len(v) >= 6:
# 		return '%s:%s:%s' % (v[0:2], v[2:4], v[4:6])
# 	return v

# ################################################################################
# # ConverterImgcnv
# ################################################################################

# class ConverterImgcnv(ConverterBase):
# 	installed = False
# 	version = None
# 	installed_formats = None
# 	CONVERTERCOMMAND = 'imgcnv' if os.name != 'nt' else 'imgcnv.exe'
# 	name = 'imgcnv'
# 	required_version = '2.0.1'

# 	info_map = {
# 		'image_num_x'        : 'image_num_x',
# 		'image_num_y'        : 'image_num_y',
# 		'image_num_z'        : 'image_num_z',
# 		'image_num_t'        : 'image_num_t',
# 		'image_num_c'        : 'image_num_c',
# 		'image_num_series'   : 'image_num_series',
# 		'image_series_index' : 'image_series_index',
# 		'image_num_fovs'     : 'image_num_fovs',
# 		'image_num_labels'   : 'image_num_labels',
# 		'image_num_previews' : 'image_num_previews',
# 		'format'             : 'format',
# 		'file_mode'          : 'file_mode',
# 		'image_mode'         : 'image_mode',
# 		'image_pixel_format' : 'image_pixel_format',
# 		'image_pixel_depth'  : 'image_pixel_depth',
# 		'raw_endian'         : 'raw_endian',
# 		'dimensions'         : 'dimensions',
# 		'pixel_resolution_x' : 'pixel_resolution_x',
# 		'pixel_resolution_y' : 'pixel_resolution_y',
# 		'pixel_resolution_z' : 'pixel_resolution_z',
# 		'pixel_resolution_unit_x' : 'pixel_resolution_unit_x',
# 		'pixel_resolution_unit_y' : 'pixel_resolution_unit_y',
# 		'pixel_resolution_unit_z' : 'pixel_resolution_unit_z',
# 		'image_num_resolution_levels': 'image_num_resolution_levels',
# 		'image_resolution_level_scales': 'image_resolution_level_scales',
# 		'tile_num_x': 'tile_num_x',
# 		'tile_num_y': 'tile_num_y',
# 	}

# 	extended_dimension_names = ['serie', 'fov', 'rotation', 'scene', 'illumination', 'phase', 'view', 'label', 'preview']

# 	#######################################
# 	# Version and Installed
# 	#######################################

# 	@classmethod
# 	def get_version(cls):
# 		'''returns the version of command line utility'''
# 		o = cls.run_command([cls.CONVERTERCOMMAND, '-v'])
# 		try:
# 			d = [int(s) for s in o.split('.')]
# 		except ValueError:
# 			log.error('imgcnv is too old, cannot proceed')
# 			raise Exception('imgcnv is too old, cannot proceed')
# 		if len(d) < 3:
# 			d.append(0)
# 		return {
# 			'full': '.'.join([str(i) for i in d]),
# 			'numeric': d,
# 			'major': d[0],
# 			'minor': d[1],
# 			'build': d[2]
# 		}

# 	#######################################
# 	# Formats
# 	#######################################

# 	@classmethod
# 	def get_formats(cls):
# 		'''inits supported file formats'''
# 		if cls.installed_formats is None:
# 			formats_xml = cls.run_command([cls.CONVERTERCOMMAND, '-fmtxml'])
# 			formats = etree.fromstring('<formats>%s</formats>' % formats_xml)

# 			cls.installed_formats = OrderedDict()
# 			codecs = formats.xpath('//codec')
# 			for c in codecs:
# 				try:
# 					name = c.get('name')
# 					fullname = c.xpath('tag[@name="fullname"]')[0].get('value', '')
# 					exts = c.xpath('tag[@name="extensions"]')[0].get('value', '').split('|')
# 					reading = len(c.xpath('tag[@name="support" and @value="reading"]')) > 0
# 					writing = len(c.xpath('tag[@name="support" and @value="writing"]')) > 0
# 					multipage = len(c.xpath('tag[@name="support" and @value="writing multiple pages"]')) > 0
# 					metadata = len(c.xpath('tag[@name="support" and @value="reading metadata"]')) > 0 or len(c.xpath('tag[@name="support" and @value="writing metadata"]')) > 0
# 					samples_min = misc.safeint(c.xpath('tag[@name="min-samples-per-pixel"]')[0].get('value', '0'))
# 					samples_max = misc.safeint(c.xpath('tag[@name="max-samples-per-pixel"]')[0].get('value', '0'))
# 					bits_min = misc.safeint(c.xpath('tag[@name="min-bits-per-sample"]')[0].get('value', '0'))
# 					bits_max = misc.safeint(c.xpath('tag[@name="max-bits-per-sample"]')[0].get('value', '0'))
# 				except IndexError:
# 					continue
# 				cls.installed_formats[name.lower()] = Format(
# 					name=name,
# 					fullname=fullname,
# 					ext=exts,
# 					reading=reading,
# 					writing=writing,
# 					multipage=multipage,
# 					metadata=metadata,
# 					samples=(samples_min, samples_max),
# 					bits=(bits_min, bits_max)
# 				)

# 	#######################################
# 	# Supported
# 	#######################################

# 	@classmethod
# 	def supported(cls, token, **kw):
# 		'''return True if the input file format is supported'''
# 		ifnm = token.first_input_file()
# 		log.debug('Supported for: %s', ifnm)
# 		supported = cls.run_read(ifnm, [cls.CONVERTERCOMMAND, '-supported', '-i', ifnm])
# 		return supported.startswith('yes')

# 	#######################################
# 	# Conversion
# 	#######################################

# 	@classmethod
# 	def run_command(cls, command):
# 		retcode, out = call_imgcnvlib(command)
# 		if retcode == 100 or retcode == 101:
# 			log.error('Libioimage retcode %s: retry once: %s', retcode, command)
# 			retcode, out = call_imgcnvlib(command)
# 		return out

# 	@classmethod
# 	def run_read(cls, ifnm, command):
# 		with Locks(ifnm, failonread=(not block_reads)) as l:
# 			if l.locked is False:
# 				raise ImageServiceFuture((1, 15))
# 			log.info('run_read dylib command: %s', misc.tounicode(command))
# 			retcode, out = call_imgcnvlib(command)
# 			if retcode == 100 or retcode == 101:
# 				log.error('Libioimage retcode %s: retry once: %s', retcode, command)
# 				retcode, out = call_imgcnvlib(command)
# 		return out

# 	@classmethod
# 	def run(cls, ifnm, ofnm, args, **kw):
# 		'''converts input filename into output using exact arguments as provided in args'''
# 		if not cls.installed:
# 			return None
# 		failonread = kw.get('failonread') or (not block_reads)
# 		tmp = None
# 		with Locks(ifnm, ofnm, failonexist=True) as l:
# 			if l.locked:
# 				command = [cls.CONVERTERCOMMAND]
# 				command.extend(args)
# 				log.debug('Run dylib command: %s', misc.tounicode(command))
# 				proceed = True
# 				if ofnm is not None and os.path.exists(ofnm) and os.path.getsize(ofnm) > 16:
# 					if kw.get('nooverwrite', False) is True:
# 						proceed = False
# 						log.warning('Run: output exists before command [%s], skipping', misc.tounicode(ofnm))
# 					else:
# 						log.warning('Run: output exists before command [%s], overwriting', misc.tounicode(ofnm))
# 				if proceed is True:
# 					retcode, out = call_imgcnvlib(command)
# 					if retcode == 100 or retcode == 101:
# 						log.error('Libioimage retcode %s: retry once: %s', retcode, command)
# 						retcode, out = call_imgcnvlib(command)
# 					if retcode == 99:
# 						log.info('Run: timed-out for [%s]', misc.tounicode(command))
# 						if ofnm is not None and os.path.exists(ofnm):
# 							os.remove(ofnm)
# 						raise ImageServiceException(412, 'Requested timeout reached')
# 					if retcode != 0:
# 						log.info('Run: returned [%s] for [%s]', retcode, misc.tounicode(command))
# 						return None
# 					if ofnm is None:
# 						return str(retcode)
# 			elif l.locked is False:
# 				raise ImageServiceFuture((1, 15))

# 		if ofnm is not None and os.path.exists(ofnm):
# 			with Locks(ofnm, failonread=failonread) as l:
# 				if l.locked is False:
# 					raise ImageServiceFuture((1, 15))

# 		if os.path.exists(ofnm) and os.path.getsize(ofnm) < cls.MINIMUM_FILE_SIZE:
# 			log.error('Run: output file is smaller than %s bytes, probably an error, removing [%s]', cls.MINIMUM_FILE_SIZE, ofnm)
# 			os.remove(ofnm)
# 			return None
# 		return ofnm

# 	#######################################
# 	# Meta - returns a dict with all the metadata fields
# 	#######################################

# 	@classmethod
# 	def meta(cls, token, **kw):
# 		'''returns a dict with file metadata'''
# 		if not cls.installed:
# 			return {}
# 		ifnm = token.first_input_file()
# 		log.debug('Meta for: %s', ifnm)

# 		command = [cls.CONVERTERCOMMAND, '-meta', '-i', ifnm]
# 		if token.series is not None and token.series != 0:
# 			command.extend(['-path', token.series])

# 		meta = cls.run_read(ifnm, command)
# 		if meta is None:
# 			return {}
# 		rd = {}
# 		for line in meta.splitlines():
# 			if not line:
# 				continue
# 			try:
# 				tag, val = [l.lstrip() for l in line.split(':', 1)]
# 			except ValueError:
# 				continue
# 			tag = safedecode(tag, 'utf-8').replace('%3A', ':')
# 			val = safedecode(val, 'utf-8').replace('\n', '').replace('%3E', '>').replace('%3C', '<').replace('%3A', ':').replace('%22', '"').replace('%0A', '\n')
# 			if val != '':
# 				log.debug("Meta Tag: %s ; Value: %s", tag, val)
# 				if tag == 'image_num_z' and 'image_num_z' in rd:
# 					log.debug("Slices already found: %s", rd['image_num_z'])
# 					pass
# 				elif tag == 'image_num_t' and 'image_num_t' in rd:
# 					log.debug("Frames already found: %s", rd['image_num_t'])
# 					pass
# 				else:
# 					rd[tag] = misc.safetypeparse(val)
# 				if tag[-16:] == 'ImageDescription':
# 					if val[:6] == "ImageJ":
# 						log.debug("ImageJ Description found")
# 						ijresult = {}
# 						for line in val.split('\n'):
# 							try:
# 								key, ijval = line.split('=')
# 							except Exception:
# 								continue
# 							key = key.strip()
# 							ijval = ijval.strip()
# 							ijresult[key] = ijval
# 						if 'slices' in ijresult:
# 							rd['image_num_z'] = int(ijresult['slices'])
# 						if 'frames' in ijresult:
# 							rd['image_num_t'] = int(ijresult['frames'])
# 		if 'dimensions' in rd:
# 			rd['dimensions'] = rd['dimensions'].replace(' ', '')

# 		if rd.get('image_num_z', 0) == 1 and rd.get('image_num_t', 0) == 1 and rd.get('image_num_p', 0) > 1:
# 			log.debug('Guessing meta z: %d', rd['image_num_p'])
# 			rd['image_num_z'] = rd['image_num_p']
# 		rd.setdefault('image_num_series', 0)
# 		rd.setdefault('image_series_index', 0)

# 		if token.is_multifile_series() is True:
# 			rd.update(token.meta)
# 			if token.meta.get('image_num_c', 0) > 1:
# 				if 'channel_color_0' in rd:
# 					del rd['channel_color_0']
# 				if 'channel_0_name' in rd:
# 					del rd['channel_0_name']

# 		for i in range(int(rd.get('image_num_c', 0))):
# 			path = 'channels/channel_%.5d' % i
# 			readAndSet(rd, 'channel_%s_name' % i, rd, '%s/name' % path)
# 			readAndSet(rd, 'channel_color_%s' % i, rd, '%s/color' % path)
# 		log.debug('RD: %s', str(rd))
# 		return rd

# 	#######################################
# 	# The info command returns the "core" metadata
# 	#######################################

# 	@classmethod
# 	def info(cls, token, **kw):
# 		'''returns a dict with file info'''
# 		ifnm = token.first_input_file()
# 		log.info('Info for: %s', ifnm)
# 		if not cls.installed:
# 			return {}
# 		if not os.path.exists(ifnm):
# 			return {}

# 		command = [cls.CONVERTERCOMMAND, '-meta-parsed', '-i', ifnm]
# 		if token.series is not None and token.series != 0:
# 			command.extend(['-path', token.series])
# 		if 'speed' in kw:
# 			command.extend(['-speed', kw.get('speed')])

# 		info = cls.run_read(ifnm, command)
# 		if info is None:
# 			return {}
# 		rd = {}
# 		for line in info.splitlines():
# 			if not line:
# 				continue
# 			try:
# 				tag, val = [l.strip() for l in line.split(':', 1)]
# 			except ValueError:
# 				continue
# 			tag = safedecode(tag, 'utf-8').replace('%3A', ':')
# 			val = safedecode(val, 'utf-8').replace('\n', '')
# 			if tag[-16:] == 'ImageDescription':
# 				if val[:6] == "ImageJ":
# 					ijresult = {}
# 					for line in val.split('%0A'):
# 						try:
# 							key, ijval = line.split('=')
# 						except Exception:
# 							continue
# 						key = key.strip()
# 						ijval = ijval.strip()
# 						ijresult[key] = ijval
# 					try:
# 						rd[cls.info_map['image_num_z']] = int(ijresult['slices'])
# 					except:
# 						continue
# 					try:
# 						rd[cls.info_map['image_num_t']] = int(ijresult['frames'])
# 					except:
# 						continue
# 			if tag == 'image_num_z' and 'image_num_z' in rd:
# 				log.debug("Slices already found: %s", rd['image_num_z'])
# 				continue
# 			if tag == 'image_num_t' and 'image_num_t' in rd:
# 				log.debug("Frames already found: %s", rd['image_num_t'])
# 				continue
# 			if tag not in cls.info_map:
# 				continue
# 			else:
# 				rd[cls.info_map[tag]] = misc.safetypeparse(val.replace('\n', ''))

# 		if 'dimensions' in rd:
# 			rd['dimensions'] = rd['dimensions'].replace(' ', '')

# 		rd.setdefault('image_num_series', 0)
# 		rd.setdefault('image_series_index', 0)
# 		rd.setdefault('image_num_z', 1)
# 		rd.setdefault('image_num_t', 1)
# 		rd.setdefault('image_num_p', 1)
# 		if rd['image_num_z'] == 1 and rd['image_num_t'] == 1 and rd['image_num_p'] > 1:
# 			log.debug('Guessing info z: %d', rd['image_num_p'])
# 			rd['image_num_z'] = rd['image_num_p']

# 		if token.is_multifile_series() is True:
# 			rd.update(token.meta)

# 		return rd

# 	#######################################
# 	# multi-file series misc
# 	#######################################

# 	@classmethod
# 	def write_files(cls, files, ofnm):
# 		'''writes a list of files into a file readable by imgcnv'''
# 		with open(ofnm, 'w', encoding='utf-8') as f:
# 			f.write('\n'.join(files))

# 	#######################################
# 	# Conversion
# 	#######################################

# 	@classmethod
# 	def convert(cls, token, ofnm, fmt=None, extra=None, **kw):
# 		'''converts a file and returns output filename'''
# 		ifnm = token.first_input_file()
# 		log.debug('convert: [%s] -> [%s] into %s for series %s with [%s]', ifnm, ofnm, fmt, token.series, extra)

# 		command = []
# 		if token.is_multifile_series() is False:
# 			if '-i' not in extra and '-il' not in extra:
# 				command.extend(['-i', ifnm])
# 		else:
# 			if '-i' not in extra and '-il' not in extra:
# 				files = token.input
# 				fl = '%s.files' % ofnm
# 				cls.write_files(files, fl)
# 				command.extend(['-il', fl])

# 			meta = token.meta or {}

# 			if '-geometry' not in extra:
# 				geom = '%s,%s' % (meta.get('image_num_z', 1), meta.get('image_num_t', 1))
# 				if meta.get('image_num_c', 0) > 1:
# 					geom = '%s,%s' % (geom, meta.get('image_num_c', 0))
# 				command.extend(['-geometry', geom])

# 			meta.update(token.dims)

# 			if '-resolution' not in extra:
# 				res = '%s,%s,%s,%s' % (meta.get('pixel_resolution_x', 0), meta.get('pixel_resolution_y', 0), meta.get('pixel_resolution_z', 0), meta.get('pixel_resolution_t', 0))
# 				command.extend(['-resolution', res])

# 		if token.series is not None and token.series != 0:
# 			command.extend(['-path', token.series])

# 		dims = token.dims or {}
# 		nz = dims.get('image_num_z', 1)
# 		nt = dims.get('image_num_t', 1)

# 		if token.histogram is not None and '-ihst' not in extra:
# 			command.extend(['-ihst', token.histogram])
# 		if ofnm is not None and '-o' not in extra:
# 			command.extend(['-o', ofnm])
# 		if fmt is not None and '-t' not in extra:
# 			command.extend(['-t', fmt])
# 			if cls.installed_formats[fmt].multipage is True:
# 				pass
# 			elif '-page' not in extra and nz * nt > 1:
# 				extra.extend(['-page', '1'])
# 		if extra is not None:
# 			command.extend(extra)
# 		return cls.run(ifnm, ofnm, command)

# 	@classmethod
# 	def thumbnail(cls, token, ofnm, width, height, **kw):
# 		'''converts input filename into output thumbnail'''
# 		ifnm = token.first_input_file()
# 		series = token.series
# 		log.debug('Thumbnail: %s %s %s for [%s]', width, height, series, ifnm)
# 		fmt = kw.get('fmt', 'jpeg')
# 		preproc = kw.get('preproc', '')
# 		preproc = preproc if preproc != '' else 'mid'

# 		command = ['-o', ofnm, '-t', fmt]
# 		if token.series is not None and token.series != 0:
# 			command.extend(['-path', token.series])

# 		info = token.dims or {}
# 		num_z = info.get('image_num_z', 1)
# 		num_t = info.get('image_num_t', 1)
# 		num_l = info.get('image_num_resolution_levels', 1)
# 		page = 0
# 		if preproc == 'mid':
# 			if num_z > 1 or num_t > 1:
# 				mx = (num_z if num_z > 1 else min(num_t, 500)) - 1
# 				page = min(max(0, mx // 2), mx)
# 		elif preproc != '':
# 			return None

# 		if num_l > 1:
# 			try:
# 				num_x = int(info.get('image_num_x', 1))
# 				num_y = int(info.get('image_num_y', 1))
# 				scales = [float(i) for i in info.get('image_resolution_level_scales', '').split(',')]
# 				sizes = [(round(num_x * i), round(num_y * i)) for i in scales]
# 				relatives = [max(width / sz[0], height / sz[1]) for sz in sizes]
# 				relatives = [i if i <= 1 else 0 for i in relatives]
# 				level = relatives.index(max(relatives))
# 				command.extend(['-res-level', str(level)])
# 			except Exception:
# 				pass

# 		queue = token.getQueue()
# 		if token.is_multifile_series() is False:
# 			if '-i' in queue:
# 				command.extend(['-i', ifnm])
# 			if '-page' not in queue:
# 				command.extend(['-page', str(page + 1)])
# 		else:
# 			files = token.input
# 			meta = token.meta or {}
# 			log.debug('thumbnail files: %s', files)

# 			samples = meta.get('image_num_c', 0)
# 			if samples < 2:
# 				token.input = files[page]
# 			else:
# 				page = page * samples
# 				command.extend(['-i', files[page]])
# 				for s in range(1, samples):
# 					command.extend(['-c', files[page + s]])

# 		command.extend(['-enhancemeta'])
# 		if info.get('image_pixel_depth', 16) != 8:
# 			command.extend(['-depth', '8,d,u'])

# 		method = kw.get('method', 'BC')
# 		command.extend(['-resize', '%s,%s,%s,AR' % (width, height, method)])

# 		command.extend(['-fusemeta'])
# 		if info.get('image_num_c', 1) < 4:
# 			command.extend(['-fusemethod', 'm'])
# 		else:
# 			command.extend(['-fusemethod', 'm'])

# 		if fmt == 'jpeg':
# 			command.extend(['-options', 'quality 95 progressive yes'])

# 		return command

# 	@classmethod
# 	def slice(cls, token, ofnm, z, t, roi=None, **kw):
# 		'''extract Z,T plane from input filename into output in OME-TIFF format'''
# 		ifnm = token.first_input_file()
# 		series = token.series

# 		log.debug('Slice: z=%s t=%s roi=%s series=%s for [%s]', z, t, roi, series, ifnm)
# 		z1, z2 = z
# 		t1, t2 = t
# 		x1, x2, y1, y2 = roi
# 		fmt = kw.get('fmt', 'bigtiff')
# 		info = token.dims or {}

# 		command = []
# 		if token.series is not None and token.series != 0:
# 			command.extend(['-path', token.series])

# 		if t2 == 0:
# 			t2 = t1
# 		if z2 == 0:
# 			z2 = z1

# 		pages = []
# 		for ti in range(t1, t2 + 1):
# 			for zi in range(z1, z2 + 1):
# 				if info.get('image_num_t', 1) == 1:
# 					page_num = zi
# 				elif info.get('image_num_z', 1) == 1:
# 					page_num = ti
# 				elif info.get('dimensions', 'XYCZT').replace(' ', '').startswith('XYCT') is False:
# 					page_num = (ti - 1) * info.get('image_num_z', 1) + zi
# 				else:
# 					page_num = (zi - 1) * info.get('image_num_t', 1) + ti
# 				pages.append(page_num)

# 		log.debug('slice pages: %s', pages)

# 		if token.is_multifile_series() is False:
# 			log.debug('Slice for single-file series')
# 			command.extend(['-page', ','.join([str(p) for p in pages])])
# 		else:
# 			log.debug('Slice for multi-file series')
# 			files = token.input
# 			meta = token.meta or {}
# 			channels = meta.get('image_num_c', 0)

# 			if len(pages) == 1 and channels <= 1:
# 				token.input = files[pages[0] - 1]
# 			else:
# 				if channels > 1:
# 					geom = '1,1,%s' % (channels)
# 					command.extend(['-geometry', geom])
# 					cpages = []
# 					for p in [p - 1 for p in pages]:
# 						for c in range(channels):
# 							cpages.append(p * channels + c)
# 					token.input = [files[p] for p in cpages]
# 				else:
# 					token.input = [files[p - 1] for p in pages]

# 		if not x1 == x2 or not y1 == y2:
# 			if not x1 == x2:
# 				if x1 > 0:
# 					x1 = x1 - 1
# 				if x2 > 0:
# 					x2 = x2 - 1
# 			if not y1 == y2:
# 				if y1 > 0:
# 					y1 = y1 - 1
# 				if y2 > 0:
# 					y2 = y2 - 1
# 			command.extend(['-roi', '%s,%s,%s,%s' % (x1, y1, x2, y2)])

# 		nd = []
# 		for k, v in kw.items():
# 			if k in cls.extended_dimension_names:
# 				if len(v) > 1:
# 					raise ImageServiceException(responses.UNPROCESSABLE_ENTITY, 'Ranges in extended dimensions are not yet supported')
# 				nd.append('%s:%s' % (k, v[0]))
# 		if len(nd) > 0:
# 			command.extend(['-slice', ','.join(nd)])

# 		return command

# 	@classmethod
# 	def tile(cls, token, ofnm, level, x, y, sz, **kw):
# 		'''extract tile Level,X,Y tile from input filename into output in OME-TIFF format'''

# 		if kw.get('arbitrary_size', False) == True or level is None or sz is None:
# 			return None

# 		ifnm = token.first_input_file()
# 		series = token.series
# 		page = 0
# 		log.debug('Tile: %s %s %s %s %s for [%s]', level, x, y, sz, series, ifnm)

# 		info = token.dims or {}
# 		tile_w = info.get('tile_num_x', 0)
# 		tile_h = info.get('tile_num_y', 0)
# 		num_l = info.get('image_num_resolution_levels', 1)
# 		if num_l <= 1 or tile_w < 1 or tile_h < 1:
# 			log.debug('Image does not contain tiles, skipping...')
# 			return None

# 		queue = token.getQueue()
# 		command = []
# 		if token.series is not None and token.series != 0:
# 			command.extend(['-path', token.series])

# 		if '-i' not in queue and '-il' not in queue and '-page' not in queue:
# 			if token.is_multifile_series() is False:
# 				command.extend(['-i', ifnm])
# 				command.extend(['-page', str(page + 1)])
# 			else:
# 				files = token.input
# 				meta = token.meta or {}
# 				samples = meta.get('image_num_c', 0)
# 				if samples < 2:
# 					command.extend(['-i', files[page]])
# 				else:
# 					page = page * samples
# 					command.extend(['-i', files[page]])
# 					for s in range(1, samples):
# 						command.extend(['-c', files[page + s]])

# 		level = misc.safeint(level, 0)
# 		x = misc.safeint(x, 0)
# 		y = misc.safeint(y, 0)
# 		sz = misc.safeint(sz, 0)
# 		command.extend(['-tile', '%s,%s,%s,%s' % (sz, x, y, level)])

# 		command.extend(['-speed', token.get_speed_file()])

# 		return command

# 	#######################################
# 	# Special methods
# 	#######################################

# 	@classmethod
# 	def writeHistogram(cls, token, ofnm, **kw):
# 		'''writes Histogram in libbioimage format'''
# 		ifnm = token.first_input_file()
# 		log.debug('Writing histogram for %s into: %s', ifnm, ofnm)
# 		command = ['-ohst', ofnm]
# 		if token.series is not None and token.series != 0:
# 			command.extend(['-path', token.series])
# 		queue = token.getQueue()
# 		page = 0
# 		if '-i' not in queue and '-il' not in queue:
# 			if token.is_multifile_series() is False:
# 				command.extend(['-i', ifnm])
# 			else:
# 				files = token.input
# 				meta = token.meta or {}
# 				samples = meta.get('image_num_c', 0)
# 				if samples < 2:
# 					command.extend(['-i', files[page]])
# 				else:
# 					page = page * samples
# 					command.extend(['-i', files[page]])
# 					for s in range(1, samples):
# 						command.extend(['-c', files[page + s]])
# 		command.extend(queue)

# 		info = token.dims or {}
# 		num_l = info.get('image_num_resolution_levels', 1)
# 		if num_l > 1:
# 			try:
# 				width = 500
# 				height = 500
# 				num_x = int(info.get('image_num_x', 1))
# 				num_y = int(info.get('image_num_y', 1))
# 				scales = [float(i) for i in info.get('image_resolution_level_scales', '').split(',')]
# 				sizes = [(round(num_x * i), round(num_y * i)) for i in scales]
# 				relatives = [max(width / sz[0], height / sz[1]) for sz in sizes]
# 				relatives = [i if i <= 1 else 0 for i in relatives]
# 				level = relatives.index(max(relatives))
# 				command.extend(['-res-level', str(level)])
# 			except Exception:
# 				pass

# 		return cls.run(ifnm, ofnm, command, failonread=(not block_tile_reads))

# 	#######################################
# 	# Sort and organize files
# 	#######################################

# 	@classmethod
# 	def group_files_dicom(cls, files, **kw):
# 		'''return list with lists containing grouped and ordered dicom file paths'''

# 		if pydicom is None:
# 			log.warning('pydicom not available, cannot group DICOM files')
# 			return False

# 		def read_tag(ds, key, default=None):
# 			"""Read DICOM tag with modern pydicom compatibility"""
# 			try:
# 				# Modern pydicom approach
# 				if hasattr(ds, 'get'):
# 					element = ds.get(key)
# 				else:
# 					element = ds[key] if key in ds else None
				
# 				if element is None:
# 					return default if default is not None else ''
				
# 				# Handle value extraction
# 				if hasattr(element, 'value'):
# 					return element.value
# 				else:
# 					return element
# 			except (KeyError, AttributeError):
# 				return default if default is not None else ''

# 		def read_tag_float(ds, key, default=None):
# 			try:
# 				val = read_tag(ds, key)
# 				if val is None or val == '':
# 					return default
# 				return float(val)
# 			except (ValueError, TypeError):
# 				return default

# 		def read_tag_int(ds, key, default=None):
# 			try:
# 				val = read_tag(ds, key)
# 				if val is None or val == '':
# 					return default
# 				return int(val)
# 			except (ValueError, TypeError):
# 				return default

# 		if not cls.installed:
# 			return False
# 		log.debug('Group %s files', len(files))
# 		data = []
# 		groups = []
# 		blobs = []
		
# 		for f in files:
# 			try:
# 				# Modern pydicom file reading
# 				ds = pydicom.dcmread(f, force=True)
# 			except Exception:
# 				blobs.append(f)
# 				continue

# 			# Check for pixel data using modern approach
# 			if not hasattr(ds, 'PixelData') and 'PixelData' not in ds:
# 				blobs.append(f)
# 				continue

# 			modality = read_tag(ds, ('0008', '0060'))
# 			patient_id = read_tag(ds, ('0010', '0020'))
# 			study_uid = read_tag(ds, ('0020', '000d'))
# 			series_uid = read_tag(ds, ('0020', '000e'))
# 			series_num = read_tag(ds, ('0020', '0012'))
# 			acqui_num = read_tag(ds, ('0020', '0011'))
# 			instance_num = read_tag_int(ds, ('0020', '0013'), 0)
# 			slice_loc = read_tag_float(ds, ('0020', '1041'), 0.0)

# 			num_temp_p = read_tag_int(ds, ('0020', '0105'), 0)
# 			num_frames = read_tag_int(ds, ('0028', '0008'), 0)

# 			mr_acq_typ = read_tag(ds, ('0018', '0023'))
# 			force_time = False
			
# 			# Logic for determining time series vs volume
# 			if mr_acq_typ == '3D' and ('0020', '1041') not in ds:
# 				force_time = True
# 			if mr_acq_typ == '2D' and ('0020', '1041') in ds:
# 				force_time = False

# 			key = '%s/%s/%s/%s/%s' % (modality, patient_id, study_uid, series_uid, acqui_num)
# 			d = (key, slice_loc or instance_num, f, num_temp_p or num_frames or force_time)
# 			data.append(d)
# 			log.debug('Key: %s, series_num: %s, instance_num: %s, num_temp_p: %s, num_frames: %s, slice_loc: %s', 
# 					 key, series_num, instance_num, num_temp_p, num_frames, slice_loc)
# 			log.debug('Data: %s', d)

# 		# Group and sort
# 		data = sorted(data, key=lambda x: x[0])
# 		for k, g in groupby(data, lambda x: x[0]):
# 			groups.append(sorted(list(g), key=lambda x: x[1]))

# 		# Prepare output
# 		images = []
# 		geometry = []
# 		for g in groups:
# 			l = [f[2] for f in g]
# 			images.append(l)
# 			frame_num = g[0][3]
# 			if frame_num is True:
# 				frame_num = len(l)
# 			if len(l) == 1:
# 				geometry.append({'t': 1, 'z': 1})
# 			elif frame_num > 0:
# 				z = len(l) // frame_num
# 				geometry.append({'t': frame_num, 'z': z})
# 			else:
# 				geometry.append({'t': 1, 'z': len(l)})

# 		log.debug('group_files_dicom found: %s image groups, %s blobs', len(images), len(blobs))
# 		return (images, blobs, geometry)

# 	#######################################
# 	# DICOM metadata parser
# 	#######################################

# 	@classmethod
# 	def meta_dicom(cls, ifnm, series=0, xml=None, **kw):
# 		'''appends nodes to XML'''
# 		if os.path.basename(ifnm) == 'DICOMDIR':
# 			return

# 		if pydicom is None:
# 			log.warning('pydicom not available, skipping DICOM metadata...')
# 			return

# 		def recurse_tree(dataset, parent, encoding='latin-1'):
# 			for de in dataset:
# 				if de.tag == ('7fe0', '0010'):
# 					continue
# 				node = etree.SubElement(parent, 'tag', name=de.name, type=':///DICOM#%04.x,%04.x' % (de.tag.group, de.tag.element))

# 				if de.VR == "SQ":
# 					for i, dataset in enumerate(de.value):
# 						recurse_tree(dataset, node, encoding)
# 				else:
# 					# Handle MultiValue properly for modern pydicom
# 					if hasattr(pydicom, 'multival') and isinstance(de.value, pydicom.multival.MultiValue):
# 						value = ','.join(safedecode(i, encoding) for i in de.value)
# 					elif hasattr(de.value, '__iter__') and not isinstance(de.value, (str, bytes)):
# 						# Handle other iterable types
# 						value = ','.join(safedecode(i, encoding) for i in de.value)
# 					else:
# 						value = safedecode(de.value, encoding)
# 					try:
# 						node.set('value', value.strip())
# 					except (ValueError, Exception):
# 						pass

# 		try:
# 			_, tmp = misc.start_nounicode_win(ifnm, [])
# 			ds = pydicom.dcmread(tmp or ifnm, force=True)
# 		except Exception:
# 			misc.end_nounicode_win(tmp)
# 			return
		
# 		encoding = dicom_init_encoding(ds)
# 		recurse_tree(ds, xml, encoding=encoding)
# 		misc.end_nounicode_win(tmp)

# 	#######################################
# 	# Most important DICOM metadata
# 	#######################################

# 	@classmethod
# 	def meta_dicom_parsed(cls, ifnm, xml=None, **kw):
# 		'''appends nodes to XML'''

# 		if pydicom is None:
# 			log.warning('pydicom not available, skipping DICOM metadata...')
# 			return

# 		def append_tag(dataset, tag, parent, name=None, fmt=None, safe=True, encoding='latin-1'):
# 			"""Modern pydicom compatible tag appending"""
# 			try:
# 				# Modern access pattern
# 				if hasattr(dataset, 'get'):
# 					de = dataset.get(tag, None)
# 				else:
# 					de = dataset[tag] if tag in dataset else None
# 			except (KeyError, AttributeError):
# 				return

# 			if de is None:
# 				return
			
# 			name = name or de.name
# 			typ = ':///DICOM#%04.x,%04.x' % (de.tag.group, de.tag.element)

# 			# Extract value
# 			if hasattr(de, 'value'):
# 				raw_value = de.value
# 			else:
# 				raw_value = de

# 			if fmt is None:
# 				# Handle MultiValue for modern pydicom
# 				if hasattr(pydicom, 'multival') and isinstance(raw_value, pydicom.multival.MultiValue):
# 					value = ','.join(safedecode(i, encoding) for i in raw_value)
# 				elif hasattr(raw_value, '__iter__') and not isinstance(raw_value, (str, bytes)):
# 					value = ','.join(safedecode(i, encoding) for i in raw_value)
# 				else:
# 					value = safedecode(raw_value, encoding)
# 			else:
# 				if safe is True:
# 					try:
# 						value = fmt(safedecode(raw_value, encoding))
# 					except Exception:
# 						value = safedecode(raw_value, encoding)
# 				else:
# 					value = fmt(safedecode(raw_value, encoding))
			
# 			value = value.strip()
# 			if len(value) > 0:
# 				etree.SubElement(parent, 'tag', name=name, value=value, type=typ)

# 		try:
# 			_, tmp = misc.start_nounicode_win(ifnm, [])
# 			ds = pydicom.dcmread(tmp or ifnm, force=True)
# 		except Exception:
# 			misc.end_nounicode_win(tmp)
# 			return

# 		encoding = dicom_init_encoding(ds)

# 		# Extract key DICOM tags
# 		append_tag(ds, ('0010', '0020'), xml, encoding=encoding)  # Patient ID
# 		try:
# 			append_tag(ds, ('0010', '0010'), xml, name='Patient\'s First Name', safe=False, fmt=lambda x: x.split('^', 1)[1], encoding=encoding)
# 			append_tag(ds, ('0010', '0010'), xml, name='Patient\'s Last Name', safe=False, fmt=lambda x: x.split('^', 1)[0], encoding=encoding)
# 		except Exception:
# 			append_tag(ds, ('0010', '0010'), xml, encoding=encoding)
		
# 		append_tag(ds, ('0010', '0040'), xml, encoding=encoding)  # Patient's Sex
# 		append_tag(ds, ('0010', '1010'), xml, encoding=encoding)  # Patient's Age
# 		append_tag(ds, ('0010', '0030'), xml, fmt=dicom_parse_date)  # Patient's Birth Date
# 		append_tag(ds, ('0012', '0062'), xml, encoding=encoding)  # Patient Identity Removed
# 		append_tag(ds, ('0008', '0020'), xml, fmt=dicom_parse_date)  # Study Date
# 		append_tag(ds, ('0008', '0030'), xml, fmt=dicom_parse_time)  # Study Time
# 		append_tag(ds, ('0008', '0060'), xml, encoding=encoding)  # Modality
# 		append_tag(ds, ('0008', '1030'), xml, encoding=encoding)  # Study Description
# 		append_tag(ds, ('0008', '103e'), xml, encoding=encoding)  # Series Description
# 		append_tag(ds, ('0008', '0080'), xml, encoding=encoding)  # Institution Name
# 		append_tag(ds, ('0008', '0090'), xml, encoding=encoding)  # Referring Physician's Name
# 		append_tag(ds, ('0008', '0008'), xml)  # Image Type
# 		append_tag(ds, ('0008', '0012'), xml, fmt=dicom_parse_date)  # Instance Creation Date
# 		append_tag(ds, ('0008', '0013'), xml, fmt=dicom_parse_time)  # Instance Creation Time
# 		append_tag(ds, ('0008', '1060'), xml, encoding=encoding)  # Name of Physician(s) Reading Study
# 		append_tag(ds, ('0008', '2111'), xml, encoding=encoding)  # Derivation Description

# 		misc.end_nounicode_win(tmp)

# try:
# 	ConverterImgcnv.init()
# except Exception as e:
# 	log.warning(f"Imgcnv not available, issue: {e}")
