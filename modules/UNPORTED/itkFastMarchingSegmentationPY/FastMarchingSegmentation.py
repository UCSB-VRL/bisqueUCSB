# Example Code to perform FastMarchingSegmentation using wrapitk - python wrapper for ITK
# http://code.google.com/p/wrapitk/
# Pg 533 ITK Software Guide

#USAGE : python FastMarchingSegmentation.py inputImage  outputImage seedX seedY Sigma SigmoidAlpha SigmoidBeta TimeThreshold StoppingValue

#USAGE : python FastMarchingSegmentation.py ./Data/BrainProtonDensitySlice.png ./Output/FastMarching_lVentricle.png 81 114 1.0  -0.5  3.0 100 100
#USAGE : python FastMarchingSegmentation.py ./Data/BrainProtonDensitySlice.png ./Output/FastMarching_rVentricle.png 99 114 1.0  -0.5  3.0 100 100
#USAGE : python FastMarchingSegmentation.py ./Data/BrainProtonDensitySlice.png ./Output/FastMarching_whiteMatter.png 56 92 1.0  -0.3  2.0 200 100
#USAGE : python FastMarchingSegmentation.py ./Data/BrainProtonDensitySlice.png ./Output/FastMarching_grayMatter.png 40 90 1.0  -0.3  2.0 200 100

from sys import argv
import itk

def doSegment(inputImage,outputImage, seedX, seedY, Sigma, SigmoidAlpha, SigmoidBeta, TimeThreshold, StoppingValue):
	InternalPixelType = itk.F
	Dimension = 2
	InternalImageType = itk.Image[InternalPixelType, Dimension]

	OutputPixelType = itk.UC
	OutputImageType = itk.Image[OutputPixelType, Dimension]
	WriterType = itk.ImageFileWriter[  OutputImageType ]

	thresholder = itk.BinaryThresholdImageFilter[InternalImageType,OutputImageType].New()
	thresholder.SetLowerThreshold( 0.0  )

	timeThreshold = float( TimeThreshold )
	thresholder.SetUpperThreshold( timeThreshold  )

	thresholder.SetOutsideValue(  0  )
	thresholder.SetInsideValue(  255 )
	
	reader = itk.ImageFileReader[InternalImageType].New()
	reader.SetFileName( inputImage )

	writer = WriterType.New()
	writer.SetFileName(outputImage)


	smoothing = itk.CurvatureAnisotropicDiffusionImageFilter[InternalImageType,InternalImageType].New()

	gradientMagnitude = itk.GradientMagnitudeRecursiveGaussianImageFilter[InternalImageType,InternalImageType].New()

	sigmoid = itk.SigmoidImageFilter[InternalImageType,InternalImageType].New()

	sigmoid.SetOutputMinimum(  0.0  )
	sigmoid.SetOutputMaximum(  1.0  )

	fastMarching = itk.FastMarchingImageFilter[InternalImageType,InternalImageType].New()

	smoothing.SetInput( reader.GetOutput() )
	gradientMagnitude.SetInput( smoothing.GetOutput() )
	sigmoid.SetInput( gradientMagnitude.GetOutput() )
	fastMarching.SetInput( sigmoid.GetOutput() )
	thresholder.SetInput( fastMarching.GetOutput() )
	writer.SetInput( thresholder.GetOutput() )

	smoothing.SetTimeStep( 0.125 )
	smoothing.SetNumberOfIterations(  5 )
	smoothing.SetConductanceParameter( 9.0 )

	sigma = float( Sigma )
	gradientMagnitude.SetSigma(  sigma  )

	alpha =  float( SigmoidAlpha )
	beta  =  float( SigmoidBeta )

	sigmoid.SetAlpha( alpha )
	sigmoid.SetBeta(  beta  )

	seedPosition = itk.Index[2]()
	seedPosition.SetElement(0, int(seedX) )
	seedPosition.SetElement(1, int(seedY) )

	node = itk.LevelSetNode[InternalPixelType, Dimension]()
	seedValue = 0.0
	node.SetValue( seedValue )
	node.SetIndex( seedPosition ) 

	seeds = itk.VectorContainer[itk.UI, itk.LevelSetNode[InternalPixelType, Dimension]].New()
	seeds.Initialize()
	seeds.InsertElement( 0, node )
	fastMarching.SetTrialPoints(  seeds  )

	fastMarching.SetOutputSize(reader.GetOutput().GetBufferedRegion().GetSize() )
	stoppingTime = float( StoppingValue )
	fastMarching.SetStoppingValue(  stoppingTime  )

	#return thresholder.GetOutput()
	writer.Update()
	print 'output file written to disk'

	## other outputs
	#def rescaleAndWrite(filter, fileName):
	#	caster = itk.RescaleIntensityImageFilter[InternalImageType, OutputImageType].New(filter,OutputMinimum=0,OutputMaximum=255)
	#	itk.write(caster, fileName)
			    
	#rescaleAndWrite(smoothing, "FastMarchingFilterOutput1.png")
	#rescaleAndWrite(gradientMagnitude, "FastMarchingFilterOutput2.png")
	#rescaleAndWrite(sigmoid, "FastMarchingFilterOutput3.png")
	#rescaleAndWrite(fastMarching, "FastMarchingFilterOutput4.png")

	##internal outputs
	
	#itk.write(fastMarching,"FastMarchingFilterOutput4.mha")
	#itk.write(sigmoid,"FastMarchingFilterOutput3.mha")
	#itk.write(gradientMagnitude,"FastMarchingFilterOutput2.mha")



