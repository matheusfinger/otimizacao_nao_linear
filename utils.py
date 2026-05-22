import sympy as sp
import numpy as np

def criar_phi_parametrizada(pontos, direcao, simbolos, f_sym):
    """
    Cria φ(α) = f(x + α*d)
    
    Args:
        pontos: lista com valores [0.5, 1.0, 2.0] (ponto inicial x₀)
        direcao: lista com direção [2.5, 0.0, -1.0] (vetor d)
        simbolos: lista de símbolos SymPy [x, y, z]
        f_sym: expressão simbólica da função
    
    Returns:
        tuple: (função_numérica, expressão_simbólica, expressões_individuais)
    """
    # Verifica se os tamanhos são compatíveis
    if len(pontos) != len(simbolos):
        raise ValueError(f"Número de pontos ({len(pontos)}) não corresponde ao número de variáveis ({len(simbolos)})")
    
    if len(direcao) != len(simbolos):
        raise ValueError(f"Número de direções ({len(direcao)}) não corresponde ao número de variáveis ({len(simbolos)})")
    
    alpha = sp.Symbol('α', real=True)
    
    # Cria dicionário de substituição: var = ponto_i + α * direcao_i
    subs_dict = {}
    expressoes = []
    for i, var in enumerate(simbolos):
        x0 = pontos[i]      # valor inicial para esta variável
        d = direcao[i]      # direção para esta variável
        expressao = x0 + alpha * d
        subs_dict[var] = expressao
        expressoes.append(f"{var} = {expressao}")
    
    # Substitui na função simbólica
    try:
        phi_sym = f_sym.subs(subs_dict)
        
        # Simplifica a expressão (opcional, mas ajuda)
        phi_sym = sp.simplify(phi_sym)
        
        # Converte para função numérica
        phi_func = sp.lambdify(alpha, phi_sym, modules=['math'])
        
        # Wrapper para garantir que retorna um float
        def phi_wrapper(alpha_val):
            result = phi_func(alpha_val)
            return float(result) if hasattr(result, '__float__') else result
        
        # Retorna tanto a função quanto a expressão simbólica
        return phi_wrapper, phi_sym, expressoes
    
    except Exception as e:
        raise RuntimeError(f"Erro ao criar φ(α): {str(e)}")


def calcular_gradiente_simbolico(f_sym, simbolos):
    """
    Calcula o gradiente simbólico de uma função.
    
    Args:
        f_sym: expressão simbólica do SymPy
        simbolos: lista de símbolos [x, y, z, ...]
    
    Returns:
        Matriz com as derivadas parciais (gradiente)
    """

    if not f_sym or not simbolos:
        raise ValueError("Função ou variáveis não definidas")
    
    # Converte para matriz e calcula o Jacobiano
    f_matrix = sp.Matrix([f_sym])
    gradiente = f_matrix.jacobian(simbolos)
    
    return gradiente


def avaliar_gradiente_numerico(gradient_sym, simbolos, ponto):
    """
    Avalia o gradiente numericamente em um ponto específico.
    
    Args:
        gradient_sym: matriz do gradiente simbólico
        simbolos: lista de símbolos [x, y, z, ...]
        ponto: lista com valores numéricos do ponto [x0, y0, z0, ...]
    
    Returns:
        Lista com os valores numéricos do gradiente
    """
    if gradient_sym is None:
        raise ValueError("Gradiente simbólico não definido")
    
    # Cria dicionário de substituição
    subs_dict = {var: ponto[i] for i, var in enumerate(simbolos)}
    
    # Avalia o gradiente no ponto
    grad_num = gradient_sym.subs(subs_dict)
    
    # Converte para lista de floats
    return [float(grad_num[i]) for i in range(len(simbolos))]


def calcular_hessiana_simbolica(f_sym, simbolos):
    """
    Calcula a Hessiana simbólica da função atual.
    
    Args:
        f_sym: expressão simbólica do SymPy
        simbolos: lista de símbolos [x, y, z, ...]
    
    Returns:
        Matriz da Hessiana
    """
    if not f_sym or not simbolos:
        raise ValueError("Função ou variáveis não definidas")
    
    # Calcula o gradiente primeiro
    gradiente = calcular_gradiente_simbolico(f_sym, simbolos)
    
    # Calcula a Hessiana (Jacobiano do gradiente)
    hessiana = gradiente.jacobian(simbolos)
    
    return hessiana


def avaliar_hessiana_numerica(hessian_sym, simbolos, ponto):
    """
    Avalia a Hessiana numericamente em um ponto específico.
    
    Args:
        hessian_sym: matriz da Hessiana simbólica
        simbolos: lista de símbolos [x, y, z, ...]
        ponto: lista com valores numéricos do ponto [x0, y0, z0, ...]
    
    Returns:
        Lista de listas com os valores numéricos da Hessiana
    """
    if hessian_sym is None:
        raise ValueError("Hessiana simbólica não definida")
    
    # Cria dicionário de substituição
    subs_dict = {var: ponto[i] for i, var in enumerate(simbolos)}
    
    # Avalia a Hessiana no ponto
    hess_num = hessian_sym.subs(subs_dict)
    
    # Converte para lista de listas de floats
    n = len(simbolos)
    hessiana = [[float(hess_num[i, j]) for j in range(n)] for i in range(n)]
    
    return hessiana


def calcular_direcao_gradiente(f_sym, simbolos, pontos):
    """
    Calcula a direção de descida usando gradiente negativo: d = -∇f(x)
    
    Args:
        gradient_sym: matriz do gradiente simbólico
        simbolos: lista de símbolos
        pontos: ponto atual
    
    Returns:
        direcao: lista com a direção de busca
        info: dicionário com informações adicionais
    """
    gradient_sym = calcular_gradiente_simbolico(f_sym, simbolos)
    grad = avaliar_gradiente_numerico(gradient_sym, simbolos, pontos)
    direcao = [-g for g in grad]
    
    info = {
        'gradiente': grad,
        'norma_gradiente': sum(g**2 for g in grad)**0.5,
        'descricao': f"d = -∇f(x₀) = {direcao}"
    }
    
    return direcao, info


def calcular_direcao_newton(f_sym, simbolos, pontos):
    """
    Calcula a direção usando método de Newton: d = -H⁻¹∇f(x)
    
    Args:
        f_sym: expressão simbólica da função
        gradient_sym: matriz do gradiente simbólico
        hessian_sym: matriz da Hessiana simbólica
        simbolos: lista de símbolos
        pontos: ponto atual
    
    Returns:
        direcao: lista com a direção de busca
        info: dicionário com informações adicionais
    """
    gradient_sym = calcular_gradiente_simbolico(f_sym, simbolos)
    grad = avaliar_gradiente_numerico(gradient_sym, simbolos, pontos)
    hessiana_sym = calcular_hessiana_simbolica(f_sym, simbolos)
    hessiana = avaliar_hessiana_numerica(hessiana_sym, simbolos, pontos)
    
    try:
        # Converte para numpy para resolver o sistema linear
        hessiana_np = np.array(hessiana)
        grad_np = np.array(grad)
        
        # Resolve H*d = -grad
        direcao_np = np.linalg.solve(hessiana_np, -grad_np)
        direcao = direcao_np.tolist()
        
        info = {
            'gradiente': grad,
            'hessiana': hessiana,
            'descricao': f"d = -H⁻¹∇f(x₀)",
            'convergiu': True
        }
        
        return direcao, info
        
    except np.linalg.LinAlgError:
        # Se hessiana for singular, usa gradiente negativo
        direcao = [-g for g in grad]
        info = {
            'gradiente': grad,
            'hessiana': hessiana,
            'descricao': f"Hessiana singular. Usando gradiente negativo: d = -∇f(x₀)",
            'convergiu': False,
            'aviso': "Hessiana singular"
        }
        return direcao, info


def calcular_direcao_quasi_newton(f_sym, simbolos, pontos):
    """
    Calcula direção usando método Quasi-Newton simplificado (BFGS aproximado).
    
    Args:
        gradient_sym: matriz do gradiente simbólico
        simbolos: lista de símbolos
        pontos: ponto atual
    
    Returns:
        direcao: lista com a direção de busca
        info: dicionário com informações adicionais
    """
    gradient_sym = calcular_gradiente_simbolico(f_sym, simbolos)
    grad = avaliar_gradiente_numerico(gradient_sym, simbolos, pontos)
    direcao = [-g for g in grad]
    
    # Normaliza a direção para evitar passos muito grandes
    norma = sum(g**2 for g in grad)**0.5
    if norma > 1e-6:
        direcao = [d / norma for d in direcao]
    
    info = {
        'gradiente': grad,
        'norma_gradiente': norma,
        'descricao': f"d = -∇f(x₀)/||∇f(x₀)|| (normalizado)",
        'direcao_normalizada': True
    }
    
    return direcao, info


def calcular_direcao(metodo, f_sym, simbolos, pontos):
    """
    Função principal que calcula a direção baseada no método escolhido.
    
    Args:
        metodo: string com o método ("gradiente", "newton", "quasi-newton")
        f_sym: expressão simbólica da função
        gradient_sym: matriz do gradiente simbólico
        hessian_sym: matriz da Hessiana simbólica
        simbolos: lista de símbolos
        pontos: ponto atual
    
    Returns:
        tuple: (direcao, info_dicionario)
    """
    metodo = metodo.lower()
    
    if metodo == "gradiente":
        return calcular_direcao_gradiente(f_sym, simbolos, pontos)
    
    elif metodo == "newton":
        return calcular_direcao_newton(f_sym, simbolos, pontos)
    
    elif metodo == "quasi-newton":
        return calcular_direcao_quasi_newton(f_sym, simbolos, pontos)
    
    else:
        # Direção padrão
        direcao = [1.0] * len(pontos)
        info = {
            'descricao': f"Direção padrão: d = {direcao}",
            'aviso': f"Método '{metodo}' não reconhecido"
        }
        return direcao, info


def validar_funcao(expr_str):
    """
    Valida se a expressão da função é sintaticamente correta.
    
    Args:
        expr_str: string com a expressão
    
    Returns:
        tuple: (valido, mensagem_erro, expressao_sympy)
    """
    try:
        expr = sp.sympify(expr_str)
        return True, None, expr
    except sp.SympifyError as e:
        mensagem = f"Erro de sintaxe: {str(e)}\n\n"
        mensagem += "Use a sintaxe correta:\n"
        mensagem += "  - ** para potência (ex: x**2)\n"
        mensagem += "  - * para multiplicação (ex: 2*x)\n"
        mensagem += f"  - Exemplo: 'x**3 + x**2 + 2'"
        return False, mensagem, None
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}", None


def detectar_variaveis(expressao_str):
    """
    Detecta automaticamente todas as variáveis na expressão.
    
    Args:
        expressao_str: string com a expressão
    
    Returns:
        lista de símbolos ordenada
    """
    expr = sp.sympify(expressao_str)
    
    # Pega todos os símbolos livres na expressão
    symbols = sorted(list(expr.free_symbols), key=str)
    
    # Remove constantes matemáticas comuns
    constantes = ['E', 'pi', 'I', 'NaN', 'Infinity', 'NegativeInfinity']
    symbols = [s for s in symbols if str(s) not in constantes]
    
    return symbols