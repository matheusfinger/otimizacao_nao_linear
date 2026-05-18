import sys
from unidimensionais.bissecao import bissecao
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QGroupBox, QComboBox,
                             QDoubleSpinBox, QSpinBox, QGridLayout)


class ModuloUnidimensional(QWidget):
    """Módulo para métodos de busca do comprimento de passo α (bisseção, Newton, Wolfe)"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grupo da função parametrizada φ(α)
        func_group = QGroupBox("Função Parametrizada φ(α)")
        func_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Ex: x**3 + x**2 + 2")
        func_layout.addWidget(QLabel("Função parametrizada φ(α):"))
        func_layout.addWidget(self.func_input)
        
        func_group.setLayout(func_layout)
        layout.addWidget(func_group)
        
        # Grupo do ponto inicial
        ponto_group = QGroupBox("Ponto inicial x0")
        ponto_layout = QGridLayout()
        
        ponto_group.setLayout(ponto_layout)
        layout.addWidget(ponto_group)
        
        # Seleção do método
        method_group = QGroupBox("Método de busca unidimensional  ")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Bisseção", "Newton", "Wolfe"])
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # Grupo de parâmetros
        self.params_group = QGroupBox("Parâmetros do Método")
        self.params_layout = QGridLayout()
        
        # Parâmetros comuns
        self.params_layout.addWidget(QLabel("Tolerância:"), 0, 0)
        self.tol_input = QDoubleSpinBox()
        self.tol_input.setRange(1e-12, 1e-2)
        self.tol_input.setValue(1e-6)
        self.params_layout.addWidget(self.tol_input, 0, 1)
        
        self.params_layout.addWidget(QLabel("Max iterações:"), 0, 2)
        self.max_iter_input = QSpinBox()
        self.max_iter_input.setRange(1, 1000)
        self.max_iter_input.setValue(100)
        self.params_layout.addWidget(self.max_iter_input, 0, 3)
        
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
        
        # Parâmetros específicos de Newton
        self.params_layout.addWidget(QLabel("Derivada φ'(α) (opcional):"), 2, 0)
        self.deriv_input = QLineEdit()
        self.deriv_input.setPlaceholderText("Deixe vazio para calcular numericamente")
        self.deriv_input.setEnabled(False)
        self.params_layout.addWidget(self.deriv_input, 2, 1, 1, 3)
        
        # Parâmetros específicos de Wolfe
        self.params_layout.addWidget(QLabel("c1 (Armijo):"), 3, 0)
        self.c1_input = QDoubleSpinBox()
        self.c1_input.setRange(0, 1)
        self.c1_input.setValue(1e-4)
        self.c1_input.setEnabled(False)
        self.params_layout.addWidget(self.c1_input, 3, 1)
        
        self.params_layout.addWidget(QLabel("c2 (Curvatura):"), 3, 2)
        self.c2_input = QDoubleSpinBox()
        self.c2_input.setRange(0, 1)
        self.c2_input.setValue(0.9)
        self.c2_input.setEnabled(False)
        self.params_layout.addWidget(self.c2_input, 3, 3)
        
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
        self.method_combo.currentTextChanged.connect(self.atualizar_parametros)
        self.calc_btn.clicked.connect(self.calcular_alpha)  # Conecta o botão
    
    def atualizar_parametros(self, metodo):
        """Habilita/desabilita campos conforme o método selecionado"""
        is_bissecao = (metodo == "Bisseção")
        self.a_input.setEnabled(is_bissecao)
        self.b_input.setEnabled(is_bissecao)
        
        is_newton = (metodo == "Newton")
        self.deriv_input.setEnabled(is_newton)
        
        is_wolfe = (metodo == "Wolfe")
        self.c1_input.setEnabled(is_wolfe)
        self.c2_input.setEnabled(is_wolfe)
    
    def calcular_alpha(self):
        """Executa o método escolhido para encontrar α*"""
        try:
            
            metodo = self.method_combo.currentText()
            tol = self.tol_input.value()
            max_iter = self.max_iter_input.value()
            
            # Limpa a área de resultados
            self.results_text.clear()
            
            # Redireciona para o método escolhido
            if metodo == "Bisseção":
                a = self.a_input.value()
                b = self.b_input.value()
                
                if a >= b:
                    self.results_text.setText("Erro: 'a' deve ser menor que 'b' no intervalo de busca.")
                    return
                
                resultado = bissecao(self.phi_function, a, b, tol, max_iter)
                self.exibir_resultados_bissecao(resultado)
                
            elif metodo == "Newton":
                # TODO: Implementar método de Newton
                self.results_text.setText("Método de Newton ainda não implementado.")
                
            elif metodo == "Wolfe":
                # TODO: Implementar condições de Wolfe
                self.results_text.setText("Condições de Wolfe ainda não implementadas.")
                
        except Exception as e:
            self.results_text.setText(f"Erro durante o cálculo: {str(e)}")

    def exibir_resultados_bissecao(self, resultado):
        """Formata e exibe os resultados da bisseção"""
        texto = "=" * 60 + "\n"
        texto += f"{'RESULTADOS DO MÉTODO DA BISSEÇÃO':^60}\n"
        texto += "=" * 60 + "\n\n"
        
        # Resultados principais
        texto += f"α* (comprimento de passo ótimo): {resultado['alpha']:.10f}\n"
        texto += f"φ(α*): {resultado['phi_alpha']:.10f}\n"
        texto += f"Convergência: {'Sim' if resultado['convergiu'] else 'Não'}\n"
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


class ModuloMultidimensional(QWidget):
    """Módulo para métodos irrestritos multidimensionais (completo)"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grupo da função multivariável
        func_group = QGroupBox("Função Multidimensional f(x)")
        func_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Ex: x[0]**2 + x[1]**2")
        func_layout.addWidget(QLabel("Função objetivo f(x):"))
        func_layout.addWidget(self.func_input)
        
        self.grad_input = QLineEdit()
        self.grad_input.setPlaceholderText("Ex: [2*x[0], 2*x[1]]")
        func_layout.addWidget(QLabel("Gradiente ∇f(x):"))
        func_layout.addWidget(self.grad_input)
        
        func_group.setLayout(func_layout)
        layout.addWidget(func_group)
        
        # Grupo do ponto inicial
        point_group = QGroupBox("Ponto inicial")
        point_layout = QHBoxLayout()
        self.point_input = QLineEdit()
        self.point_input.setPlaceholderText("Ex: 1.0, 2.0")
        point_layout.addWidget(QLabel("x0:"))
        point_layout.addWidget(self.point_input)
        point_group.setLayout(point_layout)
        layout.addWidget(point_group)
        
        # Seleção do método de busca multidimensional
        method_group = QGroupBox("Método de busca multidimensional")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Gradiente descendente", "Newton", "Quasi-Newton"])
        self.method_combo.setEnabled(False)  # Desabilitado até implementar
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # Sub-módulo: qual método unidimensional usar para busca de α
        alpha_group = QGroupBox("Método para cálculo do comprimento de passo α")
        alpha_layout = QVBoxLayout()
        self.alpha_method_combo = QComboBox()
        self.alpha_method_combo.addItems(["Bisseção", "Newton", "Wolfe"])
        self.alpha_method_combo.setEnabled(False)
        alpha_layout.addWidget(self.alpha_method_combo)
        alpha_group.setLayout(alpha_layout)
        layout.addWidget(alpha_group)
        
        # Botão
        self.calc_btn = QPushButton("Otimizar")
        self.calc_btn.setEnabled(False)
        layout.addWidget(self.calc_btn)
        
        # Resultados
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Otimização - Métodos de Busca Unidimensional e Multidimensional")
        self.setGeometry(100, 100, 800, 700)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(ModuloUnidimensional(), "Módulo 1: Comprimento de Passo α")
        self.tabs.addTab(ModuloMultidimensional(), "Módulo 2: Otimização Irrestrita Multidimensional")
        
        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())