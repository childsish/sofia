from subprocess import Popen, PIPE
from paths import cluster, qsub, qdel, qstat

class ClusterJob:
    def __init__(self, exe, args, taskid, logdir):
        self.exe = exe
        self.args = args
        self.taskid = taskid
        self.jobid = None
        self.logdir = logdir

    def __del__(self):
        if self.jobid != None and self.isAlive():
            prc = Popen([cluster.qdel, self.jobid], stdout=PIPE, stderr=PIPE)
            stdout, stderr = prc.communicate()
            sys.stdout.write(stdout)
            sys.stderr.write(stderr)

    def start(self):
        prc = Popen([cluster.qsub,
                     '-o', self.logdir,
                     '-e', self.logdir,
                     '-N', self.exe,
                     '-v', self.args,
                     cluster.wrapper],
                    stdout=PIPE, stderr=PIPE)
        stdout, stderr = prc.communicate()
        if stderr != '':
            raise Exception(stderr)
        self.jobid = stdout.strip()

    def isAlive(self):
        if self.jobid == None:
            return False
        prc = Popen([cluster.qstat, self.jobid], stdout=PIPE, stderr=PIPE)
        stdout, stderr = prc.communicate()

        return stderr.strip() != 'qstat: Unknown Job Id ' + self.jobid

