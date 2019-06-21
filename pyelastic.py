import pyone, pprint, one
import time

class PyElastic:

    def __init__(self):
        self._server = pyone.OneServer("http://192.168.1.10:2633/RPC2", session="oneadmin:opennebula")
        self.upper = 0.7
        self.lower = 0.3
        self.times = 0
        self.minimal = 10
        self.minimal_vms = 1
        self.running_vms = 0
        self.monitor_period = 1

    def initialize(self):
        enabled_hosts = [9, 10]
        host_pool = []
        for host in self._server.hostpool.info().HOST:
            if host.ID in enabled_hosts:
                print("Getting Host: " + str(host.ID) + " -> " + host.NAME)
                host_dict = {'ID': host.ID, 'NAME': host.NAME, 'vm':None}
                host_pool.append(host_dict)
        self._host_pool = host_pool
        self.addVM()

    def monitoring(self):
        while(True):
            max_cpu = 0
            used_cpu = 0

            for host in self._host_pool:
                if host['vm'] != None:
                    host_info = self._server.host.info(host['ID']).HOST_SHARE
                    #print("HOST: " + host.NAME + " -> " + str(host_info.USED_CPU))
                    used_cpu += host_info.USED_CPU
                    max_cpu += host_info.MAX_CPU
            self.log('running_vms', self.running_vms)
            self.log('max_cpu', max_cpu)
            totalCpu = used_cpu/max_cpu
            self.log('cpu', totalCpu)
            self.verify(totalCpu)
            time.sleep(self.monitor_period)

    def verify(self, totalCpu):
        if (totalCpu > self.upper):
            if (self.times < 0): # reset if in other way
                self.times = 0
            self.times+=1
            if (self.times == self.minimal):
                self.addVM()
        elif (totalCpu < self.lower):
            if (self.times > 0): # reset if in other way
                self.times = 0
            self.times-=1
            if (abs(self.times) == self.minimal):
                self.removeVM()
        else: # reset when between threasholds
            self.times = 0

    def addVM(self):
        template = one.Template(1, self._server)
        vm = one.Vm(template, self._server)
        for host in self._host_pool:
            if host['vm'] == None:
                vm_id = vm.allocate(host['ID'])
                host['vm'] = vm
                self.log('addedVM HOST_ID', host['ID'])
                self.log('addedVM VM_ID', vm_id)
                self.running_vms += 1
                break

    def removeVM(self):
        self.log('removingVM', None)
        if (self.running_vms > self.minimal_vms):
            # remove last allocated VM
            last_host = None
            for host in self._host_pool:
                if host['vm'] == None:
                    break
                last_host = host

            if last_host != None:
                vm = last_host['vm']
                self.log('removedVM', vm._identifier)
                vm.deallocate()
                self.running_vms -= 1
                last_host['vm'] = None

    def log(self, label, value):
        print(str(int(time.time())) + ',' + label + ',' + str(value))


if __name__ == "__main__":
    py = PyElastic()
    py.initialize()
    py.monitoring()

