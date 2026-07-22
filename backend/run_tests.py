import urllib.request
import json
import time

url = 'http://127.0.0.1:8000/api/copilot/chat'
headers = {'Content-Type': 'application/json'}

questions = [
    ('A', 'What is the required UPS efficiency?'),
    ('B', 'Which equipment currently threatens the commissioning schedule?'),
    ('C', 'What is the required battery autonomy?'),
    ('D', 'Tell me about RFI-042.'),
    ('E', 'What fire suppression system is specified for Data Hall 3?')
]

results = {}

for letter, q in questions:
    data = json.dumps({'question': q}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            results[letter] = {
                'status': 'SUCCESS',
                'question': q,
                'response': res_json
            }
            print(f"=== TEST {letter} ===")
            print(f"Question: {q}")
            print(f"Role: {res_json.get('role')}")
            print(f"Content:\n{res_json.get('content')}")
            print(f"Sources: {res_json.get('sources')}")
            print(f"Meta: {res_json.get('meta')}")
            print("=" * 60 + "\n")
    except Exception as e:
        results[letter] = {
            'status': 'ERROR',
            'question': q,
            'error': str(e)
        }
        print(f"=== TEST {letter} FAILED: {e} ===\n")
    
    time.sleep(2)

with open('test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
