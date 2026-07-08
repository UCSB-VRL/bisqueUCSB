# Third-Party Notices

This file summarizes major third-party components used by BisQue. It is not a
complete dependency bill of materials and is not legal advice. When distributing
BisQue, review the licenses of all bundled dependencies, Python packages,
JavaScript assets, converter tools, operating system packages, and container
layers.

## BisQue

BisQue source code is covered by the project license in `LICENSE`, unless a file
or directory states a different license.

## Bundled Frontend Components

### Ext JS

- Component: Ext JS 4.2
- Path: `source/bqcore/bq/core/public/extjs`
- License: GNU General Public License version 3.0, according to
  `source/bqcore/bq/core/public/extjs/license.txt`
- Notes: This directory is bundled in this repository branch. Applications using
  the GPL version of Ext JS should comply with GPLv3 terms or use an appropriate
  commercial Sencha license.

### Sencha Touch Gesture Code

- Component: Sencha Touch / ExtTouch gesture support
- Path: `source/bqcore/bq/core/public/js/senchatouch`
- License: verify against the original Sencha Touch distribution used to create
  this copy. Sencha Touch has historically been offered under GPLv3 or a
  commercial license.
- Notes: BisQue includes `/core/js/senchatouch/sencha-touch-gestures.js` in the
  frontend runtime.

## Image Conversion And Reading Tools

### imgcnv / BioImage Convert

- Component: BioImage Convert command-line tool and library
- Paths:
  - `bin/imgcnv`
  - `.local/bin/imgcnv` when installed locally
  - `.local/lib/libimgcnv.*` when installed locally
- Source: VIQI/BioImage Convert packages or a user-provided `imgcnv` on `PATH`
- License: verify against the exact package or source release being used.
- Notes: BisQue uses `imgcnv` as the primary image converter for most image
  service operations.

### OpenSlide

- Component: OpenSlide and openslide-python
- License: GNU Lesser General Public License version 2.1
- Source: https://openslide.org/
- Notes: BisQue uses OpenSlide for whole-slide image metadata, thumbnails, tiles,
  and histogram support. The current OpenSlide integration does not convert full
  slides to OME-TIFF.

### Bio-Formats

- Component: Bio-Formats command-line tools, including `showinf`, `bfconvert`,
  and `formatlist`
- Paths when installed locally:
  - `.local/bin/showinf`
  - `.local/bin/bfconvert`
  - `.local/bin/formatlist`
  - `.local/share/bioformats`
- Source: https://www.openmicroscopy.org/bio-formats/
- License: Bio-Formats is distributed under the GNU General Public License;
  current upstream metadata identifies the project as GPL-2.0. Commercial
  licenses are available from Glencoe Software.
- Notes: Bio-Formats should be treated as an optional converter unless a
  distribution has reviewed and accepted the licensing implications. Public
  container images should not bundle Bio-Formats by default without legal review.

## Other Bundled Browser Libraries

The repository also contains other browser libraries and assets under their own
licenses, including but not limited to Three.js, Raphael, Proj4js, Async.js,
KineticJS, Dagre/D3-related code, and SVG/image assets. Preserve upstream
copyright and license notices when redistributing.

## Distribution Guidance

- Do not assume the BisQue project license applies to third-party code.
- Preserve license files and copyright notices for bundled components.
- Prefer optional installation for GPL components that are not required for the
  default developer or production image.
- For Docker or Kubernetes distributions, document whether Bio-Formats and other
  optional converters are included in the image, installed at runtime, or
  provided as separate services.
