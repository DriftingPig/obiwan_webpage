:orphan:

API Documentation
=================

Modules
-------
.. autosummary::
	:toctree: _autosummary
	:template: module.rst

	obiwan.mk_fits_image
	obiwan.kenobi
	obiwan.runs
	obiwan.common
	obiwan._version
	obiwan.time_per_brick
	obiwan.fetch
	obiwan.db_tools
	obiwan.draw_radec_color_z

Post-Processing
---------------
.. autosummary::
	:toctree: _autosummary
	:template: module.rst

	obiwan.runmanager.qdo_tasks
	obiwan.runmanager.update_imagefn_if_doesnt_exist
	obiwan.runmanager.derived_tables
	obiwan.runmanager.status
	obiwan.runmanager.merge_tables

Analysis & Plotting
-------------------
.. autosummary::
	:toctree: _autosummary
	:template: module.rst

	obiwan.qa.plots_common
	obiwan.qa.plots_footprint
	obiwan.qa.number_finished_by_slurm
	obiwan.qa.plots_using_csv_files
	obiwan.qa.plots_randomsprops_fluxdiff
	obiwan.qa.aaron_healpix
	obiwan.qa.unique_ccds_dr3
	obiwan.qa.cpu_hours
	obiwan.qa.tally
	obiwan.qa.visual

Scaling Tests
-------------
.. autosummary::
	:toctree: _autosummary
	:template: module.rst

	obiwan.scaling.select_bricks
	obiwan.scaling.timing

Tests
-----
.. autosummary::
	:toctree: _autosummary
	:template: module.rst

	tests.__init__
	tests.run_200x200_pixel_regions
	tests.test_200x200_pixel_regions

Deep Learning
-------------
.. autosummary::
	:toctree: _autosummary
	:template: module.rst

	obiwan.dplearn.create_training
	obiwan.dplearn.split_testtrain
	obiwan.dplearn.cnn

