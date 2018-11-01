#! /usr/bin/env python

import os
import pkg_resources
from ..abstract_task import *
 
class Intron_retention(Abstract_task):

    task_name = "intron-retention"

    def __init__(self, output_dir, task_dir, sample_conf, param_conf, run_conf):

        super(Intron_retention, self).__init__(
            pkg_resources.resource_filename("genomon_pipeline_cloud", "script/{}.sh".format(self.__class__.task_name)),
            param_conf.get("intron_retention", "image"),
            param_conf.get("intron_retention", "resource"),
            output_dir + "/logging")
        
        self.task_file = self.task_file_generation(output_dir, task_dir, sample_conf, param_conf, run_conf)


    def task_file_generation(self, output_dir, task_dir, sample_conf, param_conf, run_conf):

        # generate fusionfusion_tasks.tsv
        #task_file = "{}/{}-tasks.tsv".format(task_dir, self.__class__.task_name)
        task_file = "{}/{}-tasks-{}-{}.tsv".format(task_dir, self.__class__.task_name, run_conf.get_owner_info(), run_conf.analysis_timestamp)
        with open(task_file, 'w') as hout:
            
            print >> hout, '\t'.join(["--env SAMPLE",
                                      "--input-recursive INPUT_DIR",
                                      "--env INPUT_BAM",
                                      "--output-recursive OUTPUT_DIR",
                                      "--env OPTION"])

            for sample in sample_conf.intron_retention:

                bam = sample_conf.bam_file[sample]
                bam_dir = os.path.dirname(bam)
                bam_file = os.path.basename(bam)

                print >> hout, '\t'.join([sample,
                                          bam_dir,
                                          bam_file,
                                          output_dir + "/intron_retention/" + sample,
                                          param_conf.get("intron_retention", "intron_retention_option")])

        return task_file
