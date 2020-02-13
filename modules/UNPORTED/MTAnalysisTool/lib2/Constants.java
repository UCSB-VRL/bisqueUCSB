public class Constants
{
	public static double log10 = Math.log(10);

	public static int MAX_MT = 2500;
	public static int MAX_LEN = 2500;
	public static int MAX_MODELS = 150;

	public static double ADRIA_BIN_GT = 0.2;	// adria
	public static double ADRIA_MIN_GT = 0.5;	// adria
	public static double ADRIA_MAX_GT = 7.5;	// adria
	public static int ADRIA_HISTOSIZE_GT = (int)((ADRIA_MAX_GT - ADRIA_MIN_GT) / ADRIA_BIN_GT);	// adria
	public static double ADRIA_ATT_THRES = 0.5;	// adria

	//*
	// Emin
	public static double SIMPLE_GROWTH_RATE = 4.0;			// microns/min
	public static double SIMPLE_GROWTH_LENGTH = 0.3;		// microns
	public static double COMPLEX_GROWTH_RATE = 4.0;			// microns/min
	public static double COMPLEX_GROWTH_LENGTH = 0.4;		// microns

	public static double SIMPLE_SHORTENING_RATE = -4.0;		// microns/min
	public static double SIMPLE_SHORTENING_LENGTH = -0.5;	// microns
	public static double COMPLEX_SHORTENING_RATE = -4.0;	// microns/min
	public static double COMPLEX_SHORTENING_LENGTH = -0.6;	// microns

	public static double SIMPLE_ATTENUATION_TIME = 5.0;		// secs
	public static double SIMPLE_ATTENUATION_LENGTH = 0.5;	// microns
	public static double COMPLEX_ATTENUATION_TIME = 4.0;	// secs
	public static double COMPLEX_ATTENUATION_LENGTH = 0.5;	// microns

	//public static double EXCLUDED_LENGTH = 0.3;			// microns
	//*/
	
	/*
	// Adria, Sasha
	public static double SIMPLE_GROWTH_RATE = 0.5;			// microns/min
	public static double SIMPLE_GROWTH_LENGTH = 0.05;		// microns
	public static double COMPLEX_GROWTH_LENGTH = 0.06;		// microns
	public static double SIMPLE_SHORTENING_RATE = -0.5;		// microns/min
	public static double SIMPLE_SHORTENING_LENGTH = -0.5;	// microns
	public static double COMPLEX_SHORTENING_LENGTH = -0.6;	// microns
	public static double SIMPLE_ATTENUATION_TIME = 4.0;		// secs
	public static double COMPLEX_ATTENUATION_TIME = 30.0;	// secs
	public static double EXCLUDED_LENGTH = 0.3;				// microns
	//*/
	
	public static double EPS = 0.0001;
}

