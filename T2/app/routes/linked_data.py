# app/semantic/routes.py
from flask import Blueprint, jsonify, session
from rdflib import Graph, Namespace, Literal, URIRef, RDF
from app.models import Visita, Curso, Workshop, Apresentacao, User
from app.auth.decorators import login_required
import requests

semantic_bp = Blueprint('semantic', __name__)

# Namespaces para RDF
EX = Namespace("http://connect.com.br/")
SCHEMA = Namespace("http://schema.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

@semantic_bp.route('/dbpedia/<string:activity_type>/<int:activity_id>')
@login_required
def dbpedia_activity_info(activity_type, activity_id):
    """Retorna informações da DBpedia para uma atividade específica"""
    activity_map = {
        'curso': Curso,
        'visita': Visita,
        'workshop': Workshop,
        'apresentacao': Apresentacao
    }
    
    activity_class = activity_map.get(activity_type)
    if not activity_class:
        return jsonify({'error': 'Tipo de atividade inválido'}), 400
    
    activity = activity_class.query.get_or_404(activity_id)
    
    dbpedia_info = get_dbpedia_info(activity.nome, lang='pt')
    
    if dbpedia_info:
        abstract = dbpedia_info.get('abstract', {}).get('value', '')
        thumbnail = dbpedia_info.get('thumbnail', {}).get('value', '')
        
        return jsonify({
            'abstract': abstract,
            'thumbnail': thumbnail,
            'activity_name': activity.nome
        })
    else:
        return jsonify({
            'abstract': None,
            'thumbnail': None,
            'message': f'Nenhuma informação encontrada na DBpedia para "{activity.nome}"'
        })

def generate_activity_rdf(activity, activity_type):
    """Gera dados RDF para uma atividade"""
    g = Graph()
    g.namespace_manager.bind("ex", EX, override=True)
    g.namespace_manager.bind("schema", SCHEMA, override=True)
    g.namespace_manager.bind("foaf", FOAF, override=True)
    
    activity_uri = EX[f"{activity_type}/{activity.id}"]
    g.add((activity_uri, RDF.type, SCHEMA.Event))
    g.add((activity_uri, SCHEMA.name, Literal(activity.nome, lang="pt")))
    
    if activity.descricao:
        g.add((activity_uri, SCHEMA.description, Literal(activity.descricao, lang="pt")))
    
    if hasattr(activity, 'data'):
        g.add((activity_uri, SCHEMA.startDate, Literal(activity.data.isoformat())))
    
    if hasattr(activity, 'local') and activity.local:
        g.add((activity_uri, SCHEMA.location, Literal(activity.local, lang="pt")))
    
    return g

@semantic_bp.route('/rdf/user/activities')
@login_required
def user_activities_rdf():
    """Gera RDF com todas as atividades do usuário"""
    user_id = session['user']['id']
    user = User.query.get(user_id)
    
    g = Graph()
    g.namespace_manager.bind("ex", EX, override=True)
    g.namespace_manager.bind("schema", SCHEMA, override=True)
    g.namespace_manager.bind("foaf", FOAF, override=True)
    
    user_uri = EX[f"user/{user.id}"]
    g.add((user_uri, RDF.type, FOAF.Person))
    g.add((user_uri, FOAF.name, Literal(user.name)))
    
    # Adiciona atividades inscritas com schema:attendee
    for curso in user.cursos_inscritos:
        curso_uri = EX[f"curso/{curso.id}"]
        g.add((curso_uri, RDF.type, SCHEMA.Event))
        g.add((curso_uri, SCHEMA.name, Literal(curso.nome, lang="pt")))
        g.add((curso_uri, SCHEMA.attendee, user_uri))
    
    for visita in user.visitas_inscritas:
        visita_uri = EX[f"visita/{visita.id}"]
        g.add((visita_uri, RDF.type, SCHEMA.Event))
        g.add((visita_uri, SCHEMA.name, Literal(visita.nome, lang="pt")))
        g.add((visita_uri, SCHEMA.attendee, user_uri))
    
    for workshop in user.workshops_inscritos:
        workshop_uri = EX[f"workshop/{workshop.id}"]
        g.add((workshop_uri, RDF.type, SCHEMA.Event))
        g.add((workshop_uri, SCHEMA.name, Literal(workshop.nome, lang="pt")))
        g.add((workshop_uri, SCHEMA.attendee, user_uri))
    
    for apresentacao in user.apresentacoes_inscritas:
        apresentacao_uri = EX[f"apresentacao/{apresentacao.id}"]
        g.add((apresentacao_uri, RDF.type, SCHEMA.Event))
        g.add((apresentacao_uri, SCHEMA.name, Literal(apresentacao.nome, lang="pt")))
        g.add((apresentacao_uri, SCHEMA.attendee, user_uri))
    
    return g.serialize(format='turtle'), 200, {
        'Content-Type': 'text/turtle',
        'Content-Disposition': 'attachment; filename=minhas_atividades.ttl'
    }

@semantic_bp.route('/rdf/activity/<string:activity_type>/<int:activity_id>')
@login_required
def activity_rdf(activity_type, activity_id):
    """Gera RDF para uma atividade específica"""
    activity_map = {
        'curso': Curso,
        'visita': Visita,
        'workshop': Workshop,
        'apresentacao': Apresentacao
    }
    
    activity_class = activity_map.get(activity_type)
    if not activity_class:
        return jsonify({'error': 'Tipo de atividade inválido'}), 400
    
    activity = activity_class.query.get_or_404(activity_id)
    g = generate_activity_rdf(activity, activity_type)
    
    return g.serialize(format='turtle'), 200, {
        'Content-Type': 'text/turtle',
        'Content-Disposition': f'attachment; filename={activity_type}_{activity_id}.ttl'
    }

import requests
import re

# Namespaces para RDF
EX = Namespace("http://connect.com.br/")
SCHEMA = Namespace("http://schema.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DBPEDIA = Namespace("http://dbpedia.org/resource/")
DBPEDIA_ONTOLOGY = Namespace("http://dbpedia.org/ontology/")

def extract_keywords(topic_name):
    """Extrai palavras-chave relevantes removendo termos genéricos"""
    stop_words = ['curso', 'workshop', 'oficina', 'palestra', 'visita', 
                 'técnica', 'técnico', 'apresentação', 'de', 'em', 'para',
                 'básico', 'avançado', 'introdução', 'fundamentos', 'sobre',
                 'programação', 'desenvolvimento', 'aprendizado']
    
    # Remove caracteres especiais e divide em palavras
    words = re.findall(r'\b[a-záàâãéèêíïóôõöúçñ]+\b', topic_name.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords

def query_dbpedia_sparql(search_term, lang='pt'):
    """Executa consulta SPARQL na DBpedia"""
    try:
        # Endpoint SPARQL da DBpedia
        sparql_endpoint = "https://dbpedia.org/sparql"
        
        formatted_term = search_term.strip().replace(" ", "_")
        # Query SPARQL para buscar abstract e thumbnail
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>

        SELECT DISTINCT ?abstract ?thumbnail
        WHERE {{
          dbr:{formatted_term} dbo:abstract ?abstract .
          FILTER (LANG(?abstract) = '{lang}' || LANG(?abstract) = 'en')
          OPTIONAL {{ dbr:{formatted_term} dbo:thumbnail ?thumbnail }}
        }}
        LIMIT 1
        """
        
        # Parâmetros da requisição
        params = {
            'query': query,
            'format': 'json',
            'timeout': 10000  # 10 segundos
        }
        
        headers = {
            'Accept': 'application/sparql-results+json'
        }
        
        print(f"🔍 Executando consulta SPARQL para: {search_term}")
        response = requests.get(sparql_endpoint, params=params, headers=headers, timeout=4)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {}).get('bindings', [])
            
            if results:
                result = results[0]
                abstract = result.get('abstract', {}).get('value') if 'abstract' in result else None
                thumbnail = result.get('thumbnail', {}).get('value') if 'thumbnail' in result else None
                
                if abstract:
                    print(f"✅ SPARQL encontrou abstract: {abstract[:100]}...")
                    return {
                        'abstract': {'value': abstract},
                        'thumbnail': {'value': thumbnail} if thumbnail else None
                    }
        
        print("❌ SPARQL não retornou resultados")
        return None
        
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout na consulta SPARQL para: {search_term}")
        return None
    except Exception as e:
        print(f"❌ Erro na consulta SPARQL para {search_term}: {e}")
        return None

def query_dbpedia_rest(search_term, lang='pt'):
    """Executa a consulta na DBpedia usando API REST (fallback)"""
    try:
        formatted_search_term = search_term.capitalize()
        print(f"🔄 Fallback para API REST: {formatted_search_term}")
        
        # Prepara o termo para URL - substitui espaços por underscores
        formatted_term = formatted_search_term.replace(' ', '_')
        
        # URL da API REST da DBpedia
        url = f"http://dbpedia.org/data/{formatted_term}.json"
        
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Debug: mostra as primeiras chaves
            print(f"Chaves encontradas: {list(data.keys())[:5]}")
            
            # Tenta encontrar o recurso principal correto
            resource_uri = None
            expected_resource = f"http://dbpedia.org/resource/{formatted_term}"
            
            # Primeiro tenta encontrar o recurso exato
            if expected_resource in data:
                resource_uri = expected_resource
            else:
                # Se não encontrar, procura por qualquer recurso que contenha o termo
                for key in data.keys():
                    if 'dbpedia.org/resource/' in key and formatted_term.lower() in key.lower():
                        resource_uri = key
                        break
            
            if resource_uri:
                print(f"Recurso selecionado: {resource_uri}")
                resource_data = data[resource_uri]
                
                # Verifica se é uma página de desambiguação
                is_disambiguation = False
                for key in resource_data.keys():
                    if 'wikiPageDisambiguates' in key or 'disambiguates' in key.lower():
                        is_disambiguation = True
                        break
                
                if is_disambiguation:
                    print("⚠️  É uma página de desambiguação, buscando opções...")
                    # Para páginas de desambiguação, tenta encontrar a opção mais relevante
                    return handle_disambiguation_page(data, search_term, lang)
                
                # Extrai informações - procura por diferentes formatos de chave
                abstract_found = None
                thumbnail_found = None
                description_found = None
                
                for key, value in resource_data.items():
                    # Procura por abstract
                    if 'abstract' in key.lower():
                        for item in value:
                            if item.get('lang') == lang:
                                abstract_found = item['value']
                                break
                            elif item.get('lang') == 'en' and not abstract_found:
                                abstract_found = item['value']
                    
                    # Procura por description
                    elif 'description' in key.lower() and not abstract_found:
                        for item in value:
                            if item.get('lang') == lang:
                                description_found = item['value']
                                break
                            elif item.get('lang') == 'en' and not description_found:
                                description_found = item['value']
                    
                    # Procura por thumbnail
                    elif 'thumbnail' in key.lower() and value and not thumbnail_found:
                        thumbnail_found = value[0]['value']
                
                # Usa description se abstract não foi encontrado
                final_abstract = abstract_found or description_found
                
                if final_abstract:
                    result = {'abstract': {'value': final_abstract}}
                    if thumbnail_found:
                        result['thumbnail'] = {'value': thumbnail_found}
                    
                    print(f"✅ REST encontrou abstract: {final_abstract[:100]}...")
                    return result
            else:
                print("❌ Recurso não encontrado na resposta REST")
                return None
        
        else:
            print(f"❌ Status code REST: {response.status_code}")
            return None
        
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout na consulta REST para: {search_term}")
        return None
    except Exception as e:
        print(f"❌ Erro na consulta REST para {search_term}: {e}")
        return None

def query_dbpedia_with_timeout(search_term, lang='pt'):
    """Executa consulta com timeout: primeiro tenta SPARQL, depois REST"""
    # Primeiro tenta SPARQL
    sparql_result = query_dbpedia_sparql(search_term, lang)
    if sparql_result:
        return sparql_result
    
    # Se SPARQL falhar ou timeout, tenta REST
    rest_result = query_dbpedia_rest(search_term, lang)
    return rest_result

def handle_disambiguation_page(data, search_term, lang):
    """Lida com páginas de desambiguação da DBpedia"""
    try:
        # Procura por opções de desambiguação
        possible_options = []
        
        for resource_uri, resource_data in data.items():
            if 'dbpedia.org/resource/' in resource_uri:
                # Verifica se tem label para identificar o tipo
                label = None
                abstract = None
                
                for key, value in resource_data.items():
                    if 'label' in key.lower():
                        for item in value:
                            if item.get('lang') == lang or item.get('lang') == 'en':
                                label = item['value']
                                break
                    
                    if 'abstract' in key.lower():
                        for item in value:
                            if item.get('lang') == lang or item.get('lang') == 'en':
                                abstract = item['value']
                                break
                
                if label and abstract:
                    possible_options.append({
                        'uri': resource_uri,
                        'label': label,
                        'abstract': abstract
                    })
        
        # Ordena por relevância (tenta encontrar a opção mais provável)
        if possible_options:
            # Prioriza opções que contenham o termo de busca no label
            for option in possible_options:
                if search_term.lower() in option['label'].lower():
                    print(f"✅ Encontrado em desambiguação: {option['label']}")
                    return {'abstract': {'value': option['abstract']}}
            
            # Se não encontrar, retorna a primeira opção
            print(f"✅ Usando primeira opção de desambiguação: {possible_options[0]['label']}")
            return {'abstract': {'value': possible_options[0]['abstract']}}
        
        return None
        
    except Exception as e:
        print(f"Erro ao processar desambiguação: {e}")
        return None
    
def is_valid_search_term(term):
    """Verifica se o termo é válido para busca na DBpedia"""
    if not term or len(term.strip()) < 2:
        return False
    
    # Termos muito comuns que não devem ser buscados
    common_terms = {'curso', 'workshop', 'oficina', 'palestra', 'visita', 'técnica', 'apresentação'}
    if term.lower() in common_terms:
        return False
    
    # Não busca números isolados
    if term.isdigit():
        return False
    
    return True

def get_dbpedia_info(topic_name, lang='pt'):
    """Função principal que obtém informações da DBpedia"""
    if not topic_name or len(topic_name.strip()) < 2:
        return None
    
    clean_topic = topic_name.strip()
    
    # Remove termos genéricos do início
    clean_topic = re.sub(r'^(apresentação|curso|workshop|oficina|palestra|aula|visita)\s+', '', clean_topic, flags=re.IGNORECASE)
    
    # Tenta diferentes variações
    variations = [
        clean_topic,
        clean_topic + " (programming language)",
    ]
    
    for variation in variations:
        result = query_dbpedia_with_timeout(variation, lang)
        if result:
            return result
    
    # Se não encontrar, tenta palavras-chave
    keywords = extract_keywords(clean_topic)
    if keywords:
        # Tenta combinação de palavras-chave
        combined_keywords = " ".join(keywords)
        result = query_dbpedia_with_timeout(combined_keywords, lang)
        if result:
            return result
        
        # Tenta cada palavra-chave individualmente (da mais longa para a mais curta)
        keywords.sort(key=len, reverse=True)
        for keyword in keywords:
            if len(keyword) > 3 and is_valid_search_term(keyword):
                result = query_dbpedia_with_timeout(keyword, lang)
                if result:
                    return result
    
    return None