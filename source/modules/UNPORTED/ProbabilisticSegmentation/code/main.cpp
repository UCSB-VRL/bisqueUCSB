#include <iostream>
#include <cmath>
#include <ctime>
#include <string>

// for mkdir() command
#include <sys/stat.h>
#include <sys/types.h>

#include "common.h"
#include "imageIO.h"
#include "cells.h"
#include "RandWalk.h"

using namespace std;


// ---------------- COMMAND LINE ARGUMENTS ---------------- 
uint OPT_DEBUG     = 0;
uint OPT_THRESHOLD = 0;
uint OPT_SEGCELL   = 0;
uint OPT_MOMENTUM  = 0;
// defualt is OFF for single cell images, ON for multicell images
uint OPT_NORMADJ_RESTART = 0;

string OPT_IMAGEIN  = "image_in.jpg";
string OPT_IMAGEOUT = "";
string OPT_CELLS    = "image_in_cells";

double OPT_RESTART   = 2e-5;
double OPT_TOLERANCE = 0.25; 


// ---------------- COMMAND LINE ARGUMENTS ---------------- 

// global file stream for summary file
ofstream fout;

bool SegAll = false;


// ---------------- FUNCTION DEFINITIONS ------------------
bool getArgs(const int & argc, const char * argv[]);
bool checkArg(const int & x, const int & argc);
int createDir();
void buildOutputDir();
// ---------------- FUNCTION DEFINITIONS ------------------

int main(int argc, char * argv[]){
  time_t timer_start, timer_stop;

  srand ( time(NULL) );
  timer_start = time(NULL);

  if (! getArgs(argc, (const char **)argv)){
    pixel * cell_centers;
    uint cell_cnt;
    string file, out_dir = OPT_IMAGEOUT;

    do{
      cout << endl << endl;
      cout << "** Segmenting cell " << OPT_SEGCELL << " **\n";
      cout << endl << endl;

      OPT_IMAGEOUT = out_dir;
      // Build and create output directory
      buildOutputDir();
      createDir();
      
      file = OPT_IMAGEOUT + "summary";
      fout.open(file.c_str());
    
      if (fout.is_open()){
	fout << "PARAMETERS: " << endl
	     << "Debug output          : " << OPT_DEBUG << endl
	     << "Thresholding          : " << OPT_THRESHOLD << endl
	     << "Segmenting Cell index : " << OPT_SEGCELL << endl
	     << "Input Image           : " << OPT_IMAGEIN << endl
	     << "Output Images         : " << OPT_IMAGEOUT << endl
	     << "Cells File            : " << OPT_CELLS << endl
	     << "Restart Probability   : " << OPT_RESTART << endl
	     << "Stopping Tolerance    : " << OPT_TOLERANCE << endl 
	     << "Normal Restart Adj    : " << OPT_NORMADJ_RESTART << endl << endl;
      }
      
      if (OPT_DEBUG > 0){
	cout << "PARAMETERS: " << endl
	     << "Debug output          : " << OPT_DEBUG << endl
	     << "Thresholding          : " << OPT_THRESHOLD << endl
	     << "Segmenting Cell index : " << OPT_SEGCELL << endl
	     << "Input Image           : " << OPT_IMAGEIN << endl
	     << "Output Images         : " << OPT_IMAGEOUT << endl
	     << "Cells File            : " << OPT_CELLS << endl
	     << "Restart Probability   : " << OPT_RESTART << endl
	     << "Stopping Tolerance    : " << OPT_TOLERANCE << endl
	     << "Normal Restart Adj    : " << OPT_NORMADJ_RESTART << endl;
	cout << endl;
      }
      
      // read in cells
      cell_centers = cells::readCells(OPT_CELLS.c_str(), cell_cnt);
      if (cell_cnt > 1){
	/*
	 * For multi-cell images, set this to true
	 */
	OPT_NORMADJ_RESTART = 1;
      }

      if (cell_centers != NULL){
	// ------- setup --------
	double xy_plane, z_plane, z_ratio;
	float * steady_state;
	imgStack * img;
	imageIO imIO(OPT_IMAGEIN);
	
	imIO.loadImage();
	img = imIO.getImage();
	imIO.getScaleFactors(xy_plane, z_plane);
	z_ratio = xy_plane / z_plane;
	
	cells imgCells(cell_centers, cell_cnt, OPT_RESTART, OPT_SEGCELL, z_ratio);
	
	pixel img_dimension = {img->width, img->height, img->depth};
	if (imgCells.updateCenters(img_dimension)){

	  // ------- perform random walk --------
	  RandWalk sim(img, &imgCells, z_ratio);
	  sim.Walk(); 
	  
	  if (OPT_DEBUG){
	    cout << "** Writing images... **\n";
	  }
	  // ------- output images -------
	  steady_state = sim.getSteadyState();
	  imIO.writeImage(steady_state, sim.getMaxVisits(), imgCells.getThisCell());
	}
      }

      fout.close();
      ++OPT_SEGCELL;
      if (OPT_SEGCELL > (cell_cnt - 1)){
	SegAll = false;
      }
    }while(SegAll);
    
  }else{
    cerr << "Could not parse command line arguments.\n";
  }

  timer_stop = time(NULL);
  cout << "\nTotal run time: " << difftime(timer_stop, timer_start) << endl << endl;
  
  return 0;
}

int createDir(){
  /*
   * S_IRWXU - read, write, execute by user
   * S_IRGRP - read by group
   * S_IROTH - read by other
   */
  int ret = 0;
  string::size_type start = 0, dir_string_len;
  string str;

  if (OPT_DEBUG > 0){
    cout << "Parsing output directory structure: " << endl
	 << OPT_IMAGEOUT << endl << endl;
  }

  do{
    dir_string_len = OPT_IMAGEOUT.find("/", (start + 1));
    str             = OPT_IMAGEOUT.substr(0, dir_string_len);
    
    if (dir_string_len < string::npos){
      if (OPT_DEBUG > 1){
	cout << "Start: " << start << " Dir string length: " << dir_string_len << endl
	     << "Creating dir: " << str << endl << endl;
      }
      ret += mkdir(str.c_str(), S_IRWXU | S_IRGRP |  S_IROTH);
    }

  }while (((start = OPT_IMAGEOUT.find("/", (start + 1))) < string::npos));

  return ret;
}

/*
 * Build directory structure for results
 * Default:
 * 
 * Results/
 * CellImageName/
 * SegCellid/
 * restartval_tolerance_#.ext
 */
void buildOutputDir(){
    char str[30];
    string name;
    int s, e;
    
    s = OPT_IMAGEIN.find_last_of("/") + 1;
    e = OPT_IMAGEIN.find_last_of(".");

    sprintf(str, "cell%i/", OPT_SEGCELL);

    name = OPT_IMAGEIN.substr(s, (e - s));
    OPT_IMAGEOUT.assign(OPT_IMAGEOUT + name + "/" + str);
}


/*
 * Parsing the command line arguments and setting global variables
 *
*/
bool checkArg(int & x, const int & argc){
  bool error = false;

  ++x;

  /*
   * Since we've just found an input flag, we need to make
   * sure that the value follows. (ie. -in filename)
   * We first need to check that there is another input element
   */
  if (x >= argc){
    error = true;
    cerr << "Invalid input arguments.\n";
  }

  return error;
}

    
bool getArgs(const int & argc, const char * argv[]){
  int x = 1;
  bool error = false;

  while ((x < argc) && (! error)){

    if (strcmp(argv[x], "-in") == 0){
      // ---- Input Image
      error = checkArg(x, argc);
      
      if (! error){
	OPT_IMAGEIN.assign(argv[x]);
      }
    }else if (strcmp(argv[x], "-r") == 0){
      // ---- restart probability
      error = checkArg(x, argc);
      
      if (! error){
	OPT_RESTART = atof(argv[x]);
      }
    }else if (strcmp(argv[x], "-d") == 0){
      // ---- Debugging output

      ++OPT_DEBUG;
    }else if (strcmp(argv[x], "-out") == 0){
      // ---- Output image
      error = checkArg(x, argc);
      
      if (! error){
	OPT_IMAGEOUT.assign(argv[x]);

	// make sure this is defined as a directory
	if ((OPT_IMAGEOUT.length() > 0) && 
	    (OPT_IMAGEOUT.at(OPT_IMAGEOUT.length() - 1) != '/')){
	  OPT_IMAGEOUT.append("/");
	}
      }
    }else if (strcmp(argv[x], "-t") == 0){
      // ---- residual tolerance
      error = checkArg(x, argc);

      if (! error){
	OPT_TOLERANCE = atof(argv[x]);
      }
    }else if (strcmp(argv[x], "-seg") == 0){
      // ---- residual tolerance
      error = checkArg(x, argc);

      if (! error){
	if (strcmp(argv[x], "all") == 0){
	  // segment all cells in image
	  OPT_SEGCELL = 0;
	  SegAll      = true;
	}else{
	  OPT_SEGCELL = atoi(argv[x]);
	}
      }
    }else if (strcmp(argv[x], "-thresh") == 0){
      // ---- Thresholding
      ++OPT_THRESHOLD;
    }else if (strcmp(argv[x], "-cells") == 0){
      // ---- cells file
      error = checkArg(x, argc);

      if (! error){
	OPT_CELLS.assign(argv[x]);
      }
    }else if (strcmp(argv[x], "-adj") == 0){
      // ---- Adjust restart probability
      // ONLY for moving away from current cell, and NOT toward another cell
      OPT_NORMADJ_RESTART = 1;
    }
    ++x;
  }
  
  return error;
}

