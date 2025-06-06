import sys
import requests
import urllib.request
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QComboBox, QVBoxLayout, QPushButton, QTextEdit, QMessageBox, QScrollArea, QHBoxLayout, QFrame)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class FilmeWidget(QFrame):
    def __init__(self, filme_info):
        super().__init__()
        self.initUI(filme_info)
        
    def initUI(self, filme_info):
        # Layout para cada filme
        layout = QVBoxLayout()
        
        # Capa do filme
        pixmap = QPixmap()
        if filme_info.get('Poster') and filme_info['Poster'] != 'N/A':
            try:
                urllib.request.urlretrieve(filme_info['Poster'], "temp_poster.jpg")
                pixmap.load("temp_poster.jpg")
                pixmap = pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            except:
                pixmap = QPixmap(200, 300)
                pixmap.fill(Qt.lightGray)
        else:
            pixmap = QPixmap(200, 300)
            pixmap.fill(Qt.lightGray)
        
        capa_label = QLabel()
        capa_label.setPixmap(pixmap)
        capa_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(capa_label)
        
        # Informações do filme
        info_texto = (
            f"Título: {filme_info.get('Title', 'N/A')}\n"
            f"Ano: {filme_info.get('Year', 'N/A')}\n"
            f"Diretor: {filme_info.get('Director', 'N/A')}"
        )
        
        info_label = QLabel(info_texto)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.setLayout(layout)
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("FilmeWidget { border: 1px solid gray; border-radius: 10px; }")

class MovieMoodSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Configurações da janela
        self.setWindowTitle('Seletor de Filmes por Estado Emocional')
        self.setGeometry(100, 100, 800, 600)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel('Como você deseja se sentir?')
        titulo.setFont(QFont('Arial', 16))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Seletor de Humor
        self.humor_combo = QComboBox()
        self.humor_combo.addItems([
            'Como deseja se sentir?',
            'Feliz',
            'Motivado',
            'Romantico',
            'Reflexivo',
            'Aventureiro',
            'Assustado'
        ])
        layout.addWidget(self.humor_combo)
        
        # Botão de buscar
        buscar_btn = QPushButton('Encontrar Filmes')
        buscar_btn.clicked.connect(self.buscar_filmes)
        layout.addWidget(buscar_btn)
        
        # Área de resultados com scroll
        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
    def buscar_filmes(self):
        # Limpa resultados anteriores
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)
        
        # Verifica se um estado emocional foi selecionado
        if self.humor_combo.currentIndex() == 0:
            QMessageBox.warning(self, 'Aviso', 'Por favor, selecione um estado emocional.')
            return
        
        # Mapeamento de estados emocionais para palavras-chave de busca
        filmes_por_estado = {
            'Feliz': ['comedy', 'adventure', 'musical'],
            'Motivado': ['inspiring', 'sports', 'success'],
            'Romantico': ['romance', 'love', 'relationship'],
            'Reflexivo': ['drama', 'psychological', 'indie'],
            'Aventureiro': ['action', 'adventure', 'thriller'],
            'Assustado': ['horror', 'psychological', 'thriller']
        }
        
        estado = self.humor_combo.currentText()
        
        try:
            # Lista para armazenar filmes encontrados
            filmes_encontrados = []
            
            # Busca filmes para cada palavra-chave
            for palavra_chave in filmes_por_estado[estado]:
                url = f"http://www.omdbapi.com/?apikey=649253f7&s={palavra_chave}&type=movie"
                resposta = requests.get(url)
                dados = resposta.json()
                
                # Adiciona filmes encontrados à lista
                if dados.get('Search'):
                    for filme in dados['Search'][:5]:
                        # Busca detalhes de cada filme
                        detalhes_url = f"http://www.omdbapi.com/?apikey=649253f7&i={filme['imdbID']}&plot=full"
                        detalhes_resposta = requests.get(detalhes_url)
                        detalhes_filme = detalhes_resposta.json()
                        
                        # Adiciona à lista de filmes
                        filmes_encontrados.append(detalhes_filme)
            
            # Se nenhum filme for encontrado
            if not filmes_encontrados:
                QMessageBox.warning(self, 'Aviso', 'Nenhum filme encontrado para este estado emocional.')
                return
            
            # Adiciona filmes à área de scroll
            for filme in filmes_encontrados:
                filme_widget = FilmeWidget(filme)
                self.scroll_layout.addWidget(filme_widget)
        
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro na busca: {str(e)}')

def main():
    app = QApplication(sys.argv)
    selector = MovieMoodSelector()
    selector.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()