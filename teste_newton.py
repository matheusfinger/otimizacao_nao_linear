# -*- coding: utf-8 -*-
import sys
import sympy as sp
import math
from unidimensionais.newton import newton
from utils import criar_phi_parametrizada

sys.stdout.reconfigure(encoding='utf-8')

# ──────────────────────────────────────────────────────────────────────────────
# Função original: f(x, y) = (x² - 5)² + (y² - 5)²
# Ponto inicial  : x0 = [0, 0]
# Direção        : d  = [1, 1]
#
# Parametrização: phi(a) = 2(a² - 5)² = 2a⁴ - 20a² + 50
# Mínimo        : a* = sqrt(5) ≈ 2.2360679...   →   floor(a*) = 2
# ──────────────────────────────────────────────────────────────────────────────

x, y = sp.symbols('x y')
f_sym = (x**2 - 5)**2 + (y**2 - 5)**2

pontos   = [0.0, 0.0]
direcao  = [1.0, 1.0]
simbolos = [x, y]

_, phi_sym, expressoes = criar_phi_parametrizada(pontos, direcao, simbolos, f_sym)

alpha_otimo = math.sqrt(5)
alpha0_1 = float(math.floor(alpha_otimo))        # floor(a*) = 2
alpha0_2 = float(math.floor(alpha_otimo) + 10)   # floor(a*) + 10 = 12

tol      = 1e-6
max_iter = 100

# ── Cabeçalho geral ───────────────────────────────────────────────────────────
sep = "=" * 76
print(sep)
print(f"{'METODO DE NEWTON  -  Busca Unidimensional':^76}")
print(sep)
print(f"\nFuncao original : f(x,y) = (x^2 - 5)^2 + (y^2 - 5)^2")
print(f"Parametrizacao  : {', '.join(str(e) for e in expressoes)}")
print(f"phi(a)          = {phi_sym}")
print(f"\na* = sqrt(5) = {alpha_otimo:.8f}")
print(f"phi(a*) = {2*(alpha_otimo**2 - 5)**2:.2e}  (aprox. 0)")
print(f"floor(a*) = {int(alpha0_1)}   ->   a0 Teste 1 = {int(alpha0_1)}")
print(f"floor(a*) + 10 = {int(alpha0_2)}   ->   a0 Teste 2 = {int(alpha0_2)}")

# ── Função auxiliar para imprimir tabela ──────────────────────────────────────
def imprimir_tabela(resultado, alpha0):
    h1, h2, h3, h4, h5 = "Iter", "a", "phi(a)", "phi'(a)", "phi''(a)"
    cab = f"{h1:^5} {h2:^16} {h3:^16} {h4:^16} {h5:^14}"
    print(f"\n{sep}")
    print(f"  a0 = {alpha0:.1f}  |  Tolerancia = {tol:.0e}  |  Max iter = {max_iter}")
    print(sep)
    print(cab)
    print("-" * 76)
    for it in resultado['historico']:
        print(f"{it['iter']:^5} "
              f"{it['alpha']:^16.8f} "
              f"{it['phi_alpha']:^16.8f} "
              f"{it['phi_prime']:^16.8f} "
              f"{it['phi_double_prime']:^14.6f}")
    print("-" * 76)
    status = "CONVERGIU" if resultado['convergiu'] else "NAO CONVERGIU"
    print(f"  {status}  |  Iteracoes: {resultado['iteracoes']}  |  a* ~= {resultado['alpha']:.8f}")
    print(f"  phi(a*) = {resultado['phi_alpha']:.6e}")

# ── Teste 1: a0 = floor(a*) = 2 ───────────────────────────────────────────────
r1 = newton(phi_sym, alpha0_1, tol=tol, max_iter=max_iter)
imprimir_tabela(r1, alpha0_1)

# ── Teste 2: a0 = floor(a*) + 10 = 12 ────────────────────────────────────────
r2 = newton(phi_sym, alpha0_2, tol=tol, max_iter=max_iter)
imprimir_tabela(r2, alpha0_2)

print(f"\n{sep}")
print(f"  Resumo: a* = sqrt(5) = {alpha_otimo:.8f}")
print(f"  Teste 1 (a0 = {int(alpha0_1):2d}):  {r1['iteracoes']:3d} iteracoes")
print(f"  Teste 2 (a0 = {int(alpha0_2):2d}):  {r2['iteracoes']:3d} iteracoes")
print(sep)
