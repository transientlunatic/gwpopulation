"""
Tests for the asimov interface.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import os
import tempfile
import shutil


class TestAsimovInterface(unittest.TestCase):
    """
    Test the GWPopulation asimov pipeline interface.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        
        # Create a mock production/analysis object
        self.mock_production = Mock()
        self.mock_production.name = "test_population_analysis"
        self.mock_production.rundir = self.test_dir
        self.mock_production.status = "ready"
        self.mock_production.analyses = []
        
        # Try to import the interface
        try:
            from gwpopulation.asimov_interface import GWPopulation
            self.GWPopulation = GWPopulation
            self.asimov_available = True
        except ImportError:
            self.asimov_available = False
            self.GWPopulation = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_import(self):
        """Test that the asimov_interface module can be imported."""
        from gwpopulation import asimov_interface
        self.assertTrue(hasattr(asimov_interface, 'GWPopulation'))
    
    def test_pipeline_creation(self):
        """Test that the GWPopulation pipeline can be instantiated."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        self.assertEqual(pipeline.name, "gwpopulation")
        self.assertEqual(pipeline.production, self.mock_production)
    
    def test_pipeline_has_required_methods(self):
        """Test that the pipeline has all required methods."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        
        # Check for required methods
        required_methods = [
            'detect_completion',
            'build_dag',
            'submit_dag',
            'collect_assets',
            'after_completion',
            'collect_logs',
            'check_progress',
        ]
        
        for method in required_methods:
            self.assertTrue(
                hasattr(pipeline, method),
                f"Pipeline missing required method: {method}"
            )
    
    def test_posteriors_property_empty(self):
        """Test posteriors property with no analyses."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        posteriors = pipeline.posteriors
        self.assertIsInstance(posteriors, list)
        self.assertEqual(len(posteriors), 0)
    
    def test_posteriors_property_with_analyses(self):
        """Test posteriors property with mock analyses."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        # Create mock analyses
        mock_analysis = Mock()
        mock_analysis.rundir = self.test_dir
        mock_analysis.pipeline = Mock()
        mock_analysis.pipeline.samples = Mock(return_value=['test.h5'])
        
        self.mock_production.analyses = [mock_analysis]
        
        pipeline = self.GWPopulation(self.mock_production)
        posteriors = pipeline.posteriors
        self.assertIsInstance(posteriors, list)
        self.assertEqual(len(posteriors), 1)
        self.assertEqual(posteriors[0], 'test.h5')
    
    def test_events_property(self):
        """Test the events property."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        self.mock_production.subjects = ['event1', 'event2']
        
        pipeline = self.GWPopulation(self.mock_production)
        events = pipeline.events
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0], 'event1')
    
    def test_detect_completion_no_rundir(self):
        """Test completion detection with no rundir."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        self.mock_production.rundir = None
        
        pipeline = self.GWPopulation(self.mock_production)
        self.assertFalse(pipeline.detect_completion())
    
    def test_detect_completion_no_results(self):
        """Test completion detection with no result files."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        self.assertFalse(pipeline.detect_completion())
    
    def test_detect_completion_with_results(self):
        """Test completion detection with result file present."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        # Create a mock result file
        result_file = os.path.join(self.test_dir, 'result.json')
        with open(result_file, 'w') as f:
            f.write('{}')
        
        pipeline = self.GWPopulation(self.mock_production)
        self.assertTrue(pipeline.detect_completion())
    
    def test_build_dag(self):
        """Test DAG building."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        command = pipeline.build_dag()
        
        self.assertIsInstance(command, list)
        self.assertGreater(len(command), 0)
    
    def test_collect_assets_empty(self):
        """Test asset collection with no files."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        assets = pipeline.collect_assets()
        
        self.assertIsInstance(assets, dict)
        self.assertEqual(len(assets), 0)
    
    def test_collect_assets_with_files(self):
        """Test asset collection with result files."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        # Create mock output files
        result_file = os.path.join(self.test_dir, 'result.json')
        with open(result_file, 'w') as f:
            f.write('{}')
        
        pipeline = self.GWPopulation(self.mock_production)
        assets = pipeline.collect_assets()
        
        self.assertIsInstance(assets, dict)
        self.assertIn('result.json', assets)
        self.assertEqual(assets['result.json'], result_file)
    
    def test_after_completion(self):
        """Test after_completion hook."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        pipeline.after_completion()
        
        self.assertEqual(self.mock_production.status, 'finished')
    
    def test_collect_logs_empty(self):
        """Test log collection with no log files."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        logs = pipeline.collect_logs()
        
        self.assertIsInstance(logs, dict)
        self.assertEqual(len(logs), 0)
    
    def test_collect_logs_with_files(self):
        """Test log collection with log files present."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        # Create a mock log file
        log_file = os.path.join(self.test_dir, f'{self.mock_production.name}.log')
        log_content = 'Test log content'
        with open(log_file, 'w') as f:
            f.write(log_content)
        
        pipeline = self.GWPopulation(self.mock_production)
        logs = pipeline.collect_logs()
        
        self.assertIsInstance(logs, dict)
        self.assertIn(f'{self.mock_production.name}.log', logs)
        self.assertEqual(logs[f'{self.mock_production.name}.log'], log_content)
    
    def test_check_progress(self):
        """Test progress checking."""
        if not self.GWPopulation:
            self.skipTest("GWPopulation not available")
        
        pipeline = self.GWPopulation(self.mock_production)
        progress = pipeline.check_progress()
        
        self.assertIsInstance(progress, dict)
        self.assertIn('completed', progress)
        self.assertIsInstance(progress['completed'], bool)


if __name__ == '__main__':
    unittest.main()
