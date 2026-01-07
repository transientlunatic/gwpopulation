Asimov Integration
==================

`GWPopulation` provides integration with the `asimov <https://github.com/etive-io/asimov>`_ framework
for managing and running gravitational-wave population analyses.

Overview
--------

The asimov integration allows you to run population inference analyses as part of an asimov project,
using events and analyses managed by asimov as input data. This is particularly useful when:

- Managing multiple parameter estimation analyses across many events
- Running population analyses as part of a larger analysis pipeline
- Coordinating analyses across a collaboration

The integration is designed to work with ``ProjectAnalysis`` instances in asimov, which aggregate
results from multiple events and/or multiple analyses per event.

Installation
------------

To use the asimov integration, you need both ``gwpopulation`` and ``asimov`` installed:

.. code-block:: bash

    pip install gwpopulation
    pip install asimov

The integration is automatically registered via Python entry points when both packages are installed.

Basic Usage
-----------

Asimov Configuration
~~~~~~~~~~~~~~~~~~~~

In your asimov ledger file, you can define a population analysis as a ``ProjectAnalysis``:

.. code-block:: yaml

    project_analyses:
      - name: population_inference
        pipeline: gwpopulation
        subjects:
          - GW150914
          - GW151012
          - GW151226
        analyses:
          - pipeline: bilby
            status: finished

This configuration creates a population analysis that will use the results from all
finished bilby analyses on the specified events.

Pipeline Interface
~~~~~~~~~~~~~~~~~~

The ``GWPopulation`` pipeline class provides the following key features:

- **Automatic posterior collection**: Collects posterior samples from all dependent analyses
- **Event aggregation**: Gathers data from multiple events in the project
- **Standard asimov hooks**: Implements all required pipeline methods for asimov integration

API Reference
-------------

.. autoclass:: gwpopulation.asimov_interface.GWPopulation
   :members:
   :undoc-members:
   :show-inheritance:

Examples
--------

Complete Workflow
~~~~~~~~~~~~~~~~~

Here's a complete example of setting up and running a population analysis through asimov:

1. Define your project in the asimov ledger:

.. code-block:: yaml

    project_analyses:
      - name: mass_distribution_analysis
        pipeline: gwpopulation
        status: ready
        subjects:
          - GW150914
          - GW151012
          - GW151226
          - GW170104
        analyses:
          - pipeline: bilby
            status: finished
        working_directory: /path/to/working/dir

2. Asimov will automatically:

   - Collect posterior samples from all specified analyses
   - Set up the working directory
   - Prepare the analysis for execution

3. The pipeline provides methods to:

   - Build and submit jobs to a scheduler
   - Monitor analysis progress
   - Collect and store results

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~

You can customize the analysis by adding additional metadata:

.. code-block:: yaml

    project_analyses:
      - name: advanced_population
        pipeline: gwpopulation
        subjects: [GW150914, GW151226]
        analyses:
          - pipeline: bilby
            status: finished
        sampler:
          nsamples: 10000
          nprocesses: 4
        scheduler:
          accounting_group: ligo.dev.o4.cbc.pe.lalinference

Accessing Results
~~~~~~~~~~~~~~~~~

After the analysis completes, results can be accessed through asimov's result storage:

.. code-block:: python

    from asimov import Ledger
    
    ledger = Ledger("ledger.yml")
    analysis = ledger.get_project_analysis("mass_distribution_analysis")
    
    # Get result files
    results = analysis.results()
    
    # Access specific result file
    posterior = analysis.results("population_result.json")

Integration with gwpopulation_pipe
-----------------------------------

For users already familiar with ``gwpopulation_pipe``, the asimov integration provides
a complementary approach. While ``gwpopulation_pipe`` focuses on HPC batch processing,
the asimov integration emphasizes:

- Interactive project management
- Integration with other asimov-managed analyses
- Collaborative workflows with shared ledgers

Both tools can be used together in larger projects.

Notes
-----

* The asimov integration is designed to work with the asimov ``v0.7-preview`` branch and the ``v0.7`` release (once available)
* The pipeline assumes posterior samples are available in standard formats (HDF5, JSON, etc.)
* Custom analysis scripts can be integrated by extending the ``GWPopulation`` class

See Also
--------

* `Asimov documentation <https://ligo-asimov.readthedocs.io/>`_
* `gwpopulation_pipe <https://docs.ligo.org/RatesAndPopulations/gwpopulation_pipe/>`_
* :doc:`likelihood` for details on the likelihood functions used
* :doc:`models` for available population models
