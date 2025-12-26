"""
Asimov integration for running gwpopulation analyses.

This module provides the interface between gwpopulation and asimov,
allowing population analyses to be run as ProjectAnalysis instances
within the asimov framework.
"""

import os

try:
    from asimov.pipeline import Pipeline
except ImportError:
    # If asimov is not installed, define a minimal Pipeline class
    # to allow the module to be imported
    class Pipeline:
        """Minimal Pipeline class for when asimov is not installed."""
        
        def __init__(self, production):
            self.production = production
            self.logger = None


# Common posterior sample file names to look for
POSTERIOR_FILE_NAMES = [
    'posterior_samples.h5',
    'result.json',
    'posterior_samples.dat',
    'posterior.h5',
]

# Common output file names from gwpopulation analyses
OUTPUT_FILE_NAMES = [
    'result.json',
    'posterior_samples.dat',
    'population_result.json',
]


class GWPopulation(Pipeline):
    """
    GWPopulation pipeline for Asimov.
    
    Provides integration for running population inference analyses
    using gwpopulation within the asimov framework. This pipeline
    is designed to work with ProjectAnalysis instances that aggregate
    results from multiple event analyses.
    
    Parameters
    ----------
    production : asimov.analysis.ProjectAnalysis
        The project analysis instance containing the events and
        analyses to be used for population inference.
    
    Attributes
    ----------
    name : str
        The name of this pipeline ("gwpopulation")
    """
    
    name = "gwpopulation"
    
    def __init__(self, production):
        """
        Initialize the GWPopulation pipeline.
        
        Parameters
        ----------
        production : asimov.analysis.ProjectAnalysis
            The project analysis instance
        """
        super().__init__(production)
    
    @property
    def posteriors(self):
        """
        Collect posterior samples from all analyses in this project.
        
        Returns
        -------
        list
            A list of paths to posterior sample files from the
            dependent analyses.
        """
        posterior_files = []
        
        if not hasattr(self.production, 'analyses'):
            return posterior_files
        
        for analysis in self.production.analyses:
            # Try to get the posterior samples from each analysis
            # This will depend on the pipeline that generated them
            if hasattr(analysis, 'pipeline'):
                if hasattr(analysis.pipeline, 'samples'):
                    samples = analysis.pipeline.samples()
                    if isinstance(samples, list):
                        posterior_files.extend(samples)
                    elif samples:
                        posterior_files.append(samples)
                elif hasattr(analysis, 'rundir'):
                    # Look for common posterior file names
                    rundir = analysis.rundir
                    if rundir and os.path.isdir(rundir):
                        for fname in POSTERIOR_FILE_NAMES:
                            fpath = os.path.join(rundir, fname)
                            if os.path.exists(fpath):
                                posterior_files.append(fpath)
                                break
        
        return posterior_files
    
    @property
    def events(self):
        """
        Get the list of events in this project analysis.
        
        Returns
        -------
        list
            List of event objects from the project analysis
        """
        if hasattr(self.production, 'subjects'):
            return self.production.subjects
        return []
    
    def detect_completion(self):
        """
        Check for the production of results to signal completion.
        
        Returns
        -------
        bool
            True if the analysis has completed, False otherwise
        """
        rundir = getattr(self.production, 'rundir', None)
        if not rundir or not os.path.isdir(rundir):
            return False
        
        # Look for common gwpopulation output files
        output_files = [os.path.join(rundir, fname) for fname in OUTPUT_FILE_NAMES]
        
        return any(os.path.exists(f) for f in output_files)
    
    def build_dag(self):
        """
        Construct the command used to run the population analysis.
        
        This should be implemented based on how gwpopulation
        analyses are typically run. For now, this returns a
        placeholder command.
        
        Returns
        -------
        list
            Command line arguments to run the analysis
        """
        rundir = getattr(self.production, 'rundir', '.')
        
        # Get the configuration file if it exists
        config_file = os.path.join(rundir, f"{self.production.name}.ini")
        
        # This is a placeholder - the actual command will depend on
        # how gwpopulation is typically invoked
        command = [
            'python',
            '-m',
            'gwpopulation',
            config_file,
        ]
        
        if self.logger:
            self.logger.info(f"Command: {' '.join(command)}")
        
        return command
    
    def submit_dag(self):
        """
        Submit the analysis job.
        
        This is a placeholder implementation. In practice, this would
        submit the job to a scheduler (e.g., HTCondor) or run it locally.
        
        Returns
        -------
        int or str
            The job ID assigned by the scheduler
        """
        if self.logger:
            self.logger.info(f"Submitting gwpopulation analysis: {self.production.name}")
        
        # Placeholder - actual implementation would submit to scheduler
        # For now, just mark as submitted
        return None
    
    def collect_assets(self):
        """
        Collect all output files from this analysis.
        
        Returns
        -------
        dict
            Dictionary mapping asset names to file paths
        """
        assets = {}
        rundir = getattr(self.production, 'rundir', None)
        
        if not rundir or not os.path.isdir(rundir):
            return assets
        
        # Common gwpopulation output files
        asset_names = [
            'result.json',
            'posterior_samples.dat',
            'population_result.json',
            f'{self.production.name}.log',
            f'{self.production.name}.out',
            f'{self.production.name}.err',
        ]
        
        for fname in asset_names:
            fpath = os.path.join(rundir, fname)
            if os.path.exists(fpath):
                assets[fname] = fpath
        
        return assets
    
    def after_completion(self):
        """
        Hook to run after the analysis completes.
        
        This updates the production status to 'finished'.
        """
        self.production.status = 'finished'
        if self.logger:
            self.logger.info(f"gwpopulation analysis {self.production.name} completed")
    
    def collect_logs(self):
        """
        Collect all log files produced by this pipeline.
        
        Returns
        -------
        dict
            Dictionary mapping log file names to their contents
        """
        logs = {}
        rundir = getattr(self.production, 'rundir', None)
        
        if not rundir or not os.path.isdir(rundir):
            return logs
        
        log_files = [
            f'{self.production.name}.out',
            f'{self.production.name}.err',
            f'{self.production.name}.log',
        ]
        
        for fname in log_files:
            fpath = os.path.join(rundir, fname)
            if os.path.exists(fpath):
                try:
                    with open(fpath, 'r') as fh:
                        logs[fname] = fh.read()
                except (IOError, OSError) as e:
                    if self.logger:
                        self.logger.warning(f"Failed to read log file {fname}: {e}")
                    continue
        
        return logs
    
    def check_progress(self):
        """
        Check the progress of the analysis.
        
        Returns
        -------
        dict
            Dictionary with progress information
        """
        return {
            'completed': self.detect_completion()
        }
