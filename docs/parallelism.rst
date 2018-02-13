Parallelism
============

CxSystem is and will be moving forward in synchrony with Brian2. Currently, parallelization in Brian2 is limited to GPU via GeNN simulator, and alpha version of multi-threading with OpenMP. Our framework supports both features for an individual simulation. This internal parallelization of Brian2 is probably going to happen in near future , and will be integrated in CxSystem. Yet, CxSystem supports parallelism in two forms: array_run and cluster_run. These features can be used for parameter search that automatically spawns multiple simulations on a workstation or a cluster and supports both python and stand-alone C++ devices. 

Array Runs
--------------
Array run (Parallel runs) can be set using the curly braces around the target parameter. For instance, to run 3 separate simulations\
with scale=1, scale=2 and scale=3, the parameter scale should be set to:

::

	...,scale,...
	...,{1,2,3},...

This parallel run will use the number of processes (threads) that is set using the number_of_process parameter, e.g. if number_of_process=3, \
then each of the 3 simulations runs in their own threads. However, if number_of_process=2, two processes run first the \
simulation for scale=1, and scale=2. The third simulation with scale=3 will start when the first of the two simulations are completed.

The array_run could also be set in range with defined step:

::

	...,scale,...
	...,{1|5|1},...

This parallel run will use four simulations with scale=1, scale=2, scale=3 and scale=4. Note the numpy style vector excluding the last index.

When two or more parameters are set to use array runs, CxSystem can run the parallel runs either as multi-dimensional runs \
or independent runs. For example: suppose a simulation is to be performed for scale {1,2,3} with do_init_vms set to {0,1}. \
If multidimension_array_run flag is set to 1, the following 6 simulations will be run separately:

::

	{scale=1, do_init_vms=0}, {scale=1, do_init_vms=1}, {scale=2, do_init_vms=0}, {scale=2, do_init_vms=1}, {scale=3, do_init_vms=0}, {scale=3, do_init_vms=1}

When multidimension_array_run flag is set to 0, however, the array_run pattern is different and 5 simulations will be run in parallel:

::

	{scale=1}, {scale=2}, {scale=3}, {do_init_vms=0}, {do_init_vms=1}

One might want to run each of the parallel simulations several times, e.g. to observe an effect of random initialization on a particular parameter set.
For this purpose the *trials_per_config* should be set to number of runs per configuration.

Cluster Run
------------
In Cluster Run mode, CxSystem connects to a connection node of a cluster via SSH and runs instances of array run on pre-defined number of nodes in the cluster. Currently Cluster Run is tested on `Taito supercluster
<https://research.csc.fi/taito-supercluster>`_ that employs Slurm workload manager.  However, with a slight modification to the Slurm template file, one can use the cluster run on other types of workload manager systems, e.g. Torque.

Setting up the environment
...........................

Before submitting the batch jobs to the cluster with CxSystem, the cluster environment should be properly set up. This includes finding/copying/assigning the Anaconda folder in the Slurm file or environment. In case you are using a custom branch you should as well clone and checkout to that branch otherwise CxSystem will clone itself and try to spawn the processes using the master branch. The parameters that are used for cluster run are as follows:

::

  
   run_in_cluster
   1

which triggers the cluster run. 

::
   
   cluster_job_file_path
   ./slurm.job

This parameter defines the address of the template workload management system file. In this case the a template for Slurm system is made available in the Github page which can be used for any cluster that utilizes the Slurm. In case the cluster of choice uses another workload management system, the template file should be specified in the configuration file.


::
   
   cluster_number_of_nodes
   10

Defines how many nodes CxSystem can have access to in the cluster.
**Important Note: the number of nodes in the cluster workload management system file should be set to 1 and instead the number of nodes should be defined here. The reason for this is that CxSystem submits separate jobs to each node in the cluster. This has some advantages, including less waiting time, and some disadvantages, complexity.** 

::

   cluster_address
   taito.csc.fi

Defines the URL of the cluster.

::

   username
   johnsmith

Defines the username for the SSH connection.

::

   remote_repo_path
   ./CxSystem

Defines the path of the CxSystem in the connection node of the cluster. In this example *./CxSystem* indicates that the CxSystem clone exists in the home folder, i.e. *~/*, in the connection node. If the repository clone does not exist there, then the latest version will be cloned and used. As mentioned earlier, in case the user is using a specific branch, CxSystem should be cloned and checked out manually. Otherwise the user can rely on CxSystem cloning itself in the connection node.

::

   remote_output_folder
   ./results

Defines the folder in which the results will be copied. In this example, a new folder *results* will be created in the remote_repo_path folder and the results will be saved there.


Transferring the Results
.........................

Usually clusters have an option to send users an email when the job is finished and users can transfer the results to their local machine. CxSystem can do this automatically: When a batch job is submitted, besides generating several Slurm files, CxSystem creates a _tmp_checker_data file. This file, which contains information about the current cluster batch job, will be used to check the status of the results in the cluster. If the results are ready, they will be copied to the local result folder. This task can be done by directly running cluster_run.py.
