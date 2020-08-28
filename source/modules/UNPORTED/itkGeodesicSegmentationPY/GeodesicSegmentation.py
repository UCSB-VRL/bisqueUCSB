# Example Code to perform GeodesicSegmentation using wrapitk - python wrapper for ITK
# http://code.google.com/p/wrapitk/
# Pg 533 ITK Software Guide

#USAGE : python GeodesicSegmentation.py inputImage  outputImage seedX, seedY, InitialDistance, Sigma, SigmoidAlpha, SigmoidBeta, PropagationScaling

#USAGE : python GeodesicSegmentation.py ../Data/BrainProtonDensitySlice.png lventricle.png 81 114 5.0 1.0 -0.5 3.0 2.0
#USAGE : python GeodesicSegmentation.py ../Data/BrainProtonDensitySlice.png rventricle.png 99 114 5.0 1.0 -0.5 3.0 2.0
#USAGE : python GeodesicSegmentation.py ../Data/BrainProtonDensitySlice.png whitematter.png 56 92 5.0 1.0 -0.3 2.0 10.0
#USAGE : python GeodesicSegmentation.py ../Data/BrainProtonDensitySlice.png greymatter.png 40 90 5.0 0.5 -0.3 2.0 10.0

from sys import argv
import itk

def doSegment(inputImage,outputImage, seedX, seedY, InitialDistance, Sigma, SigmoidAlpha, SigmoidBeta, PropagationScaling):
  
	InternalPixelType = itk.F
	Dimension = 2
	InternalImageType = itk.Image[InternalPixelType, Dimension]

	OutputPixelType = itk.UC
	OutputImageType = itk.Image[OutputPixelType, Dimension]

	reader = itk.ImageFileReader[InternalImageType].New(FileName=inputImage)
	# needed to give the size to the fastmarching filter
	reader.Update()
    
	smoothing = itk.CurvatureAnisotropicDiffusionImageFilter[InternalImageType, InternalImageType].New(reader,
			    TimeStep=0.125,
			NumberOfIterations=5,
			ConductanceParameter=9.0)
    
	gradientMagnitude = itk.GradientMagnitudeRecursiveGaussianImageFilter[InternalImageType, InternalImageType].New(smoothing,
		                Sigma=float(Sigma) )

	sigmoid = itk.SigmoidImageFilter[InternalImageType, InternalImageType].New(gradientMagnitude,
		                OutputMinimum=0.0,
			OutputMaximum=1.1,
			Alpha=float(SigmoidAlpha),
			Beta=float(SigmoidBeta))

	seedPosition = itk.Index[2]()
	seedPosition.SetElement(0, int(seedX))
	seedPosition.SetElement(1, int(seedY))
		
	node = itk.LevelSetNode[InternalPixelType, Dimension]()
	node.SetValue(-InitialDistance)
	node.SetIndex(seedPosition)

	seeds = itk.VectorContainer[itk.UI, itk.LevelSetNode[InternalPixelType, Dimension]].New()
	seeds.Initialize()
	seeds.InsertElement(0, node)

	fastMarching = itk.FastMarchingImageFilter[InternalImageType, InternalImageType].New(sigmoid,
		                TrialPoints=seeds,
			SpeedConstant=1.0,
			OutputSize=reader.GetOutput().GetBufferedRegion().GetSize() )


	geodesicActiveContour = itk.GeodesicActiveContourLevelSetImageFilter[InternalImageType, InternalImageType, InternalPixelType].New(fastMarching,
		                FeatureImage=sigmoid.GetOutput(), # it is required to use the explicitly the FeatureImage - itk segfault without that :-(
		                PropagationScaling=float(PropagationScaling),
			CurvatureScaling=1.0,
			AdvectionScaling=1.0,
			MaximumRMSError=0.02,
			NumberOfIterations=800
			)
		
	thresholder = itk.BinaryThresholdImageFilter[InternalImageType, OutputImageType].New(geodesicActiveContour,
		                LowerThreshold=-1000,
			UpperThreshold=0,
			OutsideValue=0,
			InsideValue=255)

	writer = itk.ImageFileWriter[OutputImageType].New(thresholder, FileName=outputImage)
	writer.Update()

	## other outputs
	#def rescaleAndWrite(filter, fileName):
	#	caster = itk.RescaleIntensityImageFilter[InternalImageType, OutputImageType].New(filter,OutputMinimum=0,OutputMaximum=255)
	#	itk.write(caster, fileName)
			    
	#rescaleAndWrite(smoothing, "GeodesicActiveContourImageFilterOutput1.png")
	#rescaleAndWrite(gradientMagnitude, "GeodesicActiveContourImageFilterOutput2.png")
	#rescaleAndWrite(sigmoid, "GeodesicActiveContourImageFilterOutput3.png")
	#rescaleAndWrite(fastMarching, "GeodesicActiveContourImageFilterOutput4.png")

	##internal outputs
	
	#itk.write(fastMarching,"GeodesicActiveContourImageFilterOutput4.mha")
	#itk.write(sigmoid,"GeodesicActiveContourImageFilterOutput3.mha")
	#itk.write(gradientMagnitude,"GeodesicActiveContourImageFilterOutput2.mha")



