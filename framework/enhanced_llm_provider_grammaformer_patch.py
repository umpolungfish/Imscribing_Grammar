            load_kwargs["local_files_only"] = True
            # ── GrammaFormer detection ──────────────────────────────────
            _cfg_path = Path(self.model_path) / "config.json"
            _is_grammaformer = False
            if _cfg_path.exists():
                try:
                    _cfg = __import__("json").loads(_cfg_path.read_text())
                    _is_grammaformer = _cfg.get("_grammaformer_marker") == "grammaformer_v1"
                except Exception:
                    pass

            if _is_grammaformer:
                logger.info("Detected GrammaFormer model; loading via grammaformer.py ...")
                # Ensure framework is importable
                _root = str(Path(__file__).resolve().parent.parent)
                if _root not in __import__("sys").path:
                    __import__("sys").path.insert(0, _root)
                from framework.grammaformer import GrammaFormerForCausalLM
                mdl = GrammaFormerForCausalLM.from_pretrained(self.model_path)
                device = device_map if isinstance(device_map, str) else (
                    list(device_map.values())[0] if device_map else "cpu")
                if device != "cpu":
                    mdl = mdl.to(device)
                mdl.eval()
                logger.info(f"GrammaFormer loaded (device={device}).")
            else:
                try:
                    mdl = AutoModelForCausalLM.from_pretrained(self.model_path, **load_kwargs)
                    logger.info(f"Local model loaded (device_map={device_map}).")
                except Exception as e:
                    logger.warning(f"Load failed ({e}); retrying on CPU.")
                    load_kwargs["device_map"] = "cpu"
                    load_kwargs["dtype"] = torch.float32
                    load_kwargs.pop("quantization_config", None)
                    mdl = AutoModelForCausalLM.from_pretrained(self.model_path, **load_kwargs)
                    logger.info("Local model loaded on CPU.")
                mdl.eval()