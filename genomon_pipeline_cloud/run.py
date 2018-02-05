#! /usr/bin/env python

import sys, argparse, tempfile, shutil, os, subprocess, multiprocessing, pkg_resources
from ConfigParser import SafeConfigParser
from batch_engine import *
from sample_conf import Sample_conf
from run_conf import Run_conf

def run(args):

    sample_conf = Sample_conf()
    sample_conf.parse_file(args.sample_conf_file)
    
    param_conf = SafeConfigParser()
    param_conf.read(args.param_conf_file)

    run_conf = Run_conf(sample_conf_file = args.sample_conf_file, 
                        analysis_type = args.analysis_type)
    
    # tmp_dir = tempfile.mkdtemp()
    # temporary procedure
    tmp_dir = os.getcwd() + "/tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        print >> sys.stdout, "Creating temporary directory: " +  tmp_dir

    # preparing batch job engine
    if args.engine == "dsub":
        factory = Dsub_factory()
    else:
        factory = Awsub_factory()

    batch_engine = Batch_engine(factory, param_conf.get("general", "instance_option"))

    ##########
    # RNA
    if args.analysis_type == "rna":
        pass

    ##########
    # DNA
    elif args.analysis_type == "dna":
        
        # BWA stage
        from tasks.bwa_alignment import *
        bwa_alignment_task = Bwa_alignment(args.output_dir, tmp_dir, sample_conf, param_conf)
        p1 = multiprocessing.Process(target = batch_engine.execute, args = (bwa_alignment_task,))
        p1.start()
        p1.join()
        
        # Mutation call stage
        from tasks.mutation_call import *
        mutation_call_task = Mutation_call(args.output_dir, tmp_dir, sample_conf, param_conf)
        p1 = multiprocessing.Process(target = batch_engine.execute, args = (mutation_call_task,))
        p1.start()
        p1.join()
        
        # QC stage
        from tasks.genomon_qc import *
        qc_task = Genomon_qc(args.output_dir, tmp_dir, sample_conf, param_conf, run_conf)
        proc_qc = multiprocessing.Process(target = batch_engine.execute, args = (qc_task,))
        proc_qc.start()
        proc_qc.join()
        
        # pmsignature
        from tasks.pmsignature import *
        pmsignature_task = Pmsignature(args.output_dir, tmp_dir, sample_conf, param_conf, run_conf)
        proc_pmsignature = multiprocessing.Process(target = batch_engine.execute, args = (pmsignature_task,))
        proc_pmsignature.start()
        proc_pmsignature.join()
        
    # paplot stage
    from tasks.paplot import *
    paplot_task = Paplot(args.output_dir, tmp_dir, sample_conf, param_conf, run_conf)
    proc_paplot = multiprocessing.Process(target = batch_engine.execute, args = (paplot_task,))
    proc_paplot.start()
    proc_paplot.join()
    
