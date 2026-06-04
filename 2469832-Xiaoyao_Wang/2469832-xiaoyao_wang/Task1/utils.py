import os
import json
import sqlite3
import subprocess
import requests
import time
import base64
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def load_environment():
    """Load environment variables from .env if available."""
    # 使用 utils.py 文件所在目录作为基准路径，而不是当前工作目录
    root = Path(__file__).parent
    dotenv_path = root / '.env'
    try:
        from dotenv import load_dotenv
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path)
            print(f'✅ Loaded environment from {dotenv_path}')
        else:
            # 如果当前目录没有找到，尝试上级目录
            dotenv_path = root.parent / '.env'
            if dotenv_path.exists():
                load_dotenv(dotenv_path=dotenv_path)
                print(f'✅ Loaded environment from {dotenv_path}')
            else:
                print('ℹ️ No .env file found')
    except ImportError:
        print('ℹ️ python-dotenv not installed')


def get_llm_client(model: str = 'openai/gpt-5.2'):
    """Return a callable that sends prompts to an external LLM API."""
    base_url = os.getenv('FREEAPI_URL', 'https://api.apifree.ai/v1/chat/completions')
    api_key = os.getenv('FREEAPI_KEY', '')
    
    if not base_url or not api_key:
        print('⚠️ FREEAPI_URL or FREEAPI_KEY not set - using mock client')
        return create_mock_llm_client()

    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

    def call_llm(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.7
        }
        if context:
            payload['context'] = context
        try:
            resp = requests.post(base_url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            return {'success': True, 'text': result.get('choices', [{}])[0].get('message', {}).get('content', '')}
        except Exception as e:
            print(f'❌ LLM API error: {e}')
            return {'success': False, 'error': str(e)}

    return call_llm


def create_mock_llm_client():
    """Create a mock LLM client for development/testing."""
    def mock_llm(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if 'problem statement' in prompt.lower():
            return {'success': True, 'text': 'Create a marketplace ordering system that allows customers to browse stalls, add items to cart, and checkout. The system should split orders by stall automatically.'}
        elif 'user stories' in prompt.lower():
            return {'success': True, 'text': json.dumps([
                {'id': 1, 'role': 'Customer', 'goal': 'Browse stalls and view products', 'benefit': 'Find products from multiple vendors'},
                {'id': 2, 'role': 'Customer', 'goal': 'Add items to cart and checkout', 'benefit': 'Complete purchase from multiple stalls in one order'},
                {'id': 3, 'role': 'Merchant', 'goal': 'View and manage orders', 'benefit': 'Process orders efficiently'},
                {'id': 4, 'role': 'System', 'goal': 'Split orders by stall', 'benefit': 'Automated order routing'}
            ])}
        elif 'requirements' in prompt.lower():
            return {'success': True, 'text': '\n'.join([
                '- User authentication (register/login/logout)',
                '- Browse stalls and products',
                '- Shopping cart functionality',
                '- Order splitting by stall',
                '- Merchant dashboard for order management',
                '- Auto-generated order flow diagram',
                '- REST API endpoints for all operations'
            ])}
        elif 'plantuml' in prompt.lower() or 'uml' in prompt.lower():
            return {'success': True, 'text': '''@startuml
actor Customer
actor Merchant
rectangle "Marketplace System" {
  usecase "Browse Stalls" as UC1
  usecase "Add to Cart" as UC2
  usecase "Checkout" as UC3
  usecase "Split Order" as UC4
  usecase "View Orders" as UC5
}
Customer --> UC1
Customer --> UC2
Customer --> UC3
UC3 --> UC4
Merchant --> UC5
@enduml'''}
        elif 'flask' in prompt.lower() or 'api' in prompt.lower():
            return {'success': True, 'text': '''from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/stalls', methods=['GET'])
def get_stalls():
    return jsonify([{'id': 'stall1', 'name': 'Fresh Market'}])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''}
        elif 'html' in prompt.lower() or 'website' in prompt.lower():
            return {'success': True, 'text': '''<!DOCTYPE html>
<html>
<head><title>Marketplace</title></head>
<body>
    <h1>🏪 Welcome to Marketplace</h1>
    <div id="stalls">Loading stalls...</div>
</body>
</html>'''}
        else:
            return {'success': True, 'text': 'This is a mock response from the LLM. For real AI generation, set FREEAPI_URL and FREEAPI_KEY in .env.'}
    
    return mock_llm


def setup_llm_client(model: str = 'openai/gpt-5.2'):
    """Setup and return LLM client with provider info."""
    client = get_llm_client(model)
    if os.getenv('FREEAPI_KEY'):
        return client, model, 'FreeAPI'
    return client, model, 'Mock'


def generate_problem_statement(business_problem: str, client) -> str:
    """Generate a clear problem statement from business description."""
    prompt = f"""Given the business problem below, generate one clear and concise problem statement:

Business Problem: {business_problem}

Return only the problem statement, no extra text."""
    
    result = client(prompt)
    return result.get('text', business_problem) if result.get('success') else business_problem


def generate_user_stories(problem_statement: str, client) -> List[Dict[str, Any]]:
    """Generate user stories from problem statement."""
    prompt = f"""Generate 4-6 user stories based on this problem statement:

Problem Statement: {problem_statement}

Return ONLY valid JSON with this schema:
{{
  "user_stories": [
    {{
      "id": 1,
      "role": "<role>",
      "goal": "<goal>",
      "benefit": "<benefit>",
      "acceptance_criteria": ["<criteria>", "<criteria>"]
    }}
  ]
}}"""
    
    result = client(prompt)
    if result.get('success'):
        try:
            return json.loads(result['text']).get('user_stories', [])
        except:
            pass
    return []


def generate_requirements(problem_statement: str, user_stories: List[Dict[str, Any]], client) -> str:
    """Generate requirements document."""
    stories_text = json.dumps(user_stories, indent=2, ensure_ascii=False)
    prompt = f"""Write a PRD (Product Requirements Document) with these headings:

## Overview
## Goals
## Non-Goals
## User Personas (brief)
## Key Features
## User Flows
## Functional Requirements
## Non-Functional Requirements

Problem Statement: {problem_statement}
User Stories: {stories_text}

Keep each section concise with 2-4 bullet points."""
    
    result = client(prompt)
    return result.get('text', '') if result.get('success') else ''


def generate_plantuml_diagram(user_stories: List[Dict[str, Any]], client, diagram_type: str = 'use_case') -> str:
    """Generate PlantUML diagram from user stories."""
    stories_text = json.dumps(user_stories, indent=2, ensure_ascii=False)
    
    prompt = f"""Generate a {diagram_type} diagram in PlantUML format based on these user stories:

{stories_text}

Use standard UML notation. Return ONLY the PlantUML code between @startuml and @enduml."""
    
    result = client(prompt)
    if result.get('success'):
        text = result['text']
        if '@startuml' not in text:
            text = '@startuml\n' + text + '\n@enduml'
        return text
    return ''


def generate_flask_api(user_stories: List[Dict[str, Any]], client) -> str:
    """Generate Flask API code from user stories."""
    stories_text = json.dumps(user_stories, indent=2, ensure_ascii=False)
    
    prompt = f"""Generate a complete Flask REST API application based on these user stories:

{stories_text}

Requirements:
1. Use Flask with jsonify, request, session
2. Include CORS support
3. Use in-memory storage for simplicity
4. Include endpoints for all CRUD operations
5. Add proper error handling
6. Include health check endpoint

Return ONLY the Python code, no explanations."""
    
    result = client(prompt)
    return result.get('text', '') if result.get('success') else ''


def generate_website(user_stories: List[Dict[str, Any]], client) -> str:
    """Generate HTML website from user stories."""
    stories_text = json.dumps(user_stories, indent=2, ensure_ascii=False)
    
    prompt = f"""Generate a complete HTML website that integrates with the marketplace API:

{stories_text}

Requirements:
1. Use Bootstrap 5 for styling via CDN
2. Include responsive design
3. Show stalls and products
4. Include shopping cart functionality
5. Use Fetch API for AJAX calls
6. Display auto-generated image

Return ONLY the HTML code, no explanations."""
    
    result = client(prompt)
    return result.get('text', '') if result.get('success') else ''


def generate_image(output_path: str, prompt: str = None) -> Path:
    """Generate an image using AI image generation API or create placeholder."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_url = os.getenv('FREEIMAGE_URL')
    api_key = os.getenv('FREEAPI_KEY')
    
    if image_url and api_key and prompt:
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'prompt': prompt,
                'model': 'dall-e-3',
                'n': 1,
                'size': '1024x1024'
            }
            print(f'🔄 Calling image API: {image_url}')
            print(f'📝 Prompt: {prompt[:100]}...')
            resp = requests.post(image_url, headers=headers, json=payload, timeout=60)
            print(f'📊 Response status: {resp.status_code}')
            
            if resp.status_code == 200:
                result = resp.json()
                if 'data' in result and len(result['data']) > 0:
                    image_url = result['data'][0].get('url')
                    if image_url:
                        # Download the image from the URL
                        img_resp = requests.get(image_url, timeout=30)
                        with open(output_path, 'wb') as f:
                            f.write(img_resp.content)
                        print(f'✅ Image generated and saved: {output_path}')
                        return output_path
                    else:
                        print('⚠️ Image URL not found in response')
                elif 'url' in result:
                    # Alternative response format
                    image_url = result.get('url')
                    img_resp = requests.get(image_url, timeout=30)
                    with open(output_path, 'wb') as f:
                        f.write(img_resp.content)
                    print(f'✅ Image generated and saved: {output_path}')
                    return output_path
                else:
                    print(f'⚠️ Unexpected response format: {result}')
            else:
                print(f'⚠️ Image API returned error: {resp.status_code} - {resp.text[:200]}')
                
        except Exception as e:
            print(f'⚠️ Image API failed: {e}')

    # Create placeholder image with flowchart pattern
    img = Image.new('RGB', (1024, 768), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font_text = ImageFont.truetype("arial.ttf", 18)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Draw flowchart pattern
    draw.rectangle([50, 50, 200, 120], fill=(100, 149, 237), outline='black')
    draw.text((125, 85), 'Start', fill='white', font=font_text, anchor='mm')
    
    draw.polygon([200, 85, 230, 60, 230, 110], fill='black')
    
    draw.rectangle([250, 30, 450, 140], fill=(240, 248, 255), outline='black')
    draw.text((350, 85), 'Browse Stalls', fill='black', font=font_text, anchor='mm')
    
    draw.polygon([450, 85, 480, 60, 480, 110], fill='black')
    
    draw.rectangle([500, 30, 700, 140], fill=(240, 248, 255), outline='black')
    draw.text((600, 85), 'Add to Cart', fill='black', font=font_text, anchor='mm')
    
    draw.polygon([700, 85, 730, 60, 730, 110], fill='black')
    
    draw.rectangle([750, 30, 950, 140], fill=(240, 248, 255), outline='black')
    draw.text((850, 85), 'Checkout', fill='black', font=font_text, anchor='mm')
    
    draw.polygon([950, 85, 980, 60, 980, 110], fill='black')
    
    draw.ellipse([990, 50, 1024, 120], fill=(60, 179, 113), outline='black')
    draw.text((1007, 85), 'Split', fill='white', font=font_text, anchor='mm')
    
    # Draw sub-order flow
    draw.rectangle([300, 180, 480, 250], fill=(255, 228, 225), outline='black')
    draw.text((390, 215), 'Stall A', fill='black', font=font_text, anchor='mm')
    
    draw.rectangle([520, 180, 700, 250], fill=(255, 228, 225), outline='black')
    draw.text((610, 215), 'Stall B', fill='black', font=font_text, anchor='mm')
    
    draw.rectangle([740, 180, 920, 250], fill=(255, 228, 225), outline='black')
    draw.text((830, 215), 'Stall C', fill='black', font=font_text, anchor='mm')
    
    # Draw status aggregation
    draw.polygon([300, 250, 315, 275, 285, 275], fill='black')
    draw.polygon([520, 250, 535, 275, 505, 275], fill='black')
    draw.polygon([740, 250, 755, 275, 725, 275], fill='black')
    
    draw.rectangle([400, 290, 824, 360], fill=(144, 238, 144), outline='black')
    draw.text((612, 325), 'Status Aggregation', fill='black', font=font_text, anchor='mm')
    
    draw.polygon([612, 360, 627, 385, 597, 385], fill='black')
    
    draw.ellipse([562, 400, 662, 470], fill=(100, 149, 237), outline='black')
    draw.text((612, 435), 'End', fill='white', font=font_title, anchor='mm')
    
    # Title
    draw.text((512, 520), 'Marketplace Order Splitting Flowchart', fill=(60, 60, 100), font=font_title, anchor='mm')
    draw.text((512, 560), '(Generated with placeholder - Image API unavailable)', fill=(120, 120, 140), font=font_text, anchor='mm')
    
    img.save(output_path)
    print(f'✅ Flowchart placeholder created: {output_path}')
    return output_path


def generate_mermaid_diagram(user_stories: List[Dict[str, Any]], client) -> str:
    """Generate Mermaid flowchart from user stories using LLM."""
    stories_text = json.dumps(user_stories, indent=2, ensure_ascii=False)
    
    prompt = f"""Generate a detailed Mermaid flowchart for a marketplace order splitting system based on these user stories:

{stories_text}

Include these key steps:
1. Customer browsing stalls
2. Adding items to cart
3. Checkout process
4. Order splitting by stall
5. Merchant processing sub-orders
6. Status aggregation back to customer

Return ONLY the Mermaid code (without markdown code blocks)."""
    
    result = client(prompt)
    if result.get('success'):
        text = result['text'].strip()
        # Clean up markdown code blocks if present
        text = text.replace('```mermaid', '').replace('```', '').strip()
        if not text.startswith('flowchart'):
            text = 'flowchart TD\n' + text
        return text
    return ''


def render_plantuml_diagram(puml_code: str, output_path: str) -> Path:
    """Render PlantUML diagram to image.
    
    Supports multiple rendering methods:
    1. Local PlantUML JAR (if PLANTUML_JAR env var is set)
    2. Online PlantUML API (default fallback)
    3. Placeholder image (last resort)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    puml_path = output_path.with_suffix('.puml')
    with open(puml_path, 'w', encoding='utf-8') as f:
        f.write(puml_code)
    
    # Method 1: Try local PlantUML JAR
    plantuml_jar = os.getenv('PLANTUML_JAR')
    if plantuml_jar and Path(plantuml_jar).exists():
        try:
            subprocess.run(
                ['java', '-jar', plantuml_jar, '-tpng', str(puml_path)],
                capture_output=True, timeout=60
            )
            print(f'✅ Diagram rendered with PlantUML JAR: {output_path}')
            return output_path
        except Exception as e:
            print(f'⚠️ PlantUML JAR failed: {e}')
    
    # Method 2: Try online PlantUML API (using PlantUML's deflate+base64 encoding)
    try:
        import zlib
        import base64
        
        compressed = zlib.compress(puml_code.encode('utf-8'))[2:-4]
        encoded = base64.b64encode(compressed).decode('ascii')
        encoded = encoded.replace('+', '-').replace('/', '_').replace('=', '')
        plantuml_url = f'https://www.plantuml.com/plantuml/png/{encoded}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/png,*/*'
        }
        resp = requests.get(plantuml_url, headers=headers, timeout=30)
        
        if resp.status_code in [200, 400] and len(resp.content) > 1000 and resp.content[:4] == b'\x89PNG':
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            print(f'✅ Diagram rendered with online PlantUML API: {output_path}')
            return output_path
        else:
            print(f'⚠️ Online PlantUML API returned status {resp.status_code}, size {len(resp.content)}')
    except Exception as e:
        print(f'⚠️ Online PlantUML API failed: {e}')
    
    # Method 3: Create placeholder image
    img = Image.new('RGB', (800, 600), color=(250, 250, 255))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 18)
        font_text = ImageFont.truetype("arial.ttf", 12)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    draw.text((400, 30), '📊 PlantUML Diagram', fill=(30, 30, 80), font=font_title, anchor='mm')
    
    lines = [
        'PlantUML Source:',
        puml_path.name,
        '',
        'To render this diagram:',
        '1. Install Java',
        '2. Download PlantUML JAR',
        '3. Set PLANTUML_JAR env var',
        '',
        'Or use online renderer:',
        'https://www.plantuml.com/plantuml'
    ]
    
    y = 100
    for line in lines:
        draw.text((20, y), line, fill=(60, 60, 100), font=font_text)
        y += 20
    
    img.save(output_path)
    print(f'⚠️ Placeholder image created: {output_path}')
    print(f'   PlantUML source saved: {puml_path}')
    return output_path


def save_artifact(content: str, filepath: str) -> str:
    """Save generated content to file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✅ Saved: {filepath}')
    return filepath


def generate_sdlc_docs(business_problem: str, client) -> Dict[str, str]:
    """Generate complete SDLC documentation."""
    docs = {}
    
    print('📝 Generating problem statement...')
    docs['problem_statement'] = generate_problem_statement(business_problem, client)
    
    print('📝 Generating user stories...')
    docs['user_stories'] = generate_user_stories(docs['problem_statement'], client)
    
    print('📝 Generating requirements...')
    docs['requirements'] = generate_requirements(docs['problem_statement'], docs['user_stories'], client)
    
    print('📝 Generating UML diagram...')
    docs['plantuml'] = generate_plantuml_diagram(docs['user_stories'], client)
    
    return docs


def generate_flask_app(user_stories: List[Dict[str, Any]], client, output_dir: str = 'app') -> str:
    """Generate complete Flask application."""
    print('🔧 Generating Flask API...')
    api_code = generate_flask_api(user_stories, client)
    
    if api_code:
        output_path = Path(output_dir) / 'main.py'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(api_code)
        print(f'✅ Flask API saved to {output_path}')
        return str(output_path)
    return ''


def generate_website_html(user_stories: List[Dict[str, Any]], client, output_dir: str = 'app') -> str:
    """Generate website HTML."""
    print('🌐 Generating website...')
    html_code = generate_website(user_stories, client)
    
    if html_code:
        output_path = Path(output_dir) / 'templates' / 'index.html'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_code)
        print(f'✅ Website saved to {output_path}')
        return str(output_path)
    return ''


def run_tests(test_path: str = 'tests') -> Dict[str, Any]:
    """Run pytest tests."""
    if not Path(test_path).exists():
        return {'success': False, 'error': 'Test path not found'}
    
    try:
        completed = subprocess.run(
            ['pytest', '-q', test_path],
            capture_output=True, text=True, timeout=120
        )
        return {
            'success': completed.returncode == 0,
            'output': completed.stdout + completed.stderr,
            'returncode': completed.returncode
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def clean_llm_output(output: str, language: str = 'text') -> str:
    """Clean and format LLM output."""
    if not output:
        return ''
    
    # Remove markdown code blocks
    output = output.replace('```python', '').replace('```html', '').replace('```json', '').replace('```', '')
    output = output.strip()
    
    if language == 'json':
        try:
            # Fix potential JSON issues
            output = output.replace("'", '"')
            json.loads(output)
        except:
            pass
    
    return output


def get_image_generation_completion(prompt: str, client=None, model_name: str = None, api_provider: str = None) -> Tuple[str, str]:
    """
    Generates an image from a text prompt using APIFREE image generation API.
    
    Uses the async task submission and polling approach:
    1. Submit request to /v1/image/submit
    2. Poll /v1/image/{request_id}/result for completion
    
    Args:
        prompt (str): The text description of the image to generate
        client: Unused but kept for API compatibility
        model_name (str): The model to use (e.g., 'qwen/qwen-image')
        api_provider (str): Provider name (e.g., 'apifree')
    
    Returns:
        Tuple[str, str]: (file_path, data_url) on success, (None, error_message) on failure
    """
    print("Generating image... This may take a moment.")
    start_time = time.time()
    
    api_key = os.getenv('APIFREE_API_KEY') or os.getenv('FREEAPI_KEY')
    if not api_key:
        return None, "Error: APIFREE_API_KEY not found in .env file."
    
    base_url = os.getenv('APIFREE_API_BASE', 'https://api.apifree.ai')
    if not model_name:
        model_name = os.getenv('IMAGE_MODEL', 'qwen/qwen-image')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "num_images": 1,
        "width": 1024,
        "height": 1024,
        "num_inference_steps": 50,
    }
    
    try:
        # Step 1: Submit the request
        submit_response = requests.post(
            f"{base_url}/v1/image/submit",
            headers=headers,
            json=payload,
            timeout=30,
        )
        
        if not submit_response.ok:
            return None, f"APIFREE submission failed: {submit_response.status_code} {submit_response.text}"
        
        submit_data = submit_response.json()
        
        if submit_data.get("code") != 200:
            return None, f"APIFREE submission failed: {submit_data.get('error', submit_data.get('code_msg'))}"
        
        request_id = submit_data.get("resp_data", {}).get("request_id")
        if not request_id:
            return None, f"APIFREE did not return request_id: {submit_data}"
        
        print(f"Task submitted. Request ID: {request_id}")
        
        # Step 2: Poll for result
        max_polls = 60
        poll_interval = 2
        
        for poll_count in range(max_polls):
            time.sleep(poll_interval)
            
            check_response = requests.get(
                f"{base_url}/v1/image/{request_id}/result",
                headers=headers,
                timeout=30,
            )
            
            if not check_response.ok:
                continue
            
            check_data = check_response.json()
            
            if check_data.get("code") != 200:
                continue
            
            status = check_data.get("resp_data", {}).get("status", "unknown")
            
            if status == "success":
                image_list = check_data.get("resp_data", {}).get("image_list", [])
                if not image_list:
                    return None, "APIFREE returned no images"
                
                # Download the first image
                img_url = image_list[0]
                img_response = requests.get(img_url, timeout=30)
                img_response.raise_for_status()
                
                image_data_base64 = base64.b64encode(img_response.content).decode('utf-8')
                
                # Save the image
                duration = time.time() - start_time
                print(f"✅ Image generated in {duration:.2f} seconds.")
                
                # Create output path
                timestamp = int(time.time() * 1000)
                output_path = Path('artifacts') / f'image_{timestamp}.png'
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"✅ Image saved to: {output_path}")
                
                return str(output_path), f"data:image/png;base64,{image_data_base64}"
            
            elif status in {"error", "failed"}:
                error_msg = check_data.get("resp_data", {}).get("error", "Unknown error")
                return None, f"APIFREE task failed: {error_msg}"
            
            if (poll_count + 1) % 5 == 0:
                print(f"Still generating image... (poll {poll_count + 1}/{max_polls})")
        
        return None, "APIFREE task timed out after 2 minutes"
        
    except requests.exceptions.RequestException as e:
        return None, f"APIFREE API error: {e}"
    except Exception as e:
        return None, f"Image generation error: {e}"


def get_completion(prompt: str, client, model_name: str, api_provider: str, temperature: float = 0.7) -> str:
    """
    Unified text completion function compatible with the reference utils.py approach.
    """
    if not client and api_provider != 'apifree':
        return "API client not initialized."
    
    if api_provider == 'apifree':
        api_key = os.getenv('APIFREE_API_KEY') or os.getenv('FREEAPI_KEY')
        if not api_key:
            return "Error: APIFREE_API_KEY not found in .env file."
        
        base_url = os.getenv('APIFREE_API_BASE', 'https://api.apifree.ai')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 8192,
            "temperature": temperature,
        }
        
        try:
            resp = requests.post(f"{base_url}/v1/chat/completions", headers=headers, json=payload, timeout=120)
            if not resp.ok:
                return f"APIFREE error: {resp.status_code} {resp.text}"
            
            data = resp.json()
            choices = data.get("choices")
            if not choices:
                return f"APIFREE error: No choices in response"
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            return content
            
        except Exception as e:
            return f"APIFREE request failed: {e}"
    
    return "Unsupported API provider"


def setup_llm_client(model_name: str = "openai/gpt-5.2"):
    """
    Setup and return LLM client with provider info.
    Matches the reference utils.py approach.
    """
    load_environment()
    
    # Map model names to providers
    model_to_provider = {
        "openai/gpt-5.2": "apifree",
        "openai/gpt-4o": "apifree",
        "google/gemini-2.5-pro": "apifree",
        "qwen/qwen-image": "apifree",
    }
    
    api_provider = model_to_provider.get(model_name, "apifree")
    client = {"provider": api_provider}  # Dummy client for apifree
    
    api_key = os.getenv('APIFREE_API_KEY') or os.getenv('FREEAPI_KEY')
    if not api_key:
        print("Warning: APIFREE_API_KEY not found in .env file.")
    
    print(f"✅ LLM Client configured: Using '{api_provider}' with model '{model_name}'")
    return client, model_name, api_provider
