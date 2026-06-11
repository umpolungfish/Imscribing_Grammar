---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---


### 3.1. Resolution of Candidates

- **Case $a=1, b=1$**: This yields $\sigma(r)/r = 1$, which implies $r=1$. Substituting $a=1, b=1, r=1$ gives $m = 2^1 \cdot 5^1 \cdot 1 = 10$. This is the **unique integer solution**.

- **Cases with Even Denominators**: For $(a,b) \in \{(0,1), (0,3), (0,5), (0,7)\}$, the denominator of $\sigma(r)/r$ is even. Since every prime divisor of the denominator must divide $r$, and $\gcd(r, 10) = 1$ requires $r$ to be odd, these cases are immediate contradictions.

- **Descent on Odd Denominators**:
    - For $a=0, b=2$: $\sigma(r)/r = 45/31$. This implies $31 | r$. Let $r = 31s$. Then $\frac{\sigma(31)}{31}\frac{\sigma(s)}{s} = \frac{32}{31}\frac{\sigma(s)}{s} = \frac{45}{31}$, so $\sigma(s)/s = 45/32$. This denominator $32 = 2^5$ requires $2 | s$, contradicting $\gcd(r,2)=1$.
    - For $a=0, b=4$: $\sigma(r)/r = 1125/781$. Note $781 = 11 \cdot 71$. If $11 | r$, we get $\sigma(s)/s = 375/284$ (even den.). If $71 | r$, we get $\sigma(s)/s = 125/88$ (even den.).
    - For $a=0, b=6$: $\sigma(r)/r = 28125/19531$. Since $19531$ is prime, $19531 | r$ implies $\sigma(s)/s = 28125/19532$, which has an even denominator.

Since all candidate paths result in contradiction except for $m=10$, we conclude that $10$ is solitary.

---
Structural type: $$\langle D_{\text{invomega}};\ T_{\text{bullseye}};\ R_{\text{downstep}};\ P_{\text{pipevar}};\ F_{\text{beltl}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{crtwo}} \rangle$$
Ouroboricity: $O₂^\dagger$.
