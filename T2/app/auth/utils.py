import re

def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica tamanho e dígitos repetidos
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calcular_digito(digs, peso_inicial):
        soma = 0
        for i, digito in enumerate(digs):
            soma += int(digito) * (peso_inicial - i)
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # Cálculo do primeiro dígito verificador (pesos de 10 a 2)
    d1 = calcular_digito(cpf[:9], 10)
    
    # Cálculo do segundo dígito verificador (pesos de 11 a 2)
    d2 = calcular_digito(cpf[:10], 11)
    
    # Verifica se os dígitos calculados batem com os informados
    return cpf[-2:] == d1 + d2

def validar_email_ufes(email):
    return (email.endswith('@ufes.br') or email.endswith('@edu.ufes.br'))