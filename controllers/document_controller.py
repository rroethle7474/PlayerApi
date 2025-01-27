from flask import Blueprint, jsonify, request, current_app, g
import requests
from bs4 import BeautifulSoup
import uuid
import os
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os

document_bp = Blueprint('document', __name__)

# Store the PineconeService instance
pinecone_service = None
@document_bp.record
def record_params(setup_state):
    global pinecone_service
    app = setup_state.app
    pinecone_service = app.services.get('pinecone_service')
    

def create_document(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        document = {
            "id": str(uuid.uuid4()),
            "url": url,
            "title": soup.title.string if soup.title else "No title",
            "html_content": response.text,
            "text_content": soup.get_text(),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "headers": dict(response.headers),
                "status_code": response.status_code
            }
        }
        
        # Get PineconeService instance
        pinecone_service = current_app.services.get('pinecone_service')
        
        # Create embedding for the document
        embedding = pinecone_service.create_embedding(document['text_content'])
        
        # Store the embedding in Pinecone
        pinecone_service.upsert_vector(document['id'], embedding, {
            "url": document['url'],
            "title": document['title'],
            "timestamp": document['metadata']['timestamp']
        })
        
        return document, soup
    except requests.RequestException as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}, None
    except Exception as e:
        return {"error": f"Error processing document: {str(e)}"}, None

def crawl_and_save(base_url, current_url, folder_name, current_level, max_levels, visited_urls):
    if current_level > max_levels or current_url in visited_urls:
        return []

    visited_urls.add(current_url)
    document, soup = create_document(current_url)
    print("IN", visited_urls)
    if 'error' in document:
        return [document]

    save_result = save_document(document, folder_name)
    results = [{"url": current_url, "save_result": save_result}]

    if soup:
        links = soup.find_all('a', href=True)
        links = links[:10]
        for link in links:
            print("LINK", link['href'])
            next_url = urljoin(current_url, link['href'])
            # this is useless, need to figure out a better way to scrape an entire website
            if urlparse(next_url).netloc == urlparse(base_url).netloc:
                print("NOT COOL IF I AM HERE", next_url)
                results.extend(crawl_and_save(base_url, next_url, folder_name, current_level + 1, max_levels, visited_urls))

    return results

def create_document(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        document = {
            "id": str(uuid.uuid4()),
            "url": url,
            "title": soup.title.string if soup.title else "No title",
            "html_content": response.text,
            "text_content": soup.get_text(),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "headers": dict(response.headers),
                "status_code": response.status_code
            }
        }
        return document, soup
    except requests.RequestException as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}, None
    except Exception as e:
        return {"error": f"Error processing document: {str(e)}"}, None

def save_document(document, folder_name, file_name=None):
    try:
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        if file_name == None:
            file_name = str(uuid.uuid4())
        
        # Generate a filename based on the document's ID
        filename = f"{file_name}.json"
        file_path = os.path.join(folder_name, filename)
        
        # Save the document as a JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=4)
        
        return {"message": f"Document saved successfully as {file_path}"}
    except Exception as e:
        return {"error": f"Failed to save document: {str(e)}"}

@document_bp.route('/create_document/<path:url>', methods=['GET'])
def create_document_param(url):
    document = create_document(url)
    return jsonify(document)

@document_bp.route('/create_document', methods=['GET'])
def create_document_query():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is missing"}), 400
    document = create_document(url)
    return jsonify(document)

@document_bp.route('/create_document', methods=['POST'])
def create_document_post():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "URL is missing in the request body"}), 400
    if 'folder_name' not in data:
        return jsonify({"error": "folder_name is missing in the request body"}), 400
    if 'file_name' not in data:
        return jsonify({"error": "file_name is missing in the request body"}), 400
    
    
    
    document = create_document(data['url'])
    if 'error' in document:
        return jsonify(document), 400
    
    save_result = save_document(document, data['folder_name'], data['file_name'])
    if 'error' in save_result:
        return jsonify(save_result), 500
    
    # Return a summary without the full HTML content to keep the response manageable
    summary = {k: v for k, v in document.items() if k != 'html_content'}
    summary['html_content'] = "HTML content saved (not shown in response)"
    
    return jsonify({**summary, **save_result})

@document_bp.route('/crawl_and_save', methods=['POST'])
def crawl_and_save_route():
    data = request.json
    if not data or 'url' not in data or 'folder_name' not in data or 'levels' not in data:
        return jsonify({"error": "Missing required parameters"}), 400

    url = data['url']
    folder_name = data['folder_name']
    levels = int(data['levels'])

    if levels < 1:
        return jsonify({"error": "Levels must be a positive integer"}), 400

    results = crawl_and_save(url, url, folder_name, 1, levels, set())

    return jsonify({"results": results})

@document_bp.route('/query_similar', methods=['POST'])
def query_similar_documents():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Query is missing in the request body"}), 400
    
    query = data['query']
    top_k = data.get('top_k', 5)  # Default to top 5 results if not specified
    
    pinecone_service = current_app.services.get('pinecone_service')
    
    # Create embedding for the query
    query_embedding = pinecone_service.create_embedding(query)
    
    # Query Pinecone for similar documents
    results = pinecone_service.query_vectors(query_embedding, top_k=top_k)
    
    # Format the results
    formatted_results = []
    for match in results['matches']:
        formatted_results.append({
            "id": match['id'],
            "score": match['score'],
            "url": match['metadata']['url'],
            "title": match['metadata']['title'],
            "timestamp": match['metadata']['timestamp']
        })
    
    return jsonify({"results": formatted_results})