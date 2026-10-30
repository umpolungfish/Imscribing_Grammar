from engine_runtime import UniversalEngineRuntime
vm = UniversalEngineRuntime()
vm.load_log()
vm.run(steps=5000)
vm.inject_paradox(42)
vm.show_stats()
print('Type vm.run(10000) to continue, or vm.inject_paradox(N) anytime')
