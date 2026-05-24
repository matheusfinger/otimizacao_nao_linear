import sys
import sympy as sp
from unidimensionais.bissecao import bissecao
from unidimensionais.newton import newton
from utils import criar_phi_parametrizada, calcular_direcao
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QCheckBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QGroupBox, QComboBox,
                             QDoubleSpinBox, QSpinBox, QGridLayout)


class ModuloNewton(QWidget):
    """Módulo para Newton"""
    
    def __init__(self):
        super().__init__()
        self.symbols = []
        self.f_sym = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grupo da função
        func_group = QGroupBox("Digite a função")
        func_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Ex: x**3 + x**2 + 2")
        func_layout.addWidget(QLabel("Função a ser analisada:"))
        self.checkbox = QCheckBox('Parametrizar a função', self)
        func_layout.addWidget(self.func_input)
        func_layout.addWidget(self.checkbox)

        self.method_label = QLabel("Escolha o método para parametrizar a função")
        self.method_label.setVisible(False)
        func_layout.addWidget(self.method_label)

        # Seleção do método
        container_widget = QWidget()
        container_layout = QHBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)  # Remove margens

        self.method_combo = QComboBox()
        self.method_combo.addItems(["Gradiente", "Newton", "Quasi-Newton"])

        container_layout.addWidget(self.method_combo, 1)
        container_layout.addStretch(1)
        self.method_container = container_widget
        self.method_container.setVisible(False)
        func_layout.addWidget(self.method_container)

        self.ponto_label = QLabel("Ponto inicial:")
        self.ponto_label.setVisible(False)
        func_layout.addWidget(self.ponto_label)
        self.inicial_input = QLineEdit()
        self.inicial_input.setPlaceholderText("Ex:[0.5 6 8]")
        self.inicial_input.setVisible(False)
        func_layout.addWidget(self.inicial_input)
        
        func_group.setLayout(func_layout)
        layout.addWidget(func_group)
    
        
        # Grupo de parâmetros
        self.params_group = QGroupBox("Parâmetros do Método")
        self.params_layout = QGridLayout()
        
        # Parâmetros comuns
        self.params_layout.addWidget(QLabel("Tolerância (10^):"), 0, 0)
        self.tol_expoente_input = QSpinBox()  # Usando SpinBox para expoente
        self.tol_expoente_input.setRange(-15, -1)  # De 10^-15 até 10^-1
        self.tol_expoente_input.setValue(-6)  # Padrão: 10^-6
        self.tol_expoente_input.setToolTip("Digite o expoente da tolerância\nExemplo: -6 = 10⁻⁶")
        self.params_layout.addWidget(self.tol_expoente_input, 0, 1)
        
        # Mostrar o valor real da tolerância
        self.tol_valor_label = QLabel("= 1.00e-06")
        self.tol_valor_label.setStyleSheet("color: gray;")
        self.params_layout.addWidget(self.tol_valor_label, 0, 2)
        
        self.params_layout.addWidget(QLabel("Max iterações:"), 0, 3)
        self.max_iter_input = QSpinBox()
        self.max_iter_input.setRange(1, 1000)
        self.max_iter_input.setValue(100)
        self.params_layout.addWidget(self.max_iter_input, 0, 4)
        
        # Parâmetros específicos de Newton
        self.params_layout.addWidget(QLabel("Chute inicial para α:"), 1, 0)
        self.chute_inicial_input = QDoubleSpinBox()
        self.chute_inicial_input.setRange(-1e6, 1e6)
        self.chute_inicial_input.setValue(0.0)
        self.params_layout.addWidget(self.chute_inicial_input, 1, 1)
        
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group)
        
        # Botão para gerar φ(α) e calcular
        btn_layout = QHBoxLayout()
        self.calc_btn = QPushButton("Calcular α*")
        btn_layout.addWidget(self.calc_btn)
        layout.addLayout(btn_layout)
        
        # Área de resultados
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("α* (comprimento do passo) e histórico aparecerão aqui...")
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
        
        # Conectar eventos
        self.checkbox.toggled.connect(self.toggle_parametrizacao)
        self.calc_btn.clicked.connect(self.calcular_alpha)  # Conecta o botão

        # Conectar evento para atualizar o label da tolerância
        self.tol_expoente_input.valueChanged.connect(self.atualizar_label_tolerancia)

    def atualizar_label_tolerancia(self):
        """Atualiza o label que mostra o valor real da tolerância"""
        expoente = self.tol_expoente_input.value()
        valor = 10 ** expoente
        self.tol_valor_label.setText(f"= {valor:.2e}")

    def toggle_parametrizacao(self, checked):
        """Mostra ou esconde campos de parametrização baseado no estado do checkbox"""
        self.method_label.setVisible(checked)
        self.method_container.setVisible(checked)
        self.ponto_label.setVisible(checked)
        self.inicial_input.setVisible(checked)

    def detectar_variaveis(self, expressao_str):
        """Detecta automaticamente todas as variáveis na expressão"""    
        # Cria um símbolo para análise
        expr = sp.sympify(expressao_str)
        
        #Pega todos os símbolos livres na expressão
        self.symbols = sorted(list(expr.free_symbols), key=str)

        # print(f"Variáveis detectadas: {self.symbols}")
        return self.symbols

    def atualizar_funcao(self):
        """Atualiza função baseado na expressão do usuário"""
        expr_str = self.func_input.text()
        try:
            #Converte string para expressão SymPy
            self.f_sym = sp.sympify(expr_str)

            # Detecta variáveis automaticamente
            self.detectar_variaveis(expr_str)

            return True
        except Exception as e:
            print(f"Erro: {e}")
            return False
    
    def calcular_alpha(self):
        """Executa Newton para encontrar α*"""
        try:
            # Atualiza a função APENAS quando clica no botão
            if not self.atualizar_funcao():
                self.results_text.setText("Erro: Função inválida. Verifique a sintaxe.")
                return
            
            tol = self.tol_expoente_input.value()
            tol = 10 ** (tol)
            max_iter = self.max_iter_input.value()
            
            # Limpa a área de resultados
            self.results_text.clear()
            
            # Redireciona para o método escolhido
            ponto_inicial = self.chute_inicial_input.value()
            
            # Variáveis para armazenar informações da parametrização
            phi_sym_expr = None
            parametrizacao_info = None
            
            if self.checkbox.isChecked():
                pontos_texto = self.inicial_input.text().strip()

                if not pontos_texto:
                    self.results_text.setText("Erro: Ponto inicial não foi informado.")
                    return

                try:
                    pontos_texto = pontos_texto.strip('[]')
                    pontos = [float(x.strip()) for x in pontos_texto.split()]

                    if not pontos:
                        self.results_text.setText("Erro: Nenhum valor válido encontrado no ponto inicial.")
                        return
                    
                    # Verifica se o número de pontos corresponde às variáveis
                    if len(pontos) != len(self.symbols):
                        self.results_text.setText(
                            f"Erro: Número de pontos ({len(pontos)}) não corresponde "
                            f"ao número de variáveis ({len(self.symbols)}).\n"
                            f"Variáveis detectadas: {', '.join(str(s) for s in self.symbols)}\n"
                            f"Exemplo de ponto inicial para {len(self.symbols)} variável(is): "
                            f"{' '.join(['0']*len(self.symbols))}"
                        )
                        return

                    metodo = self.method_combo.currentText()
                    direcao, info_direcao = calcular_direcao(
                        metodo, self.f_sym, self.symbols, pontos
                    )
                    
                    # Mostra informações da direção
                    self.results_text.append(info_direcao['descricao'])
                    if 'gradiente' in info_direcao:
                        self.results_text.append(f"Gradiente: {info_direcao['gradiente']}")
                    
                    # Cria φ(α) parametrizada
                    phi_function, phi_sym_expr, expressoes = criar_phi_parametrizada(
                        pontos, direcao, self.symbols, self.f_sym
                    )
                    
                    # Guarda infos para exibição
                    parametrizacao_info = {
                        'pontos': pontos,
                        'direcao': direcao,
                        'expressoes': expressoes,
                        'phi_simbolica': phi_sym_expr
                    }
                    
                    # TESTA A FUNÇÃO CRIADA COM UM VALOR DE α
                    try:
                        test_alpha = (ponto_inicial)
                        test_value = phi_function(test_alpha)
                        if not isinstance(test_value, (int, float)):
                            raise ValueError(f"Função retornou {type(test_value)} em vez de número")
                    except Exception as e:
                        self.results_text.setText(f"Erro: Função φ(α) não retornou um valor numérico válido.\nDetalhe: {str(e)}")
                        return
                    
                except ValueError as e:
                    self.results_text.setText(f"Erro: Não foi possível converter o ponto inicial em números reais.\n"
                                f"Certifique-se de usar números separados por espaço.\n"
                                f"Exemplo: '0.5 6 8' ou '[0.5 6 8]'\n"
                                f"Erro detalhado: {str(e)}")
                    return
                except Exception as e:
                    self.results_text.setText(f"Erro ao parametrizar a função:\n{str(e)}")
                    return
                
            else:
                # CASO SEM PARAMETRIZAÇÃO (apenas 1 variável)
                if len(self.symbols) != 1:
                    self.results_text.setText(
                        f"Erro: Função com {len(self.symbols)} variáveis detectadas.\n"
                        f"Marque 'Parametrizar a função' para usar múltiplas variáveis."
                    )
                    return
                
                # Pega a variável original (ex: x, t, y)
                var_original = self.symbols[0]
                
                # Cria o símbolo α para o método de Newton
                alpha = sp.Symbol('α', real=True)
                
                # Substitui a variável original por α
                phi_sym_expr = self.f_sym.subs(var_original, alpha)

            # Executa Newton
            resultado = newton(phi_sym_expr, ponto_inicial, tol, max_iter)
            
            # Exibe os resultados e a parametrização
            self.exibir_resultados_newton(resultado, parametrizacao_info)
                
        except Exception as e:
            self.results_text.setText(f"Erro durante o cálculo: {str(e)}")

    def exibir_resultados_newton(self, resultado, parametrizacao_info=None):
        """Formata e exibe os resultados de Newton"""
        texto = "=" * 60 + "\n"
        texto += f"{'RESULTADOS DO MÉTODO DE NEWTON':^60}\n"
        texto += "=" * 60 + "\n\n"
        
        # Exibe informações da parametrização se disponível
        if parametrizacao_info:
            texto += "PARAMETRIZAÇÃO DA FUNÇÃO\n"
            texto += "-" * 60 + "\n"
            texto += f"Função original: f({', '.join(str(s) for s in self.symbols)}) = {self.f_sym}\n\n"
            
            texto += "Ponto inicial x₀:\n"
            for i, var in enumerate(self.symbols):
                texto += f"  {var}₀ = {parametrizacao_info['pontos'][i]:.6f}\n"
            
            texto += "\nDireção de busca d:\n"
            for i, var in enumerate(self.symbols):
                texto += f"  d_{var} = {parametrizacao_info['direcao'][i]:.6f}\n"
            
            texto += "\nParametrização x(α) = x₀ + α·d:\n"
            for expr in parametrizacao_info['expressoes']:
                texto += f"  {expr}\n"
            
            texto += f"\nφ(α) = {parametrizacao_info['phi_simbolica']}\n"
            
            # Expande a expressão se possível
            try:
                expanded = sp.expand(parametrizacao_info['phi_simbolica'])
                if expanded != parametrizacao_info['phi_simbolica']:
                    texto += f"φ(α) expandido = {expanded}\n"
            except:
                pass
            
            texto += "\n" + "=" * 60 + "\n\n"
        
        # Resultados principais
        texto += "RESULTADOS DA OTIMIZAÇÃO\n"
        texto += "-" * 60 + "\n"
        texto += f"α* (comprimento de passo ótimo): {resultado['alpha']:.10f}\n"
        texto += f"φ(α*): {resultado['phi_alpha']:.10f}\n"
        
        # Se temos parametrização, mostra também o ponto ótimo x*
        if parametrizacao_info:
            texto += "\nPonto ótimo x* = x₀ + α*·d:\n"
            for i, var in enumerate(self.symbols):
                x_otimo = parametrizacao_info['pontos'][i] + resultado['alpha'] * parametrizacao_info['direcao'][i]
                texto += f"  {var}* = {x_otimo:.10f}\n"
            
            # Verifica se o ponto ótimo satisfaz a função original
            try:
                f_otimo = float(self.f_sym.subs({
                    self.symbols[i]: parametrizacao_info['pontos'][i] + resultado['alpha'] * parametrizacao_info['direcao'][i]
                    for i in range(len(self.symbols))
                }))
                texto += f"\nVerificação: f(x*) = {f_otimo:.10f}\n"
                texto += f"Diferença |f(x*) - φ(α*)| = {abs(f_otimo - resultado['phi_alpha']):.2e}\n"
            except:
                pass
        
        texto += f"\nConvergência: {'Sim' if resultado['convergiu'] else 'Não'}\n"
        texto += f"Iterações realizadas: {resultado['iteracoes']}\n\n"
        
        # Tabela de histórico
        if resultado['historico']:
            texto += "=" * 80 + "\n"
            texto += f"{'HISTÓRICO DAS ITERAÇÕES':^80}\n"
            texto += "=" * 80 + "\n\n"
            
            # Cabeçalho da tabela
            texto += f"{'Iter':^6} {'α':^12} {'φ(α)':^12}\n"
            texto += "-" * 80 + "\n"
            
            # Dados de cada iteração
            for item in resultado['historico']:
                texto += f"{item['iter']:^6} "
                texto += f"{item['alpha']:^12.6f} "
                texto += f"{item['phi_alpha']:^12.6f} \n"
            
            texto += "-" * 80 + "\n\n"
            
            # Informações adicionais sobre a convergência
            if resultado['convergiu']:
                texto += "✓ Convergência alcançada com sucesso!\n"
                # Remover a linha que tenta acessar 'intervalo'
                if 'phi_prime' in resultado['historico'][-1]:
                    texto += f"  - Último |φ'(α)| = {abs(resultado['historico'][-1]['phi_prime']):.2e}\n"
            else:
                texto += "⚠ Aviso: Número máximo de iterações atingido sem convergência!\n"
                texto += f"  - Aumente max_iter ou ajuste a tolerância.\n"
        
        self.results_text.setText(texto)


class ModuloBissecao(QWidget):
    """Módulo para métodos de busca do comprimento de passo α (bisseção)"""
    
    def __init__(self):
        super().__init__()
        self.symbols = []
        self.f_sym = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grupo da função
        func_group = QGroupBox("Digite a função")
        func_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Ex: x**3 + x**2 + 2")
        func_layout.addWidget(QLabel("Função a ser analisada:"))
        self.checkbox = QCheckBox('Parametrizar a função', self)
        func_layout.addWidget(self.func_input)
        func_layout.addWidget(self.checkbox)

        self.method_label = QLabel("Escolha o método para parametrizar a função")
        self.method_label.setVisible(False)
        func_layout.addWidget(self.method_label)

        # Seleção do método
        container_widget = QWidget()
        container_layout = QHBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)  # Remove margens

        self.method_combo = QComboBox()
        self.method_combo.addItems(["Gradiente", "Newton", "Quasi-Newton"])

        container_layout.addWidget(self.method_combo, 1)
        container_layout.addStretch(1)
        self.method_container = container_widget
        self.method_container.setVisible(False)
        func_layout.addWidget(self.method_container)

        self.ponto_label = QLabel("Ponto inicial:")
        self.ponto_label.setVisible(False)
        func_layout.addWidget(self.ponto_label)
        self.inicial_input = QLineEdit()
        self.inicial_input.setPlaceholderText("Ex:[0.5 6 8]")
        self.inicial_input.setVisible(False)
        func_layout.addWidget(self.inicial_input)
        
        func_group.setLayout(func_layout)
        layout.addWidget(func_group)
    
        
        # Grupo de parâmetros
        self.params_group = QGroupBox("Parâmetros do Método")
        self.params_layout = QGridLayout()
        
        # Parâmetros comuns
        self.params_layout.addWidget(QLabel("Tolerância (10^):"), 0, 0)
        self.tol_expoente_input = QSpinBox()  # Usando SpinBox para expoente
        self.tol_expoente_input.setRange(-15, -1)  # De 10^-15 até 10^-1
        self.tol_expoente_input.setValue(-6)  # Padrão: 10^-6
        self.tol_expoente_input.setToolTip("Digite o expoente da tolerância\nExemplo: -6 = 10⁻⁶")
        self.params_layout.addWidget(self.tol_expoente_input, 0, 1)
        
        # Mostrar o valor real da tolerância
        self.tol_valor_label = QLabel("= 1.00e-06")
        self.tol_valor_label.setStyleSheet("color: gray;")
        self.params_layout.addWidget(self.tol_valor_label, 0, 2)
        
        self.params_layout.addWidget(QLabel("Max iterações:"), 0, 3)
        self.max_iter_input = QSpinBox()
        self.max_iter_input.setRange(1, 1000)
        self.max_iter_input.setValue(100)
        self.params_layout.addWidget(self.max_iter_input, 0, 4)
        
        # Parâmetros específicos da bisseção
        self.params_layout.addWidget(QLabel("Intervalo a (α):"), 1, 0)
        self.a_input = QDoubleSpinBox()
        self.a_input.setRange(-1e6, 1e6)
        self.a_input.setValue(0.0)
        self.params_layout.addWidget(self.a_input, 1, 1)
        
        self.params_layout.addWidget(QLabel("Intervalo b (α):"), 1, 2)
        self.b_input = QDoubleSpinBox()
        self.b_input.setRange(-1e6, 1e6)
        self.b_input.setValue(1.0)
        self.params_layout.addWidget(self.b_input, 1, 3)
        
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group)
        
        # Botão para gerar φ(α) e calcular
        btn_layout = QHBoxLayout()
        self.calc_btn = QPushButton("Calcular α*")
        btn_layout.addWidget(self.calc_btn)
        layout.addLayout(btn_layout)
        
        # Área de resultados
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("α* (comprimento do passo) e histórico aparecerão aqui...")
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
        
        # Conectar eventos
        self.checkbox.toggled.connect(self.toggle_parametrizacao)
        self.calc_btn.clicked.connect(self.calcular_alpha)  # Conecta o botão

        # Conectar evento para atualizar o label da tolerância
        self.tol_expoente_input.valueChanged.connect(self.atualizar_label_tolerancia)

    def atualizar_label_tolerancia(self):
        """Atualiza o label que mostra o valor real da tolerância"""
        expoente = self.tol_expoente_input.value()
        valor = 10 ** expoente
        self.tol_valor_label.setText(f"= {valor:.2e}")

    def toggle_parametrizacao(self, checked):
        """Mostra ou esconde campos de parametrização baseado no estado do checkbox"""
        self.method_label.setVisible(checked)
        self.method_container.setVisible(checked)
        self.ponto_label.setVisible(checked)
        self.inicial_input.setVisible(checked)

    def detectar_variaveis(self, expressao_str):
        """Detecta automaticamente todas as variáveis na expressão"""    
        # Cria um símbolo para análise
        expr = sp.sympify(expressao_str)
        
        #Pega todos os símbolos livres na expressão
        self.symbols = sorted(list(expr.free_symbols), key=str)

        # print(f"Variáveis detectadas: {self.symbols}")
        return self.symbols

    def atualizar_funcao(self):
        """Atualiza função baseado na expressão do usuário"""
        expr_str = self.func_input.text()
        try:
            #Converte string para expressão SymPy
            self.f_sym = sp.sympify(expr_str)

            # Detecta variáveis automaticamente
            self.detectar_variaveis(expr_str)

            return True
        except Exception as e:
            print(f"Erro: {e}")
            return False
    
    def calcular_alpha(self):
        """Executa a bisseção para encontrar α*"""
        try:
            # Atualiza a função APENAS quando clica no botão
            if not self.atualizar_funcao():
                self.results_text.setText("Erro: Função inválida. Verifique a sintaxe.")
                return
            
            tol = self.tol_expoente_input.value()
            tol = 10 ** (tol)
            max_iter = self.max_iter_input.value()
            
            # Limpa a área de resultados
            self.results_text.clear()
            
            # Redireciona para o método escolhido
            a = self.a_input.value()
            b = self.b_input.value()
            
            if a >= b:
                self.results_text.setText("Erro: 'a' deve ser menor que 'b' no intervalo de busca.")
                return
            
            # Variáveis para armazenar informações da parametrização
            phi_sym_expr = None
            parametrizacao_info = None
            
            if self.checkbox.isChecked():
                pontos_texto = self.inicial_input.text().strip()

                if not pontos_texto:
                    self.results_text.setText("Erro: Ponto inicial não foi informado.")
                    return

                try:
                    pontos_texto = pontos_texto.strip('[]')
                    pontos = [float(x.strip()) for x in pontos_texto.split()]

                    if not pontos:
                        self.results_text.setText("Erro: Nenhum valor válido encontrado no ponto inicial.")
                        return
                    
                    # VERIFICA SE O NÚMERO DE PONTOS CORRESPONDE ÀS VARIÁVEIS
                    if len(pontos) != len(self.symbols):
                        self.results_text.setText(
                            f"Erro: Número de pontos ({len(pontos)}) não corresponde "
                            f"ao número de variáveis ({len(self.symbols)}).\n"
                            f"Variáveis detectadas: {', '.join(str(s) for s in self.symbols)}\n"
                            f"Exemplo de ponto inicial para {len(self.symbols)} variável(is): "
                            f"{' '.join(['0']*len(self.symbols))}"
                        )
                        return

                    metodo = self.method_combo.currentText()
                    direcao, info_direcao = calcular_direcao(
                        metodo, self.f_sym, self.symbols, pontos
                    )
                    
                    # Mostra informações da direção
                    self.results_text.append(info_direcao['descricao'])
                    if 'gradiente' in info_direcao:
                        self.results_text.append(f"Gradiente: {info_direcao['gradiente']}")
                    
                    # CRIA φ(α) PARAMETRIZADA - AGORA RETORNA 3 VALORES
                    phi_function, phi_sym_expr, expressoes = criar_phi_parametrizada(
                        pontos, direcao, self.symbols, self.f_sym
                    )
                    
                    # GUARDA INFORMAÇÕES PARA EXIBIÇÃO
                    parametrizacao_info = {
                        'pontos': pontos,
                        'direcao': direcao,
                        'expressoes': expressoes,
                        'phi_simbolica': phi_sym_expr
                    }
                    
                    # TESTA A FUNÇÃO CRIADA COM UM VALOR DE α
                    try:
                        test_alpha = (a + b) / 2
                        test_value = phi_function(test_alpha)
                        if not isinstance(test_value, (int, float)):
                            raise ValueError(f"Função retornou {type(test_value)} em vez de número")
                    except Exception as e:
                        self.results_text.setText(f"Erro: Função φ(α) não retornou um valor numérico válido.\nDetalhe: {str(e)}")
                        return
                    
                except ValueError as e:
                    self.results_text.setText(f"Erro: Não foi possível converter o ponto inicial em números reais.\n"
                                f"Certifique-se de usar números separados por espaço.\n"
                                f"Exemplo: '0.5 6 8' ou '[0.5 6 8]'\n"
                                f"Erro detalhado: {str(e)}")
                    return
                except Exception as e:
                    self.results_text.setText(f"Erro ao parametrizar a função:\n{str(e)}")
                    return
                
            else:
                # CASO SEM PARAMETRIZAÇÃO (apenas 1 variável)
                if len(self.symbols) != 1:
                    self.results_text.setText(
                        f"Erro: Função com {len(self.symbols)} variáveis detectadas.\n"
                        f"Marque 'Parametrizar a função' para usar múltiplas variáveis."
                    )
                    return
                
                # Cria uma função phi que usa f_sym já atualizado
                def phi_function(alpha):
                    try:
                        if not self.f_sym or not self.symbols:
                            return float('inf')
                        # Avalia f(α) - assume primeira variável é α
                        return float(self.f_sym.subs({self.symbols[0]: alpha}))
                    except:
                        return float('inf')

            # EXECUTA A BISSEÇÃO
            resultado = bissecao(phi_function, a, b, tol, max_iter)
            
            # EXIBE OS RESULTADOS COM A PARAMETRIZAÇÃO
            self.exibir_resultados_bissecao(resultado, parametrizacao_info)
                
        except Exception as e:
            self.results_text.setText(f"Erro durante o cálculo: {str(e)}")

    def exibir_resultados_bissecao(self, resultado, parametrizacao_info=None):
        """Formata e exibe os resultados da bisseção"""
        texto = "=" * 60 + "\n"
        texto += f"{'RESULTADOS DO MÉTODO DA BISSEÇÃO':^60}\n"
        texto += "=" * 60 + "\n\n"
        
        # EXIBE INFORMAÇÕES DA PARAMETRIZAÇÃO SE DISPONÍVEL
        if parametrizacao_info:
            texto += "PARAMETRIZAÇÃO DA FUNÇÃO\n"
            texto += "-" * 60 + "\n"
            texto += f"Função original: f({', '.join(str(s) for s in self.symbols)}) = {self.f_sym}\n\n"
            
            texto += "Ponto inicial x₀:\n"
            for i, var in enumerate(self.symbols):
                texto += f"  {var}₀ = {parametrizacao_info['pontos'][i]:.6f}\n"
            
            texto += "\nDireção de busca d:\n"
            for i, var in enumerate(self.symbols):
                texto += f"  d_{var} = {parametrizacao_info['direcao'][i]:.6f}\n"
            
            texto += "\nParametrização x(α) = x₀ + α·d:\n"
            for expr in parametrizacao_info['expressoes']:
                texto += f"  {expr}\n"
            
            texto += f"\nφ(α) = {parametrizacao_info['phi_simbolica']}\n"
            
            # Expande a expressão se possível
            try:
                expanded = sp.expand(parametrizacao_info['phi_simbolica'])
                if expanded != parametrizacao_info['phi_simbolica']:
                    texto += f"φ(α) expandido = {expanded}\n"
            except:
                pass
            
            texto += "\n" + "=" * 60 + "\n\n"
        
        # Resultados principais
        texto += "RESULTADOS DA OTIMIZAÇÃO\n"
        texto += "-" * 60 + "\n"
        texto += f"α* (comprimento de passo ótimo): {resultado['alpha']:.10f}\n"
        texto += f"φ(α*): {resultado['phi_alpha']:.10f}\n"
        
        # Se temos parametrização, mostra também o ponto ótimo x*
        if parametrizacao_info:
            texto += "\nPonto ótimo x* = x₀ + α*·d:\n"
            for i, var in enumerate(self.symbols):
                x_otimo = parametrizacao_info['pontos'][i] + resultado['alpha'] * parametrizacao_info['direcao'][i]
                texto += f"  {var}* = {x_otimo:.10f}\n"
            
            # Verifica se o ponto ótimo satisfaz a função original
            try:
                f_otimo = float(self.f_sym.subs({
                    self.symbols[i]: parametrizacao_info['pontos'][i] + resultado['alpha'] * parametrizacao_info['direcao'][i]
                    for i in range(len(self.symbols))
                }))
                texto += f"\nVerificação: f(x*) = {f_otimo:.10f}\n"
                texto += f"Diferença |f(x*) - φ(α*)| = {abs(f_otimo - resultado['phi_alpha']):.2e}\n"
            except:
                pass
        
        texto += f"\nConvergência: {'Sim' if resultado['convergiu'] else 'Não'}\n"
        texto += f"Iterações realizadas: {resultado['iteracoes']}\n\n"
        
        # Tabela de histórico
        if resultado['historico']:
            texto += "=" * 80 + "\n"
            texto += f"{'HISTÓRICO DAS ITERAÇÕES':^80}\n"
            texto += "=" * 80 + "\n\n"
            
            # Cabeçalho da tabela
            texto += f"{'Iter':^6} {'a':^12} {'b':^12} {'c':^12} {'φ(a)':^12} {'φ(b)':^12} {'φ(c)':^12} {'Intervalo':^12}\n"
            texto += "-" * 80 + "\n"
            
            # Dados de cada iteração
            for item in resultado['historico']:
                texto += f"{item['iter']:^6} "
                texto += f"{item['a']:^12.6f} "
                texto += f"{item['b']:^12.6f} "
                texto += f"{item['c']:^12.6f} "
                texto += f"{item['phi_a']:^12.6f} "
                texto += f"{item['phi_b']:^12.6f} "
                texto += f"{item['phi_c']:^12.6f} "
                texto += f"{item['intervalo']:^12.6e}\n"
            
            texto += "-" * 80 + "\n\n"
            
            # Informações adicionais sobre a convergência
            if resultado['convergiu']:
                texto += "✓ Convergência alcançada com sucesso!\n"
                texto += f"  - Tolerância atingida: {abs(resultado['historico'][-1]['intervalo']):.2e}\n"
                texto += f"  - Intervalo final: [{resultado['historico'][-1]['a']:.8f}, {resultado['historico'][-1]['b']:.8f}]\n"
            else:
                texto += "⚠ Aviso: Número máximo de iterações atingido sem convergência!\n"
                texto += f"  - Aumente max_iter ou ajuste a tolerância.\n"
        
        self.results_text.setText(texto)

class ModuloWolfe(QWidget):
    """Módulo para condições de Wolfe"""
    #TODO: Implementar interface para condições de Wolfe


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Otimização - Métodos de Busca Unidimensional")
        self.setGeometry(100, 100, 800, 700)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(ModuloBissecao(), "Bisseção")
        self.tabs.addTab(ModuloNewton(), "Newton")
        self.tabs.addTab(ModuloWolfe(), "Wolfe")
        
        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())