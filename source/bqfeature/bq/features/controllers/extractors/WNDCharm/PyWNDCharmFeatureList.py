feature_list = {}
from pyWNDCharmLib import extractChebyshevCoefficients,extractChebyshevFourierCoefficients,extractCombFirstFourMoments,extractGaborTextures,extractHaralickTextures,extractMultiscaleHistograms,extractRadonCoefficients,extractTamuraTextures,extractZernikeCoefficients,extractPixelIntensityStatistics,extractColorHistogram,extractFractalFeatures,extractEdgeFeatures,extractObjectFeatures,extractInverseObjectFeatures,extractGiniCoefficient,extractColorHistogram

#naming convention begins with the extractor and ends with the transforms in the order stated
#
#["Extractor","transform1","transform2","length","require colored image(True/False)","required colored image into the transform"]

# Chebishev Statistics Extractors
feature_list["Chebishev_Statistics"] = [extractChebyshevCoefficients,"Empty Transform","Empty Transform",32,False,False,'bad'] #inconsistant results between machines
feature_list["Chebishev_Statistics_Chebyshev"] = [extractChebyshevCoefficients,"chebyshev","Empty Transform",32,False,False,'bad']
feature_list["Chebishev_Statistics_Hue_Chebyshev"] = [extractChebyshevCoefficients,"Hue Transform","chebyshev",32,True,False,'bad']
feature_list["Chebishev_Statistics_Color"] = [extractChebyshevCoefficients,"wndchrmcolor","Empty Transform",32,True,False,'bad']
feature_list["Chebishev_Statistics_Edge"] = [extractChebyshevCoefficients,"edge","Empty Transform",32,False,False,'bad']
feature_list["Chebishev_Statistics_Fourier"] = [extractChebyshevCoefficients,"fourier","Empty Transform",32,False,False,'bad']
feature_list["Chebishev_Statistics_Edge_Fourier"] = [extractChebyshevCoefficients,"edge","fourier",32,False,False,'bad']
feature_list["Chebishev_Statistics_Hue_Fourier"] = [extractChebyshevCoefficients,"Hue Transform","fourier",32,True,False,'bad']
feature_list["Chebishev_Statistics_Fourier_Wavelet"] = [extractChebyshevCoefficients,"fourier","wavelet",32,False,False,'bad']
feature_list["Chebishev_Statistics_Hue"] = [extractChebyshevCoefficients,"Hue Transform","Empty Transform",32,True,False,'bad']
feature_list["Chebishev_Statistics_Wavelet"] = [extractChebyshevCoefficients,"wavelet","Empty Transform",32,False,False,'bad'] 
feature_list["Chebishev_Statistics_Edge_Wavelet"] = [extractChebyshevCoefficients,"edge","wavelet",32,False,False,'bad']

# Chebyshev Fourier Transform Extractors
feature_list["Chebyshev_Fourier_Transform"] = [extractChebyshevFourierCoefficients,"Empty Transform","Empty Transform",32,False,False,'good']
feature_list["Chebishev_Fourier_Transform_Chebyshev"] = [extractChebyshevFourierCoefficients,"chebyshev","Empty Transform",32,False,False,'good'] 
feature_list["Chebishev_Fourier_Transform_Hue_Chebyshev"] = [extractChebyshevFourierCoefficients,"Hue Transform","chebyshev",32,True,False,'good']
feature_list["Chebishev_Fourier_Transform_Color"] = [extractChebyshevFourierCoefficients,"wndchrmcolor","Empty Transform",32,True,False,'good']
feature_list["Chebishev_Fourier_Transform_Edge"] = [extractChebyshevFourierCoefficients,"edge","Empty Transform",32,False,False,'good']
feature_list["Chebishev_Fourier_Transform_Fourier"] = [extractChebyshevFourierCoefficients,"fourier","Empty Transform",32,False,False,'good']
feature_list["Chebishev_Fourier_Transform_Edge_Fourier"] = [extractChebyshevFourierCoefficients,"edge","fourier",32,False,False,'good']
feature_list["Chebishev_Fourier_Transform_Hue_Fourier"] = [extractChebyshevFourierCoefficients,"Hue Transform","fourier",32,True,False,'good']
feature_list["Chebishev_Fourier_Transform_Fourier_Wavelet"] = [extractChebyshevFourierCoefficients,"fourier","wavelet",32,False,False,'good']
feature_list["Chebishev_Fourier_Transform_Hue"] = [extractChebyshevFourierCoefficients,"Hue Transform","Empty Transform",32,True,False,'good']
feature_list["Chebishev_Fourier_Transform_Wavelet"] = [extractChebyshevFourierCoefficients,"wavelet","Empty Transform",32,False,False,'good']
feature_list["Chebishev_Fourier_Transform_Edge_Wavelet"] = [extractChebyshevFourierCoefficients,"edge","wavelet",32,False,False,'good']

#color histogram
feature_list["Color_Histogram"] = [extractColorHistogram,"Empty Transform","Empty Transform",20,True,True,'good']

#Comb Moments Extractors
#4 orientations mean std skew kurt 3 bins each
feature_list["Comb_Moments"] = [extractCombFirstFourMoments,"Empty Transform","Empty Transform",48,False,False,'bad'] #inconsistant between machines
feature_list["Comb_Moments_Chebyshev"] = [extractCombFirstFourMoments,"chebyshev","Empty Transform",48,False,False,'bad']
feature_list["Comb_Moments_Fourier_Chebyshev"] = [extractCombFirstFourMoments,"fourier","chebyshev",48,False,False,'bad']
feature_list["Comb_Moments_Hue_Fourier"] = [extractCombFirstFourMoments,"Hue Transform","fourier",48,True,False,'bad']
feature_list["Comb_Moments_Wavelet_Chebyshev"] = [extractCombFirstFourMoments,"wavelet","chebyshev",48,False,False,'bad']
feature_list["Comb_Moments_Color"] = [extractCombFirstFourMoments,"wndchrmcolor","Empty Transform",48,True,False,'bad']
feature_list["Comb_Moments_Edge"] = [extractCombFirstFourMoments,"edge","Empty Transform",48,False,False,'bad']
feature_list["Comb_Moments_Fourier"] = [extractCombFirstFourMoments,"fourier","Empty Transform",48,False,False,'bad']
feature_list["Comb_Moments_Chebyshev_Fourier"] = [extractCombFirstFourMoments,"chebyshev","fourier",48,False,False,'bad']
feature_list["Comb_Moments_Edge_Fourier"] = [extractCombFirstFourMoments,"edge","fourier",48,False,False,'bad']
feature_list["Comb_Moments_Hue_Fourier"] = [extractCombFirstFourMoments,"Hue Transform","fourier",48,True,False,'bad']
feature_list["Comb_Moments_Wavelet_Fourier"] = [extractCombFirstFourMoments,"wavelet","fourier",48,False,False,'bad']
feature_list["Comb_Moments_Hue"] = [extractCombFirstFourMoments,"Hue Transform","Empty Transform",48,True,False,'bad']
feature_list["Comb_Moments_Wavelet"] = [extractCombFirstFourMoments,"wavelet","Empty Transform",48,False,False,'bad']
feature_list["Comb_Moments_Edge_Wavelet"] = [extractCombFirstFourMoments,"edge","wavelet",48,False,False,'bad']
feature_list["Comb_Moments_Fourier_Wavelet"] = [extractCombFirstFourMoments,"fourier","wavelet",48,False,False,'bad']

#Edge Features Extractors
feature_list["Edge_Features"] = [extractEdgeFeatures,"Empty Transform","Empty Transform",28,False,False,'good']

#Fractal Extractors
feature_list["Fractal_Features"] = [extractFractalFeatures,"Empty Transform","Empty Transform",20,False,False,'good'] 
feature_list["Fractal_Features_Chebyshev"] = [extractFractalFeatures,"chebyshev","Empty Transform",20,False,False,'good'] 
feature_list["Fractal_Features_Fourier_Chebyshev"] = [extractFractalFeatures,"fourier","chebyshev",20,False,False,'good'] 
feature_list["Fractal_Features_Hue_Chebyshev"] = [extractFractalFeatures,"Hue Transform","chebyshev",20,True,False,'good']
feature_list["Fractal_Features_Wavelet_Chebyshev"] = [extractFractalFeatures,"wavelet","chebyshev",20,False,False,'good'] 
feature_list["Fractal_Features_Color"] = [extractFractalFeatures,"wndchrmcolor","Empty Transform",20,True,False,'good'] 
feature_list["Fractal_Features_Edge"] = [extractFractalFeatures,"edge","Empty Transform",20,False,False,'good'] 
feature_list["Fractal_Features_Fourier"] = [extractFractalFeatures,"fourier","Empty Transform",20,False,False,'good'] 
feature_list["Fractal_Features_Chebyshev_Fourier"] = [extractFractalFeatures,"chebyshev","fourier",20,False,False,'good'] 
feature_list["Fractal_Features_Edge_Fourier"] = [extractFractalFeatures,"edge","fourier",20,False,False,'good'] 
feature_list["Fractal_Features_Hue_Fourier"] = [extractFractalFeatures,"Hue Transform","fourier",20,True,False,'good'] 
feature_list["Fractal_Features_Wavelet_Fourier"] = [extractFractalFeatures,"wavelet","fourier",20,False,False,'good'] 
feature_list["Fractal_Features_Hue"] = [extractFractalFeatures,"Hue Transform","Empty Transform",20,True,False,'good'] 
feature_list["Fractal_Features_Wavelet"] = [extractFractalFeatures,"wavelet","Empty Transform",20,False,False,'good'] 
feature_list["Fractal_Features_Edge_Wavelet"] = [extractFractalFeatures,"edge","wavelet",20,False,False,'good'] 
feature_list["Fractal_Features_Fourier_Wavelet"] = [extractFractalFeatures,"fourier","wavelet",20,False,False,'good'] 

#Gini Coeffivient
feature_list["Gini_Coefficient"] = [extractGiniCoefficient,"Empty Transform","Empty Transform",1,False,False,'good'] 
feature_list["Gini_Coefficient_Fourier"] = [extractGiniCoefficient,"fourier","Empty Transform",1,False,False,'good'] 
feature_list["Gini_Coefficient_Wavelet"] = [extractGiniCoefficient,"wavelet","Empty Transform",1,False,False,'good'] 
feature_list["Gini_Coefficient_Chebyshev"] = [extractGiniCoefficient,"chebyshev","Empty Transform",1,False,False,'good'] 
feature_list["Gini_Coefficient_Fourier_Chebyshev"] = [extractGiniCoefficient,"fourier","chebyshev",1,False,False,'good'] 
feature_list["Gini_Coefficient_Fourier_Wavelet"] = [extractGiniCoefficient,"fourier","wavelet",1,False,False,'good'] 
feature_list["Gini_Coefficient_Wavelet_Fourier"] = [extractGiniCoefficient,"wavelet","fourier",1,False,False,'good']
feature_list["Gini_Coefficient_Chebyshev_Fourier"] = [extractGiniCoefficient,"chebyshev","fourier",1,False,False,'good']
feature_list["Gini_Coefficient_Wavelet_Chebyshev"] = [extractGiniCoefficient,"wavelet","chebyshev",1,False,False,'good']
feature_list["Gini_Coefficient_Edge"] = [extractGiniCoefficient,"edge","Empty Transform",1,False,False,'good']
feature_list["Gini_Coefficient_Fourier_Edge"] = [extractGiniCoefficient,"edge","fourier",1,False,False,'good']
feature_list["Gini_Coefficient_Wavelet_Edge"] = [extractGiniCoefficient,"edge","wavelet",1,False,False,'good']

#Gabor Textures
feature_list["Gabor_Textures"] = [extractGaborTextures,"Empty Transform","Empty Transform",7,False,False,'good'] 

#Haralick Textures
#disable
#feature_list["Haralick_Textures"] = [extractHaralickTextures,"Empty Transform","Empty Transform",28,False,False,'good'] #double free or seg fault for multithread
#feature_list["Haralick_Textures_Chebyshev"] = [extractHaralickTextures,"chebyshev","Empty Transform",28,False,False,'good'] 
#feature_list["Haralick_Textures_Fourier_Chebyshev"] = [extractHaralickTextures,"fourier","chebyshev",28,False,False,'good'] 
#feature_list["Haralick_Textures_Hue_Chebyshev"] = [extractHaralickTextures,"Hue Transform","chebyshev",28,True,False,'good'] 
#feature_list["Haralick_Textures_Wavelet_Chebyshev"] = [extractHaralickTextures,"wavelet","chebyshev",28,False,False,'good'] 
#feature_list["Haralick_Textures_Color"] = [extractHaralickTextures,"wndchrmcolor","Empty Transform",28,True,False,'good'] 
#feature_list["Haralick_Textures_Edge"] = [extractHaralickTextures,"edge","Empty Transform",28,False,False,'good'] 
#feature_list["Haralick_Textures_Fourier"] = [extractHaralickTextures,"fourier","Empty Transform",28,False,False,'good'] 
#feature_list["Haralick_Textures_Chebyshev_Fourier"] = [extractHaralickTextures,"chebyshev","fourier",28,False,False,'good'] 
#feature_list["Haralick_Textures_Edge_Fourier"] = [extractHaralickTextures,"edge","fourier",28,False,False,'good'] 
#feature_list["Haralick_Textures_Hue_Fourier"] = [extractHaralickTextures,"Hue Transform","fourier",28,True,False,'good'] 
#feature_list["Haralick_Textures_Wavelet_Fourier"] = [extractHaralickTextures,"wavelet","fourier",28,False,False,'good'] 
#feature_list["Haralick_Textures_Hue"] = [extractHaralickTextures,"Hue Transform","Empty Transform",28,True,False,'good'] 
#feature_list["Haralick_Textures_Wavelet"] = [extractHaralickTextures,"wavelet","Empty Transform",28,False,False,'good'] 
#feature_list["Haralick_Textures_Edge_Wavelet"] = [extractHaralickTextures,"edge","wavelet",28,False,False,'good'] 
#feature_list["Haralick_Textures_Fourier_Wavelet"] = [extractHaralickTextures,"fourier","wavelet",28,False,False,'good'] 

#Multiscale Historgram
feature_list["Multiscale_Historgram"] = [extractMultiscaleHistograms,"Empty Transform","Empty Transform",24,False,False,'good']
feature_list["Multiscale_Historgram_Chebyshev"] = [extractMultiscaleHistograms,"chebyshev","Empty Transform",24,False,False,'good']
feature_list["Multiscale_Historgram_Fourier_Chebyshev"] = [extractMultiscaleHistograms,"fourier","chebyshev",24,False,False,'good']
feature_list["Multiscale_Historgram_Hue_Chebyshev"] = [extractMultiscaleHistograms,"Hue Transform","chebyshev",24,True,False,'good']
feature_list["Multiscale_Historgram_Wavelet_Chebyshev"] = [extractMultiscaleHistograms,"wavelet","chebyshev",24,False,False,'good']
feature_list["Multiscale_Historgram_Color"] = [extractMultiscaleHistograms,"wndchrmcolor","Empty Transform",24,True,False,'good']
feature_list["Multiscale_Historgram_Edge"] = [extractMultiscaleHistograms,"edge","Empty Transform",24,False,False,'good']
feature_list["Multiscale_Historgram_Fourier"] = [extractMultiscaleHistograms,"fourier","Empty Transform",24,False,False,'good']
feature_list["Multiscale_Historgram_Chebyshev_Fourier"] = [extractMultiscaleHistograms,"chebyshev","fourier",24,False,False,'good']
feature_list["Multiscale_Historgram_Edge_Fourier"] = [extractMultiscaleHistograms,"edge","fourier",24,False,False,'good']
feature_list["Multiscale_Historgram_Hue_Fourier"] = [extractMultiscaleHistograms,"Hue Transform","fourier",24,True,False,'good']
feature_list["Multiscale_Historgram_Wavelet_Fourier"] = [extractMultiscaleHistograms,"wavelet","fourier",24,False,False,'good']
feature_list["Multiscale_Historgram_Hue"] = [extractMultiscaleHistograms,"Hue Transform","Empty Transform",24,True,False,'good']
feature_list["Multiscale_Historgram_Wavelet"] = [extractMultiscaleHistograms,"wavelet","Empty Transform",24,False,False,'good']
feature_list["Multiscale_Historgram_Edge_Wavelet"]  = [extractMultiscaleHistograms,"edge","wavelet",24,False,False,'good']
feature_list["Multiscale_Historgram_Fourier_Wavelet"] = [extractMultiscaleHistograms,"fourier","wavelet",24,False,False,'good']

# Giving removing from the feature set until fixed
# WindowsError: exception: access violation reading 0x0000000415AE314C
#Object Feature
feature_list["Object_Feature"] = [extractObjectFeatures,"Empty Transform","Empty Transform",34,False,False,'fair'] #failed one multi-threaded test

#Inverse Object Feature
feature_list["Inverse_Object_Features"] = [extractInverseObjectFeatures,"Empty Transform","Empty Transform",34,False,False,'fair'] #failed one multi-threaded test

#Pixel Intensity Statistics
#mean median std min max
feature_list["Pixel_Intensity_Statistics"] = [extractPixelIntensityStatistics,"Empty Transform","Empty Transform",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Chebyshev"] = [extractPixelIntensityStatistics,"chebyshev","Empty Transform",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Fourier_Chebyshev"] = [extractPixelIntensityStatistics,"fourier","chebyshev",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Hue_Chebyshev"] = [extractPixelIntensityStatistics,"Hue Transform","chebyshev",5,True,False,'good']
feature_list["Pixel_Intensity_Statistics_Wavelet_Chebyshev"] = [extractPixelIntensityStatistics,"wavelet","chebyshev",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Color"] = [extractPixelIntensityStatistics,"wndchrmcolor","Empty Transform",5,True,False,'good']
feature_list["Pixel_Intensity_Statistics_Edge"] = [extractPixelIntensityStatistics,"edge","Empty Transform",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Fourier"] = [extractPixelIntensityStatistics,"fourier","Empty Transform",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Chebyshev_Fourier"] = [extractPixelIntensityStatistics,"chebyshev","fourier",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Edge_Fourier"] = [extractPixelIntensityStatistics,"edge","fourier",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Hue_Fourier"] = [extractPixelIntensityStatistics,"Hue Transform","fourier",5,True,False,'good']
feature_list["Pixel_Intensity_Statistics_Wavelet_Fourier"] = [extractPixelIntensityStatistics,"wavelet","fourier",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Hue"] = [extractPixelIntensityStatistics,"Hue Transform","Empty Transform",5,True,False,'good']
feature_list["Pixel_Intensity_Statistics_Wavelet"] = [extractPixelIntensityStatistics,"wavelet","Empty Transform",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Edge_Wavelet"] = [extractPixelIntensityStatistics,"edge","wavelet",5,False,False,'good']
feature_list["Pixel_Intensity_Statistics_Fourier_Wavelet"] = [extractPixelIntensityStatistics,"fourier","wavelet",5,False,False,'good']

#Radon Coefficients
feature_list["Radon_Coefficients"] = [extractRadonCoefficients,"Empty Transform","Empty Transform",12,False,False,'good']
feature_list["Radon_Coefficients_Chebyshev"] = [extractRadonCoefficients,"chebyshev","Empty Transform",12,False,False,'good']
feature_list["Radon_Coefficients_Fourier_Chebyshev"] = [extractRadonCoefficients,"fourier","chebyshev",12,False,False,'good']
feature_list["Radon_Coefficients_Hue_Chebyshev"] = [extractRadonCoefficients,"Hue Transform","chebyshev",12,True,False,'good']
feature_list["Radon_Coefficients_Wavelet_Chebyshev"] = [extractRadonCoefficients,"wavelet","chebyshev",12,False,False,'good']
feature_list["Radon_Coefficients_Color"] = [extractRadonCoefficients,"wndchrmcolor","Empty Transform",12,True,False,'good']
feature_list["Radon_Coefficients_Edge"] = [extractRadonCoefficients,"edge","Empty Transform",12,False,False,'good']
feature_list["Radon_Coefficients_Fourier"] = [extractRadonCoefficients,"fourier","Empty Transform",12,False,False,'good']
feature_list["Radon_Coefficients_Chebyshev_Fourier"] = [extractRadonCoefficients,"chebyshev","fourier",12,False,False,'good']
feature_list["Radon_Coefficients_Edge_Fourier"] = [extractRadonCoefficients,"edge","fourier",12,False,False,'good']
feature_list["Radon_Coefficients_Hue_Fourier"] = [extractRadonCoefficients,"Hue Transform","fourier",12,True,False,'good']
feature_list["Radon_Coefficients_Wavelet_Fourier"] = [extractRadonCoefficients,"wavelet","fourier",12,False,False,'good']
feature_list["Radon_Coefficients_Hue"] = [extractRadonCoefficients,"Hue Transform","Empty Transform",12,True,False,'good']
feature_list["Radon_Coefficients_Wavelet"] = [extractRadonCoefficients,"wavelet","Empty Transform",12,False,False,'good']
feature_list["Radon_Coefficients_Edge_Wavelet"] = [extractRadonCoefficients,"edge","wavelet",12,False,False,'good']
feature_list["Radon_Coefficients_Fourier_Wavelet"] = [extractRadonCoefficients,"fourier","wavelet",12,False,False,'good']


#Tamura Textures
feature_list["Tamura_Textures"] = [extractTamuraTextures,"Empty Transform","Empty Transform",6,False,False,'good']
feature_list["Tamura_Textures_Chebyshev"] = [extractTamuraTextures,"chebyshev","Empty Transform",6,False,False,'good']
feature_list["Tamura_Textures_Fourier_Chebyshev"] = [extractTamuraTextures,"fourier","chebyshev",6,False,False,'good']
feature_list["Tamura_Textures_Hue_Chebyshev"] = [extractTamuraTextures,"Hue Transform","chebyshev",6,True,False,'good']
feature_list["Tamura_Textures_Wavelet_Chebyshev"] = [extractTamuraTextures,"wavelet","chebyshev",6,False,False,'good']
feature_list["Tamura_Textures_Color"] = [extractTamuraTextures,"wndchrmcolor","Empty Transform",6,True,False,'good']
feature_list["Tamura_Textures_Edge"] = [extractTamuraTextures,"edge","Empty Transform",6,False,False,'good']
feature_list["Tamura_Textures_Fourier"] = [extractTamuraTextures,"fourier","Empty Transform",6,False,False,'good']
feature_list["Tamura_Textures_Chebyshev_Fourier"] = [extractTamuraTextures,"chebyshev","fourier",6,False,False,'good']
feature_list["Tamura_Textures_Edge_Fourier"] = [extractTamuraTextures,"edge","fourier",6,False,False,'good']
feature_list["Tamura_Textures_Hue_Fourier"] = [extractTamuraTextures,"Hue Transform","fourier",6,True,False,'good']
feature_list["Tamura_Textures_Wavelet_Fourier"] = [extractTamuraTextures,"wavelet","fourier",6,False,False,'good']
feature_list["Tamura_Textures_Hue"] = [extractTamuraTextures,"Hue Transform","Empty Transform",6,True,False,'good']
feature_list["Tamura_Textures_Wavelet"] = [extractTamuraTextures,"wavelet","Empty Transform",6,False,False,'good']
feature_list["Tamura_Textures_Edge_Wavelet"] = [extractTamuraTextures,"edge","wavelet",6,False,False,'good']
feature_list["Tamura_Textures_Fourier_Wavelet"] = [extractTamuraTextures,"fourier","wavelet",6,False,False,'good']

#Zernike Coeffivients
feature_list["Zernike_Coefficients"] = [extractZernikeCoefficients,"Empty Transform","Empty Transform",72,False,False,'good']
feature_list["Zernike_Coefficients_Chebyshev"] = [extractZernikeCoefficients,"chebyshev","Empty Transform",72,False,False,'good']
feature_list["Zernike_Coefficients_Hue_Chebyshev"] = [extractZernikeCoefficients,"Hue Transform","chebyshev",72,True,False,'good']
feature_list["Zernike_Coefficients_Color"] = [extractZernikeCoefficients,"wndchrmcolor","Empty Transform",72,True,False,'good']
feature_list["Zernike_Coefficients_Edge"] = [extractZernikeCoefficients,"edge","Empty Transform",72,False,False,'good']
feature_list["Zernike_Coefficients_Fourier"] = [extractZernikeCoefficients,"fourier","Empty Transform",72,False,False,'good']
feature_list["Zernike_Coefficients_Edge_Fourier"] = [extractZernikeCoefficients,"edge","fourier",72,False,False,'good']
feature_list["Zernike_Coefficients_Hue_Fourier"] = [extractZernikeCoefficients,"Hue Transform","fourier",72,True,False,'good']
feature_list["Zernike_Coefficients_Wavelet_Fourier"] = [extractZernikeCoefficients,"wavelet","fourier",72,False,False,'good']
feature_list["Zernike_Coefficients_Hue"] = [extractZernikeCoefficients,"Hue Transform","Empty Transform",72,True,False,'good']
feature_list["Zernike_Coefficients_Wavelet"] = [extractZernikeCoefficients,"wavelet","Empty Transform",72,False,False,'good']
feature_list["Zernike_Coefficients_Edge_Wavelet"] = [extractZernikeCoefficients,"edge","wavelet",72,False,False,'good']

