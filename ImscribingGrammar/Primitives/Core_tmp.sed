/theorem o_inf_requires_P_pm_sym/,^  cases phi <;> cases pol <;> simp \[ouroboricityTier\] at h$ {
  s/^  cases phi <;> cases pol <;> simp \[ouroboricityTier\] at h$/  cases pol <;> (\n    try rfl;\n    all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)\n  )/
}
