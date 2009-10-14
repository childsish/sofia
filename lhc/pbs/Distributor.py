class Distributer:

    SLEEP = 30.0

    def __init__(self, max_jobs, sleep=SLEEP):
        """ Initialise the Distributer to run, at most, max_jobs and wait sleep
           sleep seconds between checking if any jobs are finished.
        """
        self.__max_jobs = max_jobs
        self.__inputs = []
        self.__sleep = sleep

    def distribute(self, n_jobs, indir, args):
        """ Distributes the n_jobs "super jobs" on the cluster. The executable
           specified in args[0] is run on each file in indir. Any occurance of
           the string "@@" in the arguments is replaced with the file name.
        """
        timestamp = time.strftime('%y%m%d_%H%M%S')

        # Create timestamped job and log directories
        t_jobdir = os.path.join(cluster.jobdir,
                                os.path.basename(args[0]),
                                timestamp)
        os.makedirs(t_jobdir)
        t_logdir = os.path.join(cluster.logdir,
                                os.path.basename(args[0]),
                                timestamp)
        os.makedirs(t_logdir)

        # Partition the jobs into n_jobs jobs.
        tmpdir = self.__allocate(indir, n_jobs)

        # Create all the jobs.
        filenames = sorted(os.listdir(tmpdir))
        jobs = [ClusterJob(os.path.basename(args[0]),
                           self.formatArgs(args,
                             lc_jobdir=t_jobdir,
                             lc_taskid=i,
                             lc_filename=os.path.join(tmpdir, filenames[i])),
                           i,
                           t_logdir)
                for i in xrange(len(filenames))]
        del filenames

        # Track the running jobs in an array.
        running_jobs = self.__max_jobs * [None]
        if self.__max_jobs == 0:
            running_jobs = len(jobs) * [None]

        # Submit jobs to the cluster.
        current_job = 0
        started_jobs = 0
        stopped_jobs = 0
        while stopped_jobs < len(jobs):
            if running_jobs[current_job] != None and\
               not jobs[running_jobs[current_job]].isAlive():
                when = time.strftime('%d/%m/%y %H:%M:%S')
                print ' stopping job %d (%s)'%(running_jobs[current_job],when)
                stopped_jobs += 1
                running_jobs[current_job] = None

            if running_jobs[current_job] == None and\
               started_jobs < len(jobs):
                when = time.strftime('%d/%m/%y %H:%M:%S')
                print 'starting job %d (%s)'%(started_jobs,when)
                running_jobs[current_job] = started_jobs
                jobs[started_jobs].start()
                started_jobs += 1

            current_job += 1
            if current_job >= len(running_jobs):
                current_job = 0
                time.sleep(self.__sleep)

        # Cleanup
        for filename in os.listdir(tmpdir):
            os.remove(os.path.join(tmpdir, filename))
        os.rmdir(tmpdir)

        return t_jobdir

    def formatArgs(self, args, **kw):
        """ Formats the arguments into a single string to be passed to the
           argument of qsub that sets the environment variable. I don't know of
           any other way to send arguments to a script on the cluster.
        """
        args = ['lc_arg%2d='%(i, args[i]) for i in xrange(len(args))]
        args += [k + '=' + str(v) for k, v in kw.iteritems()]
        return ','.join(args)

    def __allocate(self, indir, n_jobs):
        """ Partitions the jobs into "super jobs". If no number is specified,
           the same number of super jobs as jobs is created effectively changing
           nothing.
        """
        filenames = os.listdir(indir)
        if n_jobs == 0 or n_jobs > len(filenames):
            n_jobs = len(filenames)

        tmpdir = tempfile.mkdtemp(dir=os.path.join(os.environ['HOME'], 'tmp'))
        for i in xrange(n_jobs):
            outfile = open(os.path.join(tmpdir, str(i)), 'w')
            outfile.write(
             '\n'.join([os.path.join(indir, filename)
                        for filename in filenames[(i+0)*len(filenames)/n_jobs:\
                                                  (i+1)*len(filenames)/n_jobs]])
            )
            outfile.close()

        return tmpdir

