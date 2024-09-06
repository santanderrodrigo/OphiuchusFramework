
class Helpers:
    #sanitizamos el texto para poder imprimirlo en el navegador
    @staticmethod
    def sanitize_text(text):
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text