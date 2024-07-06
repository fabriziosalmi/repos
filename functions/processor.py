from datetime import datetime

def humanize_commit_date(commit_date):
    now = datetime.utcnow()
    diff = now - commit_date

    if diff.days == 0:
        return 'today'
    elif diff.days == 1:
        return 'yesterday'
    elif diff.days < 7:
        return f'{diff.days} days'
    elif diff.days < 30:
        weeks = diff.days // 7
        return f'{weeks} {"week" if weeks == 1 else "weeks"}'
    elif diff.days < 365:
        months = diff.days // 30
        return f'{months} {"month" if months == 1 else "months"}'
    else:
        years = diff.days // 365
        return f'{years} {"year" if years == 1 else "years"}'

def get_freshness_badge(humanized_commit_date, for_markdown=False):
    color = 'lightgrey'
    if 'today' in humanized_commit_date or 'yesterday' in humanized_commit_date or 'days' in humanized_commit_date or '1 week' in humanized_commit_date:
        color = 'brightgreen'
    elif 'weeks' in humanized_commit_date or '1 month' in humanized_commit_date:
        color = 'yellow'
    elif 'months' in humanized_commit_date or '1 year' in humanized_commit_date:
        color = 'orange'
    elif 'years' in humanized_commit_date:
        color = 'red'

    if for_markdown:
        return f'![{humanized_commit_date}](https://img.shields.io/badge/{humanized_commit_date.replace(" ", "%20")}-{color}?style=flat-square)'
    return f'<img src="https://img.shields.io/badge/{humanized_commit_date.replace(" ", "%20")}-{color}?style=flat-square" alt="{humanized_commit_date}">'
