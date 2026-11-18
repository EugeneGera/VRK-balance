"""Join verified task timings to the agent audit without mixing execution modes."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import json
from pathlib import Path
from statistics import median


def read_events(path):
    grouped = defaultdict(dict)
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except ValueError:
                continue  # Container logs also contain startup messages.
            if isinstance(event, dict) and event.get('attempt_id') and event.get('request_id'):
                grouped[event['attempt_id']][event['request_id']] = event
    return {key: list(events.values()) for key, events in grouped.items()}


def timestamp(value):
    if not value:
        return None
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.utcoffset() is None:
        raise ValueError('Укажите часовой пояс в started_at и verified_at.')
    return stamp


def attempt_events(row, events):
    start, end = timestamp(row['started_at']), timestamp(row['verified_at'])
    return sorted(
        (event for event in events
         if (not start or timestamp(event['started_at']) >= start)
         and (not end or timestamp(event['finished_at']) <= end)),
        key=lambda event: timestamp(event['finished_at']),
    )


def classify(events, profile):
    if not events:
        return 'missing_audit'
    if any(event.get('execution_mode') == 'template' for event in events):
        return 'template'
    if any(event.get('outcome') == 'error' for event in events):
        return 'error'
    if any(event.get('profile') != 'experiment' or event.get('action') != 'chat'
           or event.get('model_requested') != profile['model']
           or event.get('model_digest') != profile['digest']
           or event.get('model_settings') != profile['settings'] for event in events):
        return 'different_configuration'
    last = events[-1]
    if last['outcome'] == 'clarification':
        return 'waiting_for_clarification'
    if last['outcome'] != 'report' or last.get('execution_mode') != 'agent' or last.get('model') != profile['model']:
        return 'other_mode'
    return 'agent'


def accepted(row):
    return all(row[key].strip().lower() in ('1', 'true', 'yes', 'да')
               for key in ('correctness_passed', 'completeness_passed'))


def summarize(rows, events, profile):
    counts = Counter()
    successful = defaultdict(list)
    attempts = []
    seen = set()
    for row in rows:
        condition = row['condition'].strip()
        if condition not in ('manual', 'agent'):
            raise ValueError('Условие должно быть manual или agent.')
        attempt_id = row['attempt_id'].strip()
        start, end = timestamp(row['started_at']), timestamp(row['verified_at'])
        if start and end and end < start:
            raise ValueError('verified_at предшествует started_at.')
        if condition == 'agent':
            if not attempt_id or attempt_id in seen:
                raise ValueError('Для каждой агентной попытки нужен уникальный attempt_id.')
            seen.add(attempt_id)
        trace = attempt_events(row, events.get(attempt_id, [])) if condition == 'agent' else []
        outcome = classify(trace, profile) if condition == 'agent' else 'manual'
        seconds = (end - start).total_seconds() if start and end else None
        if outcome in ('agent', 'manual'):
            if seconds is None:
                outcome += '_unverified'
            elif not accepted(row):
                outcome += '_quality_failed'
            else:
                successful[outcome].append(seconds)
        counts[outcome] += 1
        last = trace[-1] if trace else {}
        attempts.append(dict(task_id=row['task_id'], condition=condition, attempt_id=attempt_id,
            outcome=outcome, total_seconds=seconds,
            correction_count=int(row['correction_count'] or 0), model=last.get('model'),
            model_requested=last.get('model_requested'), model_digest=last.get('model_digest'),
            execution_mode=last.get('execution_mode'),
            clarification_count=sum(event.get('clarification_count', 0) for event in trace)
                if condition == 'agent' else int(row['clarification_count'] or 0),
            fallback_reasons=sorted({event['fallback_reason'] for event in trace if event.get('fallback_reason')}),
            error_codes=sorted({event['error_code'] for event in trace if event.get('error_code')})))
    return dict(attempts=attempts, counts=dict(counts),
                median_verified_seconds={key: median(values) for key, values in successful.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path, default=Path('experiments/measurements.csv'))
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--profile', type=Path, default=Path('.runtime/experiment-profile.json'))
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text(encoding='utf-8'))
    events = read_events(args.audit)
    with args.measurements.open(encoding='utf-8', newline='') as stream:
        report = summarize(csv.DictReader(stream), events, profile)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
