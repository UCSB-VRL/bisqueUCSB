#!/usr/bin/env python3

##########################################################################################################
# Author: Wahid Sadique Koly
# Test Converter Initialization
# Run the following commands from root directory after building and running the container
# docker cp ./dev/test-converter-init.py bisque:/test-converter-init.py
# docker exec -it bisque bash -c "source /usr/lib/bisque/bin/activate && python3 /test-converter-init.py"
##########################################################################################################

import sys
sys.path.insert(0, '/source')

print("Testing converter initialization...")

# Test OpenSlide
try:
    from bq.image_service.controllers.converters.converter_openslide import ConverterOpenSlide
    version = ConverterOpenSlide.get_version()
    installed = ConverterOpenSlide.get_installed()
    print(f"OpenSlide version: {version}")
    print(f"OpenSlide installed: {installed}")
    print(f"OpenSlide required version: {ConverterOpenSlide.required_version}")
except Exception as e:
    print(f"OpenSlide error: {e}")

# Test Bioformats
try:
    from bq.image_service.controllers.converters.converter_bioformats import ConverterBioformats
    version = ConverterBioformats.get_version()
    installed = ConverterBioformats.get_installed()
    print(f"Bioformats version: {version}")
    print(f"Bioformats installed: {installed}")
    print(f"Bioformats required version: {ConverterBioformats.required_version}")
except Exception as e:
    print(f"Bioformats error: {e}")

# Test ImarisConvert
try:
    from bq.image_service.controllers.converters.converter_imaris import ConverterImaris
    version = ConverterImaris.get_version()
    installed = ConverterImaris.get_installed()
    print(f"ImarisConvert version: {version}")
    print(f"ImarisConvert installed: {installed}")
    print(f"ImarisConvert required version: {ConverterImaris.required_version}")
except Exception as e:
    print(f"ImarisConvert error: {e}")
