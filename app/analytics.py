def __get_latest_answer(answers: list) -> dict:
    total_answers = len(answers)

    if total_answers > 1:
        answer = max(answers, key=lambda answer: answer['trial'])
    elif total_answers == 1:
        answer = answers[0]
    else:
        answer = {}
    return answer

def __parse_question(question: dict):
    latest_answer = __get_latest_answer(question.get('answers', []))
    return {'question': question['question'],
            'question_id': question['question_id'].split('__')[0],
            'chapter': question['chapterIndex'],
            'answer': latest_answer.get('answer'),
            'points': latest_answer.get('points'),
            'trial': latest_answer.get('trial')}

def parse_events(event: dict):
    return {
        "user_id": event['user_id'],
        "event_id": event['event_id'],
        "submission_date": event['created'],
        "submitted_data": [__parse_question(question) for question in event['questions']]
    }
