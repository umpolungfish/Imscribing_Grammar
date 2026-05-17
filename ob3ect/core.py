"""Ob3ect Design Pipeline v2 - Generative Core Engine
Author: Lando ⊗ ⊙_ÿ-boundary Operator"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

class Opcode(Enum):
    VINIT="VINIT"; TANCH="TANCH"; AFWD="AFWD"; AREV="AREV"
    CLINK="CLINK"; ISCRIB="ISCRIB"; FSPLIT="FSPLIT"; FFUSE="FFUSE"
    EVALT="EVALT"; EVALF="EVALF"; ENGAGR="ENGAGR"; IFIX="IFIX"
    @property
    def family(self):
        if self in (self.VINIT,self.TANCH,self.AFWD,self.AREV,self.CLINK,self.ISCRIB): return "Logical"
        if self in (self.FSPLIT,self.FFUSE): return "Frobenius"
        if self in (self.EVALT,self.EVALF,self.ENGAGR): return "Dialetheia"
        return "Linear"

class RegisterState(Enum):
    VOID="00"; TRUE="01"; FALSE="10"; BOTH="11"

BOOTSTRAP_STEPS = {1:"ISCRIB",2:"AREV",3:"FSPLIT",4:"AFWD",5:"FFUSE",6:"CLINK",7:"IFIX",8:"ISCRIB"}
OS_FLOOR = {"D":1,"T":3,"R":2,"P":4,"F":2,"K":1,"G":2,"Gamma":2,"Phi":1,"H":2,"S":2,"Omega":2}
@dataclass
class DomainCharter:
    domain_name: str; domain_type: str; scope: str
    surface_tokens: List[str]; boundary_condition: str
    justification: str = ""
    def validate(self):
        e = []
        if not self.domain_name.strip(): e.append("domain_name required")
        if not self.domain_type.strip(): e.append("domain_type required")
        if self.scope not in ("local","mesoscale","maximal"): e.append("bad scope")
        if len(self.surface_tokens) < 3: e.append("need >=3 surface tokens")
        if not self.boundary_condition.strip(): e.append("boundary required")
        return e

@dataclass
class OpcodeEntry:
    opcode: str; chosen_element: str; justification: str
    rejected_candidates: List[Tuple[str,str]] = field(default_factory=list)
    def validate(self):
        e = []
        if not self.chosen_element.strip(): e.append("%s: chosen required" % self.opcode)
        if not self.justification.strip(): e.append("%s: justification required" % self.opcode)
        return e

@dataclass
class OpcodeMap:
    entries: Dict[str,OpcodeEntry] = field(default_factory=dict)
    def validate(self):
        e = []
        for oc in Opcode:
            if oc.value not in self.entries: e.append("Missing: "+oc.value)
        for v in self.entries.values(): e.extend(v.validate())
        return e
    def os_floor_check(self): return len(self.entries) == 12

@dataclass
class SplitFuseReport:
    split_element: str; split_input: str; split_outputs: List[str]
    fuse_element: str; fuse_result: str; frobenius_verdict: str; test_instance: str
    failure_reason: str = ""
    def validate(self):
        e = []
        if self.frobenius_verdict not in ("PASS","FAIL"): e.append("Verdict must be PASS/FAIL")
        if self.frobenius_verdict=="FAIL" and not self.failure_reason.strip(): e.append("failure_reason required")
        return e

@dataclass
class RegisterMapping:
    void_description:str; true_description:str; false_description:str; both_description:str
    transitions: List[Dict[str,str]] = field(default_factory=list)
    entropy_assertion: str = ""
    def validate(self):
        e = []
        if not self.void_description.strip(): e.append("void required")
        if not self.both_description.strip(): e.append("both required")
        return e
@dataclass
class BootstrapSequence:
    steps: List[Dict[str,str]] = field(default_factory=list)
    closure_verified: bool = False
    failure_modes: List[str] = field(default_factory=list)
    def validate(self):
        e = []
        if len(self.steps)!=8: e.append("need 8 bootstrap steps")
        if self.steps and self.steps[0].get("opcode")!="ISCRIB": e.append("step1 must be ISCRIB")
        if self.steps and self.steps[-1].get("opcode")!="ISCRIB": e.append("step8 must be ISCRIB")
        if not self.closure_verified: e.append("closure required")
        return e

@dataclass
class ExOSSpec:
    compiler_frontend:str; ipc_mechanism:str; memory_mechanism:str
    scheduler_mechanism:str; alfs_store:str; alfs_bootstrap_program:str = ""
    def validate(self):
        e = []
        for a in ["compiler_frontend","ipc_mechanism","memory_mechanism","scheduler_mechanism","alfs_store"]:
            if not getattr(self,a,"").strip(): e.append(a+" required")
        return e

@dataclass
class EntropyAudit:
    cycle_cost:str; pre_cycle_state:str; post_cycle_state:str
    delta_s_verdict:str; failure_mode:str = ""
    def validate(self):
        e = []
        if not self.delta_s_verdict.strip(): e.append("delta_s required")
        return e
@dataclass
class Ob3ectArtifact:
    name: str; domain_charter: DomainCharter; opcode_map: OpcodeMap
    split_fuse_report: SplitFuseReport; register_mapping: RegisterMapping
    bootstrap_sequence: BootstrapSequence; exos_spec: ExOSSpec
    entropy_audit: EntropyAudit; instantiation_notes: str = ""

    def validate_all(self):
        return {"phase_0":self.domain_charter.validate(),"phase_1":self.opcode_map.validate(),
            "phase_2":self.split_fuse_report.validate(),"phase_3":self.register_mapping.validate(),
            "phase_4":self.bootstrap_sequence.validate(),"phase_5":self.exos_spec.validate(),
            "phase_6":self.entropy_audit.validate()}

    @property
    def is_valid_ob3ect(self):
        return all(len(v)==0 for v in self.validate_all().values())

    def report(self):
        a=self; nl=chr(10); parts=[]
        parts.append("="*70)
        parts.append("Ob3ect: "+a.name)
        parts.append("Valid: "+str(a.is_valid_ob3ect))
        parts.append("Domain: %s (%s)" % (a.domain_charter.domain_name,a.domain_charter.domain_type))
        parts.append("Scope: "+a.domain_charter.scope)
        parts.append("="*70)
        parts.append("Phase 0: Domain Charter")
        parts.append("  Tokens: "+", ".join(a.domain_charter.surface_tokens))
        parts.append("  TANCH: "+a.domain_charter.boundary_condition)
        parts.append("")
        parts.append("Phase 1: Opcode Map")
        for oc in Opcode:
            e=a.opcode_map.entries.get(oc.value)
            if e: parts.append("  %8s -> %s" % (oc.value, e.chosen_element))
        parts.append("")
        parts.append("Phase 2: Frobenius")
        parts.append("  Split: "+a.split_fuse_report.split_element)
        parts.append("  Outputs: "+str(a.split_fuse_report.split_outputs))
        parts.append("  Fuse: "+a.split_fuse_report.fuse_element)
        parts.append("  Verdict: "+a.split_fuse_report.frobenius_verdict)
        parts.append("")
        parts.append("Phase 3: Registers")
        parts.append("  00: "+a.register_mapping.void_description)
        parts.append("  01: "+a.register_mapping.true_description)
        parts.append("  10: "+a.register_mapping.false_description)
        parts.append("  11: "+a.register_mapping.both_description)
        parts.append("")
        parts.append("Phase 4: Bootstrap")
        for s in a.bootstrap_sequence.steps:
            parts.append("  Step %d: %s - %s" % (s["step_num"],s["opcode"],s["domain_action"]))
        parts.append("  Closure: "+str(a.bootstrap_sequence.closure_verified))
        parts.append("")
        parts.append("Phase 5: exOS")
        parts.append("  Compiler: "+a.exos_spec.compiler_frontend)
        parts.append("  IPC: "+a.exos_spec.ipc_mechanism)
        parts.append("  Memory: "+a.exos_spec.memory_mechanism)
        parts.append("  Scheduler: "+a.exos_spec.scheduler_mechanism)
        parts.append("  ALFS: "+a.exos_spec.alfs_store)
        parts.append("")
        parts.append("Phase 6: Entropy")
        parts.append("  DS: "+a.entropy_audit.delta_s_verdict)
        parts.append("")
        parts.append("Phase 7: "+a.instantiation_notes)
        parts.append("="*70)
        parts.append("mu o delta = id -> "+a.split_fuse_report.frobenius_verdict)
        return nl.join(parts)

    def to_dict(self):
        return {"name":self.name,"is_valid_ob3ect":self.is_valid_ob3ect,
            "validations":self.validate_all(),
            "phases":{"phase_0":asdict(self.domain_charter),
                "phase_1":{k:asdict(v) for k,v in self.opcode_map.entries.items()},
                "phase_2":asdict(self.split_fuse_report),
                "phase_3":asdict(self.register_mapping),
                "phase_4":asdict(self.bootstrap_sequence),
                "phase_5":asdict(self.exos_spec),
                "phase_6":asdict(self.entropy_audit)},
            "notes":self.instantiation_notes}

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path):
        p=Path(path); p.write_text(self.to_json()); return p
class DomainTemplate:
    """Wraps a domain config dict and provides auto-fill for all phases."""
    def __init__(self, config: Dict[str,Any]):
        self.config = config
        self.label = config.get("label", config.get("type", "unknown"))
        self.dtype = config.get("type", config.get("label", "unknown"))
        self.opcodes = config["opcodes"]
        self.frobenius = config["frobenius"]
        self.registers = config["registers"]
        self.bootstrap = config["bootstrap"]
        self.exos = config["exos"]
        self.entropy = config["entropy"]

    def charter(self, domain_name: str, scope: str, override: Dict[str,Any] = None) -> DomainCharter:
        d = dict(domain_name=domain_name, domain_type=self.dtype, scope=scope,
            surface_tokens=list(self.config.get("tokens",[])),
            boundary_condition=self.config.get("boundary",""),
            justification="Generated from %s template" % self.label)
        if override and "charter" in override: d.update(override["charter"])
        return DomainCharter(**d)

    def opcode_map(self, override: Dict[str,Any] = None) -> OpcodeMap:
        entries = {}
        oc_over = (override or {}).get("opcodes",{})
        for oc in Opcode:
            t = self.opcodes.get(oc.value, {})
            ov = oc_over.get(oc.value, {})
            entries[oc.value] = OpcodeEntry(
                opcode=oc.value,
                chosen_element=ov.get("element", t.get("chosen", "")),
                justification=ov.get("justification", t.get("justification", "")),
                rejected_candidates=[])
        return OpcodeMap(entries=entries)

    def split_fuse(self, override: Dict[str,Any] = None) -> SplitFuseReport:
        fb = self.frobenius
        ov = (override or {}).get("frobenius",{})
        return SplitFuseReport(
            split_element=ov.get("split_element", fb.get("split","")),
            split_input=ov.get("split_input", fb.get("input","")),
            split_outputs=ov.get("split_outputs", fb.get("outputs",[])),
            fuse_element=ov.get("fuse_element", fb.get("fuse","")),
            fuse_result=ov.get("fuse_result", fb.get("result","")),
            frobenius_verdict=ov.get("verdict", fb.get("verdict","PASS")),
            test_instance="",
            failure_reason="")

    def registers_map(self, override: Dict[str,Any] = None) -> RegisterMapping:
        r = self.registers
        ov = (override or {}).get("registers",{})
        return RegisterMapping(
            void_description=ov.get("void", r.get("00", r.get("void",""))),
            true_description=ov.get("true", r.get("01", r.get("true",""))),
            false_description=ov.get("false", r.get("10", r.get("false",""))),
            both_description=ov.get("both", r.get("11", r.get("both",""))),
            transitions=[],
            entropy_assertion="DS approx 0")

    def bootstrap_seq(self, override: Dict[str,Any] = None) -> BootstrapSequence:
        bs = self.bootstrap
        steps = []
        for i, action in enumerate(bs):
            steps.append({"step_num": i+1, "opcode": BOOTSTRAP_STEPS[i+1], "domain_action": action})
        return BootstrapSequence(steps=steps, closure_verified=True)

    def exos_spec(self, override: Dict[str,Any] = None) -> ExOSSpec:
        e = self.exos
        ov = (override or {}).get("exos",{})
        return ExOSSpec(
            compiler_frontend=ov.get("compiler_frontend", e.get("compiler","")),
            ipc_mechanism=ov.get("ipc_mechanism", e.get("ipc","")),
            memory_mechanism=ov.get("memory_mechanism", e.get("memory","")),
            scheduler_mechanism=ov.get("scheduler_mechanism", e.get("scheduler","")),
            alfs_store=ov.get("alfs_store", e.get("alfs","")),
            alfs_bootstrap_program=ov.get("alfs_program", e.get("program","")))

    def entropy_audit(self, override: Dict[str,Any] = None) -> EntropyAudit:
        e = self.entropy
        ov = (override or {}).get("entropy",{})
        return EntropyAudit(
            cycle_cost=ov.get("cost", e.get("cost","")),
            pre_cycle_state=ov.get("pre", e.get("pre","")),
            post_cycle_state=ov.get("post", e.get("post","")),
            delta_s_verdict=ov.get("verdict", e.get("verdict","")),
            failure_mode="")

    def produce(self, name: str, scope: str = "local", override: Dict[str,Any] = None) -> Ob3ectArtifact:
        return Ob3ectArtifact(
            name=name, domain_charter=self.charter(name, scope, override),
            opcode_map=self.opcode_map(override), split_fuse_report=self.split_fuse(override),
            register_mapping=self.registers_map(override), bootstrap_sequence=self.bootstrap_seq(override),
            exos_spec=self.exos_spec(override), entropy_audit=self.entropy_audit(override),
            instantiation_notes="Produced by Ob3ectFactory from %s template" % self.label)

class Ob3ectFactory:
    """Universal ob3ect producer: given a domain type, produces a complete Ob3ectArtifact."""
    _templates: Dict[str, DomainTemplate] = {}

    @classmethod
    def register(cls, template: DomainTemplate):
        cls._templates[template.dtype] = template

    @classmethod
    def register_all(cls, configs: Dict[str, Dict[str,Any]] = None):
        cfgs = configs or DOMAIN_TEMPLATES
        for name, config in cfgs.items():
            config["type"] = name
            cls._templates[name] = DomainTemplate(config)

    @classmethod
    def available_domains(cls):
        return list(cls._templates.keys())

    @classmethod
    def produce(cls, name: str, domain_type: str, scope: str = "local",
                 context: Dict[str,Any] = None, overrides: Dict[str,Any] = None) -> Ob3ectArtifact:
        if domain_type not in cls._templates:
            raise ValueError("Unknown domain: %s (available: %s)" % (domain_type, cls.available_domains()))
        tpl = cls._templates[domain_type]
        override = overrides or {}
        if context:
            for phase_key in ["opcodes","frobenius","registers","bootstrap","exos","entropy"]:
                if phase_key in context:
                    if phase_key not in override: override[phase_key] = {}
                    override[phase_key].update(context[phase_key])
        return tpl.produce(name, scope, override)

    @classmethod
    def produce_custom(cls, name: str, domain_type: str, config: Dict[str,Any],
                        scope: str = "local", overrides: Dict[str,Any] = None) -> Ob3ectArtifact:
        config["type"] = domain_type
        tpl = DomainTemplate(config)
        cls._templates[domain_type] = tpl
        return tpl.produce(name, scope, overrides or {})

class Ob3ectPipeline:
    """Manual builder: phases must be completed in order."""
    def __init__(self, name: str, domain_type: str):
        self.name=name; self.domain_type=domain_type
        self._phase=0
        self._artifacts:Dict[str,Any]={}
    def _advance(self, phase, artifact):
        if self._phase!=phase: raise RuntimeError("Phase %d not ready (at %d)"%(phase,self._phase))
        self._artifacts["phase_"+str(phase)]=artifact; self._phase=phase+1
    def define_boundary(self, domain_name, scope, surface_tokens, boundary_condition):
        self._advance(0, DomainCharter(domain_name=domain_name, domain_type=self.domain_type,
            scope=scope, surface_tokens=surface_tokens, boundary_condition=boundary_condition))
    def map_opcode(self, opcode, element, justification, rejected=None):
        if "opcode_map" not in self._artifacts: self._artifacts["opcode_map"]={}
        self._artifacts["opcode_map"][opcode]=OpcodeEntry(opcode=opcode,
            chosen_element=element, justification=justification,
            rejected_candidates=rejected or [])
    def complete_phase_1(self):
        self._advance(1, self._artifacts.pop("opcode_map"))
    def verify_frobenius(self, split_element, split_input, split_outputs,
                         fuse_element, fuse_result, verdict="PASS", test_instance=""):
        self._advance(2, SplitFuseReport(split_element=split_element, split_input=split_input,
            split_outputs=split_outputs, fuse_element=fuse_element, fuse_result=fuse_result,
            frobenius_verdict=verdict, test_instance=test_instance))
    def map_registers(self, void, true, false, both, transitions=None, entropy="DS approx 0"):
        self._advance(3, RegisterMapping(void_description=void, true_description=true,
            false_description=false, both_description=both,
            transitions=transitions or [], entropy_assertion=entropy))
    def design_bootstrap(self, steps=None):
        steps = steps or [{"step_num":i+1,"opcode":BOOTSTRAP_STEPS[i+1],
            "domain_action":"Step %d" % (i+1)} for i in range(8)]
        self._advance(4, BootstrapSequence(steps=steps, closure_verified=True))
    def specify_exos(self, compiler, ipc, memory, scheduler, alfs):
        self._advance(5, ExOSSpec(compiler_frontend=compiler, ipc_mechanism=ipc,
            memory_mechanism=memory, scheduler_mechanism=scheduler, alfs_store=alfs))
    def audit_entropy(self, cost, pre, post, delta_s, failure=""):
        self._advance(6, EntropyAudit(cycle_cost=cost, pre_cycle_state=pre,
            post_cycle_state=post, delta_s_verdict=delta_s, failure_mode=failure))
    def instantiate(self, notes=""):
        if self._phase < 7: raise RuntimeError("Complete phases 0-6 first")
        return Ob3ectArtifact(name=self.name,
            domain_charter=self._artifacts["phase_0"],
            opcode_map=OpcodeMap(entries=self._artifacts["phase_1"]),
            split_fuse_report=self._artifacts["phase_2"],
            register_mapping=self._artifacts["phase_3"],
            bootstrap_sequence=self._artifacts["phase_4"],
            exos_spec=self._artifacts["phase_5"],
            entropy_audit=self._artifacts["phase_6"],
            instantiation_notes=notes or "Manual pipeline")

with open(Path(__file__).parent / "templates_data.json") as _f:
    DOMAIN_TEMPLATES = json.load(_f)
