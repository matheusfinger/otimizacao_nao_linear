import numpy as np

def bissecao(phi, a, b, tol=1e-6, max_iter=100):
    """
    Método da bisseção para encontrar o mínimo de φ(α).
    
    Parâmetros:
    phi: função φ(α) unidimensional
    a: limite inferior do intervalo
    b: limite superior do intervalo
    tol: tolerância para o critério de parada
    max_iter: número máximo de iterações
    
    Retorna:
    dict com:
        - alpha: valor ótimo de α
        - phi_alpha: valor de φ(α*)
        - iteracoes: número de iterações realizadas
        - historico: lista com histórico das iterações
        - convergiu: booleano indicando se convergiu
    """
    
    # Inicialização
    alpha_a = a
    alpha_b = b
    phi_a = phi(alpha_a)
    phi_b = phi(alpha_b)
    
    historico = []
    
    # Verifica se a função é unimodal no intervalo
    # Se φ(a) > φ(b), o mínimo está mais perto de b, então inverte
    if phi_a > phi_b:
        alpha_a, alpha_b = alpha_b, alpha_a
        phi_a, phi_b = phi_b, phi_a
    
    for k in range(max_iter):
        # Ponto médio
        alpha_c = (alpha_a + alpha_b) / 2
        phi_c = phi(alpha_c)
        
        # Registra iteração
        historico.append({
            'iter': k + 1,
            'a': alpha_a,
            'b': alpha_b,
            'c': alpha_c,
            'phi_a': phi_a,
            'phi_b': phi_b,
            'phi_c': phi_c,
            'intervalo': alpha_b - alpha_a
        })
        
        # Critério de parada
        if abs(alpha_b - alpha_a) < tol:
            alpha_otimo = (alpha_a + alpha_b) / 2
            return {
                'alpha': alpha_otimo,
                'phi_alpha': phi(alpha_otimo),
                'iteracoes': k + 1,
                'historico': historico,
                'convergiu': True
            }
        
        # Determina novo intervalo
        if phi_c < phi_a:  # Mínimo está entre c e b
            alpha_a, phi_a = alpha_c, phi_c
        elif phi_c < phi_b:  # Mínimo está entre a e c
            alpha_b, phi_b = alpha_c, phi_c
        else:  # phi_c é maior que ambos, mínimo está em c
            alpha_otimo = alpha_c
            return {
                'alpha': alpha_otimo,
                'phi_alpha': phi_c,
                'iteracoes': k + 1,
                'historico': historico,
                'convergiu': True
            }
    
    # Se chegou aqui, não convergiu dentro do número máximo de iterações
    alpha_otimo = (alpha_a + alpha_b) / 2
    return {
        'alpha': alpha_otimo,
        'phi_alpha': phi(alpha_otimo),
        'iteracoes': max_iter,
        'historico': historico,
        'convergiu': False
    }


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo: φ(α) = α² - 4α + 4, mínimo em α = 2
    def phi_exemplo(alpha):
        return -1512*(alpha**3) + 1080*(alpha**2) -180*alpha + 8
    
    resultado = bissecao(phi_exemplo, a=0, b=0.2, tol=1e-4)
    
    print(f"α* = {resultado['alpha']:.8f}")
    print(f"φ(α*) = {resultado['phi_alpha']:.8f}")
    print(f"Iterações: {resultado['iteracoes']}")
    print(f"Convergência: {resultado['convergiu']}")
    print("\nHistórico:")
    for item in resultado['historico']:
        print(f"  Iter {item['iter']}: a={item['a']:.6f}, b={item['b']:.6f}, c={item['c']:.6f}, φ(c)={item['phi_c']:.6f}")