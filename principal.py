import sys
import simpy as sp
from unidimensionais.bissecao import bissecao
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QCheckBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QGroupBox, QComboBox,
                             QDoubleSpinBox, QSpinBox, QGridLayout)


class ModuloBissecao(QWidget):
    """Módulo para métodos de busca do comprimento de passo α (bisseção)"""
    
    def __init__(self):
        super().__init__()
        self.symbols = []
        self.f_sym = None
        self.gradient_sym = None
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

        self.ponto_label = QLabel("Ponto inicial x0:")
        self.ponto_label.setVisible(False)
        func_layout.addWidget(self.ponto_label)
        self.inicial_input = QLineEdit()
        self.inicial_input.setPlaceholderText("Ex: 0.5")
        self.inicial_input.setVisible(False)
        func_layout.addWidget(self.inicial_input)
        
        func_group.setLayout(func_layout)
        layout.addWidget(func_group)
    
        
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

        # Filtrar constantes (n, e) se necessário
        # self.symbols = [s for s in self.symbols if not s.is_constante()]

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
    
    def criar_phi_parametrizada(self, ponto_atual, direcao):
        """
        Cria φ(α) = f(x + α*d)
        ponto_atual: dict com valores {x1: 0.5, x2: 1.0, ...}
        direcao: dict com direção {x1: d1, x2: d2, ...}
        """
        alpha = sp.Symbol('α')
        
        # Cria ponto parametrizado: x + α*d
        subs_dict = {}
        for var in self.symbols:
            x0 = ponto_atual.get(str(var), 0)
            d = direcao.get(str(var), 0)
            subs_dict[var] = x0 + alpha * d
        
        # Substitui na função
        phi_sym = self.f_sym.subs(subs_dict)
        
        # Retorna função numérica de α
        return sp.lambdify(alpha, phi_sym, 'numpy')

    def calcular_alpha(self):
        """Executa o método escolhido para encontrar α*"""
        try:
            # Atualiza a função APENAS quando clica no botão
            if not self.atualizar_funcao():
                self.results_text.setText("Erro: Função inválida. Verifique a sintaxe.")
                return
            
            tol = self.tol_input.value()
            max_iter = self.max_iter_input.value()
            
            # Limpa a área de resultados
            self.results_text.clear()
            
            # Redireciona para o método escolhido
            a = self.a_input.value()
            b = self.b_input.value()
            
            if a >= b:
                self.results_text.setText("Erro: 'a' deve ser menor que 'b' no intervalo de busca.")
                return
            
            if self.checkbox.isChecked():
                ponto_atual = {'x': float(self.inicial_input.text()) if self.inicial_input.text() else 0}
                direcao = {'x': 1.0}  # Direção padrão
                phi_function = self.criar_phi_parametrizada(ponto_atual, direcao)
            else:
                # Cria uma função phi que usa f_sym já atualizado
                def phi_function(alpha):
                    if not self.f_sym or not self.symbols:
                        return float('inf')
                    # Avalia f(α) - assume primeira variável é α
                    return float(self.f_sym.subs({self.symbols[0]: alpha}))

            resultado = bissecao(phi_function, a, b, tol, max_iter)
            self.exibir_resultados_bissecao(resultado)
                
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


class ModuloNewton(QWidget):
    """Módulo para método de Newton"""
    #TODO: Implementar interface para método de Newton

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