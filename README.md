This project is mean to use the espn api to collect data and output in a specific way.

## ENVIRONMENT VARIABLES NEEDED

* `LEAGUE_ID` - look at the url once you log into espn fantasy football
* `ESPN_SWID`- to find log into https://fantasy.espn.com/football/ and inspect the page (right click inspect)
and open the applications tab.  There should be a place to look at the cookies under the storage section.
Copy the value that you find here.
* `ESPN_S2_CODE`- to find log into https://fantasy.espn.com/football/ and inspect the page (right click inspect)
                and open the applications tab.  There should be a place to look at the cookies under the storage section.
                Copy the value that you find here.
                
                
## Local Development

* Ensure Conda is installed for local development

  * Download and install Miniconda
  https://conda.io/miniconda.html 
  Choose the distribution that corresponds with the major Python version required (2.7 or 3.4)
  To use Minidconda from the command line, Anaconda will either need to be added to the system PATH or interacted with through the Anaconda prompt. Adding Anaconda to the PATH is the simplest way to get up and running, though the installer warns against it.
  * Once the installation completes, verify it was successful
  Open a new command prompt (or Anaconda prompt) and type:
  conda --version
  If successful, ensure Miniconda is fully up to date:
  conda upgrade conda

* Clone this repository.

* From the command line, create a new Conda environment using the environment.yml file
  * `conda env create -f environment.yml`
  
* Use python found in the conda environment ().
  * `~/Applications/miniconda2/envs/espn-power-rankings/bin/python3`