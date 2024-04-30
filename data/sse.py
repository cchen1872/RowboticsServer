def format_sse(data: str, event=None) -> str:
    end = chr(6) * 10000
    msg = f'data: {data}{end}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg