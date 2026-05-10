'''Human-AI Feedback Loop Module.'''

import json
import redis  # Assume installed

class FeedbackLoop:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0)

    def collect_feedback(self, user_id, response, rating):
        '''Store user feedback.'''
        feedback = {'user_id': user_id, 'rating': rating, 'response': response}
        self.r.lpush(f'feedback:{user_id}', json.dumps(feedback))

    def analyze_trends(self, user_id):
        '''Analyze avg rating, trigger improvement.'''
        feedbacks = self.r.lrange(f'feedback:{user_id}', 0, 10)
        ratings = [json.loads(f)['rating'] for f in feedbacks]
        avg = sum(ratings) / len(ratings) if ratings else 0
        if avg < 3.0:
            print('Low feedback: Trigger model fine-tune')
        return avg

# Example
if __name__ == '__main__':
    loop = FeedbackLoop()
    loop.collect_feedback('user1', 'Good response', 4)
    print(loop.analyze_trends('user1'))

