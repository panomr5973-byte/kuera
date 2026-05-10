import requests

# Test predict dan feedback langsung
r = requests.post('http://localhost:8000/predict', 
    json={'model_id': 'best_model_logistic_regression'})
print(f'Predict status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Interaction ID: {data.get("interaction_id")}')
    
    # Feedback
    r2 = requests.post('http://localhost:8000/feedback', 
        json={'interaction_id': data['interaction_id'], 'feedback': 1})
    print(f'Feedback status: {r2.status_code}')
    print(f'Response: {r2.text}')
